"""Tests for flight, VFR, and vehicle state machines."""

import unittest
from sim.clock import SimClock
from sim.events import EventBus
from sim.types import IFRState, VFRPatternState, VehicleState, ClearanceType, reset_ids
from sim.state.flight import FlightStateMachine
from sim.state.vfr_pattern import VFRPatternStateMachine
from sim.state.vehicle import VehicleStateMachine


class TestFlightStateMachine(unittest.TestCase):
    def setUp(self):
        reset_ids()
        self.clock = SimClock()
        self.event_bus = EventBus(self.clock)

    def _make_flight(self, state=IFRState.PARKED):
        return FlightStateMachine("FL100", state, self.clock, self.event_bus)

    def test_valid_departure_sequence(self):
        """Full departure: PARKED → CLEARANCE_DELIVERED → PUSHBACK → TAXIING_OUT → HOLDING_SHORT."""
        f = self._make_flight()
        self.assertTrue(f.transition(IFRState.CLEARANCE_DELIVERED, ClearanceType.IFR_CLEARANCE))
        self.assertTrue(f.transition(IFRState.PUSHBACK_APPROVED, ClearanceType.PUSHBACK_APPROVAL))
        self.assertTrue(f.transition(IFRState.TAXIING_OUT, ClearanceType.TAXI_OUT))
        self.assertTrue(f.transition(IFRState.HOLDING_SHORT))  # surveillance-triggered
        self.assertEqual(f.state, IFRState.HOLDING_SHORT)

    def test_invalid_transition_rejected(self):
        """Cannot skip states: PARKED → TAKEOFF_ROLL should fail."""
        f = self._make_flight()
        self.assertFalse(f.transition(IFRState.TAKEOFF_ROLL, ClearanceType.TAKEOFF))
        self.assertEqual(f.state, IFRState.PARKED)

    def test_takeoff_from_holding_short(self):
        """Direct takeoff from HOLDING_SHORT (without LUAW)."""
        f = self._make_flight(IFRState.HOLDING_SHORT)
        self.assertTrue(f.transition(IFRState.TAKEOFF_ROLL, ClearanceType.TAKEOFF))

    def test_takeoff_from_luaw(self):
        """LINEUP_WAIT → TAKEOFF_ROLL."""
        f = self._make_flight(IFRState.LINEUP_WAIT)
        self.assertTrue(f.transition(IFRState.TAKEOFF_ROLL, ClearanceType.TAKEOFF))

    def test_arrival_sequence(self):
        """INBOUND → FINAL_APPROACH → LANDING_CLEARED → LANDING_ROLL → RUNWAY_EXIT."""
        f = self._make_flight(IFRState.INBOUND)
        self.assertTrue(f.transition(IFRState.FINAL_APPROACH))  # surveillance
        self.assertTrue(f.transition(IFRState.LANDING_CLEARED, ClearanceType.LANDING))
        self.assertTrue(f.transition(IFRState.LANDING_ROLL))  # surveillance
        self.assertTrue(f.transition(IFRState.RUNWAY_EXIT))  # surveillance
        self.assertEqual(f.state, IFRState.RUNWAY_EXIT)

    def test_go_around_from_final(self):
        """Go-around from FINAL_APPROACH."""
        f = self._make_flight(IFRState.FINAL_APPROACH)
        self.assertTrue(f.transition(IFRState.GO_AROUND_CLIMB, ClearanceType.GO_AROUND))

    def test_go_around_from_landing_cleared(self):
        """Go-around from LANDING_CLEARED."""
        f = self._make_flight(IFRState.LANDING_CLEARED)
        self.assertTrue(f.transition(IFRState.GO_AROUND_CLIMB, ClearanceType.GO_AROUND))

    def test_emergency_overlay(self):
        """Emergency can be declared from any state."""
        f = self._make_flight(IFRState.TAXIING_OUT)
        f.enter_emergency()
        self.assertTrue(f.emergency)
        self.assertEqual(f.state, IFRState.TAXIING_OUT)  # state unchanged
        f.resolve_emergency()
        self.assertFalse(f.emergency)

    def test_clearance_required_for_landing(self):
        """Cannot transition to LANDING_CLEARED without LANDING clearance."""
        f = self._make_flight(IFRState.FINAL_APPROACH)
        self.assertFalse(f.transition(IFRState.LANDING_CLEARED))  # no clearance
        self.assertFalse(f.transition(IFRState.LANDING_CLEARED, ClearanceType.TAKEOFF))  # wrong type


class TestVFRPatternStateMachine(unittest.TestCase):
    def setUp(self):
        reset_ids()
        self.clock = SimClock()
        self.event_bus = EventBus(self.clock)

    def test_pattern_legs_no_clearance(self):
        """Pattern legs transition without clearance (pilot discretion)."""
        vfr = VFRPatternStateMachine("VFR1", "10L", self.clock, self.event_bus)
        self.assertTrue(vfr.transition(VFRPatternState.CROSSWIND))
        self.assertTrue(vfr.transition(VFRPatternState.DOWNWIND))
        self.assertTrue(vfr.transition(VFRPatternState.BASE))
        self.assertTrue(vfr.transition(VFRPatternState.PATTERN_FINAL))

    def test_touch_and_go_requires_clearance(self):
        """Touch-and-go from PATTERN_FINAL requires clearance."""
        vfr = VFRPatternStateMachine("VFR1", "10L", self.clock, self.event_bus,
                                      initial_state=VFRPatternState.PATTERN_FINAL)
        self.assertFalse(vfr.transition(VFRPatternState.TOUCH_AND_GO))  # no clearance
        self.assertTrue(vfr.transition(VFRPatternState.TOUCH_AND_GO, ClearanceType.TOUCH_AND_GO))

    def test_lap_counter(self):
        """Laps increment after touch-and-go → UPWIND."""
        vfr = VFRPatternStateMachine("VFR1", "10L", self.clock, self.event_bus,
                                      initial_state=VFRPatternState.TOUCH_AND_GO)
        vfr.transition(VFRPatternState.UPWIND)
        self.assertEqual(vfr.laps_completed, 1)


class TestVehicleStateMachine(unittest.TestCase):
    def setUp(self):
        reset_ids()
        self.clock = SimClock()
        self.event_bus = EventBus(self.clock)

    def test_normal_crossing_sequence(self):
        """STATIONARY → TAXI_CLEARED → MOVING → HOLDING_SHORT → CROSSING_CLEARED."""
        v = VehicleStateMachine("TRUCK1", "fire_truck", self.clock, self.event_bus)
        self.assertTrue(v.transition(VehicleState.TAXI_CLEARED, ClearanceType.TAXI_OUT))
        self.assertTrue(v.transition(VehicleState.MOVING))  # surveillance
        self.assertTrue(v.transition(VehicleState.HOLDING_SHORT))  # surveillance
        self.assertTrue(v.transition(VehicleState.CROSSING_CLEARED, ClearanceType.RUNWAY_CROSSING))

    def test_crossing_requires_clearance(self):
        """Cannot cross runway without RUNWAY_CROSSING clearance."""
        v = VehicleStateMachine("TRUCK1", "fire_truck", self.clock, self.event_bus,
                                initial_state=VehicleState.HOLDING_SHORT)
        self.assertFalse(v.transition(VehicleState.CROSSING_CLEARED))  # no clearance
        self.assertTrue(v.transition(VehicleState.CROSSING_CLEARED, ClearanceType.RUNWAY_CROSSING))


if __name__ == "__main__":
    unittest.main()
