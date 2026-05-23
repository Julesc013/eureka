"""Validate Track B Eureka WorkUnit result governance artifacts.

The validator is deterministic and read-only. It checks declarative result
envelopes and registries without running WorkUnits, creating node state,
calling sources, or granting runtime permission.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.validate_eureka_workunit import ALLOWED_TYPES as WORKUNIT_TYPES
from scripts.validate_eureka_workunit import FORBIDDEN_INPUTS as WORKUNIT_FORBIDDEN_INPUTS
from scripts.validate_eureka_workunit import FORBIDDEN_ACTIONS


REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = "contracts/schema/control/policies/node/work_unit_result.v0.json"
RESULT_POLICY_PATH = "control/inventory/nodes/workunit_result_policy.json"
STATUS_REGISTRY_PATH = "control/inventory/nodes/workunit_result_status_registry.json"
OUTPUT_POLICY_PATH = "control/inventory/nodes/workunit_result_output_policy.json"
REVIEW_POLICY_PATH = "control/inventory/nodes/workunit_result_review_policy.json"
RECOVERY_POLICY_PATH = "control/inventory/nodes/workunit_result_recovery_policy.json"
WORKUNIT_TYPE_REGISTRY_PATH = "control/inventory/nodes/workunit_type_registry.json"
AUDIT_REPORT_PATH = "control/audits/track-b-05-workunit-result-contract-v0/track_b_05_report.json"
EXAMPLE_ROOT = "examples/work_units/results"
DOC_PATHS = (
    "docs/reference/WORKUNIT_RESULT_CONTRACT.md",
    "docs/architecture/WORKUNIT_RESULT_MODEL.md",
    "docs/operations/WORKUNIT_RESULT_REVIEW.md",
)

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
CURRENT_EXECUTION_MODES = {
    "contract_only",
    "validate_only",
    "dry_run_only",
    "report_only",
    "repo_local_only",
    "human_operated",
    "blocked",
}
FUTURE_OR_BLOCKED_STATUSES = {
    "blocked",
    "deferred",
    "policy_blocked",
    "rights_blocked",
    "risk_blocked",
    "permission_needed",
    "operator_gated",
    "approval_gated",
    "not_evaluable",
}
ACTION_STATUSES = {
    "planned",
    "executed",
    "skipped",
    "blocked",
    "forbidden_checked",
    "not_applicable",
    "deferred",
    "failed",
}
INPUT_STATUSES = {
    "used",
    "not_used",
    "missing",
    "unavailable",
    "blocked",
    "invalid",
    "future",
    "deferred",
}
ALLOWED_INPUTS = {
    "repo_local_fixture",
    "committed_pack_example",
    "committed_static_artifact",
    "committed_eval_report",
    "committed_audit_report",
    "committed_public_data_summary",
    "manual_pending_slot",
    "observation_candidate",
    "observation_review_decision",
    "source_lead_candidate",
    "node_manifest",
    "node_policy",
    "node_capability",
    "search_need_seed_future",
    "candidate_record_future",
    "evidence_record_future",
    "source_policy_future",
    "local_private_state_future",
}
ALLOWED_OUTPUTS = {
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
FORBIDDEN_OUTPUTS = {
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
OUTPUT_STATUSES = {
    "proposed",
    "drafted",
    "validated",
    "needs_review",
    "rejected",
    "blocked",
    "duplicate",
    "deferred",
    "future",
    "not_created",
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
VALIDATION_STATUSES = {
    "pass",
    "pass_with_warnings",
    "warn",
    "fail",
    "not_run",
    "not_applicable",
}
REVIEW_GATES = {
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
TRUTH_FALSE_FIELDS = {
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
PRODUCT_BOUNDARY_FIELDS = {
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
DUPLICATE_BEHAVIORS = {
    "validate_and_record_noop",
    "resume_from_missing_acceptance",
    "classify_and_quarantine",
    "not_applicable",
}
RECOVERY_BEHAVIORS = {
    "inspect_preserve_and_continue",
    "repair_if_bounded_else_record_blocker",
    "reconcile_from_evidence",
    "repair_if_in_scope_else_record_blocker",
    "inspect_queue_and_resume_valid_next",
    "classify_noop_resume_or_repair",
    "not_applicable",
}
IDEMPOTENCY_FIELDS = {
    "safe_to_rerun",
    "duplicate_detected",
    "duplicate_behavior_applied",
    "noop_recorded",
    "resume_required",
    "conflict_detected",
}
RECOVERY_FIELDS = {
    "dirty_tree_handled",
    "missing_dependency_handled",
    "stale_status_reconciled",
    "failed_validation_handled",
    "out_of_order_task_handled",
    "repeated_prompt_handled",
}
SENSITIVE_KEY_NAMES = {"api_key", "password", "secret", "token"}
PRIVATE_PATH_MARKERS = ("c:\\", "\\users\\", "/users/", "/home/")
FORBIDDEN_TEXT_CLAIMS = (
    "production ready",
    "production-ready",
    "rights clearance confirmed",
    "rights cleared",
    "malware safe",
    "malware-safe",
    "verified installability",
    "verified installable",
    "exhaustive global search proof",
)


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Eureka WorkUnit result contract files.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help="Repository root to validate.")
    parser.add_argument("--json", action="store_true", help="Emit deterministic JSON.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_eureka_workunit_result(Path(args.repo_root))
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


def validate_eureka_workunit_result(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    root = repo_root.resolve()
    errors: list[str] = []
    warnings: list[str] = []

    schema = _load_json(root / SCHEMA_PATH, errors, root)
    result_policy = _load_json(root / RESULT_POLICY_PATH, errors, root)
    status_registry = _load_json(root / STATUS_REGISTRY_PATH, errors, root)
    output_policy = _load_json(root / OUTPUT_POLICY_PATH, errors, root)
    review_policy = _load_json(root / REVIEW_POLICY_PATH, errors, root)
    recovery_policy = _load_json(root / RECOVERY_POLICY_PATH, errors, root)
    type_registry = _load_json(root / WORKUNIT_TYPE_REGISTRY_PATH, errors, root)
    audit_report = _load_json(root / AUDIT_REPORT_PATH, errors, root)

    workunit_types = set(_string_items(_mapping(type_registry).get("allowed_types"))) or WORKUNIT_TYPES

    errors.extend(validate_docs(root))
    errors.extend(validate_schema(schema, SCHEMA_PATH))
    errors.extend(validate_workunit_result_policy(result_policy, RESULT_POLICY_PATH))
    errors.extend(validate_status_registry(status_registry, STATUS_REGISTRY_PATH))
    errors.extend(validate_output_policy(output_policy, OUTPUT_POLICY_PATH))
    errors.extend(validate_review_policy(review_policy, REVIEW_POLICY_PATH))
    errors.extend(validate_recovery_policy(recovery_policy, RECOVERY_POLICY_PATH))
    errors.extend(validate_audit_report(audit_report, AUDIT_REPORT_PATH))

    example_paths = list_example_result_paths(root)
    if len(example_paths) != 6:
        errors.append(f"{EXAMPLE_ROOT}: expected 6 WorkUnitResult examples, found {len(example_paths)}")
    seen_ids: set[str] = set()
    for path in example_paths:
        payload = _load_json(path, errors, root)
        source = _relative(root, path)
        result_id = _mapping(payload).get("workunit_result_id")
        if isinstance(result_id, str):
            if result_id in seen_ids:
                errors.append(f"{source}: duplicate workunit_result_id {result_id}")
            seen_ids.add(result_id)
        errors.extend(validate_workunit_result_record(payload, source, repo_root=root, workunit_types=workunit_types))

    return {
        "schema_version": "eureka_workunit_result_validation.v0",
        "status": "valid" if not errors else "invalid",
        "validated_files": sorted(
            [
                SCHEMA_PATH,
                RESULT_POLICY_PATH,
                STATUS_REGISTRY_PATH,
                OUTPUT_POLICY_PATH,
                REVIEW_POLICY_PATH,
                RECOVERY_POLICY_PATH,
                WORKUNIT_TYPE_REGISTRY_PATH,
                AUDIT_REPORT_PATH,
                *DOC_PATHS,
                *[_relative(root, path) for path in example_paths],
            ]
        ),
        "errors": sorted(set(errors)),
        "warnings": sorted(set(warnings)),
    }


def list_example_result_paths(repo_root: Path = REPO_ROOT) -> list[Path]:
    return sorted((repo_root.resolve() / EXAMPLE_ROOT).glob("*/work_unit_result.json"))


def validate_docs(repo_root: Path) -> list[str]:
    errors: list[str] = []
    for path in DOC_PATHS:
        full_path = repo_root / path
        if not full_path.is_file():
            errors.append(f"docs: missing {path}")
            continue
        text = full_path.read_text(encoding="utf-8").lower()
        for phrase in ("workunit result", "review", "noop", "master-index"):
            if phrase not in text:
                errors.append(f"{path}: missing required phrase {phrase!r}")
    return errors


def validate_schema(payload: Any, source: str) -> list[str]:
    data = _mapping(payload)
    errors: list[str] = []
    if data.get("title") != "EurekaWorkUnitResultV0":
        errors.append(f"{source}: title must be EurekaWorkUnitResultV0")
    properties = _mapping(data.get("properties"))
    schema_version = _mapping(properties.get("schema_version"))
    if schema_version.get("const") != "work_unit_result.v0":
        errors.append(f"{source}: schema_version const must be work_unit_result.v0")
    errors.extend(_missing_items(data.get("required"), _required_fields(), f"{source}: required"))
    for key in (
        "x-workunit-result-is-public-truth",
        "x-workunit-runtime-implemented",
        "x-node-runtime-implemented",
        "x-network-access-enabled",
        "x-model-provider-calls-enabled",
        "x-local-state-created",
        "x-master-index-mutation-allowed",
    ):
        if data.get(key) is not False:
            errors.append(f"{source}: {key} must be false")
    return errors


def validate_workunit_result_policy(payload: Any, source: str) -> list[str]:
    data = _mapping(payload)
    errors: list[str] = []
    if data.get("schema_version") != "workunit_result_policy.v0":
        errors.append(f"{source}: schema_version must be workunit_result_policy.v0")
    errors.extend(_missing_items(data.get("required_fields"), _required_fields(), f"{source}: required_fields"))
    errors.extend(_missing_items(data.get("required_false_truth_booleans"), TRUTH_FALSE_FIELDS, f"{source}: required_false_truth_booleans"))
    errors.extend(_missing_items(data.get("product_boundary_false_fields"), PRODUCT_BOUNDARY_FIELDS, f"{source}: product_boundary_false_fields"))
    errors.extend(_boundary_false_errors(_mapping(data.get("product_boundary")), source))
    return errors


def validate_status_registry(payload: Any, source: str) -> list[str]:
    data = _mapping(payload)
    errors: list[str] = []
    if data.get("schema_version") != "workunit_result_status_registry.v0":
        errors.append(f"{source}: schema_version must be workunit_result_status_registry.v0")
    errors.extend(_missing_items(data.get("allowed_result_statuses"), ALLOWED_RESULT_STATUSES, f"{source}: allowed_result_statuses"))
    errors.extend(_missing_items(data.get("allowed_execution_modes"), ALLOWED_EXECUTION_MODES, f"{source}: allowed_execution_modes"))
    errors.extend(_missing_items(data.get("current_allowed_execution_modes"), CURRENT_EXECUTION_MODES, f"{source}: current_allowed_execution_modes"))
    errors.extend(_missing_items(data.get("allowed_action_statuses"), ACTION_STATUSES, f"{source}: allowed_action_statuses"))
    errors.extend(_missing_items(data.get("allowed_input_statuses"), INPUT_STATUSES, f"{source}: allowed_input_statuses"))
    errors.extend(_missing_items(data.get("validation_statuses"), VALIDATION_STATUSES, f"{source}: validation_statuses"))
    errors.extend(_boundary_false_errors(_mapping(data.get("product_boundary")), source))
    return errors


def validate_output_policy(payload: Any, source: str) -> list[str]:
    data = _mapping(payload)
    errors: list[str] = []
    if data.get("schema_version") != "workunit_result_output_policy.v0":
        errors.append(f"{source}: schema_version must be workunit_result_output_policy.v0")
    errors.extend(_missing_items(data.get("allowed_output_types"), ALLOWED_OUTPUTS, f"{source}: allowed_output_types"))
    errors.extend(_missing_items(data.get("forbidden_output_types"), FORBIDDEN_OUTPUTS, f"{source}: forbidden_output_types"))
    errors.extend(_missing_items(data.get("allowed_output_statuses"), OUTPUT_STATUSES, f"{source}: allowed_output_statuses"))
    errors.extend(_missing_items(data.get("review_required_output_types"), REVIEW_REQUIRED_OUTPUTS, f"{source}: review_required_output_types"))
    errors.extend(_boundary_false_errors(_mapping(data.get("product_boundary")), source))
    return errors


def validate_review_policy(payload: Any, source: str) -> list[str]:
    data = _mapping(payload)
    errors: list[str] = []
    if data.get("schema_version") != "workunit_result_review_policy.v0":
        errors.append(f"{source}: schema_version must be workunit_result_review_policy.v0")
    errors.extend(_missing_items(data.get("required_review_gates"), REVIEW_GATES, f"{source}: required_review_gates"))
    errors.extend(_boundary_false_errors(_mapping(data.get("product_boundary")), source))
    return errors


def validate_recovery_policy(payload: Any, source: str) -> list[str]:
    data = _mapping(payload)
    errors: list[str] = []
    if data.get("schema_version") != "workunit_result_recovery_policy.v0":
        errors.append(f"{source}: schema_version must be workunit_result_recovery_policy.v0")
    errors.extend(_missing_items(data.get("required_idempotency_result_fields"), IDEMPOTENCY_FIELDS, f"{source}: required_idempotency_result_fields"))
    errors.extend(_missing_items(data.get("required_recovery_result_fields"), RECOVERY_FIELDS, f"{source}: required_recovery_result_fields"))
    errors.extend(_missing_items(data.get("duplicate_behavior_values"), DUPLICATE_BEHAVIORS, f"{source}: duplicate_behavior_values"))
    errors.extend(_missing_items(data.get("recovery_behavior_values"), RECOVERY_BEHAVIORS, f"{source}: recovery_behavior_values"))
    errors.extend(_boundary_false_errors(_mapping(data.get("product_boundary")), source))
    return errors


def validate_audit_report(payload: Any, source: str) -> list[str]:
    data = _mapping(payload)
    errors: list[str] = []
    if data.get("schema_version") != "track_b_05_report.v0":
        errors.append(f"{source}: schema_version must be track_b_05_report.v0")
    if data.get("task") != "TRACK-B-05":
        errors.append(f"{source}: task must be TRACK-B-05")
    errors.extend(_boundary_false_errors(_mapping(data.get("product_boundary")), source))
    truth = _mapping(data.get("truth_boundary"))
    for field in (
        "workunit_result_is_public_truth",
        "workunit_result_is_accepted_evidence",
        "workunit_result_can_mutate_master_index",
    ):
        if truth.get(field) is not False:
            errors.append(f"{source}: truth_boundary.{field} must be false")
    if truth.get("human_review_required_for_truth") is not True:
        errors.append(f"{source}: truth_boundary.human_review_required_for_truth must be true")
    return errors


def validate_workunit_result_record(
    payload: Any,
    source: str,
    *,
    repo_root: Path = REPO_ROOT,
    workunit_types: set[str] | None = None,
) -> list[str]:
    data = _mapping(payload)
    errors: list[str] = []
    if data.get("schema_version") != "work_unit_result.v0":
        errors.append(f"{source}: schema_version must be work_unit_result.v0")
    errors.extend(_missing_items(data, _required_fields(), f"{source}: top-level"))

    status = str(data.get("workunit_result_status", ""))
    execution_mode = str(data.get("execution_mode", ""))
    workunit_type = str(data.get("workunit_type", ""))
    if status not in ALLOWED_RESULT_STATUSES:
        errors.append(f"{source}: workunit_result_status {status!r} is not allowed")
    if execution_mode not in ALLOWED_EXECUTION_MODES:
        errors.append(f"{source}: execution_mode {execution_mode!r} is not allowed")
    if execution_mode not in CURRENT_EXECUTION_MODES and status not in FUTURE_OR_BLOCKED_STATUSES:
        errors.append(f"{source}: future execution_mode {execution_mode!r} requires future/blocked/gated result status")
    if workunit_type not in (workunit_types or WORKUNIT_TYPES):
        errors.append(f"{source}: workunit_type {workunit_type!r} is not known")

    for ref in _string_items([data.get("source_workunit_ref"), data.get("node_manifest_ref"), data.get("node_policy_ref")]) + _string_items(data.get("output_contract_refs")):
        if not (repo_root / ref).is_file():
            errors.append(f"{source}: referenced file does not exist: {ref}")

    errors.extend(_validate_execution_summary(_mapping(data.get("execution_summary")), source))
    errors.extend(_validate_validation_summary(_mapping(data.get("validation_summary")), source))
    for section in ("planned_actions", "executed_actions", "skipped_actions", "blocked_actions", "forbidden_actions_checked"):
        for item in _sequence(data.get(section)):
            errors.extend(_validate_action_record(_mapping(item), source, section))
    for item in _sequence(data.get("forbidden_actions_checked")):
        if _mapping(item).get("action_status") == "executed":
            errors.append(f"{source}: forbidden action cannot be executed")
    for item in _sequence(data.get("inputs_observed")):
        errors.extend(_validate_input_record(_mapping(item), source))
    for item in _sequence(data.get("outputs_proposed")) + _sequence(data.get("outputs_rejected")):
        errors.extend(_validate_output_record(_mapping(item), source, _mapping(data.get("review_gates"))))

    errors.extend(_validate_review_gates(_mapping(data.get("review_gates")), source))
    errors.extend(_validate_idempotency_result(_mapping(data.get("idempotency_result")), source))
    errors.extend(_validate_recovery_result(_mapping(data.get("recovery_result")), source))
    errors.extend(_validate_noop_quarantine(data, source))
    errors.extend(_false_field_errors(_mapping(data.get("truth_boundary")), TRUTH_FALSE_FIELDS, f"{source}: truth_boundary"))
    errors.extend(_boundary_false_errors(_mapping(data.get("product_boundary")), source))
    errors.extend(_sensitive_key_errors(data, source))
    errors.extend(_private_path_errors(data, source))
    errors.extend(_forbidden_text_claim_errors(data, source))
    return errors


def _validate_execution_summary(payload: Mapping[str, Any], source: str) -> list[str]:
    errors: list[str] = []
    for field in ("runtime_used", "network_used", "model_provider_used", "local_state_created"):
        if payload.get(field) is not False:
            errors.append(f"{source}: execution_summary.{field} must be false")
    return errors


def _validate_validation_summary(payload: Mapping[str, Any], source: str) -> list[str]:
    errors: list[str] = []
    status = payload.get("validation_status")
    if status not in VALIDATION_STATUSES:
        errors.append(f"{source}: validation_summary.validation_status {status!r} is not allowed")
    errors_count = payload.get("errors_count")
    warnings_count = payload.get("warnings_count")
    if not isinstance(errors_count, int) or errors_count < 0:
        errors.append(f"{source}: validation_summary.errors_count must be a nonnegative integer")
    if not isinstance(warnings_count, int) or warnings_count < 0:
        errors.append(f"{source}: validation_summary.warnings_count must be a nonnegative integer")
    if status == "pass_with_warnings" and errors_count != 0:
        errors.append(f"{source}: pass_with_warnings requires errors_count 0")
    if status == "pass_with_warnings" and warnings_count < 1:
        errors.append(f"{source}: pass_with_warnings requires documented warnings")
    return errors


def _validate_action_record(record: Mapping[str, Any], source: str, section: str) -> list[str]:
    errors: list[str] = []
    action_status = record.get("action_status")
    if action_status not in ACTION_STATUSES:
        errors.append(f"{source}: {section} action_status {action_status!r} is not allowed")
    action_type = record.get("action_type")
    if action_type in FORBIDDEN_ACTIONS and action_status != "forbidden_checked":
        errors.append(f"{source}: {section} forbidden action {action_type!r} must only be forbidden_checked")
    if section == "forbidden_actions_checked" and action_status != "forbidden_checked":
        errors.append(f"{source}: forbidden_actions_checked action_status must be forbidden_checked")
    return errors


def _validate_input_record(record: Mapping[str, Any], source: str) -> list[str]:
    errors: list[str] = []
    input_type = record.get("input_type")
    input_status = record.get("input_status")
    if input_type not in ALLOWED_INPUTS:
        errors.append(f"{source}: inputs_observed input_type {input_type!r} is not allowed")
    if input_type in WORKUNIT_FORBIDDEN_INPUTS:
        errors.append(f"{source}: inputs_observed uses forbidden input_type {input_type!r}")
    if input_status not in INPUT_STATUSES:
        errors.append(f"{source}: inputs_observed input_status {input_status!r} is not allowed")
    return errors


def _validate_output_record(record: Mapping[str, Any], source: str, review_gates: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    output_type = record.get("output_type")
    output_status = record.get("output_status")
    if output_type in FORBIDDEN_OUTPUTS:
        errors.append(f"{source}: output_type {output_type!r} is forbidden")
    elif output_type not in ALLOWED_OUTPUTS:
        errors.append(f"{source}: output_type {output_type!r} is not allowed")
    if output_status not in OUTPUT_STATUSES:
        errors.append(f"{source}: output_status {output_status!r} is not allowed")
    if output_type in REVIEW_REQUIRED_OUTPUTS and record.get("output_requires_review") is not True:
        errors.append(f"{source}: output {record.get('output_id', '<unknown>')} requires review")
    if output_type in REVIEW_REQUIRED_OUTPUTS and review_gates.get("human_review_required") is not True:
        errors.append(f"{source}: output {record.get('output_id', '<unknown>')} requires human_review_required gate")
    if output_type == "source_lead_candidate" and review_gates.get("source_policy_review_required") is not True:
        errors.append(f"{source}: source lead output requires source_policy_review_required gate")
    if output_type == "evidence_draft_future" and review_gates.get("evidence_review_required") is not True:
        errors.append(f"{source}: evidence output requires evidence_review_required gate")
    if output_type in {"observation_candidate", "observation_candidate_summary", "candidate_record_future"} and review_gates.get("candidate_review_required") is not True:
        errors.append(f"{source}: candidate output requires candidate_review_required gate")
    errors.extend(_false_field_errors(_mapping(record.get("output_truth_boundary")), {"accepted_public_truth", "accepted_evidence_truth", "master_index_mutation"}, f"{source}: output {record.get('output_id', '<unknown>')}.output_truth_boundary"))
    return errors


def _validate_review_gates(payload: Mapping[str, Any], source: str) -> list[str]:
    errors: list[str] = []
    errors.extend(_missing_items(payload, REVIEW_GATES, f"{source}: review_gates"))
    return errors


def _validate_idempotency_result(payload: Mapping[str, Any], source: str) -> list[str]:
    errors: list[str] = []
    errors.extend(_missing_items(payload, IDEMPOTENCY_FIELDS, f"{source}: idempotency_result"))
    if payload.get("safe_to_rerun") is not True:
        errors.append(f"{source}: idempotency_result.safe_to_rerun must be true")
    if payload.get("duplicate_behavior_applied") not in DUPLICATE_BEHAVIORS:
        errors.append(f"{source}: idempotency_result.duplicate_behavior_applied is not allowed")
    return errors


def _validate_recovery_result(payload: Mapping[str, Any], source: str) -> list[str]:
    errors: list[str] = []
    errors.extend(_missing_items(payload, RECOVERY_FIELDS, f"{source}: recovery_result"))
    for field in RECOVERY_FIELDS:
        if field in payload and payload.get(field) not in RECOVERY_BEHAVIORS:
            errors.append(f"{source}: recovery_result.{field} is not allowed")
    return errors


def _validate_noop_quarantine(data: Mapping[str, Any], source: str) -> list[str]:
    errors: list[str] = []
    noop = _mapping(data.get("noop_result"))
    quarantine = _mapping(data.get("quarantine_result"))
    if data.get("workunit_result_status") == "noop" and noop.get("noop_recorded") is not True:
        errors.append(f"{source}: noop status requires noop_result.noop_recorded true")
    if _mapping(data.get("idempotency_result")).get("conflict_detected") is True and quarantine.get("quarantined") is not True:
        errors.append(f"{source}: conflict result requires quarantine_result.quarantined true")
    return errors


def _format_plain(report: Mapping[str, Any]) -> str:
    lines = [f"validate_eureka_workunit_result: {report['status']}"]
    lines.append(f"schema_version: {report['schema_version']}")
    lines.append(f"validated_files: {len(report.get('validated_files', []))}")
    errors = report.get("errors", [])
    if errors:
        lines.append("errors:")
        lines.extend(f"- {error}" for error in errors)
    warnings = report.get("warnings", [])
    if warnings:
        lines.append("warnings:")
        lines.extend(f"- {warning}" for warning in warnings)
    return "\n".join(lines) + "\n"


def _load_json(path: Path, errors: list[str], repo_root: Path) -> Any:
    if not path.is_file():
        errors.append(f"{_relative(repo_root, path)}: missing file")
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"{_relative(repo_root, path)}: invalid JSON: {exc}")
        return None


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _sequence(value: Any) -> list[Any]:
    return list(value) if isinstance(value, list) else []


def _string_items(value: Any) -> list[str]:
    return [item for item in value if isinstance(item, str)] if isinstance(value, list) else []


def _missing_items(value: Any, required: set[str], label: str) -> list[str]:
    if isinstance(value, Mapping):
        present = set(str(key) for key in value)
    elif isinstance(value, set):
        present = set(value)
    else:
        present = set(_string_items(value))
    return [f"{label} missing {item}" for item in sorted(required - present)]


def _boundary_false_errors(payload: Mapping[str, Any], source: str) -> list[str]:
    return _false_field_errors(payload, PRODUCT_BOUNDARY_FIELDS, f"{source}: product_boundary")


def _false_field_errors(payload: Mapping[str, Any], fields: set[str], label: str) -> list[str]:
    errors: list[str] = []
    for field in sorted(fields):
        if payload.get(field) is not False:
            errors.append(f"{label}.{field} must be false")
    return errors


def _sensitive_key_errors(value: Any, source: str, path: str = "$") -> list[str]:
    errors: list[str] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key).lower()
            if key_text in SENSITIVE_KEY_NAMES:
                errors.append(f"{source}: sensitive key {path}.{key_text} is not allowed")
            errors.extend(_sensitive_key_errors(child, source, f"{path}.{key_text}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            errors.extend(_sensitive_key_errors(child, source, f"{path}[{index}]"))
    return errors


def _private_path_errors(value: Any, source: str, path: str = "$") -> list[str]:
    errors: list[str] = []
    if isinstance(value, str):
        lowered = value.lower()
        if any(marker in lowered for marker in PRIVATE_PATH_MARKERS):
            errors.append(f"{source}: private/local user path marker at {path}")
    elif isinstance(value, Mapping):
        for key, child in value.items():
            errors.extend(_private_path_errors(child, source, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            errors.extend(_private_path_errors(child, source, f"{path}[{index}]"))
    return errors


def _forbidden_text_claim_errors(value: Any, source: str, path: str = "$") -> list[str]:
    errors: list[str] = []
    if isinstance(value, str):
        lowered = value.lower()
        for marker in FORBIDDEN_TEXT_CLAIMS:
            if marker in lowered:
                errors.append(f"{source}: forbidden product claim marker {marker!r} at {path}")
    elif isinstance(value, Mapping):
        for key, child in value.items():
            errors.extend(_forbidden_text_claim_errors(child, source, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            errors.extend(_forbidden_text_claim_errors(child, source, f"{path}[{index}]"))
    return errors


def _required_fields() -> set[str]:
    return {
        "schema_version",
        "workunit_result_id",
        "workunit_result_label",
        "workunit_id",
        "workunit_type",
        "workunit_result_status",
        "result_scope",
        "produced_by",
        "produced_at_note",
        "source_workunit_ref",
        "node_manifest_ref",
        "node_policy_ref",
        "node_capability_refs",
        "execution_mode",
        "execution_summary",
        "validation_summary",
        "planned_actions",
        "executed_actions",
        "skipped_actions",
        "blocked_actions",
        "forbidden_actions_checked",
        "inputs_observed",
        "outputs_proposed",
        "outputs_rejected",
        "output_contract_refs",
        "review_gates",
        "idempotency_result",
        "recovery_result",
        "duplicate_result",
        "out_of_order_result",
        "noop_result",
        "quarantine_result",
        "warnings",
        "errors",
        "limitations",
        "audit_refs",
        "truth_boundary",
        "product_boundary",
        "no_goals",
        "notes",
    }


def _relative(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
