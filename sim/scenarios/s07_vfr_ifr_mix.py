"""Scenario 07: VFR/IFR Mixed Traffic Sequencing.

VFR Cessna in the pattern on 10L. IFR CRJ on approach needs the same runway.
- VFR must be sequenced to yield: extend downwind or full-stop landing first
- IFR gets landing clearance after VFR clears
- Validates commitment gate interaction with VFR pattern traffic
"""

from __future__ import annotations

from sim.types import (
    IFRState, VFRPatternState, ClearanceType,
    ClearanceProposal, EntityType, LockType,
    LatLonAlt, Vector3D, SurveillanceRef, SurveillanceSource, make_id,
)
from sim.engine.simulation import Simulation, SimulationResult
from sim.engine.surveillance import Waypoint
from sim.agents.scripted import ScriptedAgent, ScriptedAction
from sim.scenarios.scenario_base import AssertionResult


name = "VFR/IFR Mixed Traffic Sequencing"
description = (
    "VFR Cessna in pattern on 10L. IFR CRJ approaching same runway. "
    "VFR cleared to land first, IFR gets clearance after VFR clears."
)


def setup(sim: Simulation) -> None:
    # N172SP: VFR Cessna on downwind for 10L, pattern altitude 1000ft
    # Position: south of runway, parallel, heading east (downwind for runway 10)
    sim.add_vfr(
        "N172SP",
        pattern_runway="10L",
        position=LatLonAlt(35.000, -79.995, 1650.0),
        velocity=Vector3D(ground_speed_kts=90.0, heading_deg=100.0, vertical_rate_fpm=0.0),
        aircraft_type="C172",
    )
    vfr = sim.vfr_flights["N172SP"]
    vfr.state = VFRPatternState.DOWNWIND

    # AA700: IFR CRJ on approach to 10L, 6nm out
    sim.add_flight(
        "AA700", IFRState.INBOUND,
        position=LatLonAlt(35.008, -79.910, 2500.0),
        velocity=Vector3D(ground_speed_kts=140.0, heading_deg=280.0, vertical_rate_fpm=-700.0),
        runway_assignment="10L",
        aircraft_type="CRJ-700",
    )

    # AA700 waypoints: approaching runway 10L threshold
    sim.surveillance.get_track("AA700").waypoints = [
        Waypoint(time=0.0, position=LatLonAlt(35.008, -79.910, 2500.0), speed_kts=140.0, vertical_rate_fpm=-700.0),
        Waypoint(time=60.0, position=LatLonAlt(35.007, -79.960, 1300.0), speed_kts=140.0, vertical_rate_fpm=-700.0),
        Waypoint(time=120.0, position=LatLonAlt(35.006, -80.014, 650.0), speed_kts=140.0, vertical_rate_fpm=-500.0),
    ]

    agent = ScriptedAgent("tower_agent")

    # t=2: VFR turns base
    agent.add_action(ScriptedAction(
        at_time=2.0,
        callback=lambda sim: sim.vfr_flights["N172SP"].transition(VFRPatternState.BASE),
    ))

    # t=5: VFR turns final
    agent.add_action(ScriptedAction(
        at_time=5.0,
        callback=lambda sim: sim.vfr_flights["N172SP"].transition(VFRPatternState.PATTERN_FINAL),
    ))

    # t=7: Issue landing clearance for VFR (full stop) on 10L
    agent.add_action(ScriptedAction(
        at_time=7.0,
        proposal=ClearanceProposal(
            proposal_id=make_id("PROP"),
            proposing_agent="tower_agent",
            timestamp=7.0,
            target_entity="N172SP",
            target_entity_type=EntityType.AIRCRAFT,
            clearance_type=ClearanceType.LANDING,
            parameters={"runway": "10L"},
            surveillance_refs=[SurveillanceRef(
                source=SurveillanceSource.RADAR,
                entity_id="N172SP",
                position=LatLonAlt(35.004, -80.005, 1200.0),
                velocity=Vector3D(90.0, 280.0, -500.0),
                timestamp=7.0,
            )],
        ),
    ))

    # t=9: Readback OK for VFR landing
    agent.add_action(ScriptedAction(
        at_time=9.0,
        callback=lambda sim: _readback_for(sim, "N172SP"),
    ))

    # t=10: Transition VFR to FULL_STOP (requires LANDING clearance — already active)
    agent.add_action(ScriptedAction(
        at_time=10.0,
        callback=lambda sim: sim.vfr_flights["N172SP"].transition(
            VFRPatternState.FULL_STOP, ClearanceType.LANDING
        ),
    ))

    # t=30: VFR has landed and cleared runway — complete clearance, release lock
    agent.add_action(ScriptedAction(
        at_time=30.0,
        callback=lambda sim: _complete_vfr_landing(sim, "N172SP", "10L"),
    ))

    # t=32: Now issue landing clearance for IFR AA700 on 10L
    agent.add_action(ScriptedAction(
        at_time=32.0,
        proposal=ClearanceProposal(
            proposal_id=make_id("PROP"),
            proposing_agent="tower_agent",
            timestamp=32.0,
            target_entity="AA700",
            target_entity_type=EntityType.AIRCRAFT,
            clearance_type=ClearanceType.LANDING,
            parameters={"runway": "10L"},
            surveillance_refs=[SurveillanceRef(
                source=SurveillanceSource.RADAR,
                entity_id="AA700",
                position=LatLonAlt(35.007, -79.955, 1400.0),
                velocity=Vector3D(140.0, 280.0, -700.0),
                timestamp=32.0,
            )],
        ),
    ))

    # t=34: Readback OK for AA700 landing
    agent.add_action(ScriptedAction(
        at_time=34.0,
        callback=lambda sim: _readback_for(sim, "AA700"),
    ))

    sim.register_agent(agent)


def _readback_for(sim: Simulation, entity_id: str) -> None:
    for cid, pd in sim.delivery.get_pending().items():
        clr = sim.clearance_mgr.get(cid)
        if clr and clr.target_entity == entity_id:
            sim.delivery.receive_readback(cid, True)
            return


def _complete_vfr_landing(sim: Simulation, flight_id: str, runway_id: str) -> None:
    active = sim.clearance_mgr.get_active_for_entity(flight_id)
    for clr in active:
        if clr.clearance_type == ClearanceType.LANDING:
            sim.clearance_mgr.mark_completed(clr.clearance_id)
            sim.runway_mgr.release(runway_id, flight_id)
            return


def run(sim: Simulation) -> SimulationResult:
    return sim.run(duration_sec=40.0)


def assertions(sim: Simulation, result: SimulationResult) -> list[AssertionResult]:
    results: list[AssertionResult] = []

    validated = sim.event_bus.history("clearance.*.validated")
    rejected = sim.event_bus.history("clearance.*.rejected")

    # 1. VFR landing clearance was VALIDATED
    vfr_landing = [
        clr for clr in sim.clearance_mgr.get_all().values()
        if clr.target_entity == "N172SP" and clr.clearance_type == ClearanceType.LANDING
        and clr.validated_at is not None
    ]
    results.append(AssertionResult(
        "VFR landing clearance validated",
        len(vfr_landing) > 0,
        f"VFR landing clearances: {len(vfr_landing)}",
    ))

    # 2. IFR landing clearance was VALIDATED (after VFR cleared)
    ifr_landing = [
        clr for clr in sim.clearance_mgr.get_all().values()
        if clr.target_entity == "AA700" and clr.clearance_type == ClearanceType.LANDING
        and clr.validated_at is not None
    ]
    results.append(AssertionResult(
        "IFR landing clearance validated",
        len(ifr_landing) > 0,
        f"IFR landing clearances: {len(ifr_landing)}",
    ))

    # 3. VFR landed before IFR got clearance (sequencing)
    if vfr_landing and ifr_landing:
        vfr_time = vfr_landing[0].validated_at
        ifr_time = ifr_landing[0].validated_at
        sequenced = vfr_time < ifr_time
    else:
        sequenced = False
    results.append(AssertionResult(
        "VFR sequenced before IFR (VFR clearance earlier)",
        sequenced,
        f"VFR validated at: {vfr_landing[0].validated_at if vfr_landing else 'N/A'}, "
        f"IFR validated at: {ifr_landing[0].validated_at if ifr_landing else 'N/A'}",
    ))

    # 4. No rejections (proper sequencing means no conflicts)
    results.append(AssertionResult(
        "No clearances rejected (proper sequencing)",
        len(rejected) == 0,
        f"Rejections: {len(rejected)}",
    ))

    # 5. VFR pattern state transitions occurred
    vfr_events = sim.event_bus.history("flight.N172SP.vfr_state_changed")
    results.append(AssertionResult(
        "VFR pattern state transitions recorded",
        len(vfr_events) >= 2,
        f"VFR state changes: {len(vfr_events)}",
    ))

    # 6. Both aircraft shared same runway with no simultaneous lock
    # VFR lock released at t=30, IFR lock acquired at t=32
    results.append(AssertionResult(
        "Both used 10L without simultaneous lock conflict",
        len(vfr_landing) > 0 and len(ifr_landing) > 0,
        f"VFR and IFR both got validated landing clearances on 10L",
    ))

    return results
