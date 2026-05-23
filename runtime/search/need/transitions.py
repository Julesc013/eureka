"""SearchNeed state transition rules."""

from .errors import SearchNeedTransitionError
from .records import SearchNeed, SearchNeedState


ALLOWED_TRANSITIONS: dict[SearchNeedState, tuple[SearchNeedState, ...]] = {
    SearchNeedState.PROPOSED: (SearchNeedState.OPEN, SearchNeedState.BLOCKED, SearchNeedState.CANCELLED),
    SearchNeedState.OPEN: (
        SearchNeedState.WAITING_FOR_USER,
        SearchNeedState.WAITING_FOR_POLICY,
        SearchNeedState.BLOCKED,
        SearchNeedState.SATISFIED_LOCALLY,
        SearchNeedState.SUPERSEDED,
        SearchNeedState.CANCELLED,
    ),
    SearchNeedState.WAITING_FOR_USER: (SearchNeedState.OPEN, SearchNeedState.CANCELLED),
    SearchNeedState.WAITING_FOR_POLICY: (SearchNeedState.OPEN, SearchNeedState.BLOCKED, SearchNeedState.CANCELLED),
    SearchNeedState.BLOCKED: (SearchNeedState.OPEN, SearchNeedState.CANCELLED),
    SearchNeedState.SATISFIED_LOCALLY: (SearchNeedState.SATISFIED_LOCALLY,),
    SearchNeedState.SUPERSEDED: (SearchNeedState.SUPERSEDED,),
    SearchNeedState.CANCELLED: (SearchNeedState.CANCELLED,),
}


def validate_transition(current_state: SearchNeedState | str, target_state: SearchNeedState | str) -> SearchNeedState:
    current = current_state if isinstance(current_state, SearchNeedState) else SearchNeedState(str(current_state))
    target = target_state if isinstance(target_state, SearchNeedState) else SearchNeedState(str(target_state))
    if target not in ALLOWED_TRANSITIONS[current]:
        raise SearchNeedTransitionError(f"invalid SearchNeed transition: {current.value} -> {target.value}")
    return target


def apply_transition(need: SearchNeed, target_state: SearchNeedState | str, reason: str | None = None) -> SearchNeed:
    target = validate_transition(need.state, target_state)
    if target == need.state:
        return need
    return need.with_state(target, reason)
