"""Durable local SearchNeed runtime."""

from .errors import (
    SearchNeedClosedError,
    SearchNeedError,
    SearchNeedIntegrityError,
    SearchNeedNotFoundError,
    SearchNeedTransitionError,
    SearchNeedValidationError,
)
from .from_hunt import (
    build_recommended_future_work,
    build_search_need_from_hunt,
    derive_desired_outcome,
    derive_need_kind,
)
from .records import (
    SearchNeed,
    SearchNeedDesiredOutcome,
    SearchNeedKind,
    SearchNeedState,
    SearchNeedSummary,
    SearchNeedTransition,
)
from .store import SearchNeedStore
from .summaries import build_search_need_summary
from .transitions import ALLOWED_TRANSITIONS, apply_transition, validate_transition
from .validation import (
    validate_need_creation_from_hunt,
    validate_no_forbidden_side_effects,
    validate_no_truth_claims,
    validate_query_text,
    validate_search_need,
)


ALLOWED_SEARCH_NEED_STATES = tuple(item.value for item in SearchNeedState)
ALLOWED_SEARCH_NEED_KINDS = tuple(item.value for item in SearchNeedKind)
ALLOWED_SEARCH_NEED_DESIRED_OUTCOMES = tuple(item.value for item in SearchNeedDesiredOutcome)

__all__ = [
    "ALLOWED_SEARCH_NEED_DESIRED_OUTCOMES",
    "ALLOWED_SEARCH_NEED_KINDS",
    "ALLOWED_SEARCH_NEED_STATES",
    "ALLOWED_TRANSITIONS",
    "SearchNeed",
    "SearchNeedClosedError",
    "SearchNeedDesiredOutcome",
    "SearchNeedError",
    "SearchNeedIntegrityError",
    "SearchNeedKind",
    "SearchNeedNotFoundError",
    "SearchNeedState",
    "SearchNeedStore",
    "SearchNeedSummary",
    "SearchNeedTransition",
    "SearchNeedTransitionError",
    "SearchNeedValidationError",
    "apply_transition",
    "build_recommended_future_work",
    "build_search_need_from_hunt",
    "build_search_need_summary",
    "derive_desired_outcome",
    "derive_need_kind",
    "validate_need_creation_from_hunt",
    "validate_no_forbidden_side_effects",
    "validate_no_truth_claims",
    "validate_query_text",
    "validate_search_need",
    "validate_transition",
]
