"""Scenario 08: LLM Ground Controller Agent.

First scenario driven by an LLM agent instead of scripted actions.
- Aircraft on final approach, lands, exits runway
- Fire truck holding short needs to cross that runway
- The LLM ground controller must wait for the runway to clear,
  then propose the crossing
- Scripted agent handles the aircraft (landing clearance, readback)
- LLM agent handles the vehicle (crossing decision)

This validates:
1. LLM agent correctly reads world state
2. LLM agent waits for runway to be available before proposing crossing
3. Safety net validates the LLM's proposal
4. End-to-end flow: LLM decision → safety net validation → clearance delivery
"""

from __future__ import annotations

from sim.types import (
    IFRState, VehicleState, ClearanceType, ClearanceState, LockType,
    ClearanceProposal, EntityType,
    LatLonAlt, Vector3D, SurveillanceRef, SurveillanceSource, make_id,
)
from sim.engine.simulation import Simulation, SimulationResult
from sim.agents.scripted import ScriptedAgent, ScriptedAction
from sim.agents.ground_controller import GroundControllerAgent
from sim.agents.mock_llm import MockLLMClient
from sim.scenarios.scenario_base import AssertionResult


name = "LLM Ground Controller"
description = (
    "LLM agent decides when to propose runway crossing for a vehicle. "
    "Aircraft lands first, then LLM correctly identifies safe crossing window."
)


# Module-level so tests can swap to real LLM
_use_real_llm = False


def setup(sim: Simulation) -> None:
    # AC300: Already on landing roll (landing clearance already issued, runway locked)
    sim.add_flight(
        "AC300", IFRState.LANDING_ROLL,
        position=LatLonAlt(35.005, -80.005, 650.0),
        velocity=Vector3D(ground_speed_kts=60.0, heading_deg=100.0, vertical_rate_fpm=0.0),
        runway_assignment="10L",
        aircraft_type="CRJ-900",
    )

    # Pre-lock runway 10L for AC300 (simulates already-issued landing clearance)
    ac300_clr_id = make_id("CLR")
    sim.runway_mgr.check_and_lock("10L", LockType.ARRIVAL, "AC300", ac300_clr_id)

    # TRUCK3: Fire truck at hold-short on Taxiway C / Runway 10L
    sim.add_vehicle(
        "TRUCK3", "fire_truck",
        position=LatLonAlt(35.0055, -80.008, 650.0),
    )
    truck = sim.vehicles["TRUCK3"]
    truck.state = VehicleState.HOLDING_SHORT

    # Scripted agent handles aircraft operations (tower controller role)
    tower = ScriptedAgent("tower_agent")

    # t=30: AC300 has landed and cleared — release lock
    tower.add_action(ScriptedAction(
        at_time=30.0,
        callback=lambda sim: _complete_landing_simple(sim, "AC300", "10L"),
    ))

    sim.register_agent(tower)

    # LLM ground controller — handles vehicle crossing decisions
    if _use_real_llm:
        ground = GroundControllerAgent(tick_interval=5.0)
    else:
        mock = MockLLMClient()
        ground = GroundControllerAgent(
            llm_client=mock,
            tick_interval=5.0,
        )
    sim.register_agent(ground)

    # Readback agent — auto-acknowledges clearances for TRUCK3
    readback = ScriptedAgent("readback_agent")
    readback.add_action(ScriptedAction(
        at_condition=lambda sim: _has_pending_for(sim, "TRUCK3"),
        callback=lambda sim: _readback_for(sim, "TRUCK3"),
    ))
    sim.register_agent(readback)


def _readback_for(sim: Simulation, entity_id: str) -> None:
    for cid, pd in sim.delivery.get_pending().items():
        clr = sim.clearance_mgr.get(cid)
        if clr and clr.target_entity == entity_id:
            sim.delivery.receive_readback(cid, True)
            return


def _has_pending_for(sim: Simulation, entity_id: str) -> bool:
    for cid, pd in sim.delivery.get_pending().items():
        clr = sim.clearance_mgr.get(cid)
        if clr and clr.target_entity == entity_id:
            return True
    return False


def _complete_landing_simple(sim: Simulation, flight_id: str, runway_id: str) -> None:
    """Release the pre-acquired lock and update flight state."""
    sim.runway_mgr.release(runway_id, flight_id)
    flight = sim.flights.get(flight_id)
    if flight:
        flight.state = IFRState.RUNWAY_EXIT


def run(sim: Simulation) -> SimulationResult:
    return sim.run(duration_sec=50.0)


def assertions(sim: Simulation, result: SimulationResult) -> list[AssertionResult]:
    results: list[AssertionResult] = []

    rejected = sim.event_bus.history("clearance.*.rejected")

    # 1. Runway was released (AC300 landing completed)
    rwy_events = sim.event_bus.history("runway.10L.lock_changed")
    released = [
        e for e in rwy_events
        if isinstance(e.payload, dict) and e.payload.get("action") == "released"
    ]
    results.append(AssertionResult(
        "AC300 landing completed and runway released",
        len(released) > 0,
        f"Release events: {len(released)}",
    ))

    # 2. LLM agent proposed a crossing clearance for TRUCK3
    truck_crossings = [
        clr for clr in sim.clearance_mgr.get_all().values()
        if clr.target_entity == "TRUCK3"
        and clr.clearance_type == ClearanceType.RUNWAY_CROSSING
    ]
    results.append(AssertionResult(
        "LLM agent proposed crossing for TRUCK3",
        len(truck_crossings) > 0,
        f"Truck crossing proposals: {len(truck_crossings)}",
    ))

    # 3. The crossing was VALIDATED (not rejected)
    truck_validated = [
        clr for clr in truck_crossings
        if clr.validated_at is not None
    ]
    results.append(AssertionResult(
        "Truck crossing clearance validated by safety net",
        len(truck_validated) > 0,
        f"Validated: {len(truck_validated)}, Rejected: {len(rejected)}",
    ))

    # 4. No crossing was proposed while runway was locked
    # (crossing proposals should only appear after t=30 when lock is released)
    early_truck_proposals = [
        clr for clr in truck_crossings
        if clr.proposed_at is not None and clr.proposed_at < 30.0
    ]
    results.append(AssertionResult(
        "No crossing proposed while runway locked (agent waited)",
        len(early_truck_proposals) == 0,
        f"Early proposals: {len(early_truck_proposals)}",
    ))

    # 5. The crossing proposal came from the ground_controller agent
    from_ground = [
        clr for clr in truck_crossings
        if clr.proposing_agent == "ground_controller"
    ]
    results.append(AssertionResult(
        "Crossing proposed by ground_controller agent",
        len(from_ground) > 0,
        f"From ground_controller: {len(from_ground)}",
    ))

    return results
