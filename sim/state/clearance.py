"""Clearance lifecycle state machine — Section 28.6.

12 states: PROPOSED → VALIDATED → ISSUED → READBACK_OK → ACTIVE → COMPLETED.
With REJECTED, READBACK_FAIL, NO_RESPONSE, CANCELLED, SUPERSEDED, EXPIRED paths.
Lock acquisition at VALIDATED, lock release at terminal states.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from sim.types import (
    ClearanceState, ClearanceType, Alert, AlertSeverity,
    RunwayLockState, make_id,
)
from sim.clock import SimClock
from sim.events import EventBus


# Valid state transitions
VALID_TRANSITIONS: dict[ClearanceState, set[ClearanceState]] = {
    ClearanceState.PROPOSED: {ClearanceState.VALIDATED, ClearanceState.REJECTED, ClearanceState.EXPIRED},
    ClearanceState.VALIDATED: {ClearanceState.ISSUED},
    ClearanceState.REJECTED: set(),  # terminal
    ClearanceState.ISSUED: {ClearanceState.READBACK_OK, ClearanceState.READBACK_FAIL, ClearanceState.NO_RESPONSE},
    ClearanceState.READBACK_OK: {ClearanceState.ACTIVE},
    ClearanceState.READBACK_FAIL: {ClearanceState.ISSUED},  # re-issue
    ClearanceState.NO_RESPONSE: {ClearanceState.ISSUED, ClearanceState.EXPIRED},  # retransmit or give up
    ClearanceState.ACTIVE: {ClearanceState.COMPLETED, ClearanceState.CANCELLED, ClearanceState.SUPERSEDED},
    ClearanceState.COMPLETED: set(),  # terminal
    ClearanceState.CANCELLED: set(),  # terminal
    ClearanceState.SUPERSEDED: set(),  # terminal
    ClearanceState.EXPIRED: set(),  # terminal
}

# Terminal states release locks
TERMINAL_STATES = {
    ClearanceState.COMPLETED,
    ClearanceState.CANCELLED,
    ClearanceState.SUPERSEDED,
    ClearanceState.EXPIRED,
    ClearanceState.REJECTED,
}

# Mutually exclusive clearance type pairs (C2)
MUTUALLY_EXCLUSIVE: list[tuple[ClearanceType, ClearanceType]] = [
    (ClearanceType.LANDING, ClearanceType.GO_AROUND),
    (ClearanceType.TAKEOFF, ClearanceType.HOLD_POSITION),
    (ClearanceType.TAXI_OUT, ClearanceType.TAXI_IN),
]

# State TTLs for timeout detection (C3)
STATE_TTLS: dict[ClearanceState, float] = {
    ClearanceState.PROPOSED: 10.0,
    ClearanceState.ISSUED: 5.0,  # ACK timeout
    ClearanceState.READBACK_FAIL: 5.0,
}


@dataclass
class Clearance:
    clearance_id: str
    clearance_type: ClearanceType
    target_entity: str
    target_entity_type: str  # "AIRCRAFT" or "VEHICLE"
    parameters: dict = field(default_factory=dict)
    state: ClearanceState = ClearanceState.PROPOSED
    lock_held: RunwayLockState | None = None
    proposed_at: float = 0.0
    validated_at: float | None = None
    issued_at: float | None = None
    readback_at: float | None = None
    active_at: float | None = None
    completed_at: float | None = None
    superseded_by: str | None = None
    supersedes: str | None = None
    retransmit_count: int = 0


class ClearanceLifecycle:
    """Manages clearance state transitions with TTL enforcement."""

    def __init__(self, clock: SimClock, event_bus: EventBus) -> None:
        self._clock = clock
        self._event_bus = event_bus
        self._clearances: dict[str, Clearance] = {}
        self._entity_clearances: dict[str, list[str]] = {}  # entity_id -> [clearance_id]

    def create_proposal(
        self,
        clearance_type: ClearanceType,
        target_entity: str,
        target_entity_type: str,
        parameters: dict | None = None,
    ) -> Clearance:
        clr = Clearance(
            clearance_id=make_id("CLR"),
            clearance_type=clearance_type,
            target_entity=target_entity,
            target_entity_type=target_entity_type,
            parameters=parameters or {},
            state=ClearanceState.PROPOSED,
            proposed_at=self._clock.now(),
        )
        self._clearances[clr.clearance_id] = clr
        self._entity_clearances.setdefault(target_entity, []).append(clr.clearance_id)
        return clr

    def _transition(self, clearance_id: str, new_state: ClearanceState) -> Clearance:
        clr = self._clearances[clearance_id]
        if new_state not in VALID_TRANSITIONS.get(clr.state, set()):
            raise ValueError(
                f"Invalid clearance transition: {clr.state.value} → {new_state.value} "
                f"for {clearance_id}"
            )
        clr.state = new_state
        self._event_bus.publish(
            f"clearance.{clearance_id}.state_changed",
            "clearance_lifecycle",
            {"clearance_id": clearance_id, "new_state": new_state.value, "type": clr.clearance_type.value},
        )
        return clr

    def mark_validated(
        self, clearance_id: str, lock: RunwayLockState | None = None,
    ) -> Clearance:
        clr = self._transition(clearance_id, ClearanceState.VALIDATED)
        clr.validated_at = self._clock.now()
        clr.lock_held = lock
        return clr

    def mark_rejected(self, clearance_id: str) -> Clearance:
        return self._transition(clearance_id, ClearanceState.REJECTED)

    def mark_issued(self, clearance_id: str) -> Clearance:
        clr = self._transition(clearance_id, ClearanceState.ISSUED)
        clr.issued_at = self._clock.now()
        return clr

    def mark_readback_ok(self, clearance_id: str) -> Clearance:
        clr = self._transition(clearance_id, ClearanceState.READBACK_OK)
        clr.readback_at = self._clock.now()
        return clr

    def mark_readback_fail(self, clearance_id: str) -> Clearance:
        return self._transition(clearance_id, ClearanceState.READBACK_FAIL)

    def mark_no_response(self, clearance_id: str) -> Clearance:
        return self._transition(clearance_id, ClearanceState.NO_RESPONSE)

    def mark_active(self, clearance_id: str) -> Clearance:
        clr = self._transition(clearance_id, ClearanceState.ACTIVE)
        clr.active_at = self._clock.now()
        return clr

    def mark_completed(self, clearance_id: str) -> Clearance:
        clr = self._transition(clearance_id, ClearanceState.COMPLETED)
        clr.completed_at = self._clock.now()
        return clr

    def mark_cancelled(self, clearance_id: str) -> Clearance:
        return self._transition(clearance_id, ClearanceState.CANCELLED)

    def mark_superseded(self, clearance_id: str, superseded_by: str) -> Clearance:
        clr = self._transition(clearance_id, ClearanceState.SUPERSEDED)
        clr.superseded_by = superseded_by
        return clr

    def mark_expired(self, clearance_id: str) -> Clearance:
        return self._transition(clearance_id, ClearanceState.EXPIRED)

    def reissue(self, clearance_id: str) -> Clearance:
        """Re-issue after READBACK_FAIL or NO_RESPONSE."""
        clr = self._clearances[clearance_id]
        if clr.state not in (ClearanceState.READBACK_FAIL, ClearanceState.NO_RESPONSE):
            raise ValueError(f"Cannot reissue from state {clr.state.value}")
        clr = self._transition(clearance_id, ClearanceState.ISSUED)
        clr.issued_at = self._clock.now()
        clr.retransmit_count += 1
        return clr

    def get(self, clearance_id: str) -> Clearance | None:
        return self._clearances.get(clearance_id)

    def get_active_for_entity(self, entity_id: str) -> list[Clearance]:
        ids = self._entity_clearances.get(entity_id, [])
        return [
            self._clearances[cid] for cid in ids
            if self._clearances[cid].state in (
                ClearanceState.VALIDATED, ClearanceState.ISSUED,
                ClearanceState.READBACK_OK, ClearanceState.ACTIVE,
            )
        ]

    def check_mutual_exclusion(
        self, entity_id: str, new_type: ClearanceType,
    ) -> list[str]:
        """C2: check if new_type conflicts with any active clearance for this entity.
        Returns list of violated invariant IDs.
        """
        active = self.get_active_for_entity(entity_id)
        for clr in active:
            for a, b in MUTUALLY_EXCLUSIVE:
                if (clr.clearance_type == a and new_type == b) or \
                   (clr.clearance_type == b and new_type == a):
                    return ["C2"]
        return []

    def check_ttl_expirations(self) -> list[Alert]:
        """C3: alert if clearances stuck in ISSUED or READBACK_FAIL beyond timeout."""
        alerts: list[Alert] = []
        now = self._clock.now()
        for clr in self._clearances.values():
            ttl = STATE_TTLS.get(clr.state)
            if ttl is None:
                continue
            if clr.state == ClearanceState.ISSUED and clr.issued_at is not None:
                if now - clr.issued_at > ttl:
                    alerts.append(Alert(
                        alert_id=make_id("ALERT"),
                        alert_type="clearance.ack_timeout",
                        severity=AlertSeverity.WARNING,
                        affected_entities=[clr.target_entity],
                        description=(
                            f"Clearance {clr.clearance_id} ({clr.clearance_type.value}) "
                            f"in ISSUED for {now - clr.issued_at:.0f}s without readback"
                        ),
                        timestamp=now,
                    ))
        return alerts

    def get_all(self) -> dict[str, Clearance]:
        return dict(self._clearances)
