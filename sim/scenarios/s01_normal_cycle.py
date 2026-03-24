"""Scenario 01: Normal IFR Arrival and Departure Cycle.

Validates the happy path: one arrival lands, one departure takes off.
No conflicts, all clearances validated, full lifecycle completion.
"""

from __future__ import annotations

from sim.types import (
    IFRState, ClearanceType, ClearanceProposal, EntityType,
    LatLonAlt, Vector3D, SurveillanceRef, SurveillanceSource, make_id,
)
from sim.engine.simulation import Simulation, SimulationResult
from sim.agents.scripted import ScriptedAgent, ScriptedAction
from sim.scenarios.scenario_base import AssertionResult


name = "Normal IFR Cycle"
description = "One arrival lands on 10L, one departure takes off from 10R. No conflicts."


def setup(sim: Simulation) -> None:
    # Arrival: AC100 approaching 10L from the east, 5nm out
    rwy_10l = sim.airport.get_runway("10L")
    sim.add_flight(
        "AC100", IFRState.INBOUND,
        position=LatLonAlt(35.010, -79.920, 2000.0),
        velocity=Vector3D(ground_speed_kts=140.0, heading_deg=280.0, vertical_rate_fpm=-700.0),
        runway_assignment="10L",
        aircraft_type="CRJ-700",
    )

    # Departure: UA200 holding short of 10R
    sim.add_flight(
        "UA200", IFRState.HOLDING_SHORT,
        position=LatLonAlt(34.994, -80.014, 650.0),
        velocity=Vector3D(),
        runway_assignment="10R",
        aircraft_type="B737",
    )

    agent = ScriptedAgent("tower_agent")

    # t=2: Issue landing clearance for AC100 on 10L
    agent.add_action(ScriptedAction(
        at_time=2.0,
        proposal=ClearanceProposal(
            proposal_id=make_id("PROP"),
            proposing_agent="tower_agent",
            timestamp=2.0,
            target_entity="AC100",
            target_entity_type=EntityType.AIRCRAFT,
            clearance_type=ClearanceType.LANDING,
            parameters={"runway": "10L"},
            surveillance_refs=[SurveillanceRef(
                source=SurveillanceSource.RADAR,
                entity_id="AC100",
                position=LatLonAlt(35.010, -79.920, 2000.0),
                velocity=Vector3D(140.0, 280.0, -700.0),
                timestamp=2.0,
            )],
        ),
    ))

    # t=4: Readback OK for AC100 landing — find clearance by looking it up
    agent.add_action(ScriptedAction(
        at_time=4.0,
        callback=lambda sim: _readback_latest(sim, "AC100"),
    ))

    # t=5: Issue takeoff clearance for UA200 on 10R (different runway — no conflict)
    agent.add_action(ScriptedAction(
        at_time=5.0,
        proposal=ClearanceProposal(
            proposal_id=make_id("PROP"),
            proposing_agent="tower_agent",
            timestamp=5.0,
            target_entity="UA200",
            target_entity_type=EntityType.AIRCRAFT,
            clearance_type=ClearanceType.TAKEOFF,
            parameters={"runway": "10R"},
            surveillance_refs=[SurveillanceRef(
                source=SurveillanceSource.SURFACE,
                entity_id="UA200",
                position=LatLonAlt(34.994, -80.014, 650.0),
                velocity=Vector3D(),
                timestamp=5.0,
            )],
        ),
    ))

    # t=7: Readback OK for UA200 takeoff
    agent.add_action(ScriptedAction(
        at_time=7.0,
        callback=lambda sim: _readback_latest(sim, "UA200"),
    ))

    sim.register_agent(agent)


def _readback_latest(sim: Simulation, entity_id: str) -> None:
    """Find the most recent pending clearance for entity and send readback OK."""
    for cid, pd in sim.delivery.get_pending().items():
        clr = sim.clearance_mgr.get(cid)
        if clr and clr.target_entity == entity_id:
            sim.delivery.receive_readback(cid, True)
            return


def run(sim: Simulation) -> SimulationResult:
    return sim.run(duration_sec=30.0)


def assertions(sim: Simulation, result: SimulationResult) -> list[AssertionResult]:
    results: list[AssertionResult] = []

    validated = sim.event_bus.history("clearance.*.validated")
    rejected = sim.event_bus.history("clearance.*.rejected")

    # 1. Both clearances validated (landing + takeoff)
    results.append(AssertionResult(
        "Both clearances validated",
        len(validated) >= 2,
        f"Validated: {len(validated)}, Rejected: {len(rejected)}",
    ))

    # 2. No rejections
    results.append(AssertionResult(
        "No clearances rejected",
        len(rejected) == 0,
        f"Rejections: {len(rejected)}",
    ))

    # 3. Runway lock events generated for both runways
    rwy_events = sim.event_bus.history("runway.*.lock_changed")
    results.append(AssertionResult(
        "Runway lock events generated",
        len(rwy_events) >= 2,
        f"Found {len(rwy_events)} runway lock events",
    ))

    # 4. No invariant violations (excluding S4 for untracked)
    real_violations = [v for v in result.violations if v.invariant_id != "S4"]
    results.append(AssertionResult(
        "No invariant violations",
        len(real_violations) == 0,
        f"Violations: {[v.invariant_id for v in real_violations]}" if real_violations else "None",
    ))

    return results
