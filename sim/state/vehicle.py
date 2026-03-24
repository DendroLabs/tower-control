"""Ground vehicle state machine — Section 28.7.

The LGA collision prevention state machine. Vehicles compete for
the same runway locks as aircraft.
"""

from __future__ import annotations

from dataclasses import dataclass

from sim.types import VehicleState, ClearanceType, LatLonAlt, Vector3D
from sim.clock import SimClock
from sim.events import EventBus


@dataclass
class VehicleTransitionRule:
    from_state: VehicleState
    to_state: VehicleState
    clearance_type: ClearanceType | None


VEHICLE_TRANSITIONS: list[VehicleTransitionRule] = [
    VehicleTransitionRule(VehicleState.STATIONARY, VehicleState.TAXI_CLEARED, ClearanceType.TAXI_OUT),
    VehicleTransitionRule(VehicleState.TAXI_CLEARED, VehicleState.MOVING, None),  # surveillance
    VehicleTransitionRule(VehicleState.MOVING, VehicleState.HOLDING_SHORT, None),  # surveillance: at hold line
    VehicleTransitionRule(VehicleState.HOLDING_SHORT, VehicleState.CROSSING_CLEARED, ClearanceType.RUNWAY_CROSSING),
    VehicleTransitionRule(VehicleState.CROSSING_CLEARED, VehicleState.ON_RUNWAY, None),  # surveillance
    VehicleTransitionRule(VehicleState.ON_RUNWAY, VehicleState.CLEAR_OF_RUNWAY, None),  # surveillance
    VehicleTransitionRule(VehicleState.CLEAR_OF_RUNWAY, VehicleState.MOVING, None),  # continues route
    VehicleTransitionRule(VehicleState.MOVING, VehicleState.STATIONARY, None),  # arrives at destination
]

_VEHICLE_BY_STATE: dict[VehicleState, list[VehicleTransitionRule]] = {}
for rule in VEHICLE_TRANSITIONS:
    _VEHICLE_BY_STATE.setdefault(rule.from_state, []).append(rule)


class VehicleStateMachine:
    def __init__(
        self,
        vehicle_id: str,
        vehicle_type: str,
        clock: SimClock,
        event_bus: EventBus,
        initial_state: VehicleState = VehicleState.STATIONARY,
        position: LatLonAlt | None = None,
    ) -> None:
        self.vehicle_id = vehicle_id
        self.vehicle_type = vehicle_type
        self.state = initial_state
        self.position = position or LatLonAlt(0, 0, 0)
        self.velocity = Vector3D()
        self.active_clearance_ids: list[str] = []
        self._clock = clock
        self._event_bus = event_bus

    def can_transition(
        self, to_state: VehicleState, clearance_type: ClearanceType | None = None,
    ) -> bool:
        rules = _VEHICLE_BY_STATE.get(self.state, [])
        for rule in rules:
            if rule.to_state == to_state:
                if rule.clearance_type is None:
                    return True
                if clearance_type == rule.clearance_type:
                    return True
        return False

    def transition(
        self, to_state: VehicleState, clearance_type: ClearanceType | None = None,
    ) -> bool:
        if not self.can_transition(to_state, clearance_type):
            return False

        old_state = self.state
        self.state = to_state

        self._event_bus.publish(
            f"vehicle.{self.vehicle_id}.state_changed",
            "vehicle_state_machine",
            {
                "vehicle_id": self.vehicle_id,
                "from_state": old_state.value,
                "to_state": to_state.value,
                "vehicle_type": self.vehicle_type,
            },
        )
        return True
