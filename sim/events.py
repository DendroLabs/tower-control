"""In-process pub-sub event bus.

Mirrors the production event bus architecture (Section 29.5) in a
single-process simulation. Provides audit trail for scenario assertions.
"""

from __future__ import annotations

import fnmatch
from dataclasses import dataclass, field
from typing import Any, Callable

from sim.clock import SimClock


@dataclass(slots=True)
class Event:
    topic: str
    timestamp: float
    source: str
    payload: Any
    sequence_num: int = 0


class EventBus:
    def __init__(self, clock: SimClock) -> None:
        self._clock = clock
        self._subscribers: list[tuple[str, Callable[[Event], None]]] = []
        self._pending: list[Event] = []
        self._history: list[Event] = []
        self._sequence_counters: dict[str, int] = {}

    def subscribe(self, topic_pattern: str, callback: Callable[[Event], None]) -> None:
        self._subscribers.append((topic_pattern, callback))

    def publish(self, topic: str, source: str, payload: Any) -> Event:
        seq = self._sequence_counters.get(topic, 0) + 1
        self._sequence_counters[topic] = seq

        event = Event(
            topic=topic,
            timestamp=self._clock.now(),
            source=source,
            payload=payload,
            sequence_num=seq,
        )
        self._pending.append(event)
        return event

    def drain(self) -> list[Event]:
        """Process all pending events: deliver to subscribers, move to history."""
        events = list(self._pending)
        self._pending.clear()
        for event in events:
            self._history.append(event)
            for pattern, callback in self._subscribers:
                if fnmatch.fnmatch(event.topic, pattern):
                    callback(event)
        return events

    def history(self, topic_pattern: str | None = None) -> list[Event]:
        if topic_pattern is None:
            return list(self._history)
        return [e for e in self._history if fnmatch.fnmatch(e.topic, topic_pattern)]

    def clear(self) -> None:
        self._pending.clear()
        self._history.clear()
        self._sequence_counters.clear()
