"""Tests for clearance lifecycle (Section 28.6)."""

import unittest
from sim.clock import SimClock
from sim.events import EventBus
from sim.types import ClearanceType, ClearanceState, reset_ids
from sim.state.clearance import ClearanceLifecycle


class TestClearanceLifecycle(unittest.TestCase):
    def setUp(self):
        reset_ids()
        self.clock = SimClock()
        self.event_bus = EventBus(self.clock)
        self.mgr = ClearanceLifecycle(self.clock, self.event_bus)

    def test_full_lifecycle(self):
        """PROPOSED → VALIDATED → ISSUED → READBACK_OK → ACTIVE → COMPLETED."""
        clr = self.mgr.create_proposal(ClearanceType.LANDING, "FL100", "AIRCRAFT")
        self.assertEqual(clr.state, ClearanceState.PROPOSED)

        self.mgr.mark_validated(clr.clearance_id)
        self.assertEqual(clr.state, ClearanceState.VALIDATED)

        self.mgr.mark_issued(clr.clearance_id)
        self.assertEqual(clr.state, ClearanceState.ISSUED)

        self.mgr.mark_readback_ok(clr.clearance_id)
        self.assertEqual(clr.state, ClearanceState.READBACK_OK)

        self.mgr.mark_active(clr.clearance_id)
        self.assertEqual(clr.state, ClearanceState.ACTIVE)

        self.mgr.mark_completed(clr.clearance_id)
        self.assertEqual(clr.state, ClearanceState.COMPLETED)

    def test_rejection(self):
        """PROPOSED → REJECTED is terminal."""
        clr = self.mgr.create_proposal(ClearanceType.RUNWAY_CROSSING, "TRUCK1", "VEHICLE")
        self.mgr.mark_rejected(clr.clearance_id)
        self.assertEqual(clr.state, ClearanceState.REJECTED)

    def test_invalid_transition_raises(self):
        """Cannot skip VALIDATED: PROPOSED → ISSUED should raise."""
        clr = self.mgr.create_proposal(ClearanceType.TAKEOFF, "FL100", "AIRCRAFT")
        with self.assertRaises(ValueError):
            self.mgr.mark_issued(clr.clearance_id)

    def test_readback_fail_reissue(self):
        """READBACK_FAIL → re-issue → back to ISSUED."""
        clr = self.mgr.create_proposal(ClearanceType.LANDING, "FL100", "AIRCRAFT")
        self.mgr.mark_validated(clr.clearance_id)
        self.mgr.mark_issued(clr.clearance_id)
        self.mgr.mark_readback_fail(clr.clearance_id)
        self.assertEqual(clr.state, ClearanceState.READBACK_FAIL)

        self.mgr.reissue(clr.clearance_id)
        self.assertEqual(clr.state, ClearanceState.ISSUED)
        self.assertEqual(clr.retransmit_count, 1)

    def test_supersede(self):
        """Active clearance can be superseded."""
        clr = self.mgr.create_proposal(ClearanceType.LANDING, "FL100", "AIRCRAFT")
        self.mgr.mark_validated(clr.clearance_id)
        self.mgr.mark_issued(clr.clearance_id)
        self.mgr.mark_readback_ok(clr.clearance_id)
        self.mgr.mark_active(clr.clearance_id)

        self.mgr.mark_superseded(clr.clearance_id, "CLR-NEW")
        self.assertEqual(clr.state, ClearanceState.SUPERSEDED)
        self.assertEqual(clr.superseded_by, "CLR-NEW")

    def test_mutual_exclusion_C2(self):
        """C2: Cannot have LANDING and GO_AROUND active simultaneously."""
        clr = self.mgr.create_proposal(ClearanceType.LANDING, "FL100", "AIRCRAFT")
        self.mgr.mark_validated(clr.clearance_id)
        self.mgr.mark_issued(clr.clearance_id)
        self.mgr.mark_readback_ok(clr.clearance_id)
        self.mgr.mark_active(clr.clearance_id)

        violations = self.mgr.check_mutual_exclusion("FL100", ClearanceType.GO_AROUND)
        self.assertEqual(violations, ["C2"])

    def test_no_mutual_exclusion_different_types(self):
        """Non-conflicting types should not trigger C2."""
        clr = self.mgr.create_proposal(ClearanceType.TAXI_OUT, "FL100", "AIRCRAFT")
        self.mgr.mark_validated(clr.clearance_id)
        self.mgr.mark_issued(clr.clearance_id)
        self.mgr.mark_readback_ok(clr.clearance_id)
        self.mgr.mark_active(clr.clearance_id)

        violations = self.mgr.check_mutual_exclusion("FL100", ClearanceType.LANDING)
        self.assertEqual(violations, [])


if __name__ == "__main__":
    unittest.main()
