"""Validation helpers for disabled agent research task contracts."""

from pathlib import Path
from typing import Any, Mapping

from .errors import AgentResearchValidationError
from .records import AgentResearchTask, AgentResearchTaskState, normalize_query


MAX_QUERY_LENGTH = 256
MAX_LIMIT = 500
FORBIDDEN_TRUTH_MARKERS = (
    "ai output is truth",
    "ai output is evidence",
    "rights cleared",
    "malware safe",
    "production ready",
    "public launch ready",
)


def validate_agent_research_task(task: AgentResearchTask) -> AgentResearchTask:
    if not task.task_id:
        raise AgentResearchValidationError("agent research task_id is required")
    if not task.search_hunt_id:
        raise AgentResearchValidationError("agent research search_hunt_id is required")
    if not task.exhaustion_report_id:
        raise AgentResearchValidationError("agent research exhaustion_report_id is required")
    validate_query_text(task.query)
    if normalize_query(task.query) != task.normalized_query:
        raise AgentResearchValidationError("agent research normalized_query mismatch")
    AgentResearchTaskState(task.state.value)
    if task.provider_enabled is not False:
        raise AgentResearchValidationError("agent research provider must be disabled")
    if task.execution_enabled is not False:
        raise AgentResearchValidationError("agent research execution must be disabled")
    if not task.output_schema:
        raise AgentResearchValidationError("agent research output_schema is required")
    validate_no_forbidden_side_effects(task.to_dict())
    validate_no_truth_claims(task.to_dict())
    return task


def validate_provider_disabled() -> dict[str, bool]:
    return {
        "provider_enabled": False,
        "execution_enabled": False,
        "browser_enabled": False,
        "source_probe_enabled": False,
        "model_provider_used": False,
        "external_network_used": False,
    }


def validate_no_forbidden_side_effects(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    for key in (
        "model_provider_used",
        "external_network_used",
        "source_probe_executed",
        "review_mutation_performed",
        "public_index_mutated",
        "master_index_mutated",
        "deployment_performed",
    ):
        if payload.get(key) is True:
            raise AgentResearchValidationError(f"forbidden agent research side effect: {key}")
    return payload


def validate_no_truth_claims(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    text = str(payload).lower()
    for marker in FORBIDDEN_TRUTH_MARKERS:
        if marker in text:
            raise AgentResearchValidationError(f"forbidden agent research truth claim: {marker}")
    return payload


def validate_query_text(query: str) -> str:
    text = str(query or "").strip()
    if not text:
        raise AgentResearchValidationError("query is required")
    if len(text) > MAX_QUERY_LENGTH:
        raise AgentResearchValidationError("query exceeds maximum length")
    return text


def validate_limit(limit: int) -> int:
    try:
        value = int(limit)
    except (TypeError, ValueError) as exc:
        raise AgentResearchValidationError("limit must be an integer") from exc
    if value < 1:
        raise AgentResearchValidationError("limit must be positive")
    return min(value, MAX_LIMIT)


def validate_store_path(path: str | Path) -> Path | str:
    if str(path) == ":memory:":
        return ":memory:"
    value = Path(path)
    if value.name == "":
        raise AgentResearchValidationError("agent research store path is required")
    forbidden = {".cache", ".local", ".aide.local", "secrets"}
    if set(value.parts) & forbidden:
        raise AgentResearchValidationError("agent research store path uses a forbidden root")
    return value
