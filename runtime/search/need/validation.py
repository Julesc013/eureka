"""Validation helpers for SearchNeed runtime records."""

from pathlib import Path
from typing import Any, Mapping

from .errors import SearchNeedValidationError
from .records import SearchNeed, SearchNeedDesiredOutcome, SearchNeedKind, SearchNeedState, normalize_query


MAX_QUERY_LENGTH = 256
MAX_TEXT_LENGTH = 2000
MAX_LIMIT = 500
FORBIDDEN_TRUTH_MARKERS = (
    "searchneed is truth",
    "searchneed is evidence",
    "searchneed is source approval",
    "searchneed clears rights",
    "searchneed clears malware",
    "production ready",
    "public launch ready",
)


def validate_search_need(need: SearchNeed) -> SearchNeed:
    if not need.id:
        raise SearchNeedValidationError("SearchNeed id is required")
    if not need.hunt_id:
        raise SearchNeedValidationError("SearchNeed hunt_id is required")
    if not need.exhaustion_report_id:
        raise SearchNeedValidationError("SearchNeed exhaustion_report_id is required")
    validate_query_text(need.query)
    if normalize_query(need.query) != need.normalized_query:
        raise SearchNeedValidationError("SearchNeed normalized_query mismatch")
    if not need.need_title.strip():
        raise SearchNeedValidationError("SearchNeed need_title is required")
    if not need.need_summary.strip():
        raise SearchNeedValidationError("SearchNeed need_summary is required")
    SearchNeedKind(need.need_kind.value)
    SearchNeedDesiredOutcome(need.desired_outcome.value)
    SearchNeedState(need.state.value)
    if need.priority < 0 or need.priority > 100:
        raise SearchNeedValidationError("SearchNeed priority must be 0..100")
    validate_no_truth_claims(need.to_dict())
    return need


def validate_query_text(query: str) -> str:
    text = str(query or "").strip()
    if not text:
        raise SearchNeedValidationError("query is required")
    if len(text) > MAX_QUERY_LENGTH:
        raise SearchNeedValidationError("query exceeds maximum length")
    return text


def validate_need_creation_from_hunt(hunt: Any, exhaustion_report: Any) -> None:
    if hunt is None:
        raise SearchNeedValidationError("existing Search Hunt session is required")
    if exhaustion_report is None:
        raise SearchNeedValidationError("SearchNeed creation requires an exhaustion report")


def validate_no_forbidden_side_effects(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    for key in (
        "workunit_creation_performed",
        "source_probe_executed",
        "external_network_used",
        "model_provider_used",
        "review_mutation_performed",
        "public_index_mutated",
        "master_index_mutated",
        "deployment_performed",
    ):
        if payload.get(key) is True:
            raise SearchNeedValidationError(f"forbidden SearchNeed side effect: {key}")
    return payload


def validate_no_truth_claims(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    text = str(payload).lower()
    for marker in FORBIDDEN_TRUTH_MARKERS:
        if marker in text:
            raise SearchNeedValidationError(f"forbidden SearchNeed truth claim: {marker}")
    return payload


def validate_limit(limit: int) -> int:
    try:
        value = int(limit)
    except (TypeError, ValueError) as exc:
        raise SearchNeedValidationError("limit must be an integer") from exc
    if value < 1:
        raise SearchNeedValidationError("limit must be positive")
    return min(value, MAX_LIMIT)


def validate_store_path(path: str | Path) -> Path | str:
    if str(path) == ":memory:":
        return ":memory:"
    value = Path(path)
    if value.name == "":
        raise SearchNeedValidationError("SearchNeed store path is required")
    forbidden = {".cache", ".local", ".aide.local", "secrets"}
    if set(value.parts) & forbidden:
        raise SearchNeedValidationError("SearchNeed store path uses a forbidden root")
    return value
