"""Fail-closed connector policy evaluation helpers."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from runtime.connectors.core.connector_interface import validate_no_boundary_violations


FIXTURE_OPERATIONS = {"inspect_fixture", "normalize_fixture", "fixture_replay"}
FORBIDDEN_BY_DEFAULT = {
    "arbitrary_url_fetch",
    "unbounded_search",
    "broad_crawl",
    "scrape_html_without_policy",
    "bypass_access_controls",
    "bypass_captcha",
    "use_credentials_without_policy",
    "download_binary",
    "fetch_item_file_payload",
    "run_installer",
    "execute_downloaded_artifact",
    "upload_to_hosted_backend",
    "mutate_public_index",
    "mutate_master_index",
    "accept_evidence_truth",
    "accept_public_truth",
}


def evaluate_connector_policy(request: Mapping[str, Any], policies: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Evaluate a connector request without performing the requested work."""

    policies = policies or {}
    operation = str(request.get("requested_operation") or request.get("operation") or "not_evaluable")
    reasons: list[str] = []
    missing: list[str] = []
    decision = "not_evaluable"
    live_requested = request.get("live_call_allowed") is True or request.get("dry_run_only") is False

    if operation in FORBIDDEN_BY_DEFAULT:
        decision = "blocked_by_forbidden_operation"
        reasons.append(f"operation is forbidden by default: {operation}")
    elif operation in FIXTURE_OPERATIONS:
        decision = "allowed_fixture_replay"
        reasons.append("fixture replay is allowed because it is offline and committed-fixture-only")
    elif live_requested:
        decision = "blocked_missing_approval"
        required = _required_approvals(policies)
        missing = [item for item in required if item not in set(_strings(request.get("approval_refs")))]
        if not missing:
            missing = ["explicit H0 live approval is not available in this bundle"]
        reasons.extend(f"missing approval: {item}" for item in missing)
    elif operation.endswith("_future"):
        decision = "allowed_dry_run_only"
        reasons.append("future operation can be represented as dry-run policy, not executed")
    else:
        decision = "not_evaluable"
        reasons.append("requested operation is not in the current connector policy vocabulary")

    result = {
        "schema_version": "connector_policy_evaluation.v0",
        "policy_evaluation_id": str(request.get("policy_evaluation_id") or "connector_policy_evaluation.generic.v0"),
        "connector_id": str(request.get("connector_id") or "unknown_connector"),
        "source_id": str(request.get("source_id") or "unknown_source"),
        "source_policy_refs": list(request.get("source_policy_refs") or []),
        "connector_capability_refs": list(request.get("connector_capability_refs") or []),
        "requested_operation": operation,
        "decision": decision,
        "reasons": reasons,
        "required_approvals": _required_approvals(policies),
        "missing_approvals": missing,
        "allowed_for_fixture_replay": decision == "allowed_fixture_replay",
        "allowed_for_live_probe": False,
        "allowed_for_source_cache_write": False,
        "allowed_for_evidence_candidate_generation": False,
        "allowed_for_public_index_mutation": False,
        "allowed_for_master_index_mutation": False,
        "truth_boundary": {
            "connector_policy_evaluation_is_truth": False,
            "connector_capability_grants_permission": False,
            "public_index_mutated": False,
            "master_index_mutated": False,
            "rights_clearance_claimed": False,
            "malware_safety_claimed": False,
            "verified_installability_claimed": False,
        },
        "product_boundary": {
            "changed_public_search_behavior": False,
            "enabled_live_probes": False,
            "enabled_source_sync": False,
            "enabled_downloads": False,
            "mutated_public_index": False,
            "mutated_master_index": False,
        },
        "notes": ["Policy evaluation is advisory and does not execute connector operations."],
    }
    validate_no_boundary_violations(result, policies)
    return result


def _required_approvals(policies: Mapping[str, Any]) -> list[str]:
    gate_policy = policies.get("connector_policy_evaluation_policy") if isinstance(policies, Mapping) else None
    if isinstance(gate_policy, Mapping) and isinstance(gate_policy.get("required_live_approval_gates"), list):
        return [str(item) for item in gate_policy["required_live_approval_gates"]]
    return [
        "source_policy_approval",
        "endpoint_allowlist",
        "user_agent_contact_decision",
        "rate_limit",
        "timeout",
        "retry_budget",
        "cache_ttl",
        "kill_switch",
        "output_path_policy",
        "review_gates",
    ]


def _strings(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if item not in (None, "")]
    if value in (None, ""):
        return []
    return [str(value)]
