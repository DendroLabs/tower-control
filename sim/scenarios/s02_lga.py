"""Scenario 02: LGA Runway Collision Prevention.

Recreates the LaGuardia March 2026 incident conditions:
- Aircraft on final approach with landing clearance
- Fire truck requests crossing of the same active runway
- Safety net must REJECT the crossing (R1, R2)
- After aircraft lands and exits, crossing must be VALIDATED
"""

from __future__ import annotations

from sim.types import (
    IFRState, VehicleState, ClearanceType, ClearanceState,
    ClearanceProposal, EntityType,
    LatLonAlt, Vector3D, SurveillanceRef, SurveillanceSource, make_id,
)
from sim.engine.simulation import Simulation, SimulationResult
from sim.agents.scripted import ScriptedAgent, ScriptedAction
from sim.scenarios.scenario_base import AssertionResult


name = "LGA Runway Collision Prevention"
description = (
    "Fire truck requests crossing of active runway while aircraft is on final. "
    "Safety net must REJECT crossing, then VALIDATE after runway is clear."
)


def setup(sim: Simulation) -> None:
    # AC8646: CRJ-900 on final for 10L, 5nm out
    sim.add_flight(
        "AC8646", IFRState.FINAL_APPROACH,
        position=LatLonAlt(35.008, -79.930, 1800.0),
        velocity=Vector3D(ground_speed_kts=140.0, heading_deg=280.0, vertical_rate_fpm=-700.0),
        runway_assignment="10L",
        aircraft_type="CRJ-900",
    )

    # Fire truck: at hold-short line on Taxiway C, waiting to cross 10L
    sim.add_vehicle(
        "TRUCK7", "fire_truck",
        position=LatLonAlt(35.0055, -80.008, 650.0),
    )
    # Set vehicle to HOLDING_SHORT
    truck = sim.vehicles["TRUCK7"]
    truck.state = VehicleState.HOLDING_SHORT

    agent = ScriptedAgent("tower_agent")

    # t=2: Agent proposes landing clearance for AC8646 on 10L
    agent.add_action(ScriptedAction(
        at_time=2.0,
        proposal=ClearanceProposal(
            proposal_id=make_id("PROP"),
            proposing_agent="tower_agent",
            timestamp=2.0,
            target_entity="AC8646",
            target_entity_type=EntityType.AIRCRAFT,
            clearance_type=ClearanceType.LANDING,
            parameters={"runway": "10L"},
            surveillance_refs=[SurveillanceRef(
                source=SurveillanceSource.RADAR,
                entity_id="AC8646",
                position=LatLonAlt(35.008, -79.930, 1800.0),
                velocity=Vector3D(140.0, 280.0, -700.0),
                timestamp=2.0,
            )],
        ),
    ))

    # t=4: Readback OK for AC8646 landing
    agent.add_action(ScriptedAction(
        at_time=4.0,
        callback=lambda sim: _readback_for(sim, "AC8646"),
    ))

    # t=8: Agent proposes runway crossing for truck on 10L
    # THIS MUST BE REJECTED — runway is locked by AC8646
    agent.add_action(ScriptedAction(
        at_time=8.0,
        proposal=ClearanceProposal(
            proposal_id=make_id("PROP"),
            proposing_agent="tower_agent",
            timestamp=8.0,
            target_entity="TRUCK7",
            target_entity_type=EntityType.VEHICLE,
            clearance_type=ClearanceType.RUNWAY_CROSSING,
            parameters={"runway": "10L"},
            surveillance_refs=[SurveillanceRef(
                source=SurveillanceSource.SURFACE,
                entity_id="TRUCK7",
                position=LatLonAlt(35.0055, -80.008, 650.0),
                velocity=Vector3D(),
                timestamp=8.0,
            )],
        ),
    ))

    # t=60: Simulate AC8646 completing landing — release the lock
    agent.add_action(ScriptedAction(
        at_time=60.0,
        callback=lambda sim: _complete_landing(sim, "AC8646", "10L"),
    ))

    # t=62: Re-propose crossing — should now be VALIDATED
    agent.add_action(ScriptedAction(
        at_time=62.0,
        proposal=ClearanceProposal(
            proposal_id=make_id("PROP"),
            proposing_agent="tower_agent",
            timestamp=62.0,
            target_entity="TRUCK7",
            target_entity_type=EntityType.VEHICLE,
            clearance_type=ClearanceType.RUNWAY_CROSSING,
            parameters={"runway": "10L"},
            surveillance_refs=[SurveillanceRef(
                source=SurveillanceSource.SURFACE,
                entity_id="TRUCK7",
                position=LatLonAlt(35.0055, -80.008, 650.0),
                velocity=Vector3D(),
                timestamp=62.0,
            )],
        ),
    ))

    # t=64: Readback OK for truck crossing
    agent.add_action(ScriptedAction(
        at_time=64.0,
        callback=lambda sim: _readback_for(sim, "TRUCK7"),
    ))

    sim.register_agent(agent)


def _readback_for(sim: Simulation, entity_id: str) -> None:
    for cid, pd in sim.delivery.get_pending().items():
        clr = sim.clearance_mgr.get(cid)
        if clr and clr.target_entity == entity_id:
            sim.delivery.receive_readback(cid, True)
            return


def _complete_landing(sim: Simulation, flight_id: str, runway_id: str) -> None:
    """Simulate landing completion: complete the clearance and release the lock."""
    active = sim.clearance_mgr.get_active_for_entity(flight_id)
    for clr in active:
        if clr.clearance_type == ClearanceType.LANDING:
            sim.clearance_mgr.mark_completed(clr.clearance_id)
            sim.runway_mgr.release(runway_id, flight_id)
            flight = sim.flights.get(flight_id)
            if flight:
                flight.state = IFRState.RUNWAY_EXIT
            return


def run(sim: Simulation) -> SimulationResult:
    return sim.run(duration_sec=70.0)


def assertions(sim: Simulation, result: SimulationResult) -> list[AssertionResult]:
    results: list[AssertionResult] = []

    # 1. AC8646 landing clearance was VALIDATED
    validated_events = sim.event_bus.history("clearance.*.validated")
    results.append(AssertionResult(
        "AC8646 landing clearance validated",
        len(validated_events) >= 1,
        f"Validated events: {len(validated_events)}",
    ))

    # 2. First truck crossing was REJECTED
    rejected_events = sim.event_bus.history("clearance.*.rejected")
    first_rejection = None
    for e in rejected_events:
        if isinstance(e.payload, dict) and "violations" in e.payload:
            first_rejection = e
            break

    results.append(AssertionResult(
        "Truck crossing REJECTED while runway locked",
        first_rejection is not None,
        f"Rejection: {first_rejection.payload if first_rejection else 'None'}",
    ))

    # 3. Rejection cited R1 and/or R2
    if first_rejection and isinstance(first_rejection.payload, dict):
        violated = first_rejection.payload.get("violations", [])
        has_r1_r2 = "R1" in violated or "R2" in violated
    else:
        has_r1_r2 = False
    results.append(AssertionResult(
        "Rejection cited R1/R2 invariants",
        has_r1_r2,
        f"Violated invariants: {violated if first_rejection else 'N/A'}",
    ))

    # 4. Truck remained in HOLDING_SHORT throughout
    truck = sim.vehicles.get("TRUCK7")
    # After the crossing is validated at t=62, the truck may transition.
    # But between t=8 and t=60 it must have stayed in HOLDING_SHORT.
    # We check that no vehicle state change to ON_RUNWAY happened before t=60
    vehicle_events = sim.event_bus.history("vehicle.TRUCK7.state_changed")
    early_runway_entry = [
        e for e in vehicle_events
        if e.timestamp < 60 and isinstance(e.payload, dict)
        and e.payload.get("to_state") == "ON_RUNWAY"
    ]
    results.append(AssertionResult(
        "Truck never entered runway before landing completed",
        len(early_runway_entry) == 0,
        f"Early runway entries: {len(early_runway_entry)}",
    ))

    # 5. Second crossing (at t=62) was VALIDATED
    # Should have at least 2 validated events (landing + second crossing)
    results.append(AssertionResult(
        "Truck crossing VALIDATED after runway clear",
        len(validated_events) >= 2,
        f"Total validated events: {len(validated_events)}",
    ))

    # 6. No S4 violations (all entities tracked)
    s4_violations = [v for v in result.violations if v.invariant_id == "S4"]
    results.append(AssertionResult(
        "No untracked entity violations (S4)",
        len(s4_violations) == 0,
        f"S4 violations: {len(s4_violations)}",
    ))

    return results
