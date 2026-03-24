"""TCP-style clearance delivery — Section 29.4.1.

Readback is the ACK. No readback after timeout = retransmit (up to 3x).
Max retries exceeded = escalate to human (RST).
"""

from __future__ import annotations

from dataclasses import dataclass

from sim.types import Alert, AlertSeverity, make_id
from sim.state.clearance import ClearanceLifecycle, ClearanceState
from sim.clock import SimClock
from sim.events import EventBus


@dataclass
class PendingDelivery:
    clearance_id: str
    issued_at: float
    retries: int = 0
    last_transmitted_at: float = 0.0


class ClearanceDelivery:
    """TCP-style reliable delivery for all clearances."""

    ACK_TIMEOUT_SEC: float = 5.0
    MAX_RETRIES: int = 3

    def __init__(
        self,
        clearance_mgr: ClearanceLifecycle,
        event_bus: EventBus,
        clock: SimClock,
    ) -> None:
        self._clearance_mgr = clearance_mgr
        self._event_bus = event_bus
        self._clock = clock
        self._pending: dict[str, PendingDelivery] = {}

    def issue(self, clearance_id: str) -> None:
        """Start delivery. Clearance moves to ISSUED, ACK timer starts."""
        self._clearance_mgr.mark_issued(clearance_id)
        now = self._clock.now()
        self._pending[clearance_id] = PendingDelivery(
            clearance_id=clearance_id,
            issued_at=now,
            last_transmitted_at=now,
        )

    def receive_readback(self, clearance_id: str, correct: bool) -> None:
        """Pilot readback received.

        correct=True -> READBACK_OK -> ACTIVE.
        correct=False -> READBACK_FAIL -> re-issue.
        """
        if clearance_id not in self._pending:
            return

        if correct:
            self._clearance_mgr.mark_readback_ok(clearance_id)
            self._clearance_mgr.mark_active(clearance_id)
            del self._pending[clearance_id]
        else:
            self._clearance_mgr.mark_readback_fail(clearance_id)
            # Re-issue
            self._clearance_mgr.reissue(clearance_id)
            pd = self._pending[clearance_id]
            pd.retries += 1
            pd.last_transmitted_at = self._clock.now()

    def tick(self) -> list[Alert]:
        """Check all pending deliveries for ACK timeouts."""
        now = self._clock.now()
        alerts: list[Alert] = []
        to_remove: list[str] = []

        for cid, pd in self._pending.items():
            elapsed = now - pd.last_transmitted_at
            if elapsed < self.ACK_TIMEOUT_SEC:
                continue

            if pd.retries >= self.MAX_RETRIES:
                # Escalate: NO_RESPONSE after max retries
                self._clearance_mgr.mark_no_response(cid)
                to_remove.append(cid)

                clr = self._clearance_mgr.get(cid)
                entity = clr.target_entity if clr else "unknown"
                alert = Alert(
                    alert_id=make_id("ALERT"),
                    alert_type="clearance.unacknowledged",
                    severity=AlertSeverity.CRITICAL,
                    affected_entities=[entity],
                    description=(
                        f"Clearance {cid} unacknowledged after {self.MAX_RETRIES} attempts. "
                        f"Escalating to human overwatcher."
                    ),
                    recommended_action="Human takes over voice comms. CVM alerted.",
                    timestamp=now,
                )
                alerts.append(alert)
                self._event_bus.publish("alert.clearance_unacknowledged", "delivery", alert)
            else:
                # Retransmit
                self._clearance_mgr.mark_no_response(cid)
                self._clearance_mgr.reissue(cid)
                pd.retries += 1
                pd.last_transmitted_at = now

        for cid in to_remove:
            del self._pending[cid]

        return alerts

    def get_pending(self) -> dict[str, PendingDelivery]:
        return dict(self._pending)
