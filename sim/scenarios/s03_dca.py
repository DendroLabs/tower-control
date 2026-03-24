"""Scenario 03: DCA Untracked Entity Detection.

Recreates the Potomac River midair collision conditions:
- Aircraft on ILS approach
- Helicopter present in airspace but NOT tracked by the system
- S4 invariant must detect the untracked entity
- CVM should detect converging trajectories
"""

from __future__ import annotations

from sim.types import (
    IFRState, LatLonAlt, Vector3D, make_id,
)
from sim.engine.simulation import Simulation, SimulationResult
from sim.engine.surveillance import Waypoint
from sim.agents.scripted import ScriptedAgent
from sim.scenarios.scenario_base import AssertionResult


name = "DCA Untracked Entity Detection"
description = (
    "Helicopter in Class C airspace not tracked by system. "
    "S4 must detect it. CVM should alert on converging trajectories."
)


def setup(sim: Simulation) -> None:
    # PSA5342: CRJ-700 on approach to 10L, 6nm out
    sim.add_flight(
        "PSA5342", IFRState.INBOUND,
        position=LatLonAlt(35.010, -79.910, 2500.0),
        velocity=Vector3D(ground_speed_kts=140.0, heading_deg=280.0, vertical_rate_fpm=-700.0),
        runway_assignment="10L",
        aircraft_type="CRJ-700",
    )

    # PAT25: Army Black Hawk — physically present, NOT tracked
    # Inject as untracked entity via surveillance
    sim.surveillance.inject_untracked(
        "PAT25",
        position=LatLonAlt(35.005, -79.960, 800.0),
        velocity=Vector3D(ground_speed_kts=120.0, heading_deg=350.0, vertical_rate_fpm=0.0),
        waypoints=[
            Waypoint(time=0.0, position=LatLonAlt(35.005, -79.960, 800.0), speed_kts=120.0),
            Waypoint(time=60.0, position=LatLonAlt(35.020, -79.965, 800.0), speed_kts=120.0),
        ],
    )

    # No agent actions needed — this scenario tests passive detection
    agent = ScriptedAgent("tower_agent")
    sim.register_agent(agent)


def run(sim: Simulation) -> SimulationResult:
    return sim.run(duration_sec=10.0)


def assertions(sim: Simulation, result: SimulationResult) -> list[AssertionResult]:
    results: list[AssertionResult] = []

    # 1. S4 violation detected (untracked entity in airspace)
    s4_violations = [v for v in result.violations if v.invariant_id == "S4"]
    results.append(AssertionResult(
        "S4: Untracked entity detected",
        len(s4_violations) > 0,
        f"S4 violations: {len(s4_violations)}, entities: {[v.affected_entities for v in s4_violations]}",
    ))

    # 2. The untracked entity is PAT25
    pat25_detected = any(
        "PAT25" in v.affected_entities for v in s4_violations
    )
    results.append(AssertionResult(
        "PAT25 identified as untracked",
        pat25_detected,
        f"S4 affected entities: {[v.affected_entities for v in s4_violations]}",
    ))

    # 3. CVM alert generated for converging traffic
    cvm_alerts = [a for a in result.alerts if "separation" in a.alert_type]
    results.append(AssertionResult(
        "CVM separation alert generated",
        len(cvm_alerts) > 0,
        f"CVM alerts: {len(cvm_alerts)}",
    ))

    return results
