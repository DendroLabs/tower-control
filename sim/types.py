"""Shared type system for the ATC simulation.

All enums, dataclasses, and identifier types used across modules.
Direct translation of ATC_AUTOMATION_REPORT.md Sections 28-29 schemas.
"""

from __future__ import annotations

import enum
import itertools
from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Identifier generation
# ---------------------------------------------------------------------------

_counters: dict[str, itertools.count] = {}


def make_id(prefix: str) -> str:
    if prefix not in _counters:
        _counters[prefix] = itertools.count(1)
    return f"{prefix}-{next(_counters[prefix]):04d}"


def reset_ids() -> None:
    _counters.clear()


# ---------------------------------------------------------------------------
# Enums — Section 28
# ---------------------------------------------------------------------------

class IFRPhase(enum.Enum):
    PRE_DEPARTURE = "PRE_DEPARTURE"
    GROUND_OUT = "GROUND_OUT"
    DEPARTURE = "DEPARTURE"
    DEPARTURE_TRACON = "DEPARTURE_TRACON"
    ARRIVAL_TRACON = "ARRIVAL_TRACON"
    ARRIVAL = "ARRIVAL"
    GROUND_IN = "GROUND_IN"
    GO_AROUND = "GO_AROUND"


class IFRState(enum.Enum):
    # PRE_DEPARTURE
    PARKED = "PARKED"
    CLEARANCE_DELIVERED = "CLEARANCE_DELIVERED"
    PUSHBACK_APPROVED = "PUSHBACK_APPROVED"
    # GROUND_OUT
    TAXIING_OUT = "TAXIING_OUT"
    HOLDING_SHORT = "HOLDING_SHORT"
    LINEUP_WAIT = "LINEUP_WAIT"
    # DEPARTURE (Tower)
    TAKEOFF_ROLL = "TAKEOFF_ROLL"
    AIRBORNE_DEPARTURE = "AIRBORNE_DEPARTURE"
    # DEPARTURE_TRACON
    DEPARTURE_CONTACT = "DEPARTURE_CONTACT"
    DEPARTURE_CLIMBING = "DEPARTURE_CLIMBING"
    CENTER_HANDOFF = "CENTER_HANDOFF"
    # ARRIVAL_TRACON
    ARRIVAL_INBOUND = "ARRIVAL_INBOUND"
    SEQUENCED = "SEQUENCED"
    VECTORING = "VECTORING"
    APPROACH_CLEARED = "APPROACH_CLEARED"
    ESTABLISHED = "ESTABLISHED"
    TOWER_HANDOFF = "TOWER_HANDOFF"
    # ARRIVAL (Tower)
    INBOUND = "INBOUND"
    FINAL_APPROACH = "FINAL_APPROACH"
    LANDING_CLEARED = "LANDING_CLEARED"
    LANDING_ROLL = "LANDING_ROLL"
    RUNWAY_EXIT = "RUNWAY_EXIT"
    # GROUND_IN
    TAXIING_IN = "TAXIING_IN"
    PARKED_IN = "PARKED_IN"
    # GO_AROUND
    GO_AROUND_CLIMB = "GO_AROUND_CLIMB"
    RESEQUENCED = "RESEQUENCED"
    # EMERGENCY (overlay, not a phase state)
    EMERGENCY_DECLARED = "EMERGENCY_DECLARED"
    EMERGENCY_RESOLVED = "EMERGENCY_RESOLVED"
    # Terminal
    FLIGHT_COMPLETE = "FLIGHT_COMPLETE"


# Mapping from state to phase
STATE_TO_PHASE: dict[IFRState, IFRPhase] = {
    IFRState.PARKED: IFRPhase.PRE_DEPARTURE,
    IFRState.CLEARANCE_DELIVERED: IFRPhase.PRE_DEPARTURE,
    IFRState.PUSHBACK_APPROVED: IFRPhase.PRE_DEPARTURE,
    IFRState.TAXIING_OUT: IFRPhase.GROUND_OUT,
    IFRState.HOLDING_SHORT: IFRPhase.GROUND_OUT,
    IFRState.LINEUP_WAIT: IFRPhase.GROUND_OUT,
    IFRState.TAKEOFF_ROLL: IFRPhase.DEPARTURE,
    IFRState.AIRBORNE_DEPARTURE: IFRPhase.DEPARTURE,
    IFRState.DEPARTURE_CONTACT: IFRPhase.DEPARTURE_TRACON,
    IFRState.DEPARTURE_CLIMBING: IFRPhase.DEPARTURE_TRACON,
    IFRState.CENTER_HANDOFF: IFRPhase.DEPARTURE_TRACON,
    IFRState.ARRIVAL_INBOUND: IFRPhase.ARRIVAL_TRACON,
    IFRState.SEQUENCED: IFRPhase.ARRIVAL_TRACON,
    IFRState.VECTORING: IFRPhase.ARRIVAL_TRACON,
    IFRState.APPROACH_CLEARED: IFRPhase.ARRIVAL_TRACON,
    IFRState.ESTABLISHED: IFRPhase.ARRIVAL_TRACON,
    IFRState.TOWER_HANDOFF: IFRPhase.ARRIVAL_TRACON,
    IFRState.INBOUND: IFRPhase.ARRIVAL,
    IFRState.FINAL_APPROACH: IFRPhase.ARRIVAL,
    IFRState.LANDING_CLEARED: IFRPhase.ARRIVAL,
    IFRState.LANDING_ROLL: IFRPhase.ARRIVAL,
    IFRState.RUNWAY_EXIT: IFRPhase.ARRIVAL,
    IFRState.TAXIING_IN: IFRPhase.GROUND_IN,
    IFRState.PARKED_IN: IFRPhase.GROUND_IN,
    IFRState.GO_AROUND_CLIMB: IFRPhase.GO_AROUND,
    IFRState.RESEQUENCED: IFRPhase.GO_AROUND,
}


class VFRPatternState(enum.Enum):
    UPWIND = "UPWIND"
    CROSSWIND = "CROSSWIND"
    DOWNWIND = "DOWNWIND"
    BASE = "BASE"
    PATTERN_FINAL = "PATTERN_FINAL"
    TOUCH_AND_GO = "TOUCH_AND_GO"
    STOP_AND_GO = "STOP_AND_GO"
    LOW_APPROACH = "LOW_APPROACH"
    FULL_STOP = "FULL_STOP"


class VehicleState(enum.Enum):
    STATIONARY = "STATIONARY"
    TAXI_CLEARED = "TAXI_CLEARED"
    MOVING = "MOVING"
    HOLDING_SHORT = "HOLDING_SHORT"
    CROSSING_CLEARED = "CROSSING_CLEARED"
    ON_RUNWAY = "ON_RUNWAY"
    CLEAR_OF_RUNWAY = "CLEAR_OF_RUNWAY"


class LockType(enum.Enum):
    DEPARTURE = "DEPARTURE"
    ARRIVAL = "ARRIVAL"
    CROSSING = "CROSSING"
    LUAW = "LUAW"
    PATTERN = "PATTERN"


class LockStatus(enum.Enum):
    AVAILABLE = "AVAILABLE"
    RESERVED = "RESERVED"
    OCCUPIED = "OCCUPIED"


class ClearanceState(enum.Enum):
    PROPOSED = "PROPOSED"
    VALIDATED = "VALIDATED"
    REJECTED = "REJECTED"
    ISSUED = "ISSUED"
    READBACK_OK = "READBACK_OK"
    READBACK_FAIL = "READBACK_FAIL"
    NO_RESPONSE = "NO_RESPONSE"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    SUPERSEDED = "SUPERSEDED"
    EXPIRED = "EXPIRED"


class ClearanceType(enum.Enum):
    IFR_CLEARANCE = "IFR_CLEARANCE"
    PUSHBACK_APPROVAL = "PUSHBACK_APPROVAL"
    TAXI_OUT = "TAXI_OUT"
    HOLD_SHORT = "HOLD_SHORT"
    LINEUP_WAIT = "LINEUP_WAIT"
    HOLD_POSITION = "HOLD_POSITION"
    TAKEOFF = "TAKEOFF"
    LANDING = "LANDING"
    GO_AROUND = "GO_AROUND"
    TAXI_IN = "TAXI_IN"
    RUNWAY_CROSSING = "RUNWAY_CROSSING"
    SEQUENCE_ASSIGNMENT = "SEQUENCE_ASSIGNMENT"
    VECTORING = "VECTORING"
    APPROACH_CLEARANCE = "APPROACH_CLEARANCE"
    ALTITUDE_HEADING = "ALTITUDE_HEADING"
    PATTERN_ENTRY = "PATTERN_ENTRY"
    TOUCH_AND_GO = "TOUCH_AND_GO"
    STOP_AND_GO = "STOP_AND_GO"
    LOW_APPROACH = "LOW_APPROACH"
    SEQUENCE_INSTRUCTION = "SEQUENCE_INSTRUCTION"
    FREQUENCY_CHANGE = "FREQUENCY_CHANGE"


# Which clearance types acquire runway locks, and what type
CLEARANCE_LOCK_TYPE: dict[ClearanceType, LockType] = {
    ClearanceType.LINEUP_WAIT: LockType.LUAW,
    ClearanceType.TAKEOFF: LockType.DEPARTURE,
    ClearanceType.LANDING: LockType.ARRIVAL,
    ClearanceType.RUNWAY_CROSSING: LockType.CROSSING,
    ClearanceType.TOUCH_AND_GO: LockType.PATTERN,
    ClearanceType.STOP_AND_GO: LockType.PATTERN,
    ClearanceType.LOW_APPROACH: LockType.PATTERN,
}


class AlertSeverity(enum.Enum):
    ADVISORY = "ADVISORY"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class SurveillanceSource(enum.Enum):
    ADSB = "ADSB"
    RADAR = "RADAR"
    MLAT = "MLAT"
    SURFACE = "SURFACE"


class EntityType(enum.Enum):
    AIRCRAFT = "AIRCRAFT"
    VEHICLE = "VEHICLE"


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass(slots=True)
class LatLonAlt:
    latitude: float
    longitude: float
    altitude_ft: float = 0.0


@dataclass(slots=True)
class Vector3D:
    ground_speed_kts: float = 0.0
    heading_deg: float = 0.0
    vertical_rate_fpm: float = 0.0


@dataclass(slots=True)
class TaxiRoute:
    segments: list[str] = field(default_factory=list)
    hold_short: list[str] = field(default_factory=list)


@dataclass(slots=True)
class SurveillanceRef:
    source: SurveillanceSource
    entity_id: str
    position: LatLonAlt
    velocity: Vector3D
    timestamp: float


@dataclass(slots=True)
class RunwayLockState:
    runway_id: str
    lock_status: LockStatus
    lock_type: LockType | None = None
    holder: str | None = None
    clearance_id: str | None = None
    acquired_at: float | None = None
    ttl_remaining: float | None = None


@dataclass(slots=True)
class ClearanceProposal:
    proposal_id: str
    proposing_agent: str
    timestamp: float
    target_entity: str
    target_entity_type: EntityType
    clearance_type: ClearanceType
    parameters: dict = field(default_factory=dict)
    surveillance_refs: list[SurveillanceRef] = field(default_factory=list)


@dataclass(slots=True)
class ValidationResult:
    proposal_id: str
    result: str  # "VALIDATED" or "REJECTED"
    timestamp: float
    clearance_id: str | None = None
    lock_acquired: RunwayLockState | None = None
    rejection: dict | None = None
    runway_state: RunwayLockState | None = None


@dataclass(slots=True)
class InvariantViolation:
    invariant_id: str
    description: str
    affected_entities: list[str] = field(default_factory=list)
    blocking_entity: str | None = None
    blocking_clearance: str | None = None


@dataclass(slots=True)
class Alert:
    alert_id: str
    alert_type: str
    severity: AlertSeverity
    affected_entities: list[str] = field(default_factory=list)
    description: str = ""
    recommended_action: str | None = None
    timestamp: float = 0.0


@dataclass(slots=True)
class FlightStateSnapshot:
    flight_id: str
    phase: IFRPhase | None
    state: IFRState
    emergency: bool = False
    position: LatLonAlt | None = None
    velocity: Vector3D | None = None
    runway_assignment: str | None = None
    active_clearance_ids: list[str] = field(default_factory=list)
