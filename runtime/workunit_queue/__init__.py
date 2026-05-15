"""Durable local work queue runtime API."""

from .errors import (
    WorkUnitNotFoundError,
    WorkUnitQueueClosedError,
    WorkUnitQueueError,
    WorkUnitTransitionError,
    WorkUnitValidationError,
)
from .records import WorkUnit, WorkUnitPayloadRef, WorkUnitPriority, WorkUnitState, WorkUnitSummary, WorkUnitTransition, WorkUnitType
from .store import WorkUnitQueueStore
from .transitions import ALLOWED_TRANSITIONS, apply_transition, validate_transition
from .validation import (
    ALLOWED_WORKUNIT_PRIORITIES,
    ALLOWED_WORKUNIT_STATES,
    ALLOWED_WORKUNIT_TYPES,
    require_reason,
    validate_no_execution_flags,
    validate_queue_path,
    validate_workunit,
    validate_workunit_kind,
    validate_workunit_priority,
    validate_workunit_state,
)

__all__ = [
    "ALLOWED_TRANSITIONS",
    "ALLOWED_WORKUNIT_PRIORITIES",
    "ALLOWED_WORKUNIT_STATES",
    "ALLOWED_WORKUNIT_TYPES",
    "WorkUnit",
    "WorkUnitNotFoundError",
    "WorkUnitPayloadRef",
    "WorkUnitPriority",
    "WorkUnitQueueClosedError",
    "WorkUnitQueueError",
    "WorkUnitQueueStore",
    "WorkUnitState",
    "WorkUnitSummary",
    "WorkUnitTransition",
    "WorkUnitTransitionError",
    "WorkUnitType",
    "WorkUnitValidationError",
    "apply_transition",
    "require_reason",
    "validate_no_execution_flags",
    "validate_queue_path",
    "validate_transition",
    "validate_workunit",
    "validate_workunit_kind",
    "validate_workunit_priority",
    "validate_workunit_state",
]
