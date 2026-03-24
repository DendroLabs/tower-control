"""Scenario 04: Forced Go-Around at Commitment Gate.

- Flight A occupying runway 10L (landing roll)
- Flight B approaching 10L, no landing clearance
- Agent fails to issue go-around
- Commitment gate forces go-around at 2nm
"""

from __future__ import annotations

from sim.types import (
    IFRState, ClearanceType, ClearanceState,
    ClearanceProposal, EntityType,
    LatLonAlt, Vector3D, SurveillanceRef, SurveillanceSource,
    LockType, make_id,
)
from sim.engine.simulation import Simulation, SimulationResult
from sim.engine.surveillance import Waypoint
from sim.agents.scripted import ScriptedAgent, ScriptedAction
from sim.scenarios.scenario_base import AssertionResult


name = "Commitment Gate Forced Go-Around"
description = (
    "Aircraft approaching locked runway without clearance. "
    "Commitment gate must force go-around at 2nm."
)


def setup(sim: Simulation) -> None:
    # Flight A: Already on runway 10L (landing roll) — holds the lock
    sim.add_flight(
        "AA100", IFRState.LANDING_ROLL,
        position=LatLonAlt(35.005, -80.005, 650.0),
        velocity=Vector3D(ground_speed_kts=60.0, heading_deg=100.0, vertical_rate_fpm=0.0),
        runway_assignment="10L",
    )

    # Manually acquire the lock for AA100 (simulating it already landed)
    aa100_clr_id = make_id("CLR")
    sim.runway_mgr.check_and_lock("10L", LockType.ARRIVAL, "AA100", aa100_clr_id)

    # Flight B: Approaching 10L from ~4nm out, descending
    # Will cross advisory gate (~5nm) then commitment gate (~2nm)
    rwy_10l = sim.airport.get_runway("10L")

    sim.add_flight(
        "DL200", IFRState.FINAL_APPROACH,
        position=LatLonAlt(35.008, -79.940, 1500.0),
        velocity=Vector3D(ground_speed_kts=140.0, heading_deg=280.0, vertical_rate_fpm=-700.0),
        runway_assignment="10L",
    )

    # Set waypoints for DL200 to fly toward runway threshold
    sim.surveillance.get_track("DL200").waypoints = [
        Waypoint(time=0.0, position=LatLonAlt(35.008, -79.940, 1500.0), speed_kts=140.0, vertical_rate_fpm=-700.0),
        Waypoint(time=30.0, position=LatLonAlt(35.007, -79.960, 900.0), speed_kts=140.0, vertical_rate_fpm=-700.0),
        Waypoint(time=60.0, position=LatLonAlt(35.006, -79.980, 300.0), speed_kts=140.0, vertical_rate_fpm=-700.0),
        Waypoint(time=90.0, position=LatLonAlt(35.006, -80.014, 650.0), speed_kts=140.0, vertical_rate_fpm=0.0),
    ]

    # Agent does NOT propose go-around — simulates agent failure
    # The commitment gate must catch this
    agent = ScriptedAgent("tower_agent")
    sim.register_agent(agent)


def run(sim: Simulation) -> SimulationResult:
    return sim.run(duration_sec=80.0)


def assertions(sim: Simulation, result: SimulationResult) -> list[AssertionResult]:
    results: list[AssertionResult] = []

    # 1. Advisory gate alert was published (when DL200 passed ~5nm with locked runway)
    advisory_alerts = sim.event_bus.history("alert.runway_unavailable")
    results.append(AssertionResult(
        "Advisory gate alert published",
        len(advisory_alerts) > 0,
        f"Advisory alerts: {len(advisory_alerts)}",
    ))

    # 2. Forced go-around was issued
    go_around_alerts = sim.event_bus.history("alert.forced_go_around")
    results.append(AssertionResult(
        "Forced go-around issued at commitment gate",
        len(go_around_alerts) > 0,
        f"Go-around alerts: {len(go_around_alerts)}",
    ))

    # 3. Go-around was for DL200
    dl200_go_around = any(
        isinstance(e.payload, dict) and e.payload.get("flight_id") == "DL200"
        for e in go_around_alerts
    )
    results.append(AssertionResult(
        "Go-around targeted DL200",
        dl200_go_around,
        f"Go-around payloads: {[e.payload for e in go_around_alerts]}",
    ))

    # 4. A go-around clearance was VALIDATED (safety-net-originated)
    go_around_clearances = [
        clr for clr in sim.clearance_mgr.get_all().values()
        if clr.clearance_type == ClearanceType.GO_AROUND
        and clr.target_entity == "DL200"
    ]
    results.append(AssertionResult(
        "Go-around clearance created for DL200",
        len(go_around_clearances) > 0,
        f"Go-around clearances: {[c.clearance_id for c in go_around_clearances]}",
    ))

    if go_around_clearances:
        ga_validated = go_around_clearances[0].validated_at is not None
        results.append(AssertionResult(
            "Go-around clearance was VALIDATED",
            ga_validated,
            f"State: {go_around_clearances[0].state.value}",
        ))
    else:
        results.append(AssertionResult(
            "Go-around clearance was VALIDATED",
            False,
            "No go-around clearance found",
        ))

    return results
