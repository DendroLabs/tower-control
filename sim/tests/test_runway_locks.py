"""Tests for runway lock model (Section 28.5)."""

import unittest
from sim.clock import SimClock
from sim.events import EventBus
from sim.types import LockType, LockStatus, reset_ids
from sim.state.runway import RunwayLockManager


class TestRunwayLockManager(unittest.TestCase):
    def setUp(self):
        reset_ids()
        self.clock = SimClock()
        self.event_bus = EventBus(self.clock)
        self.mgr = RunwayLockManager(
            physical_runway_ids=["10L/28R", "10R/28L"],
            runway_to_physical={"10L": "10L/28R", "28R": "10L/28R", "10R": "10R/28L", "28L": "10R/28L"},
            clock=self.clock,
            event_bus=self.event_bus,
        )

    def test_acquire_lock(self):
        """Basic lock acquisition succeeds on available runway."""
        ok, state, reason = self.mgr.check_and_lock("10L", LockType.ARRIVAL, "FL100", "CLR-001")
        self.assertTrue(ok)
        self.assertEqual(state.lock_type, LockType.ARRIVAL)
        self.assertEqual(state.holder, "FL100")
        self.assertIsNone(reason)

    def test_mutual_exclusion_R1(self):
        """R1: Cannot acquire second lock on same runway."""
        self.mgr.check_and_lock("10L", LockType.ARRIVAL, "FL100", "CLR-001")
        ok, state, reason = self.mgr.check_and_lock("10L", LockType.CROSSING, "TRUCK1", "CLR-002")
        self.assertFalse(ok)
        self.assertIn("locked", reason)

    def test_reciprocal_locking(self):
        """Locking 10L also locks 28R (same physical runway)."""
        self.mgr.check_and_lock("10L", LockType.DEPARTURE, "FL100", "CLR-001")
        ok, _, reason = self.mgr.check_and_lock("28R", LockType.ARRIVAL, "FL200", "CLR-002")
        self.assertFalse(ok)

    def test_independent_runways(self):
        """10L and 10R are independent — can lock both simultaneously."""
        ok1, _, _ = self.mgr.check_and_lock("10L", LockType.ARRIVAL, "FL100", "CLR-001")
        ok2, _, _ = self.mgr.check_and_lock("10R", LockType.DEPARTURE, "FL200", "CLR-002")
        self.assertTrue(ok1)
        self.assertTrue(ok2)

    def test_release(self):
        """Release allows re-acquisition."""
        self.mgr.check_and_lock("10L", LockType.ARRIVAL, "FL100", "CLR-001")
        self.mgr.release("10L", "FL100")
        ok, _, _ = self.mgr.check_and_lock("10L", LockType.CROSSING, "TRUCK1", "CLR-002")
        self.assertTrue(ok)

    def test_release_wrong_holder(self):
        """Only the lock holder can release."""
        self.mgr.check_and_lock("10L", LockType.ARRIVAL, "FL100", "CLR-001")
        self.mgr.release("10L", "WRONG_ENTITY")
        # Lock should still be held
        self.assertTrue(self.mgr.is_locked("10L"))

    def test_upgrade_luaw_to_departure(self):
        """LUAW → DEPARTURE upgrade for same holder."""
        self.mgr.check_and_lock("10L", LockType.LUAW, "FL100", "CLR-001")
        ok, state, reason = self.mgr.upgrade_luaw_to_departure("10L", "FL100", "CLR-002")
        self.assertTrue(ok)
        self.assertEqual(state.lock_type, LockType.DEPARTURE)

    def test_upgrade_wrong_holder_fails(self):
        """Cannot upgrade LUAW if not the holder."""
        self.mgr.check_and_lock("10L", LockType.LUAW, "FL100", "CLR-001")
        ok, _, reason = self.mgr.upgrade_luaw_to_departure("10L", "FL200", "CLR-002")
        self.assertFalse(ok)

    def test_ttl_expiration_alert(self):
        """R4: TTL expiration generates alert."""
        self.mgr.check_and_lock("10L", LockType.CROSSING, "TRUCK1", "CLR-001")
        # Advance clock past CROSSING TTL (45s)
        self.clock.advance_to(50.0)
        alerts = self.mgr.check_ttl_expirations()
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0].alert_type, "runway.ttl_expired")

    def test_mark_occupied(self):
        """Runway transitions to OCCUPIED when entity detected on surface."""
        self.mgr.check_and_lock("10L", LockType.ARRIVAL, "FL100", "CLR-001")
        self.mgr.mark_occupied("10L")
        state = self.mgr.get_state("10L")
        self.assertEqual(state.lock_status, LockStatus.OCCUPIED)

    def test_race_condition_prevented(self):
        """Two proposals for same runway: first wins, second rejected."""
        ok1, _, _ = self.mgr.check_and_lock("10L", LockType.ARRIVAL, "FL100", "CLR-001")
        ok2, _, _ = self.mgr.check_and_lock("10L", LockType.CROSSING, "TRUCK1", "CLR-002")
        self.assertTrue(ok1)
        self.assertFalse(ok2)


if __name__ == "__main__":
    unittest.main()
