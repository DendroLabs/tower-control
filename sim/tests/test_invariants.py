"""Tests for formal invariant checks (Section 28.8)."""

import unittest
from sim.clock import SimClock
from sim.events import EventBus
from sim.types import (
    LockType, ClearanceType, ClearanceProposal, EntityType,
    SurveillanceRef, SurveillanceSource, LatLonAlt, Vector3D,
    reset_ids,
)
from sim.state.runway import RunwayLockManager
from sim.state.clearance import ClearanceLifecycle
from sim.safety.invariants import InvariantChecker


class TestInvariantChecker(unittest.TestCase):
    def setUp(self):
        reset_ids()
        self.clock = SimClock()
        self.event_bus = EventBus(self.clock)
        self.runway_mgr = RunwayLockManager(
            ["10L/28R", "10R/28L"],
            {"10L": "10L/28R", "28R": "10L/28R", "10R": "10R/28L", "28L": "10R/28L"},
            self.clock, self.event_bus,
        )
        self.clearance_mgr = ClearanceLifecycle(self.clock, self.event_bus)
        self.checker = InvariantChecker(self.runway_mgr, self.clearance_mgr, self.clock)

    def test_R2_detects_locked_runway(self):
        """R2: Detects attempt to lock already-locked runway."""
        self.runway_mgr.check_and_lock("10L", LockType.ARRIVAL, "FL100", "CLR-001")
        v = self.checker.check_R2("10L", LockType.CROSSING)
        self.assertIsNotNone(v)
        self.assertEqual(v.invariant_id, "R2")
        self.assertEqual(v.blocking_entity, "FL100")

    def test_R2_passes_on_available(self):
        """R2: No violation when runway is available."""
        v = self.checker.check_R2("10L", LockType.ARRIVAL)
        self.assertIsNone(v)

    def test_C5_detects_stale_data(self):
        """C5: Detects stale surveillance data."""
        refs = [SurveillanceRef(
            source=SurveillanceSource.RADAR,
            entity_id="FL100",
            position=LatLonAlt(35.0, -80.0, 2000.0),
            velocity=Vector3D(140.0, 280.0, -700.0),
            timestamp=0.0,  # data from t=0
        )]
        self.clock.advance_to(10.0)  # now=10, data is 10s old
        v = self.checker.check_C5(refs, max_age_sec=5.0)
        self.assertIsNotNone(v)
        self.assertEqual(v.invariant_id, "C5")

    def test_C5_passes_fresh_data(self):
        """C5: No violation with fresh data."""
        self.clock.advance_to(10.0)
        refs = [SurveillanceRef(
            source=SurveillanceSource.RADAR,
            entity_id="FL100",
            position=LatLonAlt(35.0, -80.0, 2000.0),
            velocity=Vector3D(140.0, 280.0, -700.0),
            timestamp=8.0,  # 2s old
        )]
        v = self.checker.check_C5(refs, max_age_sec=5.0)
        self.assertIsNone(v)

    def test_S4_detects_untracked(self):
        """S4: Detects entity visible to sensors but not tracked."""
        tracked = {"FL100", "FL200"}
        detected = {"FL100", "FL200", "HELO1"}  # HELO1 is untracked
        violations = self.checker.check_S4(tracked, detected)
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0].invariant_id, "S4")
        self.assertIn("HELO1", violations[0].affected_entities)

    def test_S4_passes_all_tracked(self):
        """S4: No violation when all detected entities are tracked."""
        tracked = {"FL100", "FL200"}
        detected = {"FL100", "FL200"}
        violations = self.checker.check_S4(tracked, detected)
        self.assertEqual(len(violations), 0)

    def test_check_proposal_landing_on_locked_runway(self):
        """Composite check: landing proposal on locked runway should fail."""
        self.runway_mgr.check_and_lock("10L", LockType.ARRIVAL, "FL100", "CLR-001")

        proposal = ClearanceProposal(
            proposal_id="PROP-001",
            proposing_agent="test",
            timestamp=0.0,
            target_entity="FL200",
            target_entity_type=EntityType.AIRCRAFT,
            clearance_type=ClearanceType.LANDING,
            parameters={"runway": "10L"},
            surveillance_refs=[SurveillanceRef(
                source=SurveillanceSource.RADAR,
                entity_id="FL200",
                position=LatLonAlt(35.0, -80.0, 2000.0),
                velocity=Vector3D(140.0, 280.0, -700.0),
                timestamp=0.0,
            )],
        )

        violations = self.checker.check_proposal(proposal)
        inv_ids = [v.invariant_id for v in violations]
        self.assertIn("R2", inv_ids)

    def test_F5_detects_past_commitment_gate(self):
        """F5: Aircraft past commitment gate without landing clearance."""
        v = self.checker.check_F5("FL100", has_landing_clearance=False, past_commitment_gate=True)
        self.assertIsNotNone(v)
        self.assertEqual(v.invariant_id, "F5")

    def test_F5_passes_with_clearance(self):
        """F5: No violation when aircraft has landing clearance."""
        v = self.checker.check_F5("FL100", has_landing_clearance=True, past_commitment_gate=True)
        self.assertIsNone(v)

    def test_S1_entity_on_runway_without_lock(self):
        """S1: Entity on runway without matching lock."""
        violations = self.checker.check_S1("10L", ["FL100"])
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0].invariant_id, "S1")

    def test_S1_entity_on_runway_with_lock(self):
        """S1: No violation when entity has matching lock."""
        self.runway_mgr.check_and_lock("10L", LockType.ARRIVAL, "FL100", "CLR-001")
        violations = self.checker.check_S1("10L", ["FL100"])
        self.assertEqual(len(violations), 0)


if __name__ == "__main__":
    unittest.main()
