"""Collision Vector Monitor — Section 29.4.

4D trajectory prediction with clearance-aware conflict detection.
Three-tier escalation: Advisory (<5nm/90s), Warning (<3nm/45s), Critical (<1nm/15s).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from sim.types import Alert, AlertSeverity, make_id
from sim.geometry import distance_nm, project_position, time_to_cpa
from sim.clock import SimClock
from sim.events import EventBus

if TYPE_CHECKING:
    from sim.engine.surveillance import SurveillanceStore


@dataclass
class CVMConflict:
    entity_a: str
    entity_b: str
    cpa_nm: float
    time_to_cpa_sec: float
    tier: AlertSeverity
    resolution_options: list[str]


# Tier thresholds (composite: distance OR time, whichever fires first)
TIER_THRESHOLDS = [
    (AlertSeverity.CRITICAL, 1.0, 15.0),   # <1nm OR <15s
    (AlertSeverity.WARNING, 3.0, 45.0),     # <3nm OR <45s
    (AlertSeverity.ADVISORY, 5.0, 90.0),    # <5nm OR <90s
]


def _classify_tier(cpa_nm: float, time_sec: float) -> AlertSeverity | None:
    """Classify conflict severity. Returns highest tier matched."""
    for severity, dist_thresh, time_thresh in TIER_THRESHOLDS:
        if cpa_nm <= dist_thresh or (time_sec > 0 and time_sec <= time_thresh):
            return severity
    return None


class CollisionVectorMonitor:
    """4D trajectory prediction with clearance-aware conflict detection."""

    def __init__(
        self,
        surveillance: SurveillanceStore,
        event_bus: EventBus,
        clock: SimClock,
    ) -> None:
        self._surveillance = surveillance
        self._event_bus = event_bus
        self._clock = clock
        self._active_conflicts: dict[tuple[str, str], CVMConflict] = {}

    def detect_conflicts(self) -> list[CVMConflict]:
        """Check all entity pairs for projected conflicts.

        Uses trajectory projection (120-second horizon).
        Alerts on unexpected convergence, not raw proximity.
        """
        tracks = self._surveillance.get_all_tracks()
        entities = list(tracks.keys())
        conflicts: list[CVMConflict] = []

        for i in range(len(entities)):
            for j in range(i + 1, len(entities)):
                eid_a, eid_b = entities[i], entities[j]
                track_a, track_b = tracks[eid_a], tracks[eid_b]

                # Skip ground vehicles vs ground vehicles
                if track_a.position.altitude_ft < 100 and track_b.position.altitude_ft < 100:
                    continue

                t_cpa, d_cpa = time_to_cpa(
                    track_a.position, track_a.velocity,
                    track_b.position, track_b.velocity,
                    max_horizon_sec=120.0,
                    step_sec=5.0,
                )

                tier = _classify_tier(d_cpa, t_cpa)
                if tier is None:
                    # Remove from active conflicts if it was there
                    key = (min(eid_a, eid_b), max(eid_a, eid_b))
                    self._active_conflicts.pop(key, None)
                    continue

                # Compute basic resolution options
                resolution = self._compute_resolution(
                    eid_a, track_a.position, track_a.velocity,
                    eid_b, track_b.position, track_b.velocity,
                )

                conflict = CVMConflict(
                    entity_a=eid_a,
                    entity_b=eid_b,
                    cpa_nm=d_cpa,
                    time_to_cpa_sec=t_cpa,
                    tier=tier,
                    resolution_options=resolution,
                )

                key = (min(eid_a, eid_b), max(eid_a, eid_b))
                self._active_conflicts[key] = conflict
                conflicts.append(conflict)

        return conflicts

    def _compute_resolution(
        self,
        eid_a: str, pos_a, vel_a,
        eid_b: str, pos_b, vel_b,
    ) -> list[str]:
        """Three-axis resolution options: lateral, vertical, speed."""
        options = []

        # Lateral: turn one aircraft
        options.append(f"Turn {eid_a} heading +30deg")
        options.append(f"Turn {eid_b} heading +30deg")

        # Vertical: climb/descend (only if altitude allows)
        if pos_a.altitude_ft > 1000:
            options.append(f"Descend {eid_a} 1000ft")
        if pos_b.altitude_ft > 1000:
            options.append(f"Descend {eid_b} 1000ft")
        options.append(f"Climb {eid_a} 1000ft")
        options.append(f"Climb {eid_b} 1000ft")

        # Speed: slow one aircraft
        if vel_a.ground_speed_kts > 100:
            options.append(f"Slow {eid_a} to {vel_a.ground_speed_kts - 30:.0f}kts")
        if vel_b.ground_speed_kts > 100:
            options.append(f"Slow {eid_b} to {vel_b.ground_speed_kts - 30:.0f}kts")

        return options

    def tick(self) -> list[Alert]:
        """Run conflict detection. Returns new/escalated alerts."""
        conflicts = self.detect_conflicts()
        alerts: list[Alert] = []

        for conflict in conflicts:
            topic = {
                AlertSeverity.ADVISORY: "alert.separation_advisory",
                AlertSeverity.WARNING: "alert.separation_warning",
                AlertSeverity.CRITICAL: "alert.separation_critical",
            }[conflict.tier]

            alert = Alert(
                alert_id=make_id("ALERT"),
                alert_type=topic,
                severity=conflict.tier,
                affected_entities=[conflict.entity_a, conflict.entity_b],
                description=(
                    f"CVM {conflict.tier.value}: {conflict.entity_a} and {conflict.entity_b} "
                    f"CPA {conflict.cpa_nm:.1f}nm in {conflict.time_to_cpa_sec:.0f}s"
                ),
                recommended_action=conflict.resolution_options[0] if conflict.resolution_options else None,
                timestamp=self._clock.now(),
            )
            alerts.append(alert)
            self._event_bus.publish(topic, "cvm", alert)

        return alerts

    def get_active_conflicts(self) -> dict[tuple[str, str], CVMConflict]:
        return dict(self._active_conflicts)
