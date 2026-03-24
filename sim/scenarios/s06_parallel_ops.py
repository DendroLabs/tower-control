"""Scenario 06: Cross-Field Taxi with Sequential Runway Locks.

A vehicle on Taxiway C must cross both runways (10L then 10R) to reach
the south side of the airport. It must:
1. Acquire crossing lock for 10L, cross, release
2. Acquire crossing lock for 10R, cross, release

Validates that:
- Crossing 10L does NOT grant access to 10R
- Each lock is independently acquired and released
- A second crossing attempt while 10R is locked by a departure is REJECTED
"""

from __future__ import annotations

from sim.types import (
    IFRState, VehicleState, ClearanceType, ClearanceState,
    ClearanceProposal, EntityType, LockType,
    LatLonAlt, Vector3D, SurveillanceRef, SurveillanceSource, make_id,
)
from sim.engine.simulation import Simulation, SimulationResult
from sim.agents.scripted import ScriptedAgent, ScriptedAction
from sim.scenarios.scenario_base import AssertionResult


name = "Cross-Field Taxi with Sequential Locks"
description = (
    "Vehicle crosses both runways via Taxiway C. Each crossing requires "
    "an independent lock. Second crossing rejected while departure holds 10R."
)


def setup(sim: Simulation) -> None:
    # MAINT1: Maintenance truck at hold-short on Taxiway C / Runway 10L
    sim.add_vehicle(
        "MAINT1", "maintenance_truck",
        position=LatLonAlt(35.0055, -80.008, 650.0),
    )
    truck = sim.vehicles["MAINT1"]
    truck.state = VehicleState.HOLDING_SHORT

    # UA500: Holding short of 10R for departure — holds the lock
    sim.add_flight(
        "UA500", IFRState.HOLDING_SHORT,
        position=LatLonAlt(34.994, -80.014, 650.0),
        velocity=Vector3D(),
        runway_assignment="10R",
        aircraft_type="B737",
    )

    agent = ScriptedAgent("tower_agent")

    # t=2: Propose crossing clearance for MAINT1 on 10L (runway is free)
    agent.add_action(ScriptedAction(
        at_time=2.0,
        proposal=ClearanceProposal(
            proposal_id=make_id("PROP"),
            proposing_agent="tower_agent",
            timestamp=2.0,
            target_entity="MAINT1",
            target_entity_type=EntityType.VEHICLE,
            clearance_type=ClearanceType.RUNWAY_CROSSING,
            parameters={"runway": "10L"},
            surveillance_refs=[SurveillanceRef(
                source=SurveillanceSource.SURFACE,
                entity_id="MAINT1",
                position=LatLonAlt(35.0055, -80.008, 650.0),
                velocity=Vector3D(),
                timestamp=2.0,
            )],
        ),
    ))

    # t=4: Readback OK for 10L crossing
    agent.add_action(ScriptedAction(
        at_time=4.0,
        callback=lambda sim: _readback_for(sim, "MAINT1"),
    ))

    # t=10: Truck has crossed 10L — complete clearance and release lock
    agent.add_action(ScriptedAction(
        at_time=10.0,
        callback=lambda sim: _complete_crossing(sim, "MAINT1", "10L"),
    ))

    # t=12: Lock 10R for UA500 departure (takeoff clearance)
    agent.add_action(ScriptedAction(
        at_time=12.0,
        proposal=ClearanceProposal(
            proposal_id=make_id("PROP"),
            proposing_agent="tower_agent",
            timestamp=12.0,
            target_entity="UA500",
            target_entity_type=EntityType.AIRCRAFT,
            clearance_type=ClearanceType.TAKEOFF,
            parameters={"runway": "10R"},
            surveillance_refs=[SurveillanceRef(
                source=SurveillanceSource.SURFACE,
                entity_id="UA500",
                position=LatLonAlt(34.994, -80.014, 650.0),
                velocity=Vector3D(),
                timestamp=12.0,
            )],
        ),
    ))

    # t=14: Readback OK for UA500 takeoff
    agent.add_action(ScriptedAction(
        at_time=14.0,
        callback=lambda sim: _readback_for(sim, "UA500"),
    ))

    # t=16: Truck now at hold-short for 10R — propose crossing
    # THIS MUST BE REJECTED — 10R locked by UA500 departure
    agent.add_action(ScriptedAction(
        at_time=16.0,
        proposal=ClearanceProposal(
            proposal_id=make_id("PROP"),
            proposing_agent="tower_agent",
            timestamp=16.0,
            target_entity="MAINT1",
            target_entity_type=EntityType.VEHICLE,
            clearance_type=ClearanceType.RUNWAY_CROSSING,
            parameters={"runway": "10R"},
            surveillance_refs=[SurveillanceRef(
                source=SurveillanceSource.SURFACE,
                entity_id="MAINT1",
                position=LatLonAlt(34.9945, -80.008, 650.0),
                velocity=Vector3D(),
                timestamp=16.0,
            )],
        ),
    ))

    # t=40: UA500 has departed — complete takeoff and release 10R lock
    agent.add_action(ScriptedAction(
        at_time=40.0,
        callback=lambda sim: _complete_departure(sim, "UA500", "10R"),
    ))

    # t=42: Re-propose 10R crossing — should now be VALIDATED
    agent.add_action(ScriptedAction(
        at_time=42.0,
        proposal=ClearanceProposal(
            proposal_id=make_id("PROP"),
            proposing_agent="tower_agent",
            timestamp=42.0,
            target_entity="MAINT1",
            target_entity_type=EntityType.VEHICLE,
            clearance_type=ClearanceType.RUNWAY_CROSSING,
            parameters={"runway": "10R"},
            surveillance_refs=[SurveillanceRef(
                source=SurveillanceSource.SURFACE,
                entity_id="MAINT1",
                position=LatLonAlt(34.9945, -80.008, 650.0),
                velocity=Vector3D(),
                timestamp=42.0,
            )],
        ),
    ))

    # t=44: Readback OK for 10R crossing
    agent.add_action(ScriptedAction(
        at_time=44.0,
        callback=lambda sim: _readback_for(sim, "MAINT1"),
    ))

    sim.register_agent(agent)


def _readback_for(sim: Simulation, entity_id: str) -> None:
    for cid, pd in sim.delivery.get_pending().items():
        clr = sim.clearance_mgr.get(cid)
        if clr and clr.target_entity == entity_id:
            sim.delivery.receive_readback(cid, True)
            return


def _complete_crossing(sim: Simulation, vehicle_id: str, runway_id: str) -> None:
    active = sim.clearance_mgr.get_active_for_entity(vehicle_id)
    for clr in active:
        if clr.clearance_type == ClearanceType.RUNWAY_CROSSING:
            sim.clearance_mgr.mark_completed(clr.clearance_id)
            sim.runway_mgr.release(runway_id, vehicle_id)
            return


def _complete_departure(sim: Simulation, flight_id: str, runway_id: str) -> None:
    active = sim.clearance_mgr.get_active_for_entity(flight_id)
    for clr in active:
        if clr.clearance_type == ClearanceType.TAKEOFF:
            sim.clearance_mgr.mark_completed(clr.clearance_id)
            sim.runway_mgr.release(runway_id, flight_id)
            flight = sim.flights.get(flight_id)
            if flight:
                flight.state = IFRState.AIRBORNE_DEPARTURE
            return


def run(sim: Simulation) -> SimulationResult:
    return sim.run(duration_sec=50.0)


def assertions(sim: Simulation, result: SimulationResult) -> list[AssertionResult]:
    results: list[AssertionResult] = []

    validated = sim.event_bus.history("clearance.*.validated")
    rejected = sim.event_bus.history("clearance.*.rejected")

    # 1. First crossing (10L) was VALIDATED
    results.append(AssertionResult(
        "First crossing (10L) validated",
        len(validated) >= 1,
        f"Validated count: {len(validated)}",
    ))

    # 2. Takeoff clearance (10R) was VALIDATED
    results.append(AssertionResult(
        "UA500 takeoff clearance validated",
        len(validated) >= 2,
        f"Validated count: {len(validated)}",
    ))

    # 3. Second crossing attempt (10R at t=16) was REJECTED
    results.append(AssertionResult(
        "Second crossing (10R) rejected while departure active",
        len(rejected) >= 1,
        f"Rejected count: {len(rejected)}",
    ))

    # 4. Rejection cited R2 (runway already locked)
    r2_cited = False
    for e in rejected:
        if isinstance(e.payload, dict):
            violations = e.payload.get("violations", [])
            if "R2" in violations:
                r2_cited = True
                break
    results.append(AssertionResult(
        "Rejection cited R2 invariant",
        r2_cited,
        f"Checked {len(rejected)} rejection events for R2",
    ))

    # 5. Third crossing (10R at t=42, after departure complete) was VALIDATED
    results.append(AssertionResult(
        "Third crossing (10R) validated after departure clear",
        len(validated) >= 3,
        f"Validated count: {len(validated)}",
    ))

    # 6. Locks were independent — 10L crossing did not affect 10R
    # (Validated 10L crossing + rejected 10R crossing proves independence)
    results.append(AssertionResult(
        "Runway locks are independent (10L crossing did not grant 10R access)",
        len(validated) >= 1 and len(rejected) >= 1,
        f"Validated: {len(validated)}, Rejected: {len(rejected)}",
    ))

    return results
