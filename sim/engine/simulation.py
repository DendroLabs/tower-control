"""Main simulation engine — orchestrates the tick cycle.

Manages entity registry, drives the clock, and coordinates all subsystems.
12-step tick cycle per the plan.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from sim.types import (
    ClearanceProposal, InvariantViolation, Alert, IFRState,
    LatLonAlt, Vector3D, reset_ids,
)
from sim.clock import SimClock
from sim.events import EventBus, Event
from sim.airport.layout import AirportLayout, build_reference_airport
from sim.airport.airspace import (
    ClassCAirspace, ApproachCorridor,
    build_reference_airspace, build_approach_corridors,
)
from sim.state.runway import RunwayLockManager
from sim.state.clearance import ClearanceLifecycle
from sim.state.flight import FlightStateMachine
from sim.state.vfr_pattern import VFRPatternStateMachine
from sim.state.vehicle import VehicleStateMachine
from sim.safety.invariants import InvariantChecker
from sim.safety.validator import ClearanceValidator
from sim.safety.commitment_gate import CommitmentGate
from sim.safety.cvm import CollisionVectorMonitor
from sim.safety.negative_space import NegativeSpaceMonitor
from sim.engine.surveillance import SurveillanceStore
from sim.engine.delivery import ClearanceDelivery


@dataclass
class SimulationResult:
    events: list[Event] = field(default_factory=list)
    final_time: float = 0.0
    violations: list[InvariantViolation] = field(default_factory=list)
    alerts: list[Alert] = field(default_factory=list)


class Simulation:
    """Central simulation orchestrator."""

    def __init__(self, airport: AirportLayout | None = None) -> None:
        reset_ids()

        self.airport = airport or build_reference_airport()
        self.airspace = build_reference_airspace(self.airport)
        self.corridors = build_approach_corridors(self.airport)

        self.clock = SimClock(step=1.0)
        self.event_bus = EventBus(self.clock)

        # Physical runway IDs
        physical_ids = list(set(self.airport.physical_runways.values()))
        self.runway_mgr = RunwayLockManager(
            physical_ids,
            self.airport.physical_runways,
            self.clock,
            self.event_bus,
        )

        self.clearance_mgr = ClearanceLifecycle(self.clock, self.event_bus)
        self.invariant_checker = InvariantChecker(
            self.runway_mgr, self.clearance_mgr, self.clock,
        )
        self.validator = ClearanceValidator(
            self.invariant_checker, self.runway_mgr,
            self.clearance_mgr, self.event_bus, self.clock,
        )
        self.surveillance = SurveillanceStore(self.clock, self.event_bus)
        self.delivery = ClearanceDelivery(self.clearance_mgr, self.event_bus, self.clock)
        self.commitment_gate = CommitmentGate(
            self.corridors, self.runway_mgr, self.clearance_mgr,
            self.validator, self.event_bus, self.clock,
        )
        self.cvm = CollisionVectorMonitor(self.surveillance, self.event_bus, self.clock)
        self.nsm = NegativeSpaceMonitor(
            self.clearance_mgr, self.runway_mgr, self.event_bus, self.clock,
        )

        # Entity registries
        self._flights: dict[str, FlightStateMachine] = {}
        self._vfr: dict[str, VFRPatternStateMachine] = {}
        self._vehicles: dict[str, VehicleStateMachine] = {}
        self._agents: list = []

        # Result accumulators
        self._trace: list[Event] = []
        self._violations: list[InvariantViolation] = []
        self._alerts: list[Alert] = []

        # Wire up registries
        self.invariant_checker.set_registries(
            self._flights, self._vehicles,
            self.surveillance, self.airspace,
        )
        self.nsm.set_flights(self._flights)

    # --- Entity management ---

    def add_flight(
        self,
        flight_id: str,
        initial_state: IFRState,
        position: LatLonAlt | None = None,
        velocity: Vector3D | None = None,
        runway_assignment: str | None = None,
        aircraft_type: str = "B737",
    ) -> FlightStateMachine:
        flight = FlightStateMachine(
            flight_id, initial_state, self.clock, self.event_bus,
            position, velocity, runway_assignment, aircraft_type,
        )
        self._flights[flight_id] = flight
        if position:
            self.surveillance.add_track(flight_id, position, velocity)
        self.nsm.record_state_change(flight_id)
        return flight

    def add_vfr(
        self,
        flight_id: str,
        pattern_runway: str,
        position: LatLonAlt | None = None,
        velocity: Vector3D | None = None,
        aircraft_type: str = "C172",
    ) -> VFRPatternStateMachine:
        vfr = VFRPatternStateMachine(
            flight_id, pattern_runway, self.clock, self.event_bus,
            position=position, velocity=velocity, aircraft_type=aircraft_type,
        )
        self._vfr[flight_id] = vfr
        if position:
            self.surveillance.add_track(flight_id, position, velocity)
        return vfr

    def add_vehicle(
        self,
        vehicle_id: str,
        vehicle_type: str,
        position: LatLonAlt | None = None,
    ) -> VehicleStateMachine:
        vehicle = VehicleStateMachine(
            vehicle_id, vehicle_type, self.clock, self.event_bus,
            position=position,
        )
        self._vehicles[vehicle_id] = vehicle
        if position:
            self.surveillance.add_track(vehicle_id, position)
        return vehicle

    def register_agent(self, agent) -> None:
        self._agents.append(agent)
        self.event_bus.subscribe("*", agent.on_event)

    # --- Accessors ---

    @property
    def flights(self) -> dict[str, FlightStateMachine]:
        return self._flights

    @property
    def vfr_flights(self) -> dict[str, VFRPatternStateMachine]:
        return self._vfr

    @property
    def vehicles(self) -> dict[str, VehicleStateMachine]:
        return self._vehicles

    # --- Tick cycle ---

    def tick(self) -> list[Event]:
        """One simulation tick — the 11-step cycle."""

        # 1. Advance clock
        self.clock.tick()

        # 2. Update surveillance positions
        self.surveillance.update()

        # 3. Sync positions from surveillance to state machines
        self._sync_positions()

        # 4. Run agents → collect proposals
        proposals: list[ClearanceProposal] = []
        for agent in self._agents:
            agent_proposals = agent.tick(self)
            if agent_proposals:
                proposals.extend(agent_proposals)

        # 5. Validate proposals through safety net
        for proposal in proposals:
            result, clr = self.validator.validate(proposal)
            if result.result == "VALIDATED":
                # 6. Issue clearance for delivery
                self.delivery.issue(clr.clearance_id)

        # 7. Process clearance delivery (readback ACK/timeout)
        delivery_alerts = self.delivery.tick()
        self._alerts.extend(delivery_alerts)

        # 8. Commitment gate checks for approaching aircraft
        for fid, flight in self._flights.items():
            if flight.state in (
                IFRState.INBOUND, IFRState.FINAL_APPROACH,
            ) and flight.runway_assignment:
                self.commitment_gate.check(
                    fid, flight.position, flight.velocity,
                    flight.runway_assignment,
                )

        # 9. CVM conflict detection
        cvm_alerts = self.cvm.tick()
        self._alerts.extend(cvm_alerts)

        # 10. Negative-space monitoring
        nsm_alerts = self.nsm.tick()
        self._alerts.extend(nsm_alerts)

        # 11. Continuous invariant checks
        violations = self._check_continuous_invariants()
        self._violations.extend(violations)

        # Drain events
        events = self.event_bus.drain()
        self._trace.extend(events)
        return events

    def _sync_positions(self) -> None:
        """Update state machine positions from surveillance."""
        for fid, flight in self._flights.items():
            result = self.surveillance.get_position(fid)
            if result:
                pos, vel, age = result
                flight.position = pos
                flight.velocity = vel

        for fid, vfr in self._vfr.items():
            result = self.surveillance.get_position(fid)
            if result:
                pos, vel, age = result
                vfr.position = pos
                vfr.velocity = vel

        for vid, vehicle in self._vehicles.items():
            result = self.surveillance.get_position(vid)
            if result:
                pos, vel, age = result
                vehicle.position = pos

    def _check_continuous_invariants(self) -> list[InvariantViolation]:
        """Run continuous monitoring invariants (R3, R4, C3, F4, S1, S2, S4)."""
        violations: list[InvariantViolation] = []
        violations.extend(self.invariant_checker.check_R3())
        violations.extend(self.invariant_checker.check_R4())
        violations.extend(self.invariant_checker.check_C3())

        # S4: untracked entities
        tracked = self.surveillance.get_tracked_ids()
        detected = self.surveillance.get_detected_ids()
        violations.extend(self.invariant_checker.check_S4(tracked, detected))

        return violations

    # --- Run methods ---

    def run(self, duration_sec: float) -> SimulationResult:
        """Run for a duration, ticking each step."""
        target = self.clock.now() + duration_sec
        while self.clock.now() < target:
            self.tick()
        return self._build_result()

    def run_until(
        self,
        predicate: Callable[[], bool],
        max_sec: float = 600.0,
    ) -> SimulationResult:
        """Run until a condition is met or timeout."""
        deadline = self.clock.now() + max_sec
        while self.clock.now() < deadline:
            self.tick()
            if predicate():
                break
        return self._build_result()

    def _build_result(self) -> SimulationResult:
        return SimulationResult(
            events=list(self._trace),
            final_time=self.clock.now(),
            violations=list(self._violations),
            alerts=list(self._alerts),
        )
