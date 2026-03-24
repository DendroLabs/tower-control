"""VFR traffic pattern state machine — Section 28.4.

Pattern legs transition on pilot discretion (no clearance).
Terminal operations (touch-and-go, etc.) require clearances with PATTERN locks.
"""

from __future__ import annotations

from dataclasses import dataclass

from sim.types import VFRPatternState, ClearanceType, LatLonAlt, Vector3D
from sim.clock import SimClock
from sim.events import EventBus


@dataclass
class VFRTransitionRule:
    from_state: VFRPatternState
    to_state: VFRPatternState
    clearance_type: ClearanceType | None  # None = pilot discretion / surveillance


VFR_TRANSITIONS: list[VFRTransitionRule] = [
    # Pattern legs — pilot discretion
    VFRTransitionRule(VFRPatternState.UPWIND, VFRPatternState.CROSSWIND, None),
    VFRTransitionRule(VFRPatternState.CROSSWIND, VFRPatternState.DOWNWIND, None),
    VFRTransitionRule(VFRPatternState.DOWNWIND, VFRPatternState.BASE, None),
    VFRTransitionRule(VFRPatternState.BASE, VFRPatternState.PATTERN_FINAL, None),

    # Terminal operations — clearance required
    VFRTransitionRule(VFRPatternState.PATTERN_FINAL, VFRPatternState.TOUCH_AND_GO, ClearanceType.TOUCH_AND_GO),
    VFRTransitionRule(VFRPatternState.PATTERN_FINAL, VFRPatternState.STOP_AND_GO, ClearanceType.STOP_AND_GO),
    VFRTransitionRule(VFRPatternState.PATTERN_FINAL, VFRPatternState.LOW_APPROACH, ClearanceType.LOW_APPROACH),
    VFRTransitionRule(VFRPatternState.PATTERN_FINAL, VFRPatternState.FULL_STOP, ClearanceType.LANDING),

    # Back to pattern after operations
    VFRTransitionRule(VFRPatternState.TOUCH_AND_GO, VFRPatternState.UPWIND, None),
    VFRTransitionRule(VFRPatternState.STOP_AND_GO, VFRPatternState.UPWIND, None),
    VFRTransitionRule(VFRPatternState.LOW_APPROACH, VFRPatternState.UPWIND, None),
]

_VFR_BY_STATE: dict[VFRPatternState, list[VFRTransitionRule]] = {}
for rule in VFR_TRANSITIONS:
    _VFR_BY_STATE.setdefault(rule.from_state, []).append(rule)


class VFRPatternStateMachine:
    def __init__(
        self,
        flight_id: str,
        pattern_runway: str,
        clock: SimClock,
        event_bus: EventBus,
        initial_state: VFRPatternState = VFRPatternState.UPWIND,
        position: LatLonAlt | None = None,
        velocity: Vector3D | None = None,
        pattern_altitude_ft: float = 1000.0,
        aircraft_type: str = "C172",
    ) -> None:
        self.flight_id = flight_id
        self.state = initial_state
        self.pattern_runway = pattern_runway
        self.pattern_altitude_ft = pattern_altitude_ft
        self.aircraft_type = aircraft_type
        self.laps_completed = 0
        self.position = position or LatLonAlt(0, 0, pattern_altitude_ft)
        self.velocity = velocity or Vector3D()
        self.active_clearance_ids: list[str] = []
        self._clock = clock
        self._event_bus = event_bus

    def can_transition(
        self, to_state: VFRPatternState, clearance_type: ClearanceType | None = None,
    ) -> bool:
        rules = _VFR_BY_STATE.get(self.state, [])
        for rule in rules:
            if rule.to_state == to_state:
                if rule.clearance_type is None:
                    return True
                if clearance_type == rule.clearance_type:
                    return True
        return False

    def transition(
        self, to_state: VFRPatternState, clearance_type: ClearanceType | None = None,
    ) -> bool:
        if not self.can_transition(to_state, clearance_type):
            return False

        old_state = self.state
        self.state = to_state

        # Track laps
        if to_state == VFRPatternState.UPWIND and old_state in (
            VFRPatternState.TOUCH_AND_GO,
            VFRPatternState.STOP_AND_GO,
            VFRPatternState.LOW_APPROACH,
        ):
            self.laps_completed += 1

        self._event_bus.publish(
            f"flight.{self.flight_id}.vfr_state_changed",
            "vfr_pattern_state_machine",
            {
                "flight_id": self.flight_id,
                "from_state": old_state.value,
                "to_state": to_state.value,
                "laps": self.laps_completed,
            },
        )
        return True
