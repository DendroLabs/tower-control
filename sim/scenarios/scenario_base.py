"""Scenario protocol and assertion framework."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from sim.engine.simulation import Simulation, SimulationResult


@dataclass
class AssertionResult:
    name: str
    passed: bool
    detail: str = ""


class Scenario(Protocol):
    name: str
    description: str

    def setup(self, sim: Simulation) -> None:
        """Add entities, configure agents, set initial positions."""
        ...

    def run(self, sim: Simulation) -> SimulationResult:
        """Execute the scenario."""
        ...

    def assertions(self, sim: Simulation, result: SimulationResult) -> list[AssertionResult]:
        """Verify the scenario produced the expected outcome."""
        ...
