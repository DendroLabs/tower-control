"""Simulated surveillance feeds — position updates via trajectory interpolation.

Entities move along scripted waypoint trajectories. The surveillance store
interpolates between waypoints as the clock advances. Supports injection
of untracked entities (DCA scenario — S4 detection).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from sim.types import LatLonAlt, Vector3D, SurveillanceSource
from sim.geometry import project_position, bearing_deg, distance_nm
from sim.clock import SimClock
from sim.events import EventBus


@dataclass
class Waypoint:
    time: float  # sim time to reach this point
    position: LatLonAlt
    speed_kts: float = 0.0
    vertical_rate_fpm: float = 0.0


@dataclass
class SurveillanceTrack:
    entity_id: str
    position: LatLonAlt
    velocity: Vector3D
    last_update: float = 0.0
    source: SurveillanceSource = SurveillanceSource.ADSB
    waypoints: list[Waypoint] = field(default_factory=list)
    is_tracked: bool = True  # False for injected untracked entities


class SurveillanceStore:
    """Simulated surveillance data. Entities move along scripted trajectories."""

    def __init__(self, clock: SimClock, event_bus: EventBus, max_age_sec: float = 5.0) -> None:
        self._clock = clock
        self._event_bus = event_bus
        self._max_age_sec = max_age_sec
        self._tracks: dict[str, SurveillanceTrack] = {}

    def add_track(
        self,
        entity_id: str,
        position: LatLonAlt,
        velocity: Vector3D | None = None,
        waypoints: list[Waypoint] | None = None,
        source: SurveillanceSource = SurveillanceSource.ADSB,
    ) -> SurveillanceTrack:
        track = SurveillanceTrack(
            entity_id=entity_id,
            position=position,
            velocity=velocity or Vector3D(),
            last_update=self._clock.now(),
            source=source,
            waypoints=waypoints or [],
            is_tracked=True,
        )
        self._tracks[entity_id] = track
        return track

    def inject_untracked(
        self,
        entity_id: str,
        position: LatLonAlt,
        velocity: Vector3D,
        waypoints: list[Waypoint] | None = None,
    ) -> SurveillanceTrack:
        """Inject an entity visible to sensors but NOT in state machine.
        Simulates DCA scenario — S4 should detect this.
        """
        track = SurveillanceTrack(
            entity_id=entity_id,
            position=position,
            velocity=velocity,
            last_update=self._clock.now(),
            source=SurveillanceSource.RADAR,
            waypoints=waypoints or [],
            is_tracked=False,
        )
        self._tracks[entity_id] = track
        return track

    def update(self) -> None:
        """Interpolate all entity positions based on their trajectories."""
        now = self._clock.now()

        for track in self._tracks.values():
            if track.waypoints:
                self._interpolate_waypoints(track, now)
            else:
                # Simple linear projection
                dt = now - track.last_update
                if dt > 0 and track.velocity.ground_speed_kts > 0:
                    track.position = project_position(track.position, track.velocity, dt)

            track.last_update = now

            self._event_bus.publish(
                f"surveillance.{track.entity_id}.position_update",
                "surveillance",
                {
                    "entity_id": track.entity_id,
                    "position": track.position,
                    "velocity": track.velocity,
                    "source": track.source.value,
                    "timestamp": now,
                },
            )

    def _interpolate_waypoints(self, track: SurveillanceTrack, now: float) -> None:
        """Interpolate position between waypoints."""
        wps = track.waypoints

        # Find the surrounding waypoints
        prev_wp = None
        next_wp = None
        for i, wp in enumerate(wps):
            if wp.time > now:
                next_wp = wp
                prev_wp = wps[i - 1] if i > 0 else None
                break
        else:
            # Past all waypoints — hold at last position
            if wps:
                last = wps[-1]
                track.position = last.position
                track.velocity = Vector3D(
                    ground_speed_kts=last.speed_kts,
                    heading_deg=track.velocity.heading_deg,
                    vertical_rate_fpm=last.vertical_rate_fpm,
                )
            return

        if prev_wp is None:
            # Before first waypoint — hold at first position
            track.position = wps[0].position
            return

        # Linear interpolation between prev_wp and next_wp
        total_dt = next_wp.time - prev_wp.time
        if total_dt <= 0:
            track.position = next_wp.position
            return

        frac = (now - prev_wp.time) / total_dt
        frac = max(0.0, min(1.0, frac))

        lat = prev_wp.position.latitude + frac * (next_wp.position.latitude - prev_wp.position.latitude)
        lon = prev_wp.position.longitude + frac * (next_wp.position.longitude - prev_wp.position.longitude)
        alt = prev_wp.position.altitude_ft + frac * (next_wp.position.altitude_ft - prev_wp.position.altitude_ft)

        track.position = LatLonAlt(lat, lon, alt)

        # Compute velocity from interpolation
        hdg = bearing_deg(prev_wp.position, next_wp.position) if distance_nm(prev_wp.position, next_wp.position) > 0.001 else track.velocity.heading_deg
        spd = prev_wp.speed_kts + frac * (next_wp.speed_kts - prev_wp.speed_kts)
        vr = prev_wp.vertical_rate_fpm + frac * (next_wp.vertical_rate_fpm - prev_wp.vertical_rate_fpm)

        track.velocity = Vector3D(
            ground_speed_kts=spd,
            heading_deg=hdg,
            vertical_rate_fpm=vr,
        )

    def get_position(self, entity_id: str) -> tuple[LatLonAlt, Vector3D, float] | None:
        """Get current position, velocity, and data age."""
        track = self._tracks.get(entity_id)
        if track is None:
            return None
        age = self._clock.now() - track.last_update
        return track.position, track.velocity, age

    def get_track(self, entity_id: str) -> SurveillanceTrack | None:
        return self._tracks.get(entity_id)

    def get_all_tracks(self) -> dict[str, SurveillanceTrack]:
        return dict(self._tracks)

    def get_tracked_ids(self) -> set[str]:
        """IDs of entities in the state machine (tracked)."""
        return {eid for eid, t in self._tracks.items() if t.is_tracked}

    def get_detected_ids(self) -> set[str]:
        """IDs of ALL entities visible to sensors (tracked + untracked)."""
        return set(self._tracks.keys())

    def set_stale(self, entity_id: str, age_sec: float) -> None:
        """Force a track to appear stale for testing S3/C5."""
        track = self._tracks.get(entity_id)
        if track:
            track.last_update = self._clock.now() - age_sec

    def update_position(self, entity_id: str, position: LatLonAlt, velocity: Vector3D | None = None) -> None:
        """Directly set an entity's position (for scripted scenarios)."""
        track = self._tracks.get(entity_id)
        if track:
            track.position = position
            if velocity:
                track.velocity = velocity
            track.last_update = self._clock.now()
