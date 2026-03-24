"""LLM-backed Ground Controller Agent.

Manages ground vehicle movements: taxi clearances and runway crossings.
Observes vehicle states, runway locks, and flight positions to decide
when it's safe to propose clearances. The deterministic safety net
validates all proposals — the agent can be wrong and the system catches it.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from sim.types import (
    ClearanceType, ClearanceProposal, EntityType,
    SurveillanceRef, SurveillanceSource,
    VehicleState, IFRState, LockStatus,
    make_id,
)
from sim.events import Event
from sim.agents.base import Agent
from sim.agents.llm_client import LLMClient

if TYPE_CHECKING:
    from sim.engine.simulation import Simulation


SYSTEM_PROMPT = """\
You are a ground controller agent at a Class C airport with parallel runways \
10L/28R (north) and 10R/28L (south), connected by cross-field taxiways C, D, E.

Your job: manage ground vehicle movements safely. You issue two types of clearances:
- TAXI_OUT: Allow a STATIONARY vehicle to begin taxiing
- RUNWAY_CROSSING: Allow a HOLDING_SHORT vehicle to cross a runway

SAFETY RULES (the deterministic safety net enforces these, but you should follow them):
1. NEVER propose a runway crossing if that runway is locked (occupied or reserved)
2. NEVER propose a crossing if an aircraft is on final approach for that runway
3. Only propose RUNWAY_CROSSING for vehicles in HOLDING_SHORT state
4. Only propose TAXI_OUT for vehicles in STATIONARY state
5. One clearance at a time per vehicle — don't re-propose if a clearance is already active

You will receive the current world state as JSON. Respond with a JSON array of \
actions to take. Each action is an object with:
- "action": "RUNWAY_CROSSING" or "TAXI_OUT"
- "vehicle_id": the vehicle identifier
- "runway": the runway ID (required for RUNWAY_CROSSING, omit for TAXI_OUT)
- "reasoning": brief explanation of why this is safe

If no action is needed this tick, respond with an empty array: []

Respond ONLY with valid JSON. No other text."""


def _nearest_hold_short_runway(sim: Simulation, position) -> str | None:
    """Find which runway a vehicle is holding short of based on position."""
    from sim.geometry import distance_nm
    best_dist = float("inf")
    best_rwy = None
    for hs in sim.airport.hold_short_lines:
        d = distance_nm(position, hs.position)
        if d < best_dist:
            best_dist = d
            best_rwy = hs.runway
    return best_rwy if best_dist < 0.1 else None  # within ~600ft


def _build_world_state(sim: Simulation) -> dict:
    """Extract the world state visible to the ground controller."""
    # Vehicles
    vehicles = {}
    for vid, v in sim.vehicles.items():
        active_clr = sim.clearance_mgr.get_active_for_entity(vid)
        vdata = {
            "type": v.vehicle_type,
            "state": v.state.value,
            "position": {
                "lat": round(v.position.latitude, 6),
                "lon": round(v.position.longitude, 6),
            },
            "has_active_clearance": len(active_clr) > 0,
            "active_clearance_types": [c.clearance_type.value for c in active_clr],
        }
        # Include which runway the vehicle is holding short of
        if v.state == VehicleState.HOLDING_SHORT:
            vdata["holding_short_of"] = _nearest_hold_short_runway(sim, v.position)
        vehicles[vid] = vdata

    # Runway states
    runways = {}
    for pid, state in sim.runway_mgr.get_all_states().items():
        runways[pid] = {
            "status": state.lock_status.value,
            "lock_type": state.lock_type.value if state.lock_type else None,
            "holder": state.holder,
        }

    # Flights relevant to ground ops (on approach, landing, on ground)
    flights = {}
    for fid, f in sim.flights.items():
        if f.state in (
            IFRState.FINAL_APPROACH, IFRState.LANDING_CLEARED,
            IFRState.LANDING_ROLL, IFRState.INBOUND,
            IFRState.HOLDING_SHORT, IFRState.TAKEOFF_ROLL,
        ):
            flights[fid] = {
                "state": f.state.value,
                "runway": f.runway_assignment,
                "aircraft_type": f.aircraft_type,
            }

    return {
        "time": sim.clock.now(),
        "vehicles": vehicles,
        "runways": runways,
        "relevant_flights": flights,
    }


class GroundControllerAgent(Agent):
    """LLM-backed ground controller that manages vehicle movements."""

    def __init__(
        self,
        agent_id: str = "ground_controller",
        llm_client: LLMClient | None = None,
        tick_interval: float = 5.0,
    ) -> None:
        super().__init__(agent_id)
        self._llm = llm_client or LLMClient()
        self._tick_interval = tick_interval
        self._last_llm_tick: float = -999.0
        self._events: list[Event] = []
        self._pending_actions: list[dict] = []
        self._call_count = 0

    def tick(self, sim: Simulation) -> list[ClearanceProposal]:
        now = sim.clock.now()

        # Only call the LLM every N seconds (not every tick)
        if now - self._last_llm_tick < self._tick_interval:
            return []

        # Check if there are any vehicles that need attention
        if not self._has_actionable_vehicles(sim):
            return []

        self._last_llm_tick = now
        self._call_count += 1

        # Build world state and query the LLM
        world_state = _build_world_state(sim)
        try:
            actions = self._llm.complete_json(SYSTEM_PROMPT, json.dumps(world_state))
        except Exception as e:
            # LLM failure is non-fatal — safety net is the floor, not the agent
            sim.event_bus.publish(
                "agent.ground_controller.error",
                self.agent_id,
                {"error": str(e), "time": now},
            )
            return []

        if not isinstance(actions, list):
            return []

        # Convert LLM actions to ClearanceProposals
        proposals = []
        for action in actions:
            proposal = self._action_to_proposal(action, sim)
            if proposal:
                proposals.append(proposal)

        return proposals

    def _has_actionable_vehicles(self, sim: Simulation) -> bool:
        """Quick check: any vehicles in a state where we might need to act?"""
        for vid, v in sim.vehicles.items():
            if v.state == VehicleState.HOLDING_SHORT:
                active = sim.clearance_mgr.get_active_for_entity(vid)
                if not active:
                    return True
            if v.state == VehicleState.STATIONARY:
                active = sim.clearance_mgr.get_active_for_entity(vid)
                if not active:
                    return True
        return False

    def _action_to_proposal(
        self, action: dict, sim: Simulation,
    ) -> ClearanceProposal | None:
        """Convert an LLM action dict to a ClearanceProposal."""
        action_type = action.get("action")
        vehicle_id = action.get("vehicle_id")

        if not action_type or not vehicle_id:
            return None

        vehicle = sim.vehicles.get(vehicle_id)
        if not vehicle:
            return None

        now = sim.clock.now()

        # Get surveillance data for the vehicle
        surv = sim.surveillance.get_position(vehicle_id)
        if surv:
            pos, vel, age = surv
        else:
            pos = vehicle.position
            vel = vehicle.velocity

        surv_ref = SurveillanceRef(
            source=SurveillanceSource.SURFACE,
            entity_id=vehicle_id,
            position=pos,
            velocity=vel,
            timestamp=now,
        )

        if action_type == "RUNWAY_CROSSING":
            runway = action.get("runway")
            if not runway:
                return None
            return ClearanceProposal(
                proposal_id=make_id("PROP"),
                proposing_agent=self.agent_id,
                timestamp=now,
                target_entity=vehicle_id,
                target_entity_type=EntityType.VEHICLE,
                clearance_type=ClearanceType.RUNWAY_CROSSING,
                parameters={"runway": runway},
                surveillance_refs=[surv_ref],
            )

        elif action_type == "TAXI_OUT":
            return ClearanceProposal(
                proposal_id=make_id("PROP"),
                proposing_agent=self.agent_id,
                timestamp=now,
                target_entity=vehicle_id,
                target_entity_type=EntityType.VEHICLE,
                clearance_type=ClearanceType.TAXI_OUT,
                parameters={},
                surveillance_refs=[surv_ref],
            )

        return None

    def on_event(self, event: Event) -> None:
        self._events.append(event)

    @property
    def call_count(self) -> int:
        return self._call_count

    @property
    def received_events(self) -> list[Event]:
        return list(self._events)
