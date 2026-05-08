"""Local-only WorkUnit dry-run helpers.

This module simulates WorkUnit policy decisions and builds WorkUnitResult
envelopes. It is intentionally standard-library only and side-effect free
except for ``load_workunit``, which reads one explicit JSON file supplied by
the caller. It does not execute WorkUnits, call networks, call providers,
create private local state, alter public search, or mutate index state.
"""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable, Mapping


RESULT_SCHEMA_VERSION = "work_unit_result.v0"

ALLOWED_RESULT_STATUSES = {
    "pass",
    "pass_with_warnings",
    "warn",
    "partial",
    "fail",
    "blocked",
    "noop",
    "skipped",
    "deferred",
    "policy_blocked",
    "rights_blocked",
    "risk_blocked",
    "permission_needed",
    "operator_gated",
    "human_operated",
    "approval_gated",
    "not_evaluable",
}
ALLOWED_EXECUTION_MODES = {
    "contract_only",
    "validate_only",
    "dry_run_only",
    "report_only",
    "repo_local_only",
    "human_operated",
    "future_runtime",
    "future_approved_source",
    "future_local_state",
    "future_model_assist",
    "blocked",
}
ALLOWED_ACTION_STATUSES = {
    "planned",
    "executed",
    "skipped",
    "blocked",
    "forbidden_checked",
    "not_applicable",
    "deferred",
    "failed",
}
DRY_RUN_CLASSIFICATIONS = {
    "allowed_for_dry_run",
    "simulated_only",
    "skipped_not_required",
    "blocked_by_policy",
    "forbidden_checked",
    "deferred_future",
    "not_applicable",
    "failed_validation",
}
ALLOWED_WORKUNIT_STATUSES = {
    "example_only",
    "contract_only",
    "planned",
    "ready_for_validation",
    "dry_run_only",
    "ready_for_manual_review",
    "human_operated",
    "approval_gated",
    "operator_gated",
    "permission_needed",
    "policy_blocked",
    "deferred",
    "blocked",
    "completed_future",
    "rejected_future",
    "superseded_future",
}
ALLOWED_WORKUNIT_TYPES = {
    "search_need_review",
    "source_lead_inspection",
    "observation_candidate_review",
    "local_eval_failure_review",
    "candidate_dedup",
    "compatibility_evidence_review",
    "evidence_pack_drafting_future",
    "contribution_pack_drafting_future",
    "source_pack_drafting_future",
    "approved_metadata_sync_future",
    "approved_metadata_probe_future",
    "wayback_metadata_trace_future",
    "container_deepening_future",
    "hash_verification_future",
    "discussion_to_evidence_future",
    "ai_assisted_drafting_future",
    "policy_blocked_work_unit",
}
ALLOWED_NODE_MODES = {
    "local_private",
    "local_pack_builder",
    "local_autonomous_dry_run",
    "community_node_future",
    "institution_node_future",
    "hosted_worker_future",
}
CURRENT_DRY_RUN_NODE_MODES = {
    "local_private",
    "local_pack_builder",
    "local_autonomous_dry_run",
}
CAPABILITY_STATUSES = {
    "repo_local_inspection": "current_repo_local_only",
    "local_eval_analysis": "current_repo_local_only",
    "search_need_analysis": "current_dry_run_only",
    "observation_candidate_preparation": "current_dry_run_only",
    "source_lead_preparation": "current_dry_run_only",
    "workunit_candidate_preparation_future": "future",
    "pack_validation": "current_validate_only",
    "pack_drafting_future": "future",
    "evidence_drafting_future": "future",
    "candidate_drafting_future": "future",
    "local_index_read_future": "deferred",
    "local_index_write_future": "deferred",
    "local_source_cache_read_future": "deferred",
    "local_source_cache_write_future": "deferred",
    "local_evidence_ledger_read_future": "deferred",
    "local_evidence_ledger_write_future": "deferred",
    "extraction_planning_future": "future",
    "extraction_runtime_future": "deferred",
    "approved_metadata_probe_future": "approval_gated",
    "approved_api_access_future": "approval_gated",
    "local_model_assist_future": "operator_gated",
    "hosted_worker_execution_future": "deferred",
    "policy_blocked_capability_v0": "policy_blocked",
}
CURRENT_CAPABILITY_STATUSES = {
    "current_repo_local_only",
    "current_dry_run_only",
    "current_validate_only",
}
ALLOWED_OUTPUT_TYPES = {
    "workunit_report",
    "dry_run_report",
    "validation_report",
    "observation_candidate",
    "observation_candidate_summary",
    "source_lead_candidate",
    "search_need_seed_future",
    "workunit_seed_future",
    "evidence_draft_future",
    "candidate_record_future",
    "contribution_pack_draft_future",
    "review_item_future",
    "pack_export_future",
}
FORBIDDEN_OUTPUT_TYPES = {
    "observed_baseline_truth",
    "accepted_evidence_truth",
    "accepted_public_record",
    "master_index_mutation",
    "rights_clearance",
    "malware_safety",
    "verified_installability",
    "exhaustive_global_search_proof",
    "production_readiness_claim",
}
REVIEW_REQUIRED_OUTPUTS = {
    "observation_candidate",
    "observation_candidate_summary",
    "source_lead_candidate",
    "search_need_seed_future",
    "workunit_seed_future",
    "evidence_draft_future",
    "candidate_record_future",
    "contribution_pack_draft_future",
    "review_item_future",
    "pack_export_future",
}
FORBIDDEN_ACTIONS = {
    "mutate_master_index",
    "mark_candidate_accepted",
    "mark_evidence_accepted",
    "mark_observation_observed_without_human",
    "mark_agent_output_as_truth",
    "enable_live_probe",
    "scrape_external_site",
    "crawl_external_site",
    "browser_automation",
    "call_unapproved_api",
    "download_binary",
    "run_installer",
    "execute_downloaded_artifact",
    "store_credentials",
    "upload_to_hosted_backend",
    "create_account_or_user_data",
    "emit_telemetry",
    "claim_rights_clearance",
    "claim_malware_safety",
    "claim_verified_installability",
    "claim_exhaustive_global_search",
    "claim_production_readiness",
}
REQUIRED_REVIEW_GATES = {
    "human_review_required",
    "source_policy_review_required",
    "evidence_review_required",
    "candidate_review_required",
    "pack_review_required",
    "master_index_review_required",
    "rights_review_required",
    "risk_review_required",
    "privacy_review_required",
    "operator_approval_required_for_network",
    "operator_approval_required_for_hosted_behavior",
    "legal_or_rights_decision_stop_required",
}
TRUTH_BOUNDARY_FALSE_FIELDS = {
    "result_is_observed_baseline",
    "result_is_accepted_evidence",
    "result_is_public_truth",
    "result_mutates_master_index",
    "result_claims_rights_clearance",
    "result_claims_malware_safety",
    "result_claims_verified_installability",
    "result_claims_exhaustive_global_search",
    "result_claims_production_readiness",
}
PRODUCT_BOUNDARY_FALSE_FIELDS = {
    "implemented_workunit_runtime",
    "implemented_node_runtime",
    "created_local_state",
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
}
FORBIDDEN_CLAIM_PHRASES = {
    "workunit executed",
    "executed workunit actions",
    "network call completed",
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
    "malware safe",
    "verified installability",
    "exhaustive global search proof",
    "production readiness",
}
REQUIREMENT_SECTIONS = {
    "source_access_requirements": "source_access_required",
    "network_requirements": "network_required",
    "model_provider_requirements": "model_provider_required",
    "credential_requirements": "credentials_required",
    "local_state_requirements": "local_state_required",
}


def default_policies() -> dict[str, Any]:
    """Return deterministic built-in dry-run policy vocabulary."""

    return {
        "allowed_workunit_statuses": sorted(ALLOWED_WORKUNIT_STATUSES),
        "allowed_workunit_types": sorted(ALLOWED_WORKUNIT_TYPES),
        "allowed_node_modes": sorted(ALLOWED_NODE_MODES),
        "current_dry_run_node_modes": sorted(CURRENT_DRY_RUN_NODE_MODES),
        "capability_statuses": dict(sorted(CAPABILITY_STATUSES.items())),
        "current_capability_statuses": sorted(CURRENT_CAPABILITY_STATUSES),
        "action_classifications": sorted(DRY_RUN_CLASSIFICATIONS),
        "forbidden_actions": sorted(FORBIDDEN_ACTIONS),
        "allowed_output_types": sorted(ALLOWED_OUTPUT_TYPES),
        "forbidden_output_types": sorted(FORBIDDEN_OUTPUT_TYPES),
        "required_review_gates": sorted(REQUIRED_REVIEW_GATES),
        "truth_boundary_false_fields": sorted(TRUTH_BOUNDARY_FALSE_FIELDS),
        "product_boundary_false_fields": sorted(PRODUCT_BOUNDARY_FALSE_FIELDS),
    }


def load_workunit(path: str | Path) -> dict[str, Any]:
    """Read one explicit WorkUnit JSON file."""

    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("WorkUnit JSON must be an object")
    return payload


def validate_workunit_for_dry_run(
    workunit: Mapping[str, Any],
    policies: Mapping[str, Any] | None = None,
) -> list[str]:
    """Return validation errors that prevent building a safe dry-run result."""

    active_policy = policies or default_policies()
    errors: list[str] = []
    if workunit.get("schema_version") != "work_unit.v0":
        errors.append("schema_version must be work_unit.v0")
    if workunit.get("workunit_status") not in set(active_policy["allowed_workunit_statuses"]):
        errors.append("workunit_status is not allowed")
    if workunit.get("workunit_type") not in set(active_policy["allowed_workunit_types"]):
        errors.append("workunit_type is not allowed")
    errors.extend(evaluate_required_node_modes(workunit, active_policy)["errors"])
    errors.extend(evaluate_required_capabilities(workunit, active_policy)["errors"])
    errors.extend(evaluate_source_access_requirements(workunit, active_policy)["errors"])
    errors.extend(evaluate_network_model_credential_requirements(workunit, active_policy)["errors"])
    for output in _sequence(workunit.get("expected_outputs")):
        output_type = output.get("output_type") if isinstance(output, Mapping) else None
        if output_type in FORBIDDEN_OUTPUT_TYPES:
            errors.append(f"expected output {output_type} is forbidden")
        elif output_type not in ALLOWED_OUTPUT_TYPES:
            errors.append(f"expected output {output_type} is not allowed")
    return sorted(errors)


def evaluate_required_node_modes(
    workunit: Mapping[str, Any],
    policies: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    active_policy = policies or default_policies()
    allowed_modes = set(active_policy["allowed_node_modes"])
    current_modes = set(active_policy["current_dry_run_node_modes"])
    required_modes = sorted(_string_items(workunit.get("required_node_modes")))
    unknown = sorted(set(required_modes) - allowed_modes)
    future_or_blocked = sorted(set(required_modes) - current_modes - set(unknown))
    errors = [f"unknown required node mode: {mode}" for mode in unknown]
    return {
        "status": "fail" if errors else ("blocked" if future_or_blocked else "pass"),
        "required_modes": required_modes,
        "unknown_modes": unknown,
        "future_or_blocked_modes": future_or_blocked,
        "errors": errors,
    }


def evaluate_required_capabilities(
    workunit: Mapping[str, Any],
    policies: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    active_policy = policies or default_policies()
    capability_statuses = dict(active_policy["capability_statuses"])
    current_statuses = set(active_policy["current_capability_statuses"])
    required = [
        item.get("capability_id")
        for item in _sequence(workunit.get("required_node_capabilities"))
        if isinstance(item, Mapping) and item.get("required", True) is True
    ]
    optional = [
        item.get("capability_id")
        for item in _sequence(workunit.get("required_node_capabilities"))
        if isinstance(item, Mapping) and item.get("required", True) is not True
    ]
    unknown = sorted(item for item in required + optional if isinstance(item, str) and item not in capability_statuses)
    blocked = sorted(
        item
        for item in required
        if isinstance(item, str)
        and item in capability_statuses
        and capability_statuses[item] not in current_statuses
    )
    errors = [f"unknown required node capability: {capability}" for capability in unknown if capability in required]
    return {
        "status": "fail" if errors else ("blocked" if blocked else "pass"),
        "required_capabilities": sorted(item for item in required if isinstance(item, str)),
        "optional_capabilities": sorted(item for item in optional if isinstance(item, str)),
        "unknown_capabilities": unknown,
        "blocked_capabilities": blocked,
        "capability_statuses": {key: capability_statuses[key] for key in sorted(capability_statuses) if key in set(required + optional)},
        "errors": errors,
    }


def evaluate_source_access_requirements(
    workunit: Mapping[str, Any],
    policies: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    source = _mapping(workunit.get("source_access_requirements"))
    required = source.get("source_access_required") is True
    current_enabled = source.get("current_enabled") is True
    blocked = required or current_enabled
    errors = ["source access is required but dry-run runner cannot perform source access"] if blocked else []
    return {
        "status": "blocked" if blocked else "pass",
        "source_access_required": required,
        "current_enabled": current_enabled,
        "errors": errors,
    }


def evaluate_network_model_credential_requirements(
    workunit: Mapping[str, Any],
    policies: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    blocked_sections: list[str] = []
    errors: list[str] = []
    for section, required_field in REQUIREMENT_SECTIONS.items():
        payload = _mapping(workunit.get(section))
        if payload.get("current_enabled") is True:
            blocked_sections.append(section)
            errors.append(f"{section}.current_enabled must be false for dry-run")
        if payload.get(required_field) is True and section != "source_access_requirements":
            blocked_sections.append(section)
            errors.append(f"{section}.{required_field} is blocked by dry-run policy")
    return {
        "status": "blocked" if blocked_sections else "pass",
        "blocked_sections": sorted(set(blocked_sections)),
        "errors": sorted(set(errors)),
    }


def classify_actions_for_dry_run(
    workunit: Mapping[str, Any],
    policies: Mapping[str, Any] | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """Classify WorkUnit actions without executing them."""

    requirements = evaluate_network_model_credential_requirements(workunit, policies)
    source_requirements = evaluate_source_access_requirements(workunit, policies)
    capability_requirements = evaluate_required_capabilities(workunit, policies)
    policy_blocked = (
        workunit.get("workunit_status") == "policy_blocked"
        or requirements["status"] == "blocked"
        or source_requirements["status"] == "blocked"
        or capability_requirements["status"] == "blocked"
    )

    planned: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    blocked: list[dict[str, Any]] = []
    forbidden_checked: list[dict[str, Any]] = []

    for index, action in enumerate(_string_items(workunit.get("allowed_actions")), start=1):
        action_id = f"dry_run_action_{index:03d}_{_slug(action)}"
        if action in FORBIDDEN_ACTIONS:
            forbidden_checked.append(_action_record(action_id, action, "forbidden_checked", "truth_boundary", False, True, "Forbidden action was checked and not executed."))
        elif policy_blocked and action not in {"produce_review_packet", "request_human_review", "request_source_policy_approval_future"}:
            blocked.append(_action_record(action_id, action, "blocked", "dry_run_policy", False, True, "Dry-run policy blocked this action before execution."))
        elif _is_future_action(action):
            skipped.append(_action_record(action_id, action, "deferred", "future_planning", True, False, "Future action was deferred and not executed."))
        else:
            planned.append(_action_record(action_id, action, "planned", "dry_run_simulation", True, False, "Action was simulated only; no side effect occurred."))

    for index, action in enumerate(_string_items(workunit.get("forbidden_actions")), start=1):
        forbidden_checked.append(
            _action_record(
                f"forbidden_check_{index:03d}_{_slug(action)}",
                action,
                "forbidden_checked",
                "dry_run_forbidden_action_model",
                False,
                True,
                "Forbidden action remains blocked and was not executed.",
            )
        )

    return {
        "planned_actions": planned,
        "executed_actions": [],
        "skipped_actions": skipped,
        "blocked_actions": blocked,
        "forbidden_actions_checked": forbidden_checked,
    }


def build_workunit_dry_run_result(
    workunit: Mapping[str, Any],
    policies: Mapping[str, Any] | None = None,
    *,
    source_workunit_ref: str | None = None,
    result_id_suffix: str = "dry_run_v0",
) -> dict[str, Any]:
    """Build a WorkUnitResult-shaped dry-run envelope without execution."""

    active_policy = policies or default_policies()
    normalized = deepcopy(dict(workunit))
    validation_errors = validate_workunit_for_dry_run(normalized, active_policy)
    mode_eval = evaluate_required_node_modes(normalized, active_policy)
    capability_eval = evaluate_required_capabilities(normalized, active_policy)
    source_eval = evaluate_source_access_requirements(normalized, active_policy)
    requirement_eval = evaluate_network_model_credential_requirements(normalized, active_policy)
    action_sections = classify_actions_for_dry_run(normalized, active_policy)
    status = _result_status(normalized, validation_errors, mode_eval, capability_eval, source_eval, requirement_eval)
    execution_mode = "blocked" if status in {"blocked", "policy_blocked", "approval_gated", "operator_gated", "permission_needed", "deferred", "fail"} else "dry_run_only"
    warnings = _dry_run_warnings(normalized, mode_eval, capability_eval, source_eval, requirement_eval, action_sections)
    outputs_proposed = _outputs_proposed(normalized, status)
    validation_status = "fail" if status == "fail" else ("pass_with_warnings" if warnings and status == "pass_with_warnings" else "pass")
    validation_summary = {
        "validation_status": validation_status,
        "commands_run": ["python scripts/run_workunit_dry_run.py --workunit <explicit-workunit> --check"],
        "validators_run": ["workunit_dry_run.validate_workunit_for_dry_run"],
        "tests_run": [],
        "warnings_count": len(warnings),
        "errors_count": len(validation_errors) if status == "fail" else 0,
        "warn_only": bool(warnings and status != "fail"),
        "validation_artifacts": ["control/audits/track-b-10-workunit-dry-run-runner-v0/track_b_10_report.json"],
        "validation_limitations": ["Dry-run validation does not execute WorkUnit actions."],
        "notes": [],
    }

    result = {
        "schema_version": RESULT_SCHEMA_VERSION,
        "workunit_result_id": f"{normalized.get('workunit_id', 'unknown_workunit')}_{result_id_suffix}",
        "workunit_result_label": f"Dry-run result for {normalized.get('workunit_label', normalized.get('workunit_id', 'unknown WorkUnit'))}",
        "workunit_id": normalized.get("workunit_id"),
        "workunit_type": normalized.get("workunit_type"),
        "workunit_result_status": status,
        "result_scope": normalized.get("workunit_scope", "repo_local"),
        "produced_by": {
            "producer_type": "local_foundry_workunit_dry_run",
            "node_id": _node_id_from_ref(_first_string(normalized.get("related_node_manifest_refs"))),
            "human_review_required": True,
        },
        "produced_at_note": "Deterministic dry-run result; no WorkUnit action was executed.",
        "source_workunit_ref": source_workunit_ref or f"examples/work_units/{normalized.get('workunit_id', 'unknown_workunit')}/work_unit.json",
        "node_manifest_ref": _first_string(normalized.get("related_node_manifest_refs")) or "examples/nodes/local_private_node_v0/eureka_node_manifest.json",
        "node_policy_ref": _first_string(normalized.get("required_node_policy_refs")) or "examples/nodes/policies/local_private_node_policy_v0.json",
        "node_capability_refs": capability_eval["required_capabilities"],
        "execution_mode": execution_mode,
        "execution_summary": {
            "workunit_executed": False,
            "runtime_used": False,
            "network_used": False,
            "model_provider_used": False,
            "local_state_created": False,
            "summary": _execution_summary_text(status),
        },
        "validation_summary": validation_summary,
        "planned_actions": action_sections["planned_actions"],
        "executed_actions": [],
        "skipped_actions": action_sections["skipped_actions"],
        "blocked_actions": action_sections["blocked_actions"],
        "forbidden_actions_checked": action_sections["forbidden_actions_checked"],
        "inputs_observed": _inputs_observed(normalized),
        "outputs_proposed": outputs_proposed if status not in {"policy_blocked", "blocked", "fail"} else [],
        "outputs_rejected": _outputs_rejected(normalized, status),
        "output_contract_refs": _output_contract_refs(normalized),
        "review_gates": _review_gates(normalized),
        "idempotency_result": _idempotency_result(status),
        "recovery_result": _recovery_result(status),
        "duplicate_result": {
            "duplicate_detected": status == "noop",
            "behavior_applied": "validate_and_record_noop" if status == "noop" else "not_applicable",
            "notes": [] if status != "noop" else ["Dry-run classified this repeated fixture as noop."]
        },
        "out_of_order_result": {
            "out_of_order_detected": False,
            "behavior_applied": "not_applicable",
        },
        "noop_result": {
            "noop_recorded": status == "noop",
            "noop_reason": "already_satisfied_fixture" if status == "noop" else "not_applicable",
            "validated_without_changes": status == "noop",
        },
        "quarantine_result": {
            "quarantined": status == "fail",
            "quarantine_reason": "failed_validation" if status == "fail" else "not_applicable",
            "review_required": status == "fail",
        },
        "warnings": warnings,
        "errors": validation_errors if status == "fail" else [],
        "limitations": [
            "Dry-run simulates policy decisions only.",
            "Dry-run results are review-gated and not public truth.",
            "No WorkUnit action, source access, model call, or network call occurred.",
        ],
        "audit_refs": ["control/audits/track-b-10-workunit-dry-run-runner-v0/track_b_10_report.json"],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "no_goals": [
            "No real WorkUnit execution",
            "No node runtime implementation",
            "No source access, network, API, or model call",
            "No accepted evidence, public truth, or master-index mutation",
        ],
        "notes": [],
    }
    return result


def summarize_workunit_dry_run(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "workunit_result_id": result.get("workunit_result_id"),
        "workunit_id": result.get("workunit_id"),
        "workunit_type": result.get("workunit_type"),
        "workunit_result_status": result.get("workunit_result_status"),
        "execution_mode": result.get("execution_mode"),
        "planned_action_count": len(_sequence(result.get("planned_actions"))),
        "executed_action_count": len(_sequence(result.get("executed_actions"))),
        "blocked_action_count": len(_sequence(result.get("blocked_actions"))),
        "forbidden_action_count": len(_sequence(result.get("forbidden_actions_checked"))),
        "output_count": len(_sequence(result.get("outputs_proposed"))),
        "review_required": _mapping(result.get("review_gates")).get("human_review_required") is True,
        "truth_boundary": {
            "dry_run_result_is_public_truth": False,
            "dry_run_result_is_accepted_evidence": False,
            "dry_run_result_can_mutate_master_index": False,
        },
    }


def detect_forbidden_runtime_claims(
    result: Mapping[str, Any],
    policies: Mapping[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []
    product = _mapping(result.get("product_boundary"))
    for field in sorted(PRODUCT_BOUNDARY_FALSE_FIELDS):
        if product.get(field) is not False:
            errors.append(f"product_boundary.{field} must be false")
    execution = _mapping(result.get("execution_summary"))
    for field in ("workunit_executed", "runtime_used", "network_used", "model_provider_used", "local_state_created"):
        if execution.get(field) is not False:
            errors.append(f"execution_summary.{field} must be false")
    text = _record_text(result).casefold()
    for phrase in sorted(FORBIDDEN_CLAIM_PHRASES):
        if phrase in text:
            errors.append(f"forbidden runtime claim phrase: {phrase}")
    return sorted(errors)


def detect_truth_boundary_violations(
    result: Mapping[str, Any],
    policies: Mapping[str, Any] | None = None,
) -> list[str]:
    truth = _mapping(result.get("truth_boundary"))
    return sorted(
        f"truth_boundary.{field} must be false"
        for field in TRUTH_BOUNDARY_FALSE_FIELDS
        if truth.get(field) is not False
    )


def validate_dry_run_result(result: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if result.get("schema_version") != RESULT_SCHEMA_VERSION:
        errors.append(f"schema_version must be {RESULT_SCHEMA_VERSION}")
    if result.get("workunit_result_status") not in ALLOWED_RESULT_STATUSES:
        errors.append("workunit_result_status is not allowed")
    if result.get("execution_mode") not in ALLOWED_EXECUTION_MODES:
        errors.append("execution_mode is not allowed")
    if _sequence(result.get("executed_actions")):
        errors.append("dry-run result must not contain executed_actions")
    for section in ("planned_actions", "skipped_actions", "blocked_actions", "forbidden_actions_checked"):
        for action in _sequence(result.get(section)):
            action_status = _mapping(action).get("action_status")
            if action_status not in ALLOWED_ACTION_STATUSES:
                errors.append(f"{section} action_status is not allowed")
            if section == "forbidden_actions_checked" and action_status != "forbidden_checked":
                errors.append("forbidden_actions_checked entries must be forbidden_checked")
    for output in _sequence(result.get("outputs_proposed")) + _sequence(result.get("outputs_rejected")):
        output_type = _mapping(output).get("output_type")
        if output_type in FORBIDDEN_OUTPUT_TYPES:
            errors.append(f"forbidden output type: {output_type}")
        elif output_type not in ALLOWED_OUTPUT_TYPES:
            errors.append(f"unknown output type: {output_type}")
        if output_type in REVIEW_REQUIRED_OUTPUTS and _mapping(output).get("output_requires_review") is not True:
            errors.append(f"output {output_type} must require review")
    review_gates = _mapping(result.get("review_gates"))
    for field in REQUIRED_REVIEW_GATES:
        if field not in review_gates:
            errors.append(f"review_gates.{field} is missing")
    errors.extend(detect_truth_boundary_violations(result))
    errors.extend(detect_forbidden_runtime_claims(result))
    return sorted(set(errors))


def format_summary_markdown(summary: Mapping[str, Any]) -> str:
    lines = [
        "# WorkUnit Dry-Run Summary",
        "",
        f"- workunit_result_id: {summary.get('workunit_result_id')}",
        f"- workunit_id: {summary.get('workunit_id')}",
        f"- workunit_result_status: {summary.get('workunit_result_status')}",
        f"- execution_mode: {summary.get('execution_mode')}",
        f"- planned_actions: {summary.get('planned_action_count')}",
        f"- executed_actions: {summary.get('executed_action_count')}",
        f"- blocked_actions: {summary.get('blocked_action_count')}",
        f"- forbidden_actions_checked: {summary.get('forbidden_action_count')}",
        f"- review_required: {str(summary.get('review_required')).lower()}",
        "- public_truth: false",
        "- accepted_evidence: false",
        "- master_index_mutation: false",
    ]
    return "\n".join(lines) + "\n"


def _result_status(
    workunit: Mapping[str, Any],
    validation_errors: list[str],
    mode_eval: Mapping[str, Any],
    capability_eval: Mapping[str, Any],
    source_eval: Mapping[str, Any],
    requirement_eval: Mapping[str, Any],
) -> str:
    if validation_errors and (
        mode_eval.get("status") == "fail" or capability_eval.get("status") == "fail"
    ):
        return "fail"
    status = workunit.get("workunit_status")
    if status == "completed_future" or _mapping(workunit.get("dry_run_fixture")).get("already_satisfied") is True:
        return "noop"
    if status == "policy_blocked" or "policy_blocked_capability_v0" in capability_eval.get("blocked_capabilities", []):
        return "policy_blocked"
    if status in {"approval_gated", "operator_gated", "permission_needed", "deferred", "blocked", "human_operated"}:
        return str(status)
    if source_eval.get("status") == "blocked" or requirement_eval.get("status") == "blocked":
        return "blocked"
    if capability_eval.get("status") == "blocked" or mode_eval.get("status") == "blocked":
        return "approval_gated"
    if validation_errors:
        return "fail"
    return "pass"


def _dry_run_warnings(
    workunit: Mapping[str, Any],
    mode_eval: Mapping[str, Any],
    capability_eval: Mapping[str, Any],
    source_eval: Mapping[str, Any],
    requirement_eval: Mapping[str, Any],
    actions: Mapping[str, list[Mapping[str, Any]]],
) -> list[str]:
    warnings: list[str] = []
    if mode_eval.get("future_or_blocked_modes"):
        warnings.append("Required node mode is future/deferred and was not activated.")
    if capability_eval.get("blocked_capabilities"):
        warnings.append("Required capability is gated, deferred, future, or policy-blocked.")
    if source_eval.get("status") == "blocked":
        warnings.append("Source access requirement was blocked by dry-run policy.")
    if requirement_eval.get("blocked_sections"):
        warnings.append("Network/model/credential/local-state requirement was blocked by dry-run policy.")
    if actions.get("skipped_actions"):
        warnings.append("Future actions were deferred and not executed.")
    if workunit.get("workunit_status") in {"approval_gated", "operator_gated", "permission_needed", "deferred", "blocked", "human_operated"}:
        warnings.append("WorkUnit status is gated or deferred; dry-run report remains review-only.")
    return sorted(set(warnings))


def _inputs_observed(workunit: Mapping[str, Any]) -> list[dict[str, Any]]:
    inputs: list[dict[str, Any]] = []
    for item in _sequence(workunit.get("input_refs")):
        record = _mapping(item)
        inputs.append(
            {
                "input_id": record.get("input_id", "input"),
                "input_type": record.get("input_type", "repo_local_fixture"),
                "input_ref": record.get("input_ref"),
                "input_status": _map_input_status(record.get("input_status")),
                "input_public_safe": record.get("input_public_safe") is not False,
                "input_used": record.get("input_required") is not False,
                "input_limitations": list(_string_items(record.get("input_limitations"))),
                "notes": list(_string_items(record.get("notes"))),
            }
        )
    if not inputs:
        inputs.append(
            {
                "input_id": "source_workunit",
                "input_type": "repo_local_fixture",
                "input_ref": workunit.get("workunit_id"),
                "input_status": "used",
                "input_public_safe": True,
                "input_used": True,
                "input_limitations": ["Dry-run used only the explicit WorkUnit JSON input."],
                "notes": [],
            }
        )
    return inputs


def _outputs_proposed(workunit: Mapping[str, Any], status: str) -> list[dict[str, Any]]:
    outputs: list[dict[str, Any]] = []
    for item in _sequence(workunit.get("expected_outputs")):
        record = _mapping(item)
        output_type = record.get("output_type")
        if output_type in FORBIDDEN_OUTPUT_TYPES:
            continue
        output_status = "needs_review" if output_type in REVIEW_REQUIRED_OUTPUTS else "proposed"
        if status in {"noop", "skipped", "deferred"}:
            output_status = "not_created" if status == "noop" else "deferred"
        outputs.append(
            {
                "output_id": record.get("output_id", f"dry_run_output_{len(outputs) + 1}"),
                "output_type": output_type,
                "output_status": output_status,
                "output_contract_ref": record.get("output_contract_ref", "contracts/node/work_unit_result.v0.json"),
                "output_ref": None,
                "output_summary": f"Dry-run proposed {output_type}; no artifact was created.",
                "output_public_safe": record.get("output_public_safe") is not False,
                "output_requires_review": True,
                "output_truth_boundary": {
                    "accepted_public_truth": False,
                    "accepted_evidence_truth": False,
                    "master_index_mutation": False,
                },
                "output_limitations": list(_string_items(record.get("output_limitations"))) + ["Dry-run output is not accepted truth."],
                "notes": list(_string_items(record.get("notes"))),
            }
        )
    if not outputs:
        outputs.append(
            {
                "output_id": "dry_run_report",
                "output_type": "dry_run_report",
                "output_status": "validated" if status == "pass" else "needs_review",
                "output_contract_ref": "contracts/node/work_unit_result.v0.json",
                "output_ref": None,
                "output_summary": "Dry-run WorkUnitResult envelope.",
                "output_public_safe": True,
                "output_requires_review": True,
                "output_truth_boundary": {
                    "accepted_public_truth": False,
                    "accepted_evidence_truth": False,
                    "master_index_mutation": False,
                },
                "output_limitations": ["Report-only dry-run output."],
                "notes": [],
            }
        )
    return outputs


def _outputs_rejected(workunit: Mapping[str, Any], status: str) -> list[dict[str, Any]]:
    outputs: list[dict[str, Any]] = []
    for output_type in _string_items(workunit.get("forbidden_outputs")):
        outputs.append(
            {
                "output_id": f"reject_{_slug(output_type)}",
                "output_type": output_type if output_type in ALLOWED_OUTPUT_TYPES else "workunit_report",
                "output_status": "rejected",
                "output_contract_ref": "contracts/node/work_unit_result.v0.json",
                "output_ref": None,
                "output_summary": f"Forbidden output {output_type} was rejected by dry-run policy.",
                "output_public_safe": True,
                "output_requires_review": True,
                "output_truth_boundary": {
                    "accepted_public_truth": False,
                    "accepted_evidence_truth": False,
                    "master_index_mutation": False,
                },
                "output_limitations": ["Rejected output was not created."],
                "notes": [],
            }
        )
    return outputs


def _output_contract_refs(workunit: Mapping[str, Any]) -> list[str]:
    refs = {"contracts/node/work_unit_result.v0.json"}
    refs.update(_string_items(workunit.get("output_contract_refs")))
    return sorted(refs)


def _review_gates(workunit: Mapping[str, Any]) -> dict[str, bool]:
    source = _mapping(workunit.get("review_gates"))
    gates = {field: True for field in sorted(REQUIRED_REVIEW_GATES)}
    for field, value in source.items():
        if field in gates:
            gates[field] = value is not False
    return gates


def _idempotency_result(status: str) -> dict[str, Any]:
    return {
        "safe_to_rerun": True,
        "duplicate_detected": status == "noop",
        "duplicate_behavior_applied": "validate_and_record_noop" if status == "noop" else "not_applicable",
        "noop_recorded": status == "noop",
        "resume_required": status == "partial",
        "conflict_detected": status == "fail",
    }


def _recovery_result(status: str) -> dict[str, str]:
    if status == "fail":
        failed = "repair_if_in_scope_else_record_blocker"
    elif status in {"blocked", "policy_blocked", "approval_gated", "operator_gated", "permission_needed"}:
        failed = "repair_if_bounded_else_record_blocker"
    else:
        failed = "not_applicable"
    return {
        "dirty_tree_handled": "not_applicable",
        "missing_dependency_handled": "not_applicable",
        "stale_status_reconciled": "not_applicable",
        "failed_validation_handled": failed,
        "out_of_order_task_handled": "not_applicable",
        "repeated_prompt_handled": "classify_noop_resume_or_repair" if status == "noop" else "not_applicable",
    }


def _truth_boundary() -> dict[str, bool]:
    return {field: False for field in sorted(TRUTH_BOUNDARY_FALSE_FIELDS)}


def _product_boundary() -> dict[str, bool]:
    return {field: False for field in sorted(PRODUCT_BOUNDARY_FALSE_FIELDS)}


def _execution_summary_text(status: str) -> str:
    if status == "noop":
        return "Dry-run validated an already-satisfied WorkUnit fixture without changes."
    if status in {"blocked", "policy_blocked", "approval_gated", "operator_gated", "permission_needed"}:
        return "Dry-run stopped at a policy, approval, source, capability, or runtime boundary."
    if status == "fail":
        return "Dry-run validation failed before any action could be simulated."
    return "Dry-run simulated allowed actions and produced a review-gated result envelope."


def _action_record(
    action_id: str,
    action_type: str,
    action_status: str,
    action_scope: str,
    allowed_by_policy: bool,
    blocked_by_policy: bool,
    reason: str,
) -> dict[str, Any]:
    return {
        "action_id": action_id,
        "action_type": action_type,
        "action_status": action_status,
        "action_scope": action_scope,
        "allowed_by_policy": allowed_by_policy,
        "blocked_by_policy": blocked_by_policy,
        "reason": reason,
        "output_refs": [],
        "validation_refs": ["workunit_dry_run"],
        "notes": [],
    }


def _map_input_status(status: Any) -> str:
    mapping = {
        "committed": "used",
        "pending": "used",
        "proposed": "used",
        "policy_blocked": "blocked",
        "future_policy_required": "future",
        "review_required": "deferred",
    }
    if isinstance(status, str) and status in {"used", "not_used", "missing", "unavailable", "blocked", "invalid", "future", "deferred"}:
        return status
    return mapping.get(str(status), "used")


def _node_id_from_ref(ref: str | None) -> str:
    if not ref:
        return "local_foundry_dry_run"
    parts = Path(ref).parts
    if len(parts) >= 2:
        return parts[-2]
    return Path(ref).stem


def _is_future_action(action: str) -> bool:
    return action.endswith("_future") or "_future" in action


def _slug(value: str) -> str:
    return "".join(char if char.isalnum() else "_" for char in value.lower()).strip("_")[:48] or "item"


def _stable_digest(record: Mapping[str, Any]) -> str:
    payload = json.dumps(record, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _record_text(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, Mapping):
        return " ".join(_record_text(child) for child in value.values())
    if isinstance(value, Iterable) and not isinstance(value, (bytes, bytearray)):
        return " ".join(_record_text(child) for child in value)
    return ""


def _sequence(value: Any) -> list[Any]:
    return list(value) if isinstance(value, list) else []


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _string_items(value: Any) -> list[str]:
    return [item for item in _sequence(value) if isinstance(item, str)]


def _first_string(value: Any) -> str | None:
    for item in _string_items(value):
        return item
    return None
