"""Validation helpers for local Search Hunt sessions."""

from typing import Any, Mapping

from .errors import SearchHuntValidationError
from .records import SearchHuntSession


MAX_QUERY_CHARS = 512
FORBIDDEN_TRUE_FLAGS = (
    "workunit_creation_performed",
    "source_probe_executed",
    "external_network_used",
    "model_provider_used",
    "review_mutation_performed",
    "public_index_mutated",
    "master_index_mutated",
    "deployment_performed",
    "production_readiness_claimed",
    "public_launch_readiness_claimed",
)
FORBIDDEN_CLAIM_TEXT = (
    "production ready",
    "public launch ready",
    "global absence",
    "exhaustive coverage",
    "accepted as truth",
)


def validate_search_hunt_session(session: SearchHuntSession) -> SearchHuntSession:
    if not session.id:
        raise SearchHuntValidationError("session id is required")
    validate_query_text(session.query)
    if session.normalized_query != " ".join(session.query.strip().lower().split()):
        raise SearchHuntValidationError("normalized_query mismatch")
    if session.reviewed_result_count < 0 or session.candidate_result_count < 0:
        raise SearchHuntValidationError("result counts must not be negative")
    return session


def validate_query_text(query: str) -> str:
    text = str(query).strip()
    if not text:
        raise SearchHuntValidationError("query is required")
    if len(text) > MAX_QUERY_CHARS:
        raise SearchHuntValidationError(f"query must be {MAX_QUERY_CHARS} characters or fewer")
    if any(ord(char) < 32 and char not in "\t\n\r" for char in text):
        raise SearchHuntValidationError("query contains control characters")
    return text


def validate_no_forbidden_side_effects(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    for key in FORBIDDEN_TRUE_FLAGS:
        if payload.get(key) is True:
            raise SearchHuntValidationError(f"forbidden side effect flag set: {key}")
    return payload


def validate_no_truth_claims(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    text = str(payload).lower()
    for claim in FORBIDDEN_CLAIM_TEXT:
        if claim in text:
            raise SearchHuntValidationError(f"forbidden completion claim: {claim}")
    return payload


def validate_limit(limit: int) -> int:
    value = int(limit)
    if value < 1 or value > 500:
        raise SearchHuntValidationError("limit must be between 1 and 500")
    return value


def validate_store_path(path: Any) -> Any:
    if str(path) == ":memory:":
        return path
    text = str(path).strip()
    if not text:
        raise SearchHuntValidationError("store path is required")
    forbidden = {".cache", ".local", "." + "aide.local", "secrets"}
    parts = set(getattr(path, "parts", ()))
    if parts & forbidden:
        raise SearchHuntValidationError("hidden/private store roots are forbidden")
    return path
