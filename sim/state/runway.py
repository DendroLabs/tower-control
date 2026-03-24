"""Runway lock model — Section 28.5.

One lock per physical runway (V1). Atomic check-and-lock.
Reciprocal runway mapping (10L and 28R share one lock).
TTL with mandatory alert on expiration (no auto-release).
"""

from __future__ import annotations

import threading
from dataclasses import dataclass

from sim.types import (
    LockType, LockStatus, RunwayLockState, Alert, AlertSeverity, make_id,
)
from sim.clock import SimClock
from sim.events import EventBus


# TTL per lock type (Section 28.5.5)
LOCK_TTLS: dict[LockType, float] = {
    LockType.DEPARTURE: 90.0,
    LockType.ARRIVAL: 120.0,
    LockType.CROSSING: 45.0,
    LockType.LUAW: 120.0,
    LockType.PATTERN: 30.0,
}


@dataclass
class RunwayLock:
    physical_id: str  # e.g., "10L/28R"
    lock_type: LockType | None = None
    holder: str | None = None
    clearance_id: str | None = None
    acquired_at: float | None = None
    ttl: float | None = None
    status: LockStatus = LockStatus.AVAILABLE

    @property
    def is_locked(self) -> bool:
        return self.lock_type is not None

    def to_state(self, clock: SimClock) -> RunwayLockState:
        ttl_remaining = None
        if self.acquired_at is not None and self.ttl is not None:
            elapsed = clock.now() - self.acquired_at
            ttl_remaining = max(0.0, self.ttl - elapsed)
        return RunwayLockState(
            runway_id=self.physical_id,
            lock_status=self.status,
            lock_type=self.lock_type,
            holder=self.holder,
            clearance_id=self.clearance_id,
            acquired_at=self.acquired_at,
            ttl_remaining=ttl_remaining,
        )


class RunwayLockManager:
    """One lock per physical runway. Atomic check-and-lock (Section 28.5.4)."""

    def __init__(
        self,
        physical_runway_ids: list[str],
        runway_to_physical: dict[str, str],
        clock: SimClock,
        event_bus: EventBus,
    ) -> None:
        self._clock = clock
        self._event_bus = event_bus
        self._runway_to_physical = dict(runway_to_physical)
        self._locks: dict[str, RunwayLock] = {
            pid: RunwayLock(physical_id=pid) for pid in physical_runway_ids
        }
        # Threading lock for atomicity (explicit even in single-threaded sim)
        self._mutex = threading.Lock()

    def _physical_id(self, runway_id: str) -> str:
        return self._runway_to_physical.get(runway_id, runway_id)

    def check_and_lock(
        self,
        runway_id: str,
        lock_type: LockType,
        holder: str,
        clearance_id: str,
    ) -> tuple[bool, RunwayLockState, str | None]:
        """Atomic check-and-lock (Section 28.5.4).

        Returns (success, current_state, rejection_reason).
        """
        pid = self._physical_id(runway_id)
        with self._mutex:
            lock = self._locks[pid]
            if lock.is_locked:
                reason = (
                    f"Runway {pid} locked: {lock.lock_type.value} "
                    f"by {lock.holder} (clearance {lock.clearance_id})"
                )
                return False, lock.to_state(self._clock), reason

            lock.lock_type = lock_type
            lock.holder = holder
            lock.clearance_id = clearance_id
            lock.acquired_at = self._clock.now()
            lock.ttl = LOCK_TTLS.get(lock_type, 120.0)
            lock.status = LockStatus.RESERVED

            state = lock.to_state(self._clock)

        self._event_bus.publish(
            f"runway.{runway_id}.lock_changed",
            "runway_lock_manager",
            {"action": "acquired", "state": state},
        )
        return True, state, None

    def release(self, runway_id: str, holder: str) -> RunwayLockState:
        """Release the lock. Only the holder can release."""
        pid = self._physical_id(runway_id)
        with self._mutex:
            lock = self._locks[pid]
            if not lock.is_locked or lock.holder != holder:
                return lock.to_state(self._clock)

            lock.lock_type = None
            lock.holder = None
            lock.clearance_id = None
            lock.acquired_at = None
            lock.ttl = None
            lock.status = LockStatus.AVAILABLE

            state = lock.to_state(self._clock)

        self._event_bus.publish(
            f"runway.{runway_id}.lock_changed",
            "runway_lock_manager",
            {"action": "released", "state": state},
        )
        return state

    def upgrade_luaw_to_departure(
        self,
        runway_id: str,
        holder: str,
        new_clearance_id: str,
    ) -> tuple[bool, RunwayLockState, str | None]:
        """Upgrade LUAW → DEPARTURE for the same holder (Section 28.6.2)."""
        pid = self._physical_id(runway_id)
        with self._mutex:
            lock = self._locks[pid]
            if not lock.is_locked:
                return False, lock.to_state(self._clock), "No lock to upgrade"
            if lock.holder != holder:
                return False, lock.to_state(self._clock), f"Lock held by {lock.holder}, not {holder}"
            if lock.lock_type != LockType.LUAW:
                return False, lock.to_state(self._clock), f"Lock type is {lock.lock_type}, not LUAW"

            lock.lock_type = LockType.DEPARTURE
            lock.clearance_id = new_clearance_id
            lock.acquired_at = self._clock.now()
            lock.ttl = LOCK_TTLS[LockType.DEPARTURE]

            state = lock.to_state(self._clock)

        self._event_bus.publish(
            f"runway.{runway_id}.lock_changed",
            "runway_lock_manager",
            {"action": "upgraded", "state": state},
        )
        return True, state, None

    def mark_occupied(self, runway_id: str) -> None:
        """Surveillance detected entity on runway surface."""
        pid = self._physical_id(runway_id)
        with self._mutex:
            lock = self._locks[pid]
            if lock.is_locked:
                lock.status = LockStatus.OCCUPIED

    def get_state(self, runway_id: str) -> RunwayLockState:
        pid = self._physical_id(runway_id)
        with self._mutex:
            return self._locks[pid].to_state(self._clock)

    def get_all_states(self) -> dict[str, RunwayLockState]:
        with self._mutex:
            return {pid: lock.to_state(self._clock) for pid, lock in self._locks.items()}

    def get_lock_holder(self, runway_id: str) -> str | None:
        pid = self._physical_id(runway_id)
        with self._mutex:
            return self._locks[pid].holder

    def is_locked(self, runway_id: str) -> bool:
        pid = self._physical_id(runway_id)
        with self._mutex:
            return self._locks[pid].is_locked

    def check_ttl_expirations(self) -> list[Alert]:
        """R4: alert on TTL expiration (no auto-release)."""
        alerts: list[Alert] = []
        now = self._clock.now()
        with self._mutex:
            for pid, lock in self._locks.items():
                if lock.is_locked and lock.acquired_at is not None and lock.ttl is not None:
                    if now - lock.acquired_at > lock.ttl:
                        alert = Alert(
                            alert_id=make_id("ALERT"),
                            alert_type="runway.ttl_expired",
                            severity=AlertSeverity.WARNING,
                            affected_entities=[lock.holder] if lock.holder else [],
                            description=(
                                f"Runway {pid} lock TTL expired: {lock.lock_type.value} "
                                f"held by {lock.holder} for "
                                f"{now - lock.acquired_at:.0f}s (TTL: {lock.ttl:.0f}s)"
                            ),
                            timestamp=now,
                        )
                        alerts.append(alert)
        return alerts
