"""Negative-space monitoring — Section 29.4.

Alerts when expected activity is absent. The complement of the CVM:
CVM detects things that shouldn't be converging;
NSM detects things that should be happening but aren't.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sim.types import (
    IFRState, Alert, AlertSeverity, ClearanceState, ClearanceType, make_id,
)
from sim.state.clearance import ClearanceLifecycle
from sim.state.runway import RunwayLockManager
from sim.clock import SimClock
from sim.events import EventBus

if TYPE_CHECKING:
    from sim.state.flight import FlightStateMachine


class NegativeSpaceMonitor:
    """Alert when expected activity is absent."""

    # Configurable timeouts
    NSM1_TIMEOUT: float = 30.0  # Aircraft in FINAL_APPROACH without landing clearance
    NSM2_TIMEOUT: float = 30.0  # Tower handoff without contact
    NSM4_TIMEOUT: float = 300.0  # No state transition when expected

    def __init__(
        self,
        clearance_mgr: ClearanceLifecycle,
        runway_mgr: RunwayLockManager,
        event_bus: EventBus,
        clock: SimClock,
    ) -> None:
        self._clearance_mgr = clearance_mgr
        self._runway_mgr = runway_mgr
        self._event_bus = event_bus
        self._clock = clock
        self._flights: dict[str, FlightStateMachine] = {}
        self._state_timestamps: dict[str, float] = {}  # flight_id -> last transition time
        self._alerted: set[tuple[str, str]] = set()  # (flight_id, nsm_type) to avoid repeats

    def set_flights(self, flights: dict[str, FlightStateMachine]) -> None:
        self._flights = flights

    def record_state_change(self, flight_id: str) -> None:
        self._state_timestamps[flight_id] = self._clock.now()

    def tick(self) -> list[Alert]:
        alerts: list[Alert] = []
        now = self._clock.now()

        for fid, flight in self._flights.items():
            # NSM-1: Aircraft in FINAL_APPROACH without landing clearance
            if flight.state == IFRState.FINAL_APPROACH:
                last_change = self._state_timestamps.get(fid, 0)
                if now - last_change > self.NSM1_TIMEOUT:
                    active = self._clearance_mgr.get_active_for_entity(fid)
                    has_landing = any(
                        c.clearance_type == ClearanceType.LANDING for c in active
                    )
                    if not has_landing and (fid, "NSM1") not in self._alerted:
                        self._alerted.add((fid, "NSM1"))
                        alert = Alert(
                            alert_id=make_id("ALERT"),
                            alert_type="nsm.final_no_clearance",
                            severity=AlertSeverity.WARNING,
                            affected_entities=[fid],
                            description=(
                                f"NSM-1: {fid} in FINAL_APPROACH for "
                                f"{now - last_change:.0f}s without landing clearance"
                            ),
                            timestamp=now,
                        )
                        alerts.append(alert)
                        self._event_bus.publish("alert.nsm", "negative_space_monitor", alert)

            # NSM-2: Tower handoff without contact
            if flight.state == IFRState.TOWER_HANDOFF:
                last_change = self._state_timestamps.get(fid, 0)
                if now - last_change > self.NSM2_TIMEOUT:
                    if (fid, "NSM2") not in self._alerted:
                        self._alerted.add((fid, "NSM2"))
                        alert = Alert(
                            alert_id=make_id("ALERT"),
                            alert_type="nsm.no_tower_contact",
                            severity=AlertSeverity.WARNING,
                            affected_entities=[fid],
                            description=(
                                f"NSM-2: {fid} handed to tower {now - last_change:.0f}s ago, "
                                f"no contact received"
                            ),
                            timestamp=now,
                        )
                        alerts.append(alert)
                        self._event_bus.publish("alert.nsm", "negative_space_monitor", alert)

            # NSM-4: No state transition for too long
            if fid in self._state_timestamps:
                if flight.state not in (
                    IFRState.PARKED, IFRState.PARKED_IN,
                    IFRState.FLIGHT_COMPLETE,
                ):
                    last_change = self._state_timestamps[fid]
                    if now - last_change > self.NSM4_TIMEOUT:
                        if (fid, "NSM4") not in self._alerted:
                            self._alerted.add((fid, "NSM4"))
                            alert = Alert(
                                alert_id=make_id("ALERT"),
                                alert_type="nsm.stale_state",
                                severity=AlertSeverity.ADVISORY,
                                affected_entities=[fid],
                                description=(
                                    f"NSM-4: {fid} in {flight.state.value} for "
                                    f"{now - last_change:.0f}s without transition"
                                ),
                                timestamp=now,
                            )
                            alerts.append(alert)
                            self._event_bus.publish("alert.nsm", "negative_space_monitor", alert)

        return alerts
