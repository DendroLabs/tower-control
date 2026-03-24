"""Approach Commitment Gate — Section 28.5.6.

Token-based flow control inspired by Cisco VOQ.
Advisory gate (~5nm): XOFF signal — slow the source.
Commitment gate (~2nm): forcing function — no token = go-around.
"""

from __future__ import annotations

from dataclasses import dataclass

from sim.types import (
    ClearanceType, ClearanceProposal, EntityType,
    Alert, AlertSeverity, SurveillanceRef, SurveillanceSource,
    LatLonAlt, Vector3D, make_id,
)
from sim.state.runway import RunwayLockManager
from sim.state.clearance import ClearanceLifecycle, ClearanceState
from sim.safety.validator import ClearanceValidator
from sim.airport.airspace import ApproachCorridor
from sim.clock import SimClock
from sim.events import EventBus


@dataclass
class AdvisoryGateAlert:
    flight_id: str
    runway_id: str
    lock_holder: str | None
    distance_to_commitment_gate_nm: float


@dataclass
class ForcedGoAround:
    flight_id: str
    runway_id: str
    clearance_id: str
    reason: str


class CommitmentGate:
    """Section 28.5.6: Token-based flow control."""

    def __init__(
        self,
        corridors: dict[str, ApproachCorridor],
        runway_mgr: RunwayLockManager,
        clearance_mgr: ClearanceLifecycle,
        validator: ClearanceValidator,
        event_bus: EventBus,
        clock: SimClock,
    ) -> None:
        self._corridors = corridors
        self._runway_mgr = runway_mgr
        self._clearance_mgr = clearance_mgr
        self._validator = validator
        self._event_bus = event_bus
        self._clock = clock
        # Track which flights already got advisory/go-around to avoid duplicates
        self._advisory_issued: set[str] = set()
        self._go_around_issued: set[str] = set()

    def check(
        self,
        flight_id: str,
        position: LatLonAlt,
        velocity: Vector3D,
        runway_id: str,
        is_vfr: bool = False,
    ) -> AdvisoryGateAlert | ForcedGoAround | None:
        """Check if an approaching aircraft needs advisory or forced go-around.

        Called every tick for aircraft on approach.
        """
        corridor = self._corridors.get(runway_id)
        if corridor is None:
            return None

        # Check if aircraft has a validated landing clearance for this runway
        has_clearance = self._has_landing_clearance(flight_id, runway_id)

        if has_clearance:
            return None  # Aircraft has its token

        # Check if runway is available (no lock or locked by this flight)
        is_locked = self._runway_mgr.is_locked(runway_id)
        lock_holder = self._runway_mgr.get_lock_holder(runway_id)

        # Commitment gate check — only force go-around if runway is locked by another entity
        # and this aircraft has no clearance (Section 28.5.6: no token = go-around)
        gate_nm = corridor.vfr_commitment_gate_nm if is_vfr else corridor.commitment_gate_nm
        if corridor.distance_to_threshold(position) <= gate_nm:
            if is_locked and lock_holder != flight_id:
                if flight_id not in self._go_around_issued:
                    return self._force_go_around(flight_id, position, velocity, runway_id)

        # Advisory gate check
        if corridor.is_past_advisory_gate(position) and is_locked and lock_holder != flight_id:
            if flight_id not in self._advisory_issued:
                self._advisory_issued.add(flight_id)
                dist_to_commit = corridor.distance_to_threshold(position) - gate_nm
                alert = AdvisoryGateAlert(
                    flight_id=flight_id,
                    runway_id=runway_id,
                    lock_holder=lock_holder,
                    distance_to_commitment_gate_nm=max(0, dist_to_commit),
                )
                self._event_bus.publish(
                    "alert.runway_unavailable",
                    "commitment_gate",
                    alert,
                )
                return alert

        return None

    def _has_landing_clearance(self, flight_id: str, runway_id: str) -> bool:
        active = self._clearance_mgr.get_active_for_entity(flight_id)
        for clr in active:
            if clr.clearance_type in (
                ClearanceType.LANDING,
                ClearanceType.TOUCH_AND_GO,
                ClearanceType.STOP_AND_GO,
                ClearanceType.LOW_APPROACH,
            ):
                if clr.parameters.get("runway") == runway_id:
                    return True
        return False

    def _force_go_around(
        self,
        flight_id: str,
        position: LatLonAlt,
        velocity: Vector3D,
        runway_id: str,
    ) -> ForcedGoAround:
        """Safety-net-originated go-around (F5).

        Enters clearance lifecycle at VALIDATED, not PROPOSED.
        """
        self._go_around_issued.add(flight_id)

        # Create and validate go-around clearance (safety net is the validator)
        proposal = ClearanceProposal(
            proposal_id=make_id("PROP"),
            proposing_agent="safety_net",
            timestamp=self._clock.now(),
            target_entity=flight_id,
            target_entity_type=EntityType.AIRCRAFT,
            clearance_type=ClearanceType.GO_AROUND,
            parameters={"runway": runway_id, "reason": "commitment_gate"},
            surveillance_refs=[SurveillanceRef(
                source=SurveillanceSource.RADAR,
                entity_id=flight_id,
                position=position,
                velocity=velocity,
                timestamp=self._clock.now(),
            )],
        )

        result, clr = self._validator.validate(proposal)

        self._event_bus.publish(
            "alert.forced_go_around",
            "commitment_gate",
            {
                "flight_id": flight_id,
                "runway_id": runway_id,
                "clearance_id": clr.clearance_id,
                "reason": "Aircraft past commitment gate without landing clearance (F5)",
            },
        )

        return ForcedGoAround(
            flight_id=flight_id,
            runway_id=runway_id,
            clearance_id=clr.clearance_id,
            reason="Commitment gate: no validated landing clearance (F5)",
        )

    def reset_tracking(self, flight_id: str) -> None:
        """Reset advisory/go-around tracking for a flight (e.g., after re-sequencing)."""
        self._advisory_issued.discard(flight_id)
        self._go_around_issued.discard(flight_id)
