"""Abstract agent interface.

The plug-in point for future AI agents. For now, ScriptedAgent implements
this with predefined action sequences.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from sim.types import ClearanceProposal
from sim.events import Event

if TYPE_CHECKING:
    from sim.engine.simulation import Simulation


class Agent(ABC):
    def __init__(self, agent_id: str) -> None:
        self.agent_id = agent_id

    @abstractmethod
    def tick(self, sim: Simulation) -> list[ClearanceProposal]:
        """Called each simulation tick. Return zero or more proposals."""
        ...

    @abstractmethod
    def on_event(self, event: Event) -> None:
        """Called when a subscribed event fires."""
        ...
