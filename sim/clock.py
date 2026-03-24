"""Discrete, steppable simulation clock.

No component calls time.time(). All timestamps come from this clock,
making the simulation deterministic and step-through-able.
"""

from __future__ import annotations


class SimClock:
    __slots__ = ("_time", "_step")

    def __init__(self, step: float = 1.0) -> None:
        self._time: float = 0.0
        self._step: float = step

    def now(self) -> float:
        return self._time

    def tick(self, dt: float | None = None) -> float:
        self._time += dt if dt is not None else self._step
        return self._time

    def advance_to(self, t: float) -> float:
        if t > self._time:
            self._time = t
        return self._time

    def reset(self) -> None:
        self._time = 0.0

    @property
    def step(self) -> float:
        return self._step
