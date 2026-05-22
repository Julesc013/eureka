"""Validate Track B Eureka WorkUnit governance artifacts.

The validator is deterministic and read-only. It checks declarative WorkUnit
records and registries without running WorkUnits, creating node state, calling
sources, or granting runtime permission.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = "contracts/control_schemas/policies/node/work_unit.v0.json"
TYPE_REGISTRY_PATH = "control/inventory/nodes/workunit_type_registry.json"
WORKUNIT_POLICY_PATH = "control/inventory/nodes/workunit_policy.json"
IDEMPOTENCY_POLICY_PATH = "control/inventory/nodes/workunit_idempotency_policy.json"
ACTION_POLICY_PATH = "control/inventory/nodes/workunit_action_policy.json"
INPUT_OUTPUT_POLICY_PATH = "control/inventory/nodes/workunit_input_output_policy.json"
REVIEW_GATE_POLICY_PATH = "control/inventory/nodes/workunit_review_gate_policy.json"
NODE_MODE_REGISTRY_PATH = "control/inventory/nodes/node_mode_registry.json"
NODE_CAPABILITY_MATRIX_PATH = "control/inventory/nodes/node_capability_matrix.json"
NODE_CAPABILITY_REGISTRY_PATH = "control/inventory/nodes/node_capability_registry.json"
AUDIT_REPORT_PATH = "control/audits/track-b-04-workunit-contract-v0/track_b_04_report.json"
EXAMPLE_ROOT = "examples/work_units"
DOC_PATHS = (
    "docs/reference/WORKUNIT_CONTRACT.md",
    "docs/architecture/WORKUNIT_MODEL.md",
    "docs/operations/WORKUNIT_IDEMPOTENCY_AND_RECOVERY.md",
)

ALLOWED_STATUSES = {
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
CURRENT_ALLOWED_STATUSES = {
    "example_only",
    "contract_only",
    "planned",
    "dry_run_only",
    "ready_for_manual_review",
    "human_operated",
    "approval_gated",
    "operator_gated",
    "permission_needed",
    "policy_blocked",
    "deferred",
    "blocked",
}
FUTURE_OR_GATED_STATUSES = {
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
ALLOWED_TYPES = {
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
ALLOWED_SCOPES = {
    "repo_local",
    "committed_fixture",
    "committed_eval",
    "committed_static_artifact",
    "manual_observation_support",
    "observation_candidate_review",
    "source_policy_review",
    "pack_validation",
    "pack_drafting_future",
    "local_private_future",
    "approved_source_future",
    "extraction_future",
    "model_assist_future",
    "hosted_worker_future",
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
FORBIDDEN_INPUTS = {
    "unapproved_live_source_result",
    "scraped_search_result",
    "scraped_forum_thread",
    "bulk_reddit_content",
    "private_user_file",
    "secret_or_credential",
    "executable_download",
    "installer_payload",
    "raw_browser_profile",
    "account_session_data",
    "telemetry_stream",
    "unreviewed_external_api_payload",
}
ALLOWED_ACTIONS = {
    "inspect_repo_local_artifact",
    "validate_contract",
    "validate_pack",
    "run_local_eval",
    "summarize_local_gap",
    "review_observation_candidate",
    "prepare_observation_candidate",
    "prepare_source_lead",
    "prepare_search_need_seed_future",
    "prepare_workunit_seed_future",
    "draft_evidence_candidate_future",
    "draft_candidate_record_future",
    "draft_pack_future",
    "produce_dry_run_report",
    "produce_review_packet",
    "request_human_review",
    "request_source_policy_approval_future",
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
    "can_create_observed_baseline",
    "can_create_accepted_evidence",
    "can_create_public_truth",
    "can_mutate_master_index",
    "can_claim_rights_clearance",
    "can_claim_malware_safety",
    "can_claim_verified_installability",
    "can_claim_exhaustive_global_search",
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
REQUIREMENT_FIELDS = {
    "source_access_requirements": "source_access_required",
    "network_requirements": "network_required",
    "model_provider_requirements": "model_provider_required",
    "credential_requirements": "credentials_required",
    "local_state_requirements": "local_state_required",
}
REQUIRED_DUPLICATE_BEHAVIOR = {
    "if_complete": "validate_and_record_noop",
    "if_partial": "resume_from_missing_acceptance",
    "if_conflicting": "classify_and_quarantine",
}
REQUIRED_RECOVERY = {
    "dirty_tree": "inspect_preserve_and_continue",
    "missing_dependency": "repair_if_bounded_else_record_blocker",
    "stale_status": "reconcile_from_evidence",
    "failed_validation": "repair_if_in_scope_else_record_blocker",
    "out_of_order_task": "inspect_queue_and_resume_valid_next",
    "repeated_prompt": "classify_noop_resume_or_repair",
}
STOP_CONDITIONS = {
    "destructive_ambiguity",
    "missing_external_credentials",
    "legal_or_licensing_decision",
    "manual_observation_requirement",
    "irreversible_action_without_approval",
    "private_data_exposure_risk",
    "unsafe_network_or_source_action",
    "production_deployment_or_hosting_mutation",
}
FUTURE_CAPABILITY_STATUSES = {"future", "deferred", "approval_gated", "operator_gated", "human_operated", "policy_blocked", "blocked", "deprecated_future"}
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
    parser = argparse.ArgumentParser(description="Validate Eureka WorkUnit contract files.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help="Repository root to validate.")
    parser.add_argument("--json", action="store_true", help="Emit deterministic JSON.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_eureka_workunit(Path(args.repo_root))
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


def validate_eureka_workunit(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    root = repo_root.resolve()
    errors: list[str] = []
    warnings: list[str] = []

    schema = _load_json(root / SCHEMA_PATH, errors, root)
    type_registry = _load_json(root / TYPE_REGISTRY_PATH, errors, root)
    workunit_policy = _load_json(root / WORKUNIT_POLICY_PATH, errors, root)
    idempotency_policy = _load_json(root / IDEMPOTENCY_POLICY_PATH, errors, root)
    action_policy = _load_json(root / ACTION_POLICY_PATH, errors, root)
    input_output_policy = _load_json(root / INPUT_OUTPUT_POLICY_PATH, errors, root)
    review_gate_policy = _load_json(root / REVIEW_GATE_POLICY_PATH, errors, root)
    mode_registry = _load_json(root / NODE_MODE_REGISTRY_PATH, errors, root)
    capability_matrix = _load_json(root / NODE_CAPABILITY_MATRIX_PATH, errors, root)
    capability_registry = _load_json(root / NODE_CAPABILITY_REGISTRY_PATH, errors, root)
    audit_report = _load_json(root / AUDIT_REPORT_PATH, errors, root)

    mode_ids = _mode_ids(mode_registry)
    capability_statuses = _capability_statuses(capability_matrix)
    capability_ids = set(capability_statuses) | _capability_ids(capability_registry)

    errors.extend(validate_docs(root))
    errors.extend(validate_schema(schema, SCHEMA_PATH))
    errors.extend(validate_workunit_type_registry(type_registry, TYPE_REGISTRY_PATH))
    errors.extend(validate_workunit_policy(workunit_policy, WORKUNIT_POLICY_PATH))
    errors.extend(validate_workunit_idempotency_policy(idempotency_policy, IDEMPOTENCY_POLICY_PATH))
    errors.extend(validate_workunit_action_policy(action_policy, ACTION_POLICY_PATH))
    errors.extend(validate_workunit_input_output_policy(input_output_policy, INPUT_OUTPUT_POLICY_PATH))
    errors.extend(validate_workunit_review_gate_policy(review_gate_policy, REVIEW_GATE_POLICY_PATH))
    errors.extend(validate_audit_report(audit_report, AUDIT_REPORT_PATH))

    example_paths = list_example_workunit_paths(root)
    if len(example_paths) != 7:
        errors.append(f"{EXAMPLE_ROOT}: expected 7 WorkUnit examples, found {len(example_paths)}")
    seen_ids: set[str] = set()
    for path in example_paths:
        payload = _load_json(path, errors, root)
        source = _relative(root, path)
        workunit_id = _mapping(payload).get("workunit_id")
        if isinstance(workunit_id, str):
            if workunit_id in seen_ids:
                errors.append(f"{source}: duplicate workunit_id {workunit_id}")
            seen_ids.add(workunit_id)
        errors.extend(
            validate_workunit_record(
                payload,
                source,
                repo_root=root,
                mode_ids=mode_ids,
                capability_ids=capability_ids,
                capability_statuses=capability_statuses,
            )
        )

    return {
        "schema_version": "eureka_workunit_validation.v0",
        "status": "valid" if not errors else "invalid",
        "validated_files": sorted(
            [
                SCHEMA_PATH,
                TYPE_REGISTRY_PATH,
                WORKUNIT_POLICY_PATH,
                IDEMPOTENCY_POLICY_PATH,
                ACTION_POLICY_PATH,
                INPUT_OUTPUT_POLICY_PATH,
                REVIEW_GATE_POLICY_PATH,
                NODE_MODE_REGISTRY_PATH,
                NODE_CAPABILITY_MATRIX_PATH,
                NODE_CAPABILITY_REGISTRY_PATH,
                AUDIT_REPORT_PATH,
                *DOC_PATHS,
                *[_relative(root, path) for path in example_paths],
            ]
        ),
        "errors": sorted(set(errors)),
        "warnings": sorted(set(warnings)),
    }


def list_example_workunit_paths(repo_root: Path = REPO_ROOT) -> list[Path]:
    return sorted((repo_root.resolve() / EXAMPLE_ROOT).glob("*/work_unit.json"))


def validate_docs(repo_root: Path) -> list[str]:
    errors: list[str] = []
    for path in DOC_PATHS:
        full_path = repo_root / path
        if not full_path.is_file():
            errors.append(f"docs: missing {path}")
            continue
        text = full_path.read_text(encoding="utf-8").lower()
        for phrase in ("workunit", "idempotency", "review", "master-index"):
            if phrase not in text:
                errors.append(f"{path}: missing required phrase {phrase!r}")
    return errors


def validate_schema(payload: Any, source: str) -> list[str]:
    data = _mapping(payload)
    errors: list[str] = []
    if data.get("title") != "EurekaWorkUnitV0":
        errors.append(f"{source}: title must be EurekaWorkUnitV0")
    properties = _mapping(data.get("properties"))
    schema_version = _mapping(properties.get("schema_version"))
    if schema_version.get("const") != "work_unit.v0":
        errors.append(f"{source}: schema_version const must be work_unit.v0")
    errors.extend(_missing_items(data.get("required"), _required_fields(), f"{source}: required"))
    for key in (
        "x-workunit-is-runtime-permission",
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


def validate_workunit_type_registry(payload: Any, source: str) -> list[str]:
    data = _mapping(payload)
    errors: list[str] = []
    if data.get("schema_version") != "workunit_type_registry.v0":
        errors.append(f"{source}: schema_version must be workunit_type_registry.v0")
    errors.extend(_missing_items(data.get("allowed_statuses"), ALLOWED_STATUSES, f"{source}: allowed_statuses"))
    errors.extend(_missing_items(data.get("current_allowed_statuses"), CURRENT_ALLOWED_STATUSES, f"{source}: current_allowed_statuses"))
    errors.extend(_missing_items(data.get("allowed_types"), ALLOWED_TYPES, f"{source}: allowed_types"))
    errors.extend(_missing_items(data.get("allowed_scopes"), ALLOWED_SCOPES, f"{source}: allowed_scopes"))
    errors.extend(_boundary_false_errors(_mapping(data.get("product_boundary")), source))
    return errors


def validate_workunit_policy(payload: Any, source: str) -> list[str]:
    data = _mapping(payload)
    errors: list[str] = []
    if data.get("schema_version") != "workunit_policy.v0":
        errors.append(f"{source}: schema_version must be workunit_policy.v0")
    errors.extend(_missing_items(data.get("required_fields"), _required_fields(), f"{source}: required_fields"))
    errors.extend(_missing_items(data.get("required_false_truth_booleans"), TRUTH_FALSE_FIELDS, f"{source}: required_false_truth_booleans"))
    errors.extend(_missing_items(data.get("product_boundary_false_fields"), PRODUCT_BOUNDARY_FIELDS, f"{source}: product_boundary_false_fields"))
    errors.extend(_boundary_false_errors(_mapping(data.get("product_boundary")), source))
    return errors


def validate_workunit_idempotency_policy(payload: Any, source: str) -> list[str]:
    data = _mapping(payload)
    errors: list[str] = []
    if data.get("schema_version") != "workunit_idempotency_policy.v0":
        errors.append(f"{source}: schema_version must be workunit_idempotency_policy.v0")
    required = _mapping(data.get("required_idempotency"))
    if required.get("safe_to_rerun") is not True:
        errors.append(f"{source}: required_idempotency.safe_to_rerun must be true")
    errors.extend(_expected_values(_mapping(required.get("duplicate_behavior")), REQUIRED_DUPLICATE_BEHAVIOR, f"{source}: required_idempotency.duplicate_behavior"))
    errors.extend(_expected_values(_mapping(data.get("required_recovery")), REQUIRED_RECOVERY, f"{source}: required_recovery"))
    errors.extend(_missing_items(data.get("required_stop_conditions"), STOP_CONDITIONS, f"{source}: required_stop_conditions"))
    errors.extend(_boundary_false_errors(_mapping(data.get("product_boundary")), source))
    return errors


def validate_workunit_action_policy(payload: Any, source: str) -> list[str]:
    data = _mapping(payload)
    errors: list[str] = []
    if data.get("schema_version") != "workunit_action_policy.v0":
        errors.append(f"{source}: schema_version must be workunit_action_policy.v0")
    errors.extend(_missing_items(data.get("allowed_actions"), ALLOWED_ACTIONS, f"{source}: allowed_actions"))
    errors.extend(_missing_items(data.get("forbidden_actions"), FORBIDDEN_ACTIONS, f"{source}: forbidden_actions"))
    errors.extend(_boundary_false_errors(_mapping(data.get("product_boundary")), source))
    return errors


def validate_workunit_input_output_policy(payload: Any, source: str) -> list[str]:
    data = _mapping(payload)
    errors: list[str] = []
    if data.get("schema_version") != "workunit_input_output_policy.v0":
        errors.append(f"{source}: schema_version must be workunit_input_output_policy.v0")
    errors.extend(_missing_items(data.get("allowed_input_types"), ALLOWED_INPUTS, f"{source}: allowed_input_types"))
    errors.extend(_missing_items(data.get("forbidden_input_types"), FORBIDDEN_INPUTS, f"{source}: forbidden_input_types"))
    errors.extend(_missing_items(data.get("allowed_output_types"), ALLOWED_OUTPUTS, f"{source}: allowed_output_types"))
    errors.extend(_missing_items(data.get("forbidden_output_types"), FORBIDDEN_OUTPUTS, f"{source}: forbidden_output_types"))
    errors.extend(_boundary_false_errors(_mapping(data.get("product_boundary")), source))
    return errors


def validate_workunit_review_gate_policy(payload: Any, source: str) -> list[str]:
    data = _mapping(payload)
    errors: list[str] = []
    if data.get("schema_version") != "workunit_review_gate_policy.v0":
        errors.append(f"{source}: schema_version must be workunit_review_gate_policy.v0")
    errors.extend(_missing_items(data.get("required_review_gates"), REVIEW_GATES, f"{source}: required_review_gates"))
    errors.extend(_boundary_false_errors(_mapping(data.get("product_boundary")), source))
    return errors


def validate_audit_report(payload: Any, source: str) -> list[str]:
    data = _mapping(payload)
    errors: list[str] = []
    if data.get("schema_version") != "track_b_04_report.v0":
        errors.append(f"{source}: schema_version must be track_b_04_report.v0")
    if data.get("task") != "TRACK-B-04":
        errors.append(f"{source}: task must be TRACK-B-04")
    errors.extend(_boundary_false_errors(_mapping(data.get("product_boundary")), source))
    truth = _mapping(data.get("truth_boundary"))
    for field in (
        "workunit_is_runtime_permission",
        "workunit_result_is_public_truth",
        "workunit_result_is_accepted_evidence",
        "workunit_can_mutate_master_index",
    ):
        if truth.get(field) is not False:
            errors.append(f"{source}: truth_boundary.{field} must be false")
    if truth.get("human_review_required_for_truth") is not True:
        errors.append(f"{source}: truth_boundary.human_review_required_for_truth must be true")
    return errors


def validate_workunit_record(
    payload: Any,
    source: str,
    *,
    repo_root: Path = REPO_ROOT,
    mode_ids: set[str] | None = None,
    capability_ids: set[str] | None = None,
    capability_statuses: Mapping[str, str] | None = None,
) -> list[str]:
    data = _mapping(payload)
    errors: list[str] = []
    if data.get("schema_version") != "work_unit.v0":
        errors.append(f"{source}: schema_version must be work_unit.v0")
    errors.extend(_missing_items(data, _required_fields(), f"{source}: top-level"))

    status = str(data.get("workunit_status", ""))
    workunit_type = str(data.get("workunit_type", ""))
    scope = str(data.get("workunit_scope", ""))
    if status not in ALLOWED_STATUSES:
        errors.append(f"{source}: workunit_status {status!r} is not allowed")
    if status not in CURRENT_ALLOWED_STATUSES:
        errors.append(f"{source}: current example cannot use status {status!r}")
    if workunit_type not in ALLOWED_TYPES:
        errors.append(f"{source}: workunit_type {workunit_type!r} is not allowed")
    if scope not in ALLOWED_SCOPES:
        errors.append(f"{source}: workunit_scope {scope!r} is not allowed")

    known_modes = mode_ids or _mode_ids(_load_json(repo_root / NODE_MODE_REGISTRY_PATH, [], repo_root)) or set()
    errors.extend(_unknown_items(set(_string_items(data.get("required_node_modes"))), known_modes, f"{source}: required_node_modes"))

    known_capabilities = capability_ids or set(capability_statuses or {})
    capability_status_map = capability_statuses or {}
    for item in _sequence(data.get("required_node_capabilities")):
        capability_id = _mapping(item).get("capability_id")
        if not isinstance(capability_id, str):
            errors.append(f"{source}: required_node_capabilities item missing capability_id")
            continue
        if capability_id not in known_capabilities:
            errors.append(f"{source}: required_node_capabilities unknown {capability_id}")
            continue
        capability_status = capability_status_map.get(capability_id)
        if capability_status in FUTURE_CAPABILITY_STATUSES and status not in FUTURE_OR_GATED_STATUSES:
            errors.append(f"{source}: future capability {capability_id} requires future/deferred/gated WorkUnit status")

    for ref in _string_items(data.get("related_node_manifest_refs")) + _string_items(data.get("required_node_policy_refs")) + _string_items(data.get("output_contract_refs")):
        if not (repo_root / ref).is_file():
            errors.append(f"{source}: referenced file does not exist: {ref}")

    inputs = _mapping(data.get("input_summary"))
    errors.extend(_unknown_items(set(_string_items(inputs.get("allowed_input_types"))), ALLOWED_INPUTS, f"{source}: input_summary.allowed_input_types"))
    errors.extend(_unknown_items(set(_string_items(inputs.get("forbidden_input_types"))), FORBIDDEN_INPUTS, f"{source}: input_summary.forbidden_input_types"))
    errors.extend(_missing_items(inputs.get("forbidden_input_types"), FORBIDDEN_INPUTS, f"{source}: input_summary.forbidden_input_types"))
    for item in _sequence(data.get("input_refs")):
        input_type = _mapping(item).get("input_type")
        if input_type not in ALLOWED_INPUTS:
            errors.append(f"{source}: input_refs input_type {input_type!r} is not allowed")

    errors.extend(_unknown_items(set(_string_items(data.get("allowed_actions"))), ALLOWED_ACTIONS, f"{source}: allowed_actions"))
    errors.extend(_unknown_items(set(_string_items(data.get("forbidden_actions"))), FORBIDDEN_ACTIONS, f"{source}: forbidden_actions"))
    errors.extend(_missing_items(data.get("forbidden_actions"), FORBIDDEN_ACTIONS, f"{source}: forbidden_actions"))

    for item in _sequence(data.get("expected_outputs")):
        record = _mapping(item)
        output_type = record.get("output_type")
        if output_type not in ALLOWED_OUTPUTS:
            errors.append(f"{source}: expected_outputs output_type {output_type!r} is not allowed")
        if record.get("output_requires_review") is not True:
            errors.append(f"{source}: expected_outputs {record.get('output_id', '<unknown>')} must require review")
        errors.extend(_false_field_errors(_mapping(record.get("output_truth_boundary")), {"accepted_public_truth", "accepted_evidence_truth", "master_index_mutation"}, f"{source}: expected_outputs {record.get('output_id', '<unknown>')}.output_truth_boundary"))
    errors.extend(_unknown_items(set(_string_items(data.get("forbidden_outputs"))), FORBIDDEN_OUTPUTS, f"{source}: forbidden_outputs"))
    errors.extend(_missing_items(data.get("forbidden_outputs"), FORBIDDEN_OUTPUTS, f"{source}: forbidden_outputs"))

    errors.extend(_validate_requirements(data, source, status))
    errors.extend(_validate_idempotency(data, source))
    errors.extend(_validate_review_gates(_mapping(data.get("review_gates")), source))
    errors.extend(_false_field_errors(_mapping(data.get("truth_boundary")), TRUTH_FALSE_FIELDS, f"{source}: truth_boundary"))
    errors.extend(_boundary_false_errors(_mapping(data.get("product_boundary")), source))
    errors.extend(_sensitive_key_errors(data, source))
    errors.extend(_private_path_errors(data, source))
    errors.extend(_forbidden_text_claim_errors(data, source))
    return errors


def _validate_requirements(data: Mapping[str, Any], source: str, status: str) -> list[str]:
    errors: list[str] = []
    required_flags: dict[str, bool] = {}
    for section, field in REQUIREMENT_FIELDS.items():
        payload = _mapping(data.get(section))
        if payload.get("current_enabled") is not False:
            errors.append(f"{source}: {section}.current_enabled must be false")
        value = payload.get(field)
        if not isinstance(value, bool):
            errors.append(f"{source}: {section}.{field} must be boolean")
            value = False
        required_flags[section] = bool(value)
    if any(required_flags.values()) and status not in FUTURE_OR_GATED_STATUSES:
        true_sections = ", ".join(sorted(section for section, value in required_flags.items() if value))
        errors.append(f"{source}: WorkUnit requiring {true_sections} must be future/deferred/gated")

    source_access = _mapping(data.get("source_access_requirements"))
    network = _mapping(data.get("network_requirements"))
    model = _mapping(data.get("model_provider_requirements"))
    credential = _mapping(data.get("credential_requirements"))
    local_state = _mapping(data.get("local_state_requirements"))
    if source_access.get("source_access_required") is True:
        for field in ("source_policy_approval_required", "operator_approval_required", "human_review_required", "kill_switch_policy_required", "rate_or_budget_policy_required"):
            if source_access.get(field) is not True:
                errors.append(f"{source}: source_access_requirements.{field} must be true when source access is required")
    if network.get("network_required") is True:
        for field in ("operator_approval_required", "source_policy_required", "kill_switch_policy_required", "rate_or_budget_policy_required"):
            if network.get(field) is not True:
                errors.append(f"{source}: network_requirements.{field} must be true when network is required")
    if model.get("model_provider_required") is True:
        for field in ("operator_approval_required", "budget_policy_required", "human_review_required"):
            if model.get(field) is not True:
                errors.append(f"{source}: model_provider_requirements.{field} must be true when model provider is required")
    if credential.get("credentials_required") is True and credential.get("operator_approval_required") is not True:
        errors.append(f"{source}: credential_requirements.operator_approval_required must be true when credentials are required")
    if local_state.get("local_state_required") is True and local_state.get("operator_approval_required") is not True:
        errors.append(f"{source}: local_state_requirements.operator_approval_required must be true when local state is required")
    return errors


def _validate_idempotency(data: Mapping[str, Any], source: str) -> list[str]:
    errors: list[str] = []
    idempotency = _mapping(data.get("idempotency"))
    if idempotency.get("safe_to_rerun") is not True:
        errors.append(f"{source}: idempotency.safe_to_rerun must be true")
    errors.extend(_expected_values(_mapping(idempotency.get("duplicate_behavior")), REQUIRED_DUPLICATE_BEHAVIOR, f"{source}: idempotency.duplicate_behavior"))
    errors.extend(_expected_values(_mapping(data.get("duplicate_policy")), REQUIRED_DUPLICATE_BEHAVIOR, f"{source}: duplicate_policy"))
    recovery = _mapping(data.get("recovery_policy"))
    errors.extend(_expected_values(recovery, REQUIRED_RECOVERY, f"{source}: recovery_policy"))
    errors.extend(_missing_items(recovery.get("stop_conditions"), STOP_CONDITIONS, f"{source}: recovery_policy.stop_conditions"))
    if _mapping(data.get("out_of_order_policy")).get("behavior") != "inspect_queue_and_resume_valid_next":
        errors.append(f"{source}: out_of_order_policy.behavior must be inspect_queue_and_resume_valid_next")
    return errors


def _validate_review_gates(payload: Mapping[str, Any], source: str) -> list[str]:
    errors: list[str] = []
    errors.extend(_missing_items(payload, REVIEW_GATES, f"{source}: review_gates"))
    for gate in sorted(REVIEW_GATES):
        if payload.get(gate) is not True:
            errors.append(f"{source}: review_gates.{gate} must be true")
    return errors


def _format_plain(report: Mapping[str, Any]) -> str:
    lines = [f"validate_eureka_workunit: {report['status']}"]
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


def _records_by_id(value: Any, key: str, label: str, errors: list[str]) -> dict[str, Mapping[str, Any]]:
    records: dict[str, Mapping[str, Any]] = {}
    for index, item in enumerate(_sequence(value)):
        record = _mapping(item)
        item_id = record.get(key)
        if not isinstance(item_id, str) or not item_id:
            errors.append(f"{label}[{index}]: missing {key}")
            continue
        if item_id in records:
            errors.append(f"{label}: duplicate {key} {item_id}")
        records[item_id] = record
    return records


def _mode_ids(payload: Any | None) -> set[str]:
    errors: list[str] = []
    return set(_records_by_id(_mapping(payload).get("modes"), "mode_id", "modes", errors))


def _capability_ids(payload: Any | None) -> set[str]:
    errors: list[str] = []
    return set(_records_by_id(_mapping(payload).get("capabilities"), "capability_id", "capabilities", errors))


def _capability_statuses(payload: Any | None) -> dict[str, str]:
    errors: list[str] = []
    records = _records_by_id(_mapping(payload).get("capabilities"), "capability_id", "capabilities", errors)
    return {capability_id: str(record.get("capability_status", "")) for capability_id, record in records.items()}


def _missing_items(value: Any, required: set[str], label: str) -> list[str]:
    if isinstance(value, Mapping):
        present = set(str(key) for key in value)
    elif isinstance(value, set):
        present = set(value)
    else:
        present = set(_string_items(value))
    return [f"{label} missing {item}" for item in sorted(required - present)]


def _unknown_items(value: set[str], allowed: set[str], label: str) -> list[str]:
    return [f"{label} unknown {item}" for item in sorted(value - allowed)]


def _expected_values(payload: Mapping[str, Any], expected: Mapping[str, str], label: str) -> list[str]:
    errors: list[str] = []
    for key, value in sorted(expected.items()):
        if payload.get(key) != value:
            errors.append(f"{label}.{key} must be {value}")
    return errors


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
        "workunit_id",
        "workunit_label",
        "workunit_type",
        "workunit_status",
        "workunit_scope",
        "priority",
        "created_from",
        "related_node_manifest_refs",
        "required_node_modes",
        "required_node_capabilities",
        "required_node_policy_refs",
        "source_access_requirements",
        "network_requirements",
        "model_provider_requirements",
        "credential_requirements",
        "local_state_requirements",
        "input_refs",
        "input_summary",
        "allowed_actions",
        "forbidden_actions",
        "expected_outputs",
        "forbidden_outputs",
        "output_contract_refs",
        "review_gates",
        "idempotency",
        "recovery_policy",
        "duplicate_policy",
        "out_of_order_policy",
        "validation_policy",
        "budget_policy_future",
        "audit_policy",
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
