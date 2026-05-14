"""Durable local Search Hunt session runtime."""

from .absence_summary import build_local_absence_summary
from .errors import (
    SearchHuntClosedError,
    SearchHuntError,
    SearchHuntIntegrityError,
    SearchHuntNotFoundError,
    SearchHuntTransitionError,
    SearchHuntValidationError,
)
from .records import (
    SearchHuntCheckedLayer,
    SearchHuntDestination,
    SearchHuntIntent,
    SearchHuntSession,
    SearchHuntState,
    SearchHuntSummary,
    SearchHuntTransition,
    SearchHuntUncheckedLayer,
)
from .search_summary import build_reviewed_index_search_summary
from .store import SearchHuntStore
from .transitions import ALLOWED_TRANSITIONS, apply_transition, validate_transition
from .validation import validate_no_forbidden_side_effects, validate_no_truth_claims, validate_query_text, validate_search_hunt_session


ALLOWED_SEARCH_HUNT_STATES = tuple(item.value for item in SearchHuntState)
ALLOWED_SEARCH_HUNT_INTENTS = tuple(item.value for item in SearchHuntIntent)
ALLOWED_SEARCH_HUNT_DESTINATIONS = tuple(item.value for item in SearchHuntDestination)
ALLOWED_SEARCH_HUNT_CHECKED_LAYERS = tuple(item.value for item in SearchHuntCheckedLayer)
ALLOWED_SEARCH_HUNT_UNCHECKED_LAYERS = tuple(item.value for item in SearchHuntUncheckedLayer)

__all__ = [
    "ALLOWED_SEARCH_HUNT_CHECKED_LAYERS",
    "ALLOWED_SEARCH_HUNT_DESTINATIONS",
    "ALLOWED_SEARCH_HUNT_INTENTS",
    "ALLOWED_SEARCH_HUNT_STATES",
    "ALLOWED_SEARCH_HUNT_UNCHECKED_LAYERS",
    "ALLOWED_TRANSITIONS",
    "SearchHuntCheckedLayer",
    "SearchHuntClosedError",
    "SearchHuntDestination",
    "SearchHuntError",
    "SearchHuntIntegrityError",
    "SearchHuntIntent",
    "SearchHuntNotFoundError",
    "SearchHuntSession",
    "SearchHuntState",
    "SearchHuntStore",
    "SearchHuntSummary",
    "SearchHuntTransition",
    "SearchHuntTransitionError",
    "SearchHuntUncheckedLayer",
    "SearchHuntValidationError",
    "apply_transition",
    "build_local_absence_summary",
    "build_reviewed_index_search_summary",
    "validate_no_forbidden_side_effects",
    "validate_no_truth_claims",
    "validate_query_text",
    "validate_search_hunt_session",
    "validate_transition",
]
