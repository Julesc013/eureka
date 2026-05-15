"""Validation helpers for local Search Hunt sessions."""

from typing import Any, Mapping

from .errors import SearchHuntValidationError
from .commands import SearchHuntCommand, command_requires_reason, coerce_command_type
from .records import SearchHuntExhaustionReport, SearchHuntSession
from .run_records import BackgroundHuntRun
from .steering import SearchHuntSteeringPreference, coerce_steering_type


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


def validate_search_hunt_command(command: SearchHuntCommand) -> SearchHuntCommand:
    if not command.command_id:
        raise SearchHuntValidationError("command_id is required")
    if not command.hunt_id:
        raise SearchHuntValidationError("hunt_id is required")
    try:
        command_type = coerce_command_type(command.command_type)
    except ValueError:
        command_type = None
    if command_type is not None and command_requires_reason(command_type) and not command.reason.strip():
        raise SearchHuntValidationError(f"{command.command_type} requires reason")
    validate_no_forbidden_side_effects(command.side_effects)
    return command


def validate_search_hunt_steering_preference(preference: SearchHuntSteeringPreference) -> SearchHuntSteeringPreference:
    if not preference.id:
        raise SearchHuntValidationError("steering preference id is required")
    if not preference.command_id:
        raise SearchHuntValidationError("steering command_id is required")
    if not preference.hunt_id:
        raise SearchHuntValidationError("hunt_id is required")
    coerce_steering_type(preference.command_type)
    validate_no_truth_claims(preference.to_dict())
    return preference


def validate_search_hunt_exhaustion_report(report: SearchHuntExhaustionReport) -> SearchHuntExhaustionReport:
    if not report.report_id:
        raise SearchHuntValidationError("exhaustion report_id is required")
    if not report.hunt_id:
        raise SearchHuntValidationError("hunt_id is required")
    payload = report.to_dict()
    required = (
        "query_summary",
        "checked_layers",
        "result_state",
        "unchecked_or_deferred_layers",
        "blocked_by_policy",
        "recommended_next_actions",
        "limitations",
        "warnings",
        "non_claims",
    )
    for key in required:
        if key not in payload:
            raise SearchHuntValidationError(f"exhaustion report missing section: {key}")
    if not report.checked_layers:
        raise SearchHuntValidationError("exhaustion report checked_layers are required")
    if not report.unchecked_or_deferred_layers:
        raise SearchHuntValidationError("exhaustion report deferred layers are required")
    if not report.blocked_by_policy:
        raise SearchHuntValidationError("exhaustion report blocked policy entries are required")
    if not report.recommended_next_actions:
        raise SearchHuntValidationError("exhaustion report recommended actions are required")
    validate_no_forbidden_side_effects(payload)
    validate_no_truth_claims(payload)
    return report


def validate_background_hunt_run(run: BackgroundHuntRun) -> BackgroundHuntRun:
    if not run.run_id:
        raise SearchHuntValidationError("background run id is required")
    if not run.hunt_id:
        raise SearchHuntValidationError("hunt_id is required")
    payload = run.to_dict()
    for key in (
        "source_probe_executed",
        "extraction_executed",
        "external_network_used",
        "model_provider_used",
        "download_install_execute_performed",
        "master_index_mutated",
        "deployment_performed",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    ):
        if payload.get(key) is True:
            raise SearchHuntValidationError(f"forbidden background runner flag set: {key}")
    return run


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
