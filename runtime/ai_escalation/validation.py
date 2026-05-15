"""Validation helpers for disabled AI escalation gates."""

from pathlib import Path
from typing import Any, Mapping

from .errors import AIEscalationValidationError
from .records import (
    AIEscalationGate,
    AIEscalationGateState,
    AIEscalationPreflightResult,
    normalize_query,
)


MAX_LIMIT = 500
MAX_QUERY_LENGTH = 256
FORBIDDEN_TRUTH_MARKERS = (
    "ai output is truth",
    "ai output is evidence",
    "rights cleared",
    "malware safe",
    "production ready",
    "public launch ready",
    "verified truth",
    "automatic source approval",
)


def validate_ai_escalation_gate(gate: AIEscalationGate) -> AIEscalationGate:
    if not gate.gate_id:
        raise AIEscalationValidationError("AI escalation gate_id is required")
    if not gate.search_hunt_id:
        raise AIEscalationValidationError("AI escalation search_hunt_id is required")
    validate_query_text(gate.query)
    if normalize_query(gate.query) != gate.normalized_query:
        raise AIEscalationValidationError("AI escalation normalized_query mismatch")
    AIEscalationGateState(gate.state.value)
    if gate.provider_enabled is not False:
        raise AIEscalationValidationError("AI escalation provider must be disabled")
    if gate.execution_enabled is not False:
        raise AIEscalationValidationError("AI escalation execution must be disabled")
    if gate.candidate_only_output is not True:
        raise AIEscalationValidationError("AI escalation output must be candidate-only")
    if gate.review_required is not True:
        raise AIEscalationValidationError("AI escalation review requirement is required")
    if not gate.input_packet.search_hunt_id:
        raise AIEscalationValidationError("AI escalation input packet requires hunt context")
    validate_no_forbidden_side_effects(gate.to_dict())
    validate_no_truth_claims(gate.to_dict())
    return gate


def validate_preflight(preflight: AIEscalationPreflightResult) -> AIEscalationPreflightResult:
    if not preflight.preflight_id:
        raise AIEscalationValidationError("AI escalation preflight_id is required")
    if not preflight.search_hunt_id:
        raise AIEscalationValidationError("AI escalation preflight requires search_hunt_id")
    if preflight.provider_enabled is not False:
        raise AIEscalationValidationError("AI escalation preflight provider must be disabled")
    if preflight.execution_enabled is not False:
        raise AIEscalationValidationError("AI escalation preflight execution must be disabled")
    if preflight.safety_checks.get("candidate_only_output") is not True:
        raise AIEscalationValidationError("AI escalation preflight output must be candidate-only")
    validate_no_forbidden_side_effects(preflight.to_dict())
    validate_no_truth_claims(preflight.to_dict())
    return preflight


def validate_provider_disabled() -> dict[str, bool]:
    return {
        "provider_enabled": False,
        "execution_enabled": False,
        "browser_enabled": False,
        "external_network_enabled": False,
        "source_probe_enabled": False,
        "extraction_enabled": False,
        "model_provider_used": False,
        "external_network_used": False,
    }


def validate_no_forbidden_side_effects(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    for key in (
        "model_provider_used",
        "external_network_used",
        "source_probe_executed",
        "extraction_executed",
        "review_mutation_performed",
        "public_index_mutated",
        "master_index_mutated",
        "deployment_performed",
    ):
        if payload.get(key) is True:
            raise AIEscalationValidationError(f"forbidden AI escalation side effect: {key}")
    return payload


def validate_no_truth_claims(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    text = str(payload).lower()
    for marker in FORBIDDEN_TRUTH_MARKERS:
        if marker in text:
            raise AIEscalationValidationError(f"forbidden AI escalation claim: {marker}")
    return payload


def validate_query_text(query: str) -> str:
    text = str(query or "").strip()
    if not text:
        raise AIEscalationValidationError("query is required")
    if len(text) > MAX_QUERY_LENGTH:
        raise AIEscalationValidationError("query exceeds maximum length")
    return text


def validate_limit(limit: int) -> int:
    try:
        value = int(limit)
    except (TypeError, ValueError) as exc:
        raise AIEscalationValidationError("limit must be an integer") from exc
    if value < 1:
        raise AIEscalationValidationError("limit must be positive")
    return min(value, MAX_LIMIT)


def validate_store_path(path: str | Path) -> Path | str:
    if str(path) == ":memory:":
        return ":memory:"
    value = Path(path)
    if value.name == "":
        raise AIEscalationValidationError("AI escalation store path is required")
    forbidden = {".cache", ".local", ".aide.local", "secrets"}
    if set(value.parts) & forbidden:
        raise AIEscalationValidationError("AI escalation store path uses a forbidden root")
    return value
