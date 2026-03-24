"""IFR aircraft state machine — Section 28.2.

Hierarchical state machine with phases containing sub-states.
A flight is always in exactly one state (except EMERGENCY overlay).
Transition guards enforce F1: no transition without required clearance.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from sim.types import (
    IFRPhase, IFRState, ClearanceType, STATE_TO_PHASE,
    LatLonAlt, Vector3D, FlightStateSnapshot,
)
from sim.clock import SimClock
from sim.events import EventBus


@dataclass
class TransitionRule:
    from_state: IFRState
    to_state: IFRState
    clearance_type: ClearanceType | None  # None = surveillance-triggered
    description: str = ""


# All valid transitions from Section 28.2.2 - 28.3.4
TRANSITION_TABLE: list[TransitionRule] = [
    # Departure transitions (28.2.2)
    TransitionRule(IFRState.PARKED, IFRState.CLEARANCE_DELIVERED, ClearanceType.IFR_CLEARANCE),
    TransitionRule(IFRState.PARKED, IFRState.PUSHBACK_APPROVED, ClearanceType.PUSHBACK_APPROVAL),
    TransitionRule(IFRState.CLEARANCE_DELIVERED, IFRState.PUSHBACK_APPROVED, ClearanceType.PUSHBACK_APPROVAL),
    TransitionRule(IFRState.PUSHBACK_APPROVED, IFRState.TAXIING_OUT, ClearanceType.TAXI_OUT),
    TransitionRule(IFRState.TAXIING_OUT, IFRState.HOLDING_SHORT, None, "Surveillance: at hold line"),
    TransitionRule(IFRState.HOLDING_SHORT, IFRState.LINEUP_WAIT, ClearanceType.LINEUP_WAIT),
    TransitionRule(IFRState.HOLDING_SHORT, IFRState.TAKEOFF_ROLL, ClearanceType.TAKEOFF),
    TransitionRule(IFRState.LINEUP_WAIT, IFRState.TAKEOFF_ROLL, ClearanceType.TAKEOFF),
    TransitionRule(IFRState.TAKEOFF_ROLL, IFRState.AIRBORNE_DEPARTURE, None, "Surveillance: liftoff"),
    TransitionRule(IFRState.AIRBORNE_DEPARTURE, IFRState.DEPARTURE_CONTACT, ClearanceType.FREQUENCY_CHANGE),

    # Aborted takeoff (28.2.3)
    TransitionRule(IFRState.TAKEOFF_ROLL, IFRState.LINEUP_WAIT, None, "Pilot abort below V1"),
    TransitionRule(IFRState.LINEUP_WAIT, IFRState.HOLDING_SHORT, None, "Exit runway instruction"),
    TransitionRule(IFRState.LINEUP_WAIT, IFRState.TAXIING_OUT, None, "Surveillance: taxied off runway"),

    # TRACON departure (28.3.1)
    TransitionRule(IFRState.DEPARTURE_CONTACT, IFRState.DEPARTURE_CLIMBING, ClearanceType.ALTITUDE_HEADING),
    TransitionRule(IFRState.DEPARTURE_CLIMBING, IFRState.CENTER_HANDOFF, ClearanceType.FREQUENCY_CHANGE),
    TransitionRule(IFRState.CENTER_HANDOFF, IFRState.FLIGHT_COMPLETE, None, "Exits TRACON"),

    # TRACON arrival (28.3.2)
    TransitionRule(IFRState.ARRIVAL_INBOUND, IFRState.SEQUENCED, ClearanceType.SEQUENCE_ASSIGNMENT),
    TransitionRule(IFRState.SEQUENCED, IFRState.VECTORING, ClearanceType.VECTORING),
    TransitionRule(IFRState.SEQUENCED, IFRState.APPROACH_CLEARED, ClearanceType.APPROACH_CLEARANCE),
    TransitionRule(IFRState.VECTORING, IFRState.VECTORING, ClearanceType.VECTORING, "Multiple vectors"),
    TransitionRule(IFRState.VECTORING, IFRState.APPROACH_CLEARED, ClearanceType.APPROACH_CLEARANCE),
    TransitionRule(IFRState.APPROACH_CLEARED, IFRState.ESTABLISHED, None, "Surveillance: on approach path"),
    TransitionRule(IFRState.ESTABLISHED, IFRState.TOWER_HANDOFF, ClearanceType.FREQUENCY_CHANGE),

    # Tower arrival (28.3.3)
    TransitionRule(IFRState.TOWER_HANDOFF, IFRState.INBOUND, None, "Pilot contacts tower"),
    TransitionRule(IFRState.INBOUND, IFRState.FINAL_APPROACH, None, "Surveillance: crosses FAF"),
    TransitionRule(IFRState.INBOUND, IFRState.LANDING_CLEARED, ClearanceType.LANDING, "Early clearance"),
    TransitionRule(IFRState.FINAL_APPROACH, IFRState.LANDING_CLEARED, ClearanceType.LANDING),
    TransitionRule(IFRState.LANDING_CLEARED, IFRState.LANDING_ROLL, None, "Surveillance: touchdown"),
    TransitionRule(IFRState.LANDING_ROLL, IFRState.RUNWAY_EXIT, None, "Surveillance: exiting runway"),
    TransitionRule(IFRState.RUNWAY_EXIT, IFRState.TAXIING_IN, ClearanceType.TAXI_IN),
    TransitionRule(IFRState.TAXIING_IN, IFRState.PARKED_IN, None, "Surveillance: at gate"),
    TransitionRule(IFRState.PARKED_IN, IFRState.FLIGHT_COMPLETE, None, "Systems release"),

    # Go-around (28.3.4)
    TransitionRule(IFRState.FINAL_APPROACH, IFRState.GO_AROUND_CLIMB, ClearanceType.GO_AROUND),
    TransitionRule(IFRState.LANDING_CLEARED, IFRState.GO_AROUND_CLIMB, ClearanceType.GO_AROUND),
    TransitionRule(IFRState.LANDING_ROLL, IFRState.GO_AROUND_CLIMB, None, "Pilot rejected landing"),
    TransitionRule(IFRState.GO_AROUND_CLIMB, IFRState.RESEQUENCED, None, "On missed approach"),
    TransitionRule(IFRState.RESEQUENCED, IFRState.SEQUENCED, ClearanceType.SEQUENCE_ASSIGNMENT, "Re-entered TRACON"),
]


# Build lookup: from_state -> [(to_state, clearance_type)]
_TRANSITIONS_BY_STATE: dict[IFRState, list[TransitionRule]] = {}
for rule in TRANSITION_TABLE:
    _TRANSITIONS_BY_STATE.setdefault(rule.from_state, []).append(rule)


class FlightStateMachine:
    def __init__(
        self,
        flight_id: str,
        initial_state: IFRState,
        clock: SimClock,
        event_bus: EventBus,
        position: LatLonAlt | None = None,
        velocity: Vector3D | None = None,
        runway_assignment: str | None = None,
        aircraft_type: str = "B737",
    ) -> None:
        self.flight_id = flight_id
        self.state = initial_state
        self.phase = STATE_TO_PHASE.get(initial_state)
        self.emergency = False
        self.position = position or LatLonAlt(0, 0, 0)
        self.velocity = velocity or Vector3D()
        self.runway_assignment = runway_assignment
        self.aircraft_type = aircraft_type
        self.active_clearance_ids: list[str] = []
        self._clock = clock
        self._event_bus = event_bus

    def can_transition(
        self, to_state: IFRState, clearance_type: ClearanceType | None = None,
    ) -> bool:
        rules = _TRANSITIONS_BY_STATE.get(self.state, [])
        for rule in rules:
            if rule.to_state == to_state:
                if rule.clearance_type is None:
                    return True  # surveillance-triggered, no clearance needed
                if clearance_type == rule.clearance_type:
                    return True
        return False

    def transition(
        self, to_state: IFRState, clearance_type: ClearanceType | None = None,
    ) -> bool:
        if not self.can_transition(to_state, clearance_type):
            return False

        old_state = self.state
        self.state = to_state
        self.phase = STATE_TO_PHASE.get(to_state, self.phase)

        self._event_bus.publish(
            f"flight.{self.flight_id}.state_changed",
            "flight_state_machine",
            {
                "flight_id": self.flight_id,
                "from_state": old_state.value,
                "to_state": to_state.value,
                "phase": self.phase.value if self.phase else None,
                "clearance_type": clearance_type.value if clearance_type else None,
            },
        )
        return True

    def enter_emergency(self) -> None:
        self.emergency = True
        self._event_bus.publish(
            f"flight.{self.flight_id}.emergency",
            "flight_state_machine",
            {"flight_id": self.flight_id, "state": self.state.value, "action": "declared"},
        )

    def resolve_emergency(self) -> None:
        self.emergency = False
        self._event_bus.publish(
            f"flight.{self.flight_id}.emergency",
            "flight_state_machine",
            {"flight_id": self.flight_id, "state": self.state.value, "action": "resolved"},
        )

    def snapshot(self) -> FlightStateSnapshot:
        return FlightStateSnapshot(
            flight_id=self.flight_id,
            phase=self.phase,
            state=self.state,
            emergency=self.emergency,
            position=self.position,
            velocity=self.velocity,
            runway_assignment=self.runway_assignment,
            active_clearance_ids=list(self.active_clearance_ids),
        )
