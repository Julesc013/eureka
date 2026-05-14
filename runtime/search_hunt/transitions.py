"""State transition helpers for local Search Hunt sessions."""

from dataclasses import replace

from .errors import SearchHuntTransitionError
from .records import SearchHuntSession, SearchHuntState, coerce_state, utc_now


ALLOWED_TRANSITIONS: dict[SearchHuntState, tuple[SearchHuntState, ...]] = {
    SearchHuntState.CREATED: (
        SearchHuntState.RUNNING,
        SearchHuntState.PAUSED,
        SearchHuntState.BLOCKED,
        SearchHuntState.CANCELLED,
    ),
    SearchHuntState.RUNNING: (
        SearchHuntState.PAUSED,
        SearchHuntState.WAITING_FOR_USER,
        SearchHuntState.WAITING_FOR_POLICY,
        SearchHuntState.COMPLETE,
        SearchHuntState.FAILED,
        SearchHuntState.BLOCKED,
        SearchHuntState.CANCELLED,
    ),
    SearchHuntState.PAUSED: (
        SearchHuntState.RUNNING,
        SearchHuntState.CANCELLED,
    ),
    SearchHuntState.WAITING_FOR_USER: (
        SearchHuntState.RUNNING,
        SearchHuntState.CANCELLED,
    ),
    SearchHuntState.WAITING_FOR_POLICY: (
        SearchHuntState.RUNNING,
        SearchHuntState.BLOCKED,
        SearchHuntState.CANCELLED,
    ),
    SearchHuntState.BLOCKED: (
        SearchHuntState.RUNNING,
        SearchHuntState.CANCELLED,
    ),
    SearchHuntState.FAILED: (
        SearchHuntState.RUNNING,
    ),
    SearchHuntState.COMPLETE: (
        SearchHuntState.COMPLETE,
    ),
    SearchHuntState.CANCELLED: (
        SearchHuntState.CANCELLED,
    ),
}


def validate_transition(current_state: SearchHuntState | str, target_state: SearchHuntState | str) -> SearchHuntState:
    current = coerce_state(current_state)
    target = coerce_state(target_state)
    if target not in ALLOWED_TRANSITIONS[current]:
        raise SearchHuntTransitionError(f"invalid Search Hunt transition: {current.value} -> {target.value}")
    return target


def apply_transition(session: SearchHuntSession, target_state: SearchHuntState | str, reason: str | None = None) -> SearchHuntSession:
    target = validate_transition(session.state, target_state)
    if session.state == target and target in (SearchHuntState.COMPLETE, SearchHuntState.CANCELLED):
        return session
    return replace(session, state=target, updated_at=utc_now())
