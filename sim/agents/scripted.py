"""Scripted scenario driver agent.

Executes a predefined sequence of actions at specified times or conditions.
Mimics what a real agent would propose — used for testing scenarios.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, TYPE_CHECKING

from sim.types import ClearanceProposal
from sim.events import Event
from sim.agents.base import Agent

if TYPE_CHECKING:
    from sim.engine.simulation import Simulation


@dataclass
class ScriptedAction:
    """A single scripted action."""
    at_time: float | None = None  # fire at this sim time
    at_condition: Callable[[Simulation], bool] | None = None  # or when this is true
    proposal: ClearanceProposal | None = None  # clearance to propose
    readback: tuple[str, bool] | None = None  # (clearance_id, correct) for readback
    callback: Callable[[Simulation], None] | None = None  # arbitrary action
    fired: bool = False


class ScriptedAgent(Agent):
    """Executes predefined actions at specified times/conditions."""

    def __init__(self, agent_id: str, actions: list[ScriptedAction] | None = None) -> None:
        super().__init__(agent_id)
        self._actions = actions or []
        self._events: list[Event] = []

    def add_action(self, action: ScriptedAction) -> None:
        self._actions.append(action)

    def tick(self, sim: Simulation) -> list[ClearanceProposal]:
        proposals: list[ClearanceProposal] = []
        now = sim.clock.now()

        for action in self._actions:
            if action.fired:
                continue

            should_fire = False
            if action.at_time is not None and now >= action.at_time:
                should_fire = True
            elif action.at_condition is not None and action.at_condition(sim):
                should_fire = True

            if not should_fire:
                continue

            action.fired = True

            if action.proposal is not None:
                proposals.append(action.proposal)

            if action.readback is not None:
                cid, correct = action.readback
                sim.delivery.receive_readback(cid, correct)

            if action.callback is not None:
                action.callback(sim)

        return proposals

    def on_event(self, event: Event) -> None:
        self._events.append(event)

    @property
    def received_events(self) -> list[Event]:
        return list(self._events)
