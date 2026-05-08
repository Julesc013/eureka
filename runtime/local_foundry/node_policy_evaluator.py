"""Local-only node policy evaluation helpers.

This module compares explicit node manifest, node policy, capability, and
WorkUnit records. It produces a report-only policy decision and never executes
WorkUnit actions or creates node runtime state.
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

try:
    from runtime.local_foundry import workunit_dry_run
except ImportError:  # pragma: no cover - direct script import fallback
    import workunit_dry_run  # type: ignore


SCHEMA_VERSION = "node_policy_evaluation_result.v0"

DECISIONS = (
    "allowed_for_dry_run",
    "allowed_for_validation",
    "allowed_for_report_only",
    "allowed_for_manual_review",
    "allowed_as_noop",
    "blocked_by_policy",
    "blocked_by_missing_policy",
    "blocked_by_unknown_capability",
    "blocked_by_source_access",
    "blocked_by_network_requirement",
    "blocked_by_model_requirement",
    "blocked_by_credential_requirement",
    "blocked_by_local_state_requirement",
    "blocked_by_forbidden_input",
    "blocked_by_forbidden_output",
    "blocked_by_forbidden_action",
    "operator_gated",
    "human_operated",
    "approval_gated",
    "permission_needed",
    "deferred_future",
    "not_evaluable",
)

REASON_CATEGORIES = (
    "node_mode_allowed",
    "node_mode_forbidden",
    "node_status_not_active",
    "node_policy_allows_scope",
    "capability_allowed",
    "capability_unknown",
    "capability_future_only",
    "input_allowed",
    "input_forbidden",
    "output_allowed",
    "output_forbidden",
    "action_allowed_for_dry_run",
    "action_forbidden",
    "source_access_allowed_repo_local",
    "source_access_requires_approval",
    "network_disabled",
    "model_provider_disabled",
    "credentials_forbidden",
    "local_state_disabled",
    "review_required",
    "truth_boundary_preserved",
    "product_boundary_preserved",
    "policy_missing",
    "policy_conflict",
    "future_deferred",
)

EVALUATION_STATUSES = (
    "pass",
    "warn",
    "blocked",
    "gated",
    "noop",
    "not_evaluable",
    "fail",
)

ALLOWED_OUTPUT_TYPES = (
    "node_policy_evaluation_result",
    "node_policy_evaluation_summary",
    "workunit_dry_run_allowance",
    "workunit_blocker_report",
    "review_gate_report",
    "source_policy_approval_request_future",
    "operator_approval_request_future",
)

FORBIDDEN_OUTPUT_TYPES = (
    "workunit_execution",
    "node_runtime_state",
    "local_private_state",
    "observed_baseline_truth",
    "accepted_evidence_truth",
    "accepted_public_record",
    "master_index_mutation",
    "rights_clearance",
    "malware_safety",
    "verified_installability",
    "production_readiness_claim",
    "exhaustive_global_search_proof",
)

FALSE_TRUTH_BOUNDARY_FIELDS = (
    "evaluation_result_is_public_truth",
    "evaluation_result_is_accepted_evidence",
    "evaluation_result_can_mutate_master_index",
    "evaluation_result_claims_rights_clearance",
    "evaluation_result_claims_malware_safety",
    "evaluation_result_claims_verified_installability",
    "evaluation_result_claims_exhaustive_global_search",
    "evaluation_result_claims_production_readiness",
)

TRUE_TRUTH_BOUNDARY_FIELDS = ("human_review_required_for_downstream_use",)

FALSE_PRODUCT_BOUNDARY_FIELDS = (
    "implemented_workunit_execution",
    "implemented_node_runtime",
    "created_local_private_state",
    "enabled_network_access",
    "enabled_live_probes",
    "enabled_source_sync",
    "enabled_source_connectors",
    "enabled_downloads",
    "enabled_installers",
    "enabled_execution",
    "enabled_uploads",
    "enabled_accounts",
    "enabled_telemetry",
    "enabled_pack_import_runtime",
    "enabled_review_runtime",
    "enabled_model_provider_calls",
    "mutated_master_index",
    "claimed_rights_clearance",
    "claimed_malware_safety",
    "claimed_verified_installability",
    "claimed_exhaustive_global_search",
    "claimed_production_readiness",
)

HARD_BLOCK_DECISIONS = (
    "blocked_by_policy",
    "blocked_by_missing_policy",
    "blocked_by_unknown_capability",
    "blocked_by_source_access",
    "blocked_by_network_requirement",
    "blocked_by_model_requirement",
    "blocked_by_credential_requirement",
    "blocked_by_local_state_requirement",
    "blocked_by_forbidden_input",
    "blocked_by_forbidden_output",
    "blocked_by_forbidden_action",
)

GATED_DECISIONS = (
    "approval_gated",
    "operator_gated",
    "human_operated",
    "permission_needed",
)

FUTURE_STATUSES = {
    "future",
    "future_deferred",
    "future_deferred_disabled",
    "deferred",
    "approval_gated",
    "operator_gated",
    "permission_needed",
}

CURRENT_CAPABILITY_STATUSES = {
    "current_repo_local_only",
    "current_dry_run_only",
    "current_validate_only",
}

FORBIDDEN_CLAIM_PHRASES = (
    "workunit action executed",
    "executed workunit action",
    "node runtime state created",
    "network access enabled",
    "api call completed",
    "model provider call completed",
    "live probe enabled",
    "source sync enabled",
    "download enabled",
    "upload enabled",
    "account enabled",
    "telemetry enabled",
    "master-index mutation allowed",
    "rights clearance confirmed",
    "malware safety confirmed",
    "verified installability confirmed",
    "production readiness confirmed",
)


def _load_json(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"expected JSON object at {path}")
    return data


def load_node_manifest(path: str | Path) -> dict[str, Any]:
    """Load an explicit node manifest JSON file."""

    return _load_json(path)


def load_node_policy(path: str | Path) -> dict[str, Any]:
    """Load an explicit node policy JSON file."""

    return _load_json(path)


def load_workunit(path: str | Path) -> dict[str, Any]:
    """Load an explicit WorkUnit JSON file."""

    return _load_json(path)


def load_capability_matrix(path: str | Path) -> dict[str, Any]:
    """Load a committed capability matrix or registry JSON file."""

    return _load_json(path)


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def _as_bool(value: Any) -> bool:
    return bool(value) if isinstance(value, bool) else False


def _record_ref(path: str | Path | None, fallback_id: str | None = None) -> str:
    if path:
        return str(path).replace("\\", "/")
    return fallback_id or "inline_record"


def _record_id(record: dict[str, Any], keys: tuple[str, ...]) -> str | None:
    for key in keys:
        value = record.get(key)
        if isinstance(value, str) and value:
            return value
    return None


def _stable_id(prefix: str, parts: list[str]) -> str:
    digest = hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:12]
    return f"{prefix}_{digest}"


def _truth_boundary() -> dict[str, bool]:
    boundary = {field: False for field in FALSE_TRUTH_BOUNDARY_FIELDS}
    boundary.update({field: True for field in TRUE_TRUTH_BOUNDARY_FIELDS})
    return boundary


def _product_boundary() -> dict[str, bool]:
    return {field: False for field in FALSE_PRODUCT_BOUNDARY_FIELDS}


def _reason(category: str, result: str, summary: str, ref: str | None = None) -> dict[str, Any]:
    item: dict[str, Any] = {
        "reason_category": category,
        "result": result,
        "summary": summary,
    }
    if ref:
        item["ref"] = ref
    return item


def _capability_records_from_matrix(capability_matrix: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    if capability_matrix:
        for entry in _as_list(capability_matrix.get("capabilities")):
            if not isinstance(entry, dict):
                continue
            capability_id = entry.get("capability_id") or entry.get("node_capability_id")
            if isinstance(capability_id, str):
                records[capability_id] = entry
    if not records:
        for capability_id, status in workunit_dry_run.CAPABILITY_STATUSES.items():
            records[capability_id] = {
                "capability_id": capability_id,
                "capability_status": status,
                "allowed_node_modes": list(workunit_dry_run.ALLOWED_NODE_MODES),
                "forbidden_node_modes": [],
                "network_required": False,
                "model_provider_required": False,
                "credentials_required": False,
                "local_state_required": False,
                "review_required": True,
            }
    return records


def default_registries(capability_matrix: dict[str, Any] | None = None) -> dict[str, Any]:
    """Build deterministic in-memory registries from committed policy inputs."""

    capability_records = _capability_records_from_matrix(capability_matrix)
    return {
        "allowed_decisions": list(DECISIONS),
        "allowed_reason_categories": list(REASON_CATEGORIES),
        "allowed_output_types": list(ALLOWED_OUTPUT_TYPES),
        "forbidden_output_types": list(FORBIDDEN_OUTPUT_TYPES),
        "capabilities": capability_records,
        "allowed_capability_statuses_current": sorted(CURRENT_CAPABILITY_STATUSES),
        "future_capability_statuses": sorted(FUTURE_STATUSES),
    }


def _node_mode(node_manifest: dict[str, Any]) -> str:
    return str(node_manifest.get("node_mode", "unknown"))


def _node_status(node_manifest: dict[str, Any]) -> str:
    return str(node_manifest.get("node_status", "unknown"))


def _policy_status(node_policy: dict[str, Any]) -> str:
    return str(node_policy.get("policy_status", "unknown"))


def _required_node_modes(workunit: dict[str, Any]) -> list[str]:
    return [str(mode) for mode in _as_list(workunit.get("required_node_modes")) if isinstance(mode, str)]


def _required_capabilities(workunit: dict[str, Any]) -> list[str]:
    capabilities: list[str] = []
    capability_items = _as_list(workunit.get("required_node_capabilities"))
    capability_items.extend(_as_list(workunit.get("required_capabilities")))
    for item in capability_items:
        if isinstance(item, str):
            capabilities.append(item)
        elif isinstance(item, dict):
            capability_id = item.get("capability_id")
            if isinstance(capability_id, str):
                capabilities.append(capability_id)
    return sorted(dict.fromkeys(capabilities))


def _manifest_capabilities(node_manifest: dict[str, Any]) -> set[str]:
    values: set[str] = set()
    capability_items = _as_list(node_manifest.get("node_capabilities"))
    capability_items.extend(_as_list(node_manifest.get("capabilities")))
    for item in capability_items:
        if isinstance(item, str):
            values.add(item)
        elif isinstance(item, dict):
            capability_id = item.get("capability_id") or item.get("node_capability_id")
            if isinstance(capability_id, str):
                values.add(capability_id)
    return values


def _policy_list(node_policy: dict[str, Any], key: str) -> set[str]:
    return {str(item) for item in _as_list(node_policy.get(key)) if isinstance(item, str)}


def _canonical_output_type(output_type: str) -> str:
    if output_type.endswith("_future"):
        return output_type[: -len("_future")]
    return output_type


def _is_future_label(value: str) -> bool:
    return value.endswith("_future") or "future" in value


def evaluate_node_mode(
    node_manifest: dict[str, Any],
    node_policy: dict[str, Any],
    workunit: dict[str, Any],
    registries: dict[str, Any],
) -> dict[str, Any]:
    """Evaluate whether the node mode and policy scope can consider the WorkUnit."""

    del registries
    mode = _node_mode(node_manifest)
    status = _node_status(node_manifest)
    policy_status = _policy_status(node_policy)
    required_modes = _required_node_modes(workunit)
    applies_modes = _as_list(node_policy.get("applies_to_node_modes"))
    reasons: list[dict[str, Any]] = []
    errors: list[str] = []
    warnings: list[str] = []
    decision = "allowed_for_validation"

    if required_modes and mode not in required_modes:
        decision = "blocked_by_policy"
        errors.append(f"node mode {mode} is not allowed by WorkUnit")
        reasons.append(_reason("node_mode_forbidden", "blocked", f"WorkUnit requires {required_modes}"))
    else:
        reasons.append(_reason("node_mode_allowed", "allowed", f"node mode {mode} is in WorkUnit scope"))

    if applies_modes and mode not in applies_modes:
        decision = "blocked_by_missing_policy"
        errors.append(f"node policy does not apply to mode {mode}")
        reasons.append(_reason("policy_missing", "blocked", f"policy applies to {applies_modes}"))
    else:
        reasons.append(_reason("node_policy_allows_scope", "allowed", f"node policy applies to {mode}"))

    if status in {"disabled", "blocked", "policy_blocked"} or policy_status in {"disabled", "blocked", "policy_blocked"}:
        decision = "blocked_by_policy"
        errors.append("node or policy status blocks evaluation")
        reasons.append(_reason("node_status_not_active", "blocked", f"node={status}; policy={policy_status}"))
    elif status in FUTURE_STATUSES or policy_status in FUTURE_STATUSES:
        decision = "approval_gated" if "approval_gated" in {status, policy_status} else "deferred_future"
        warnings.append("node or policy is future/gated and cannot be active execution")
        reasons.append(_reason("node_status_not_active", "gated", f"node={status}; policy={policy_status}"))

    return {
        "decision": decision,
        "node_mode": mode,
        "node_status": status,
        "node_policy_status": policy_status,
        "required_node_modes": required_modes,
        "reasons": reasons,
        "warnings": warnings,
        "errors": errors,
    }


def evaluate_required_capabilities(
    node_manifest: dict[str, Any],
    node_policy: dict[str, Any],
    workunit: dict[str, Any],
    registries: dict[str, Any],
) -> dict[str, Any]:
    """Compare WorkUnit capability requirements with node mode and capability policy."""

    del node_policy
    mode = _node_mode(node_manifest)
    declared = _manifest_capabilities(node_manifest)
    capabilities = registries.get("capabilities", {})
    required = _required_capabilities(workunit)
    results: list[dict[str, Any]] = []
    reasons: list[dict[str, Any]] = []
    warnings: list[str] = []
    errors: list[str] = []

    for capability_id in required:
        matrix_record = capabilities.get(capability_id)
        if not isinstance(matrix_record, dict):
            results.append(
                {
                    "capability_id": capability_id,
                    "decision": "blocked_by_unknown_capability",
                    "declared_by_manifest": capability_id in declared,
                }
            )
            errors.append(f"unknown capability: {capability_id}")
            reasons.append(_reason("capability_unknown", "blocked", "capability is not in the registry", capability_id))
            continue

        status = str(matrix_record.get("capability_status", matrix_record.get("status", "unknown")))
        allowed_modes = {str(item) for item in _as_list(matrix_record.get("allowed_node_modes"))}
        forbidden_modes = {str(item) for item in _as_list(matrix_record.get("forbidden_node_modes"))}
        declared_by_manifest = capability_id in declared
        decision = "allowed_for_dry_run"

        if mode in forbidden_modes:
            decision = "blocked_by_policy"
            errors.append(f"capability {capability_id} forbids node mode {mode}")
            reasons.append(_reason("policy_conflict", "blocked", f"{mode} is forbidden", capability_id))
        elif allowed_modes and mode not in allowed_modes:
            decision = "blocked_by_policy"
            errors.append(f"capability {capability_id} does not allow node mode {mode}")
            reasons.append(_reason("policy_conflict", "blocked", f"{mode} is outside allowed modes", capability_id))
        elif status == "policy_blocked":
            decision = "blocked_by_policy"
            errors.append(f"capability {capability_id} is policy blocked")
            reasons.append(_reason("capability_future_only", "blocked", f"status is {status}", capability_id))
        elif status == "approval_gated":
            decision = "approval_gated"
            warnings.append(f"capability {capability_id} is approval gated")
            reasons.append(_reason("future_deferred", "gated", "approval is required before use", capability_id))
        elif status == "operator_gated":
            decision = "operator_gated"
            warnings.append(f"capability {capability_id} is operator gated")
            reasons.append(_reason("future_deferred", "gated", "operator approval is required before use", capability_id))
        elif status in FUTURE_STATUSES or status not in CURRENT_CAPABILITY_STATUSES:
            decision = "deferred_future"
            warnings.append(f"capability {capability_id} is not current: {status}")
            reasons.append(_reason("capability_future_only", "deferred", f"status is {status}", capability_id))
        else:
            reasons.append(_reason("capability_allowed", "allowed", f"capability {capability_id} is dry-run safe", capability_id))

        if not declared_by_manifest and decision == "allowed_for_dry_run":
            warnings.append(f"capability {capability_id} is registry-allowed but not declared by manifest")
            reasons.append(_reason("capability_allowed", "warn", "registry allowed dry-run despite manifest omission", capability_id))

        results.append(
            {
                "capability_id": capability_id,
                "capability_status": status,
                "declared_by_manifest": declared_by_manifest,
                "decision": decision,
                "network_required": _as_bool(matrix_record.get("network_required")),
                "model_provider_required": _as_bool(matrix_record.get("model_provider_required")),
                "credentials_required": _as_bool(matrix_record.get("credentials_required")),
                "local_state_required": _as_bool(matrix_record.get("local_state_required")),
            }
        )

    return {
        "decision": _highest_priority_decision([item["decision"] for item in results], default="allowed_for_dry_run"),
        "capability_results": results,
        "reasons": reasons,
        "warnings": warnings,
        "errors": errors,
    }


def evaluate_input_policy(
    node_policy: dict[str, Any],
    workunit: dict[str, Any],
    registries: dict[str, Any],
) -> dict[str, Any]:
    """Evaluate WorkUnit input references against node policy."""

    del registries
    allowed_inputs = _policy_list(node_policy, "allowed_inputs")
    forbidden_inputs = _policy_list(node_policy, "forbidden_inputs")
    results: list[dict[str, Any]] = []
    reasons: list[dict[str, Any]] = []
    warnings: list[str] = []
    errors: list[str] = []

    for item in _as_list(workunit.get("input_refs")):
        if not isinstance(item, dict):
            continue
        input_type = str(item.get("input_type", "unknown"))
        ref = str(item.get("input_ref", item.get("ref", item.get("input_id", input_type))))
        decision = "allowed_for_validation"
        if input_type in forbidden_inputs or input_type in {"secret_or_credential", "private_user_file", "telemetry_stream"}:
            decision = "blocked_by_forbidden_input"
            errors.append(f"forbidden input type: {input_type}")
            reasons.append(_reason("input_forbidden", "blocked", f"input type {input_type} is forbidden", ref))
        elif input_type in allowed_inputs or not allowed_inputs:
            reasons.append(_reason("input_allowed", "allowed", f"input type {input_type} is allowed", ref))
        elif _is_future_label(input_type):
            warnings.append(f"input type {input_type} is future/deferred")
            reasons.append(_reason("future_deferred", "deferred", f"input type {input_type} is not current", ref))
        else:
            decision = "blocked_by_forbidden_input"
            errors.append(f"input type {input_type} is not allowed by node policy")
            reasons.append(_reason("input_forbidden", "blocked", f"input type {input_type} is not allowed", ref))
        results.append({"input_type": input_type, "ref": ref, "decision": decision})

    return {
        "decision": _highest_priority_decision([item["decision"] for item in results], default="allowed_for_validation"),
        "input_policy_results": results,
        "reasons": reasons,
        "warnings": warnings,
        "errors": errors,
    }


def evaluate_output_policy(
    node_policy: dict[str, Any],
    workunit: dict[str, Any],
    registries: dict[str, Any],
) -> dict[str, Any]:
    """Evaluate WorkUnit proposed outputs against node policy."""

    del registries
    allowed_outputs = _policy_list(node_policy, "allowed_outputs")
    forbidden_outputs = _policy_list(node_policy, "forbidden_outputs") | set(FORBIDDEN_OUTPUT_TYPES)
    results: list[dict[str, Any]] = []
    reasons: list[dict[str, Any]] = []
    warnings: list[str] = []
    errors: list[str] = []

    for item in _as_list(workunit.get("expected_outputs")):
        if not isinstance(item, dict):
            continue
        output_type = str(item.get("output_type", "unknown"))
        ref = str(item.get("output_id", item.get("id", output_type)))
        canonical = _canonical_output_type(output_type)
        requires_review = bool(item.get("output_requires_review", item.get("review_required", True)))
        decision = "allowed_for_report_only"
        if output_type in forbidden_outputs or canonical in forbidden_outputs:
            decision = "blocked_by_forbidden_output"
            errors.append(f"forbidden output type: {output_type}")
            reasons.append(_reason("output_forbidden", "blocked", f"output type {output_type} is forbidden", ref))
        elif output_type in allowed_outputs or canonical in allowed_outputs or not allowed_outputs:
            reasons.append(_reason("output_allowed", "allowed", f"output type {output_type} is allowed for report/review", ref))
        elif _is_future_label(output_type) and requires_review:
            warnings.append(f"output type {output_type} is future/deferred and review-gated")
            reasons.append(_reason("future_deferred", "deferred", f"output type {output_type} requires future review", ref))
        else:
            decision = "blocked_by_forbidden_output"
            errors.append(f"output type {output_type} is not allowed by node policy")
            reasons.append(_reason("output_forbidden", "blocked", f"output type {output_type} is not allowed", ref))
        results.append({"output_type": output_type, "decision": decision, "review_required": requires_review})

    return {
        "decision": _highest_priority_decision([item["decision"] for item in results], default="allowed_for_report_only"),
        "output_policy_results": results,
        "reasons": reasons,
        "warnings": warnings,
        "errors": errors,
    }


def evaluate_action_policy(
    node_policy: dict[str, Any],
    workunit: dict[str, Any],
    registries: dict[str, Any],
) -> dict[str, Any]:
    """Classify WorkUnit actions as dry-run safe, blocked, or deferred."""

    del registries
    allowed_actions = _policy_list(node_policy, "allowed_actions")
    forbidden_actions = _policy_list(node_policy, "forbidden_actions") | set(workunit_dry_run.FORBIDDEN_ACTIONS)
    results: list[dict[str, Any]] = []
    reasons: list[dict[str, Any]] = []
    warnings: list[str] = []
    errors: list[str] = []

    for action in _as_list(workunit.get("allowed_actions")):
        if not isinstance(action, str):
            continue
        decision = "allowed_for_dry_run"
        classification = "action_allowed_for_dry_run"
        if action in forbidden_actions:
            decision = "blocked_by_forbidden_action"
            classification = "action_forbidden"
            errors.append(f"forbidden action: {action}")
            reasons.append(_reason("action_forbidden", "blocked", f"action {action} is forbidden", action))
        elif action in allowed_actions or not allowed_actions:
            reasons.append(_reason("action_allowed_for_dry_run", "allowed", f"action {action} can be simulated", action))
        elif _is_future_label(action):
            classification = "future_deferred"
            warnings.append(f"action {action} is future/deferred and simulated only")
            reasons.append(_reason("future_deferred", "deferred", f"action {action} is future only", action))
        else:
            decision = "blocked_by_forbidden_action"
            classification = "action_forbidden"
            errors.append(f"action {action} is not allowed by node policy")
            reasons.append(_reason("action_forbidden", "blocked", f"action {action} is not allowed", action))
        results.append({"action": action, "classification": classification, "decision": decision, "executed": False})

    return {
        "decision": _highest_priority_decision([item["decision"] for item in results], default="allowed_for_dry_run"),
        "action_policy_results": results,
        "blocked_actions": [item["action"] for item in results if item["decision"].startswith("blocked_")],
        "skipped_actions": [item["action"] for item in results if item["decision"] in {"deferred_future", "not_evaluable"}],
        "reasons": reasons,
        "warnings": warnings,
        "errors": errors,
    }


def evaluate_source_access_policy(
    node_policy: dict[str, Any],
    workunit: dict[str, Any],
    registries: dict[str, Any],
) -> dict[str, Any]:
    """Evaluate source access requirements without performing any access."""

    del registries
    source_requirements = workunit.get("source_access_requirements", {})
    if not isinstance(source_requirements, dict):
        source_requirements = {}
    source_required = _as_bool(source_requirements.get("source_access_required"))
    source_policy = node_policy.get("source_access_policy", {})
    if not isinstance(source_policy, dict):
        source_policy = {}
    allowed_mode = str(source_policy.get("allowed_mode", "repo_local_only"))
    approval_required = bool(source_policy.get("operator_approval_required", True))
    reasons: list[dict[str, Any]] = []
    warnings: list[str] = []
    errors: list[str] = []
    decision = "allowed_for_validation"

    if not source_required:
        reasons.append(_reason("source_access_allowed_repo_local", "allowed", "no live source access is required"))
    elif allowed_mode == "repo_local_only":
        decision = "blocked_by_source_access"
        errors.append("source access is required but node policy is repo-local only")
        reasons.append(_reason("source_access_requires_approval", "blocked", "repo-local policy blocks source access"))
    elif approval_required:
        decision = "approval_gated"
        warnings.append("source access requires approval")
        reasons.append(_reason("source_access_requires_approval", "gated", "approval required before source access"))
    else:
        decision = "permission_needed"
        warnings.append("source access is future permission-gated")
        reasons.append(_reason("source_access_requires_approval", "gated", "permission required before source access"))

    return {
        "decision": decision,
        "source_access_required": source_required,
        "allowed_mode": allowed_mode,
        "reasons": reasons,
        "warnings": warnings,
        "errors": errors,
    }


def evaluate_network_model_credential_policy(
    node_policy: dict[str, Any],
    workunit: dict[str, Any],
    registries: dict[str, Any],
) -> dict[str, Any]:
    """Evaluate network, model, and credential requirements without enabling them."""

    del registries
    network_requirements = workunit.get("network_requirements", {})
    if not isinstance(network_requirements, dict):
        network_requirements = {}
    model_requirements = workunit.get("model_provider_requirements", workunit.get("model_requirements", {}))
    if not isinstance(model_requirements, dict):
        model_requirements = {}
    credential_requirements = workunit.get("credential_requirements", {})
    if not isinstance(credential_requirements, dict):
        credential_requirements = {}

    network_policy = node_policy.get("network_policy", {})
    model_policy = node_policy.get("model_provider_policy", {})
    credential_policy = node_policy.get("credential_policy", {})
    if not isinstance(network_policy, dict):
        network_policy = {}
    if not isinstance(model_policy, dict):
        model_policy = {}
    if not isinstance(credential_policy, dict):
        credential_policy = {}

    reasons: list[dict[str, Any]] = []
    warnings: list[str] = []
    errors: list[str] = []
    results: list[dict[str, Any]] = []

    def _requirement_decision(
        label: str,
        required: bool,
        enabled: bool,
        block_decision: str,
        reason_category: str,
        future_gated: bool = False,
    ) -> dict[str, Any]:
        if not required:
            return {"policy": label, "required": False, "enabled": enabled, "decision": "allowed_for_validation"}
        if enabled:
            reasons.append(_reason(reason_category, "gated", f"{label} would require review even if enabled"))
            return {"policy": label, "required": True, "enabled": enabled, "decision": "approval_gated"}
        if future_gated:
            warnings.append(f"{label} is future/gated and remains disabled")
            reasons.append(_reason(reason_category, "gated", f"{label} is disabled and approval-gated"))
            return {"policy": label, "required": True, "enabled": False, "decision": "approval_gated"}
        errors.append(f"{label} is required but disabled")
        reasons.append(_reason(reason_category, "blocked", f"{label} is disabled"))
        return {"policy": label, "required": True, "enabled": False, "decision": block_decision}

    status_labels = {
        str(_policy_status(node_policy)),
        str(workunit.get("workunit_status", "")),
        str(workunit.get("workunit_type", "")),
    }
    future_gated = bool(status_labels & {"approval_gated", "permission_needed"}) or any("future" in item for item in status_labels)
    results.append(
        _requirement_decision(
            "network",
            _as_bool(network_requirements.get("network_required")),
            _as_bool(network_policy.get("network_enabled")),
            "blocked_by_network_requirement",
            "network_disabled",
            future_gated=future_gated,
        )
    )
    results.append(
        _requirement_decision(
            "model_provider",
            _as_bool(model_requirements.get("model_required")) or _as_bool(model_requirements.get("model_provider_required")),
            _as_bool(model_policy.get("model_provider_enabled")),
            "blocked_by_model_requirement",
            "model_provider_disabled",
            future_gated=False,
        )
    )
    results.append(
        _requirement_decision(
            "credentials",
            _as_bool(credential_requirements.get("credentials_required")),
            _as_bool(credential_policy.get("credentials_allowed")),
            "blocked_by_credential_requirement",
            "credentials_forbidden",
            future_gated=False,
        )
    )

    return {
        "decision": _highest_priority_decision([item["decision"] for item in results], default="allowed_for_validation"),
        "network_policy_results": [item for item in results if item["policy"] == "network"],
        "model_provider_policy_results": [item for item in results if item["policy"] == "model_provider"],
        "credential_policy_results": [item for item in results if item["policy"] == "credentials"],
        "reasons": reasons,
        "warnings": warnings,
        "errors": errors,
    }


def evaluate_local_state_policy(
    node_policy: dict[str, Any],
    workunit: dict[str, Any],
    registries: dict[str, Any],
) -> dict[str, Any]:
    """Evaluate local state requirements without creating local state."""

    del registries
    local_state_requirements = workunit.get("local_state_requirements", {})
    if not isinstance(local_state_requirements, dict):
        local_state_requirements = {}
    local_state_policy = node_policy.get("local_state_policy", {})
    if not isinstance(local_state_policy, dict):
        local_state_policy = {}
    required = _as_bool(local_state_requirements.get("local_state_required"))
    enabled = _as_bool(local_state_policy.get("local_state_enabled"))
    decision = "allowed_for_validation"
    reasons: list[dict[str, Any]] = []
    warnings: list[str] = []
    errors: list[str] = []
    if required and not enabled:
        decision = "blocked_by_local_state_requirement"
        errors.append("local state is required but disabled")
        reasons.append(_reason("local_state_disabled", "blocked", "local state stays disabled"))
    else:
        reasons.append(_reason("local_state_disabled", "allowed", "local state creation is not required"))
    return {
        "decision": decision,
        "local_state_required": required,
        "local_state_enabled": enabled,
        "reasons": reasons,
        "warnings": warnings,
        "errors": errors,
    }


def evaluate_review_gate_policy(
    node_policy: dict[str, Any],
    workunit: dict[str, Any],
    registries: dict[str, Any],
) -> dict[str, Any]:
    """Evaluate review gates and preserve downstream human review."""

    del registries
    node_review = node_policy.get("review_gate_policy", {})
    if not isinstance(node_review, dict):
        node_review = {}
    workunit_gates = workunit.get("review_gates", {})
    if not isinstance(workunit_gates, dict):
        workunit_gates = {}
    required = {
        "human_review_required",
        "policy_review_required",
        "source_policy_review_required",
        "evidence_review_required",
        "master_index_review_required",
    }
    results: list[dict[str, Any]] = []
    warnings: list[str] = []
    reasons: list[dict[str, Any]] = []
    for gate in sorted(required | set(workunit_gates) | set(node_review)):
        if not gate.endswith("_required"):
            continue
        node_value = bool(node_review.get(gate, True))
        workunit_value = bool(workunit_gates.get(gate, True))
        preserved = node_value or workunit_value
        if not preserved:
            warnings.append(f"review gate {gate} is not explicitly preserved by inputs")
        results.append(
            {
                "review_gate": gate,
                "node_policy_requires": node_value,
                "workunit_requires": workunit_value,
                "preserved": preserved,
            }
        )
    reasons.append(_reason("review_required", "allowed", "evaluation remains review-gated"))
    return {
        "decision": "allowed_for_manual_review",
        "review_gate_results": results,
        "reasons": reasons,
        "warnings": warnings,
        "errors": [],
    }


def _highest_priority_decision(decisions: list[str], default: str = "allowed_for_validation") -> str:
    filtered = [decision for decision in decisions if decision]
    if not filtered:
        return default
    for decision in HARD_BLOCK_DECISIONS:
        if decision in filtered:
            return decision
    for decision in GATED_DECISIONS:
        if decision in filtered:
            return decision
    if "deferred_future" in filtered:
        return "deferred_future"
    if "allowed_as_noop" in filtered:
        return "allowed_as_noop"
    for decision in (
        "allowed_for_dry_run",
        "allowed_for_validation",
        "allowed_for_report_only",
        "allowed_for_manual_review",
    ):
        if decision in filtered:
            return decision
    return filtered[0]


def _status_from_decision(decision: str, warnings: list[str], errors: list[str]) -> str:
    if decision == "allowed_as_noop":
        return "noop"
    if decision in HARD_BLOCK_DECISIONS:
        return "blocked"
    if decision in GATED_DECISIONS:
        return "gated"
    if decision == "deferred_future":
        return "warn"
    if decision == "not_evaluable":
        return "not_evaluable"
    if errors:
        return "fail"
    if warnings:
        return "warn"
    return "pass"


def _is_noop_workunit(workunit: dict[str, Any]) -> bool:
    fixture = workunit.get("dry_run_fixture", {})
    if isinstance(fixture, dict) and fixture.get("already_satisfied") is True:
        return True
    return str(workunit.get("workunit_status")) in {"noop", "completed_future", "already_satisfied"}


def _is_policy_blocked_workunit(workunit: dict[str, Any]) -> bool:
    status = str(workunit.get("workunit_status", ""))
    kind = str(workunit.get("workunit_type", ""))
    if status in {"policy_blocked", "blocked", "rejected"} or kind == "policy_blocked":
        return True
    for capability in _required_capabilities(workunit):
        if capability == "policy_blocked_capability_v0":
            return True
    return False


def build_node_policy_evaluation_result(
    inputs: dict[str, Any],
    policies: dict[str, Any] | None = None,
    registries: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a deterministic policy evaluation report from explicit inputs."""

    del policies
    node_manifest = copy.deepcopy(inputs["node_manifest"])
    node_policy = copy.deepcopy(inputs["node_policy"])
    workunit = copy.deepcopy(inputs["workunit"])
    capability_matrix = inputs.get("capability_matrix")
    registries = registries or default_registries(capability_matrix)

    sections: list[dict[str, Any]] = []
    sections.append(evaluate_node_mode(node_manifest, node_policy, workunit, registries))
    sections.append(evaluate_required_capabilities(node_manifest, node_policy, workunit, registries))
    sections.append(evaluate_input_policy(node_policy, workunit, registries))
    sections.append(evaluate_output_policy(node_policy, workunit, registries))
    sections.append(evaluate_action_policy(node_policy, workunit, registries))
    sections.append(evaluate_source_access_policy(node_policy, workunit, registries))
    sections.append(evaluate_network_model_credential_policy(node_policy, workunit, registries))
    sections.append(evaluate_local_state_policy(node_policy, workunit, registries))
    sections.append(evaluate_review_gate_policy(node_policy, workunit, registries))

    decisions = [str(section.get("decision")) for section in sections]
    decision_reasons: list[dict[str, Any]] = []
    warnings: list[str] = []
    errors: list[str] = []
    for section in sections:
        decision_reasons.extend(_as_list(section.get("reasons")))
        warnings.extend(str(item) for item in _as_list(section.get("warnings")))
        errors.extend(str(item) for item in _as_list(section.get("errors")))

    if _is_policy_blocked_workunit(workunit):
        decisions.insert(0, "blocked_by_policy")
        errors.append("WorkUnit is policy-blocked")
        decision_reasons.append(_reason("policy_conflict", "blocked", "WorkUnit policy status blocks evaluation"))

    if _is_noop_workunit(workunit) and not any(decision in HARD_BLOCK_DECISIONS for decision in decisions):
        decisions.insert(0, "allowed_as_noop")
        decision_reasons.append(_reason("future_deferred", "allowed", "WorkUnit is already satisfied/noop for replay"))

    decision = _highest_priority_decision(decisions, default="allowed_for_dry_run")
    status = _status_from_decision(decision, warnings, errors)
    allowed_for_dry_run = decision in {
        "allowed_for_dry_run",
        "allowed_for_validation",
        "allowed_for_report_only",
        "allowed_for_manual_review",
        "allowed_as_noop",
    }
    if decision == "allowed_for_validation":
        decision = "allowed_for_dry_run"
        allowed_for_dry_run = True

    node_manifest_ref = _record_ref(
        inputs.get("node_manifest_path"),
        _record_id(node_manifest, ("node_manifest_id", "node_id")),
    )
    node_policy_ref = _record_ref(
        inputs.get("node_policy_path"),
        _record_id(node_policy, ("node_policy_id", "policy_id")),
    )
    workunit_ref = _record_ref(
        inputs.get("workunit_path"),
        _record_id(workunit, ("workunit_id", "work_unit_id")),
    )
    workunit_id = _record_id(workunit, ("workunit_id", "work_unit_id")) or "unknown_workunit"
    node_id = _record_id(node_manifest, ("node_manifest_id", "node_id")) or "unknown_node"

    result = {
        "schema_version": SCHEMA_VERSION,
        "evaluation_result_id": _stable_id("node_policy_eval", [node_id, workunit_id, node_policy_ref]),
        "evaluation_status": status,
        "decision": decision,
        "decision_reasons": decision_reasons,
        "evaluated_node_manifest_ref": node_manifest_ref,
        "evaluated_node_policy_ref": node_policy_ref,
        "evaluated_workunit_ref": workunit_ref,
        "evaluated_capability_refs": _required_capabilities(workunit),
        "node_mode_result": sections[0],
        "capability_results": sections[1].get("capability_results", []),
        "input_policy_results": sections[2].get("input_policy_results", []),
        "output_policy_results": sections[3].get("output_policy_results", []),
        "action_policy_results": sections[4].get("action_policy_results", []),
        "source_access_results": {
            "source_access_required": sections[5].get("source_access_required", False),
            "allowed_mode": sections[5].get("allowed_mode"),
            "decision": sections[5].get("decision"),
        },
        "network_policy_results": sections[6].get("network_policy_results", []),
        "model_provider_policy_results": sections[6].get("model_provider_policy_results", []),
        "credential_policy_results": sections[6].get("credential_policy_results", []),
        "local_state_policy_results": {
            "local_state_required": sections[7].get("local_state_required", False),
            "local_state_enabled": sections[7].get("local_state_enabled", False),
            "decision": sections[7].get("decision"),
        },
        "review_gate_results": sections[8].get("review_gate_results", []),
        "blocked_actions": sections[4].get("blocked_actions", []),
        "skipped_actions": sections[4].get("skipped_actions", []),
        "allowed_for_dry_run": allowed_for_dry_run,
        "allowed_for_execution": False,
        "allowed_for_public_export": False,
        "allowed_for_master_index_mutation": False,
        "warnings": sorted(dict.fromkeys(warnings)),
        "errors": sorted(dict.fromkeys(errors)),
        "limitations": [
            "Evaluation is report-only and does not execute WorkUnits.",
            "Evaluation does not access live sources, networks, APIs, models, credentials, or browser state.",
            "Evaluation does not accept evidence, accept candidates, or mutate the master index.",
        ],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": [
            "Allowed decisions only authorize validation or dry-run simulation.",
            "Human review is required before downstream use.",
        ],
    }
    return result


def summarize_node_policy_evaluation(result: dict[str, Any]) -> str:
    """Return a stable Markdown summary for a node policy evaluation result."""

    lines = [
        f"# Node Policy Evaluation: {result.get('evaluation_result_id', 'unknown')}",
        "",
        f"- Status: {result.get('evaluation_status', 'unknown')}",
        f"- Decision: {result.get('decision', 'unknown')}",
        f"- Node manifest: {result.get('evaluated_node_manifest_ref', 'unknown')}",
        f"- Node policy: {result.get('evaluated_node_policy_ref', 'unknown')}",
        f"- WorkUnit: {result.get('evaluated_workunit_ref', 'unknown')}",
        f"- Allowed for dry-run: {str(result.get('allowed_for_dry_run', False)).lower()}",
        f"- Allowed for execution: {str(result.get('allowed_for_execution', False)).lower()}",
        f"- Allowed for master-index mutation: {str(result.get('allowed_for_master_index_mutation', False)).lower()}",
    ]
    warnings = _as_list(result.get("warnings"))
    errors = _as_list(result.get("errors"))
    if warnings:
        lines.extend(["", "## Warnings"])
        lines.extend(f"- {warning}" for warning in warnings)
    if errors:
        lines.extend(["", "## Errors"])
        lines.extend(f"- {error}" for error in errors)
    return "\n".join(lines) + "\n"


def _scan_forbidden_claims(value: Any, path: str = "$") -> list[str]:
    violations: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            violations.extend(_scan_forbidden_claims(item, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            violations.extend(_scan_forbidden_claims(item, f"{path}[{index}]"))
    elif isinstance(value, str):
        lowered = value.lower()
        for phrase in FORBIDDEN_CLAIM_PHRASES:
            if phrase in lowered:
                violations.append(f"{path}: forbidden claim phrase {phrase!r}")
    return violations


def detect_policy_boundary_violations(
    result: dict[str, Any],
    policies: dict[str, Any] | None = None,
) -> list[str]:
    """Detect product/policy boundary violations in an evaluation result."""

    del policies
    violations: list[str] = []
    for field in ("allowed_for_execution", "allowed_for_public_export", "allowed_for_master_index_mutation"):
        if result.get(field) is not False:
            violations.append(f"{field} must be false")
    product_boundary = result.get("product_boundary", {})
    if not isinstance(product_boundary, dict):
        violations.append("product_boundary must be an object")
    else:
        for field in FALSE_PRODUCT_BOUNDARY_FIELDS:
            if product_boundary.get(field) is not False:
                violations.append(f"product_boundary.{field} must be false")
    violations.extend(_scan_forbidden_claims(result))
    return sorted(dict.fromkeys(violations))


def detect_truth_boundary_violations(
    result: dict[str, Any],
    policies: dict[str, Any] | None = None,
) -> list[str]:
    """Detect truth-boundary violations in an evaluation result."""

    del policies
    violations: list[str] = []
    truth_boundary = result.get("truth_boundary", {})
    if not isinstance(truth_boundary, dict):
        violations.append("truth_boundary must be an object")
    else:
        for field in FALSE_TRUTH_BOUNDARY_FIELDS:
            if truth_boundary.get(field) is not False:
                violations.append(f"truth_boundary.{field} must be false")
        for field in TRUE_TRUTH_BOUNDARY_FIELDS:
            if truth_boundary.get(field) is not True:
                violations.append(f"truth_boundary.{field} must be true")
    return sorted(dict.fromkeys(violations))


def validate_node_policy_evaluation_result(
    result: dict[str, Any],
    policies: dict[str, Any] | None = None,
) -> list[str]:
    """Return deterministic validation errors for an evaluation result."""

    errors: list[str] = []
    required_fields = (
        "schema_version",
        "evaluation_result_id",
        "evaluation_status",
        "decision",
        "decision_reasons",
        "evaluated_node_manifest_ref",
        "evaluated_node_policy_ref",
        "evaluated_workunit_ref",
        "allowed_for_dry_run",
        "allowed_for_execution",
        "allowed_for_public_export",
        "allowed_for_master_index_mutation",
        "truth_boundary",
        "product_boundary",
    )
    for field in required_fields:
        if field not in result:
            errors.append(f"missing required field: {field}")
    if result.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")
    if result.get("evaluation_status") not in EVALUATION_STATUSES:
        errors.append(f"invalid evaluation_status: {result.get('evaluation_status')}")
    if result.get("decision") not in DECISIONS:
        errors.append(f"invalid decision: {result.get('decision')}")
    if not isinstance(result.get("decision_reasons"), list):
        errors.append("decision_reasons must be a list")
    else:
        for index, reason in enumerate(result.get("decision_reasons", [])):
            if not isinstance(reason, dict):
                errors.append(f"decision_reasons[{index}] must be an object")
                continue
            category = reason.get("reason_category")
            if category not in REASON_CATEGORIES:
                errors.append(f"invalid reason category at decision_reasons[{index}]: {category}")
    if result.get("decision") in HARD_BLOCK_DECISIONS and result.get("allowed_for_dry_run") is True:
        errors.append("blocked decisions must not be allowed_for_dry_run")
    errors.extend(detect_truth_boundary_violations(result, policies))
    errors.extend(detect_policy_boundary_violations(result, policies))
    return sorted(dict.fromkeys(errors))
