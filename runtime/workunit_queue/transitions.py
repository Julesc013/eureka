"""State transition rules for durable local work records."""

from dataclasses import replace
from typing import Mapping

from .errors import WorkUnitTransitionError
from .records import WorkUnit, WorkUnitState, utc_now


ALLOWED_TRANSITIONS: Mapping[WorkUnitState, tuple[WorkUnitState, ...]] = {
    WorkUnitState.QUEUED: (
        WorkUnitState.RUNNING,
        WorkUnitState.PAUSED,
        WorkUnitState.BLOCKED,
        WorkUnitState.CANCELLED,
    ),
    WorkUnitState.RUNNING: (
        WorkUnitState.PAUSED,
        WorkUnitState.COMPLETE,
        WorkUnitState.FAILED,
        WorkUnitState.BLOCKED,
        WorkUnitState.CANCELLED,
    ),
    WorkUnitState.PAUSED: (WorkUnitState.QUEUED, WorkUnitState.CANCELLED),
    WorkUnitState.BLOCKED: (WorkUnitState.QUEUED, WorkUnitState.CANCELLED),
    WorkUnitState.FAILED: (WorkUnitState.QUEUED,),
    WorkUnitState.COMPLETE: (WorkUnitState.COMPLETE,),
    WorkUnitState.CANCELLED: (WorkUnitState.CANCELLED,),
}


def validate_transition(current_state: WorkUnitState | str, target_state: WorkUnitState | str) -> None:
    current = current_state if isinstance(current_state, WorkUnitState) else WorkUnitState(str(current_state))
    target = target_state if isinstance(target_state, WorkUnitState) else WorkUnitState(str(target_state))
    if target not in ALLOWED_TRANSITIONS.get(current, ()):
        raise WorkUnitTransitionError(f"invalid transition: {current.value} -> {target.value}")


def apply_transition(workunit: WorkUnit, target_state: WorkUnitState | str, reason: str | None = None) -> WorkUnit:
    target = target_state if isinstance(target_state, WorkUnitState) else WorkUnitState(str(target_state))
    validate_transition(workunit.state, target)
    blocked_reason = reason if target == WorkUnitState.BLOCKED else None
    if workunit.state == target and target in {WorkUnitState.COMPLETE, WorkUnitState.CANCELLED}:
        return workunit
    return replace(
        workunit,
        state=target,
        updated_at=utc_now(),
        blocked_reason=blocked_reason,
    )
