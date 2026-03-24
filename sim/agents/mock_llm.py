"""Mock LLM client for testing without API access.

Implements basic ground controller logic deterministically,
returning the same JSON format that the real LLM would.
Used for unit tests and offline scenario validation.
"""

from __future__ import annotations

import json

from sim.agents.llm_client import LLMResponse


class MockLLMClient:
    """Deterministic mock that mimics Claude's ground controller responses."""

    def __init__(self) -> None:
        self.calls: list[dict] = []

    def complete(self, system: str, user: str) -> LLMResponse:
        self.calls.append({"system": system, "user": user})
        actions = self._decide(json.loads(user))
        return LLMResponse(
            content=json.dumps(actions),
            model="mock",
            input_tokens=0,
            output_tokens=0,
        )

    def complete_json(self, system: str, user: str) -> list | dict:
        self.calls.append({"system": system, "user": user})
        return self._decide(json.loads(user))

    def _decide(self, world: dict) -> list[dict]:
        """Simple rule-based logic matching what we'd expect the LLM to do."""
        actions = []
        vehicles = world.get("vehicles", {})
        runways = world.get("runways", {})
        flights = world.get("relevant_flights", {})

        for vid, v in vehicles.items():
            # Skip vehicles that already have active clearances
            if v.get("has_active_clearance"):
                continue

            if v["state"] == "HOLDING_SHORT":
                # Use the runway the vehicle is actually holding short of
                runway = v.get("holding_short_of")
                if runway and self._is_runway_safe(runway, runways, flights):
                    actions.append({
                        "action": "RUNWAY_CROSSING",
                        "vehicle_id": vid,
                        "runway": runway,
                        "reasoning": f"Runway {runway} is available, no conflicting traffic",
                    })

            elif v["state"] == "STATIONARY":
                actions.append({
                    "action": "TAXI_OUT",
                    "vehicle_id": vid,
                    "reasoning": "Vehicle is stationary and ready to taxi",
                })

        return actions

    def _is_runway_safe(
        self, runway_id: str, runways: dict, flights: dict,
    ) -> bool:
        """Check if a specific runway is safe for crossing."""
        # Map runway IDs to physical IDs
        rwy_to_phys = {
            "10L": "10L/28R", "28R": "10L/28R",
            "10R": "10R/28L", "28L": "10R/28L",
        }
        phys_id = rwy_to_phys.get(runway_id, runway_id)
        state = runways.get(phys_id)
        if not state or state["status"] != "AVAILABLE":
            return False

        # Check no flights on approach/departure for this runway
        phys_rwys = {"10L/28R": ["10L", "28R"], "10R/28L": ["10R", "28L"]}
        rwy_ids = phys_rwys.get(phys_id, [runway_id])
        for fid, f in flights.items():
            if f.get("runway") in rwy_ids and f["state"] in (
                "FINAL_APPROACH", "LANDING_CLEARED", "LANDING_ROLL",
                "TAKEOFF_ROLL", "INBOUND",
            ):
                return False

        return True
