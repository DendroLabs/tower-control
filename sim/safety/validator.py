"""Clearance Validation API — Section 29.2.

The deterministic safety net. Agents propose, this validates.
Atomic validation + lock acquisition per Section 28.5.4.
"""

from __future__ import annotations

from sim.types import (
    ClearanceProposal, ValidationResult, ClearanceType, ClearanceState,
    CLEARANCE_LOCK_TYPE, make_id,
)
from sim.state.runway import RunwayLockManager
from sim.state.clearance import ClearanceLifecycle, Clearance
from sim.safety.invariants import InvariantChecker
from sim.clock import SimClock
from sim.events import EventBus


class ClearanceValidator:
    """The deterministic safety net. No clearance reaches a pilot without this."""

    def __init__(
        self,
        invariant_checker: InvariantChecker,
        runway_mgr: RunwayLockManager,
        clearance_mgr: ClearanceLifecycle,
        event_bus: EventBus,
        clock: SimClock,
    ) -> None:
        self._invariants = invariant_checker
        self._runway_mgr = runway_mgr
        self._clearance_mgr = clearance_mgr
        self._event_bus = event_bus
        self._clock = clock

    def validate(self, proposal: ClearanceProposal) -> tuple[ValidationResult, Clearance]:
        """Atomic validation + lock acquisition.

        1. Create clearance in PROPOSED state
        2. Check all applicable invariants
        3. If all pass AND clearance acquires a lock: atomic check-and-lock
        4. Return VALIDATED or REJECTED
        """
        # Step 1: Create clearance
        clr = self._clearance_mgr.create_proposal(
            clearance_type=proposal.clearance_type,
            target_entity=proposal.target_entity,
            target_entity_type=proposal.target_entity_type.value,
            parameters=proposal.parameters,
            proposing_agent=proposal.proposing_agent,
        )

        # Step 2: Check invariants
        violations = self._invariants.check_proposal(proposal)

        if violations:
            self._clearance_mgr.mark_rejected(clr.clearance_id)
            result = ValidationResult(
                proposal_id=proposal.proposal_id,
                result="REJECTED",
                timestamp=self._clock.now(),
                rejection={
                    "invariants_violated": [v.invariant_id for v in violations],
                    "reason": "; ".join(v.description for v in violations),
                    "blocking_entity": violations[0].blocking_entity,
                    "blocking_clearance": violations[0].blocking_clearance,
                },
            )
            # Include runway state if relevant
            runway_id = proposal.parameters.get("runway")
            if runway_id:
                result.runway_state = self._runway_mgr.get_state(runway_id)

            self._event_bus.publish(
                f"clearance.{clr.clearance_id}.rejected",
                "clearance_validator",
                {"proposal_id": proposal.proposal_id, "violations": [v.invariant_id for v in violations]},
            )
            return result, clr

        # Step 3: Acquire lock if needed (atomic with validation)
        lock_type = CLEARANCE_LOCK_TYPE.get(proposal.clearance_type)
        runway_id = proposal.parameters.get("runway")
        lock_state = None

        if lock_type and runway_id:
            # Special case: TAKEOFF upgrades LUAW if same holder
            if (proposal.clearance_type == ClearanceType.TAKEOFF
                    and self._runway_mgr.is_locked(runway_id)
                    and self._runway_mgr.get_lock_holder(runway_id) == proposal.target_entity):
                success, lock_state, reason = self._runway_mgr.upgrade_luaw_to_departure(
                    runway_id, proposal.target_entity, clr.clearance_id,
                )
            else:
                success, lock_state, reason = self._runway_mgr.check_and_lock(
                    runway_id, lock_type, proposal.target_entity, clr.clearance_id,
                )

            if not success:
                self._clearance_mgr.mark_rejected(clr.clearance_id)
                result = ValidationResult(
                    proposal_id=proposal.proposal_id,
                    result="REJECTED",
                    timestamp=self._clock.now(),
                    rejection={
                        "invariants_violated": ["R1", "R2"],
                        "reason": reason or "Lock acquisition failed",
                        "blocking_entity": lock_state.holder if lock_state else None,
                        "blocking_clearance": lock_state.clearance_id if lock_state else None,
                    },
                    runway_state=lock_state,
                )
                self._event_bus.publish(
                    f"clearance.{clr.clearance_id}.rejected",
                    "clearance_validator",
                    {"proposal_id": proposal.proposal_id, "violations": ["R1", "R2"]},
                )
                return result, clr

        # Step 4: Mark validated
        self._clearance_mgr.mark_validated(clr.clearance_id, lock_state)

        result = ValidationResult(
            proposal_id=proposal.proposal_id,
            result="VALIDATED",
            timestamp=self._clock.now(),
            clearance_id=clr.clearance_id,
            lock_acquired=lock_state,
        )
        if runway_id:
            result.runway_state = self._runway_mgr.get_state(runway_id)

        self._event_bus.publish(
            f"clearance.{clr.clearance_id}.validated",
            "clearance_validator",
            {"proposal_id": proposal.proposal_id, "clearance_id": clr.clearance_id},
        )
        return result, clr
