"""Scenario 05: CVM Separation Escalation.

Two aircraft converging head-on at similar altitudes.
CVM should escalate through Advisory → Warning → Critical tiers
as distance closes. Resolution options must be generated at each tier.
"""

from __future__ import annotations

from sim.types import (
    IFRState, AlertSeverity,
    LatLonAlt, Vector3D, make_id,
)
from sim.engine.simulation import Simulation, SimulationResult
from sim.engine.surveillance import Waypoint
from sim.agents.scripted import ScriptedAgent
from sim.scenarios.scenario_base import AssertionResult


name = "CVM Separation Escalation"
description = (
    "Two aircraft converging head-on. CVM escalates through "
    "Advisory → Warning → Critical tiers as distance closes."
)


def setup(sim: Simulation) -> None:
    # Two aircraft on opposing tracks offset laterally by ~4nm.
    # CPA distance ≈ 4nm (Advisory on distance, not Warning).
    # As time_to_cpa decreases: Advisory (≤90s) → Warning (≤45s) → Critical (≤15s).

    # WN300: Westbound at 3000ft, on the north track
    sim.add_flight(
        "WN300", IFRState.INBOUND,
        position=LatLonAlt(35.070, -79.830, 3000.0),
        velocity=Vector3D(ground_speed_kts=200.0, heading_deg=280.0, vertical_rate_fpm=0.0),
        runway_assignment="10L",
        aircraft_type="B737",
    )

    sim.surveillance.get_track("WN300").waypoints = [
        Waypoint(time=0.0, position=LatLonAlt(35.070, -79.830, 3000.0), speed_kts=200.0),
        Waypoint(time=180.0, position=LatLonAlt(35.070, -80.200, 3000.0), speed_kts=200.0),
    ]

    # EV400: Eastbound at 3000ft, on the south track (~4nm south of WN300)
    sim.add_flight(
        "EV400", IFRState.INBOUND,
        position=LatLonAlt(35.005, -80.100, 3000.0),
        velocity=Vector3D(ground_speed_kts=180.0, heading_deg=100.0, vertical_rate_fpm=0.0),
        runway_assignment="28R",
        aircraft_type="CRJ-700",
    )

    sim.surveillance.get_track("EV400").waypoints = [
        Waypoint(time=0.0, position=LatLonAlt(35.005, -80.100, 3000.0), speed_kts=180.0),
        Waypoint(time=180.0, position=LatLonAlt(35.005, -79.700, 3000.0), speed_kts=180.0),
    ]

    # No agent actions — this tests passive CVM detection
    agent = ScriptedAgent("tower_agent")
    sim.register_agent(agent)


def run(sim: Simulation) -> SimulationResult:
    return sim.run(duration_sec=90.0)


def assertions(sim: Simulation, result: SimulationResult) -> list[AssertionResult]:
    results: list[AssertionResult] = []

    # Collect CVM alerts by tier
    advisory_alerts = sim.event_bus.history("alert.separation_advisory")
    warning_alerts = sim.event_bus.history("alert.separation_warning")
    critical_alerts = sim.event_bus.history("alert.separation_critical")

    all_cvm = advisory_alerts + warning_alerts + critical_alerts

    # 1. At least one CVM alert was generated
    results.append(AssertionResult(
        "CVM detected converging traffic",
        len(all_cvm) > 0,
        f"Total CVM alerts: {len(all_cvm)}",
    ))

    # 2. Advisory tier fired
    results.append(AssertionResult(
        "Advisory tier alert generated",
        len(advisory_alerts) > 0,
        f"Advisory alerts: {len(advisory_alerts)}",
    ))

    # 3. Warning tier fired (closer convergence)
    results.append(AssertionResult(
        "Warning tier alert generated",
        len(warning_alerts) > 0,
        f"Warning alerts: {len(warning_alerts)}",
    ))

    # 4. Critical tier fired (very close)
    results.append(AssertionResult(
        "Critical tier alert generated",
        len(critical_alerts) > 0,
        f"Critical alerts: {len(critical_alerts)}",
    ))

    # 5. Alerts identify both aircraft
    both_identified = any(
        isinstance(e.payload, object)
        and hasattr(e.payload, 'affected_entities')
        and "WN300" in e.payload.affected_entities
        and "EV400" in e.payload.affected_entities
        for e in all_cvm
    )
    results.append(AssertionResult(
        "Alerts identify both WN300 and EV400",
        both_identified,
        f"Alert entities checked",
    ))

    # 6. Resolution options present in alerts
    has_resolution = any(
        hasattr(e.payload, 'recommended_action')
        and e.payload.recommended_action is not None
        for e in all_cvm
    )
    results.append(AssertionResult(
        "Resolution options provided",
        has_resolution,
        f"Checked recommended_action on {len(all_cvm)} alerts",
    ))

    # 7. Escalation ordering: advisory fires before critical
    if advisory_alerts and critical_alerts:
        first_advisory = min(e.timestamp for e in advisory_alerts)
        first_critical = min(e.timestamp for e in critical_alerts)
        escalated_in_order = first_advisory < first_critical
    else:
        escalated_in_order = False
    results.append(AssertionResult(
        "Escalation order: Advisory before Critical",
        escalated_in_order,
        f"First advisory: {min(e.timestamp for e in advisory_alerts) if advisory_alerts else 'N/A'}, "
        f"First critical: {min(e.timestamp for e in critical_alerts) if critical_alerts else 'N/A'}",
    ))

    return results
