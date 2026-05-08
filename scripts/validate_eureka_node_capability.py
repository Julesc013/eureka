"""Validate Track B Eureka Node capability governance artifacts.

The validator is deterministic and read-only. It checks declarative capability
records and registries without creating node runtime state, calling sources, or
granting runtime permission.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = "contracts/node/node_capability.v0.json"
CAPABILITY_POLICY_PATH = "control/inventory/nodes/node_capability_policy.json"
CAPABILITY_MATRIX_PATH = "control/inventory/nodes/node_capability_matrix.json"
DEPENDENCY_POLICY_PATH = "control/inventory/nodes/node_capability_dependency_policy.json"
SIDE_EFFECT_POLICY_PATH = "control/inventory/nodes/node_capability_side_effect_policy.json"
NODE_CAPABILITY_REGISTRY_PATH = "control/inventory/nodes/node_capability_registry.json"
NODE_MODE_REGISTRY_PATH = "control/inventory/nodes/node_mode_registry.json"
AUDIT_REPORT_PATH = "control/audits/track-b-03-node-capability-contract-v0/track_b_03_report.json"
EXAMPLE_ROOT = "examples/nodes/capabilities"
DOC_PATHS = (
    "docs/reference/NODE_CAPABILITY_CONTRACT.md",
    "docs/architecture/EUREKA_NODE_CAPABILITIES.md",
    "docs/operations/NODE_CAPABILITY_REVIEW.md",
)
MANIFEST_EXAMPLE_ROOT = "examples/nodes"

REQUIRED_CAPABILITIES = {
    "repo_local_inspection",
    "local_eval_analysis",
    "search_need_analysis",
    "observation_candidate_preparation",
    "source_lead_preparation",
    "workunit_candidate_preparation_future",
    "pack_validation",
    "pack_drafting_future",
    "evidence_drafting_future",
    "candidate_drafting_future",
    "local_index_read_future",
    "local_index_write_future",
    "local_source_cache_read_future",
    "local_source_cache_write_future",
    "local_evidence_ledger_read_future",
    "local_evidence_ledger_write_future",
    "extraction_planning_future",
    "extraction_runtime_future",
    "approved_metadata_probe_future",
    "approved_api_access_future",
    "local_model_assist_future",
    "hosted_worker_execution_future",
}
ALLOWED_STATUSES = {
    "current_contract_only",
    "current_repo_local_only",
    "current_validate_only",
    "current_dry_run_only",
    "future",
    "deferred",
    "approval_gated",
    "operator_gated",
    "human_operated",
    "policy_blocked",
    "blocked",
    "deprecated_future",
}
CURRENT_STATUSES = {
    "current_contract_only",
    "current_repo_local_only",
    "current_validate_only",
    "current_dry_run_only",
    "policy_blocked",
    "blocked",
}
FUTURE_OR_GATED_STATUSES = ALLOWED_STATUSES - CURRENT_STATUSES
ALLOWED_FAMILIES = {
    "repo_inspection",
    "validation",
    "local_eval",
    "observation",
    "source_lead",
    "search_need",
    "workunit_future",
    "candidate_future",
    "evidence_future",
    "pack",
    "source_cache_future",
    "evidence_ledger_future",
    "extraction_future",
    "approved_source_future",
    "local_model_future",
    "hosted_worker_future",
    "review_future",
}
ALLOWED_SIDE_EFFECTS = {
    "read_only_repo_local",
    "read_only_committed_fixture",
    "validate_only",
    "report_only",
    "dry_run_report_only",
    "local_state_future",
    "local_index_write_future",
    "source_cache_write_future",
    "evidence_ledger_write_future",
    "pack_draft_future",
    "pack_export_future",
    "network_probe_future",
    "model_call_future",
    "hosted_runtime_future",
    "blocked",
}
CURRENT_SIDE_EFFECTS = {
    "read_only_repo_local",
    "read_only_committed_fixture",
    "validate_only",
    "report_only",
    "dry_run_report_only",
    "blocked",
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
    "workunit_future",
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
ALLOWED_OUTPUTS = {
    "capability_report",
    "validation_report",
    "dry_run_report",
    "observation_candidate",
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
ALLOWED_MODES = {
    "local_private",
    "local_pack_builder",
    "local_autonomous_dry_run",
    "community_node_future",
    "institution_node_future",
    "hosted_worker_future",
}
REVIEW_GATES = {
    "human_review_required",
    "source_policy_review_required",
    "evidence_review_required",
    "candidate_review_required",
    "pack_review_required",
    "master_index_review_required",
    "operator_approval_required_for_network",
    "operator_approval_required_for_hosted_behavior",
    "legal_or_rights_decision_stop_required",
    "risk_review_required",
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
DEPENDENCY_TYPES = {
    "node_manifest",
    "node_policy",
    "node_capability",
    "source_policy_future",
    "review_gate",
    "operator_gate",
    "budget_policy_future",
    "kill_switch_policy_future",
    "rate_limit_policy_future",
}
REQUIREMENT_FIELDS = {
    "network_requirement": "network_required",
    "source_access_requirement": "source_access_required",
    "local_state_requirement": "local_state_required",
    "model_provider_requirement": "model_provider_required",
    "credential_requirement": "credentials_required",
}
SENSITIVE_KEY_NAMES = {"api_key", "password", "secret", "credential", "credentials", "token"}
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
    parser = argparse.ArgumentParser(description="Validate Eureka Node capability contract files.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help="Repository root to validate.")
    parser.add_argument("--json", action="store_true", help="Emit deterministic JSON.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_eureka_node_capability(Path(args.repo_root))
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


def validate_eureka_node_capability(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    root = repo_root.resolve()
    errors: list[str] = []
    warnings: list[str] = []

    schema = _load_json(root / SCHEMA_PATH, errors)
    capability_policy = _load_json(root / CAPABILITY_POLICY_PATH, errors)
    matrix = _load_json(root / CAPABILITY_MATRIX_PATH, errors)
    dependency_policy = _load_json(root / DEPENDENCY_POLICY_PATH, errors)
    side_effect_policy = _load_json(root / SIDE_EFFECT_POLICY_PATH, errors)
    capability_registry = _load_json(root / NODE_CAPABILITY_REGISTRY_PATH, errors)
    mode_registry = _load_json(root / NODE_MODE_REGISTRY_PATH, errors)
    audit_report = _load_json(root / AUDIT_REPORT_PATH, errors)

    errors.extend(validate_docs(root))
    errors.extend(validate_schema(schema, SCHEMA_PATH))
    errors.extend(validate_capability_policy(capability_policy, CAPABILITY_POLICY_PATH))
    errors.extend(validate_dependency_policy(dependency_policy, DEPENDENCY_POLICY_PATH))
    errors.extend(validate_side_effect_policy(side_effect_policy, SIDE_EFFECT_POLICY_PATH))
    matrix_errors, matrix_ids = validate_capability_matrix(matrix, CAPABILITY_MATRIX_PATH, capability_registry, mode_registry)
    errors.extend(matrix_errors)
    errors.extend(validate_audit_report(audit_report, AUDIT_REPORT_PATH))
    errors.extend(validate_manifest_capability_refs(root, matrix_ids))

    example_paths = list_example_capability_paths(root)
    if len(example_paths) != 6:
        errors.append(f"{EXAMPLE_ROOT}: expected 6 example capabilities, found {len(example_paths)}")
    seen_ids: set[str] = set()
    for path in example_paths:
        payload = _load_json(path, errors)
        source = _relative(root, path)
        capability_id = _mapping(payload).get("capability_id")
        if isinstance(capability_id, str):
            if capability_id in seen_ids:
                errors.append(f"{source}: duplicate capability_id {capability_id}")
            seen_ids.add(capability_id)
        errors.extend(validate_node_capability_record(payload, source, matrix_ids=matrix_ids))

    return {
        "schema_version": "eureka_node_capability_validation.v0",
        "status": "valid" if not errors else "invalid",
        "validated_files": sorted(
            [
                SCHEMA_PATH,
                CAPABILITY_POLICY_PATH,
                CAPABILITY_MATRIX_PATH,
                DEPENDENCY_POLICY_PATH,
                SIDE_EFFECT_POLICY_PATH,
                NODE_CAPABILITY_REGISTRY_PATH,
                NODE_MODE_REGISTRY_PATH,
                AUDIT_REPORT_PATH,
                *DOC_PATHS,
                *[_relative(root, path) for path in example_paths],
            ]
        ),
        "errors": sorted(set(errors)),
        "warnings": sorted(set(warnings)),
    }


def list_example_capability_paths(repo_root: Path = REPO_ROOT) -> list[Path]:
    return sorted((repo_root.resolve() / EXAMPLE_ROOT).glob("*.json"))


def validate_docs(repo_root: Path) -> list[str]:
    errors: list[str] = []
    for path in DOC_PATHS:
        full_path = repo_root / path
        if not full_path.is_file():
            errors.append(f"docs: missing {path}")
            continue
        text = full_path.read_text(encoding="utf-8").lower()
        for phrase in ("node capability", "review", "source", "master index"):
            if phrase not in text:
                errors.append(f"{path}: missing required phrase {phrase!r}")
    return errors


def validate_schema(payload: Any, source: str) -> list[str]:
    data = _mapping(payload)
    errors: list[str] = []
    if data.get("title") != "EurekaNodeCapabilityV0":
        errors.append(f"{source}: title must be EurekaNodeCapabilityV0")
    properties = _mapping(data.get("properties"))
    schema_version = _mapping(properties.get("schema_version"))
    if schema_version.get("const") != "node_capability.v0":
        errors.append(f"{source}: schema_version const must be node_capability.v0")
    errors.extend(_missing_items(data.get("required"), _required_fields(), f"{source}: required"))
    for key in (
        "x-capability-is-runtime-permission",
        "x-network-access-enabled",
        "x-model-provider-calls-enabled",
        "x-local-state-created",
        "x-master-index-mutation-allowed",
    ):
        if data.get(key) is not False:
            errors.append(f"{source}: {key} must be false")
    return errors


def validate_capability_policy(payload: Any, source: str) -> list[str]:
    data = _mapping(payload)
    errors: list[str] = []
    if data.get("schema_version") != "node_capability_policy.v0":
        errors.append(f"{source}: schema_version must be node_capability_policy.v0")
    errors.extend(_missing_items(data.get("required_fields"), _required_fields(), f"{source}: required_fields"))
    errors.extend(_missing_items(data.get("allowed_statuses"), ALLOWED_STATUSES, f"{source}: allowed_statuses"))
    errors.extend(_missing_items(data.get("allowed_families"), ALLOWED_FAMILIES, f"{source}: allowed_families"))
    errors.extend(_missing_items(data.get("allowed_side_effect_classes"), ALLOWED_SIDE_EFFECTS, f"{source}: allowed_side_effect_classes"))
    errors.extend(_missing_items(data.get("current_allowed_side_effect_classes"), CURRENT_SIDE_EFFECTS, f"{source}: current_allowed_side_effect_classes"))
    errors.extend(_missing_items(data.get("allowed_inputs"), ALLOWED_INPUTS, f"{source}: allowed_inputs"))
    errors.extend(_missing_items(data.get("forbidden_inputs"), FORBIDDEN_INPUTS, f"{source}: forbidden_inputs"))
    errors.extend(_missing_items(data.get("allowed_outputs"), ALLOWED_OUTPUTS, f"{source}: allowed_outputs"))
    errors.extend(_missing_items(data.get("forbidden_outputs"), FORBIDDEN_OUTPUTS, f"{source}: forbidden_outputs"))
    errors.extend(_missing_items(data.get("required_false_truth_booleans"), TRUTH_FALSE_FIELDS, f"{source}: required_false_truth_booleans"))
    errors.extend(_missing_items(data.get("product_boundary_false_fields"), PRODUCT_BOUNDARY_FIELDS, f"{source}: product_boundary_false_fields"))
    return errors


def validate_dependency_policy(payload: Any, source: str) -> list[str]:
    data = _mapping(payload)
    errors: list[str] = []
    if data.get("schema_version") != "node_capability_dependency_policy.v0":
        errors.append(f"{source}: schema_version must be node_capability_dependency_policy.v0")
    errors.extend(_missing_items(data.get("allowed_dependency_types"), DEPENDENCY_TYPES, f"{source}: allowed_dependency_types"))
    errors.extend(_boundary_false_errors(_mapping(data.get("product_boundary")), source))
    return errors


def validate_side_effect_policy(payload: Any, source: str) -> list[str]:
    data = _mapping(payload)
    errors: list[str] = []
    if data.get("schema_version") != "node_capability_side_effect_policy.v0":
        errors.append(f"{source}: schema_version must be node_capability_side_effect_policy.v0")
    errors.extend(_missing_items(data.get("side_effect_classes"), ALLOWED_SIDE_EFFECTS, f"{source}: side_effect_classes"))
    errors.extend(_missing_items(data.get("allowed_current_side_effects"), CURRENT_SIDE_EFFECTS, f"{source}: allowed_current_side_effects"))
    errors.extend(_boundary_false_errors(_mapping(data.get("product_boundary")), source))
    return errors


def validate_capability_matrix(
    payload: Any,
    source: str,
    capability_registry: Any | None = None,
    mode_registry: Any | None = None,
) -> tuple[list[str], set[str]]:
    data = _mapping(payload)
    errors: list[str] = []
    if data.get("schema_version") != "node_capability_matrix.v0":
        errors.append(f"{source}: schema_version must be node_capability_matrix.v0")
    mode_ids = _mode_ids(mode_registry) or ALLOWED_MODES
    registry_ids = _capability_ids(capability_registry) or REQUIRED_CAPABILITIES
    records = _records_by_id(data.get("capabilities"), "capability_id", f"{source}: capabilities", errors)
    matrix_ids = set(records)
    errors.extend(_missing_items(matrix_ids, registry_ids, f"{source}: capabilities"))
    for capability_id, record in records.items():
        errors.extend(_validate_matrix_record(record, capability_id, source, mode_ids))
    errors.extend(_boundary_false_errors(_mapping(data.get("product_boundary")), source))
    return errors, matrix_ids


def validate_manifest_capability_refs(repo_root: Path, known_capability_ids: set[str]) -> list[str]:
    errors: list[str] = []
    for path in sorted((repo_root / MANIFEST_EXAMPLE_ROOT).glob("*/eureka_node_manifest.json")):
        payload = _load_json(path, errors)
        for item in _sequence(_mapping(payload).get("node_capabilities")):
            capability_id = _mapping(item).get("capability_id")
            if isinstance(capability_id, str) and capability_id not in known_capability_ids:
                errors.append(f"{_relative(repo_root, path)}: node_capabilities unknown {capability_id}")
    return errors


def validate_audit_report(payload: Any, source: str) -> list[str]:
    data = _mapping(payload)
    errors: list[str] = []
    if data.get("schema_version") != "track_b_03_report.v0":
        errors.append(f"{source}: schema_version must be track_b_03_report.v0")
    if data.get("task") != "TRACK-B-03":
        errors.append(f"{source}: task must be TRACK-B-03")
    errors.extend(_boundary_false_errors(_mapping(data.get("product_boundary")), source))
    truth = _mapping(data.get("truth_boundary"))
    for field in (
        "capability_is_runtime_permission",
        "capability_can_create_public_truth",
        "capability_can_create_accepted_evidence",
        "capability_can_mutate_master_index",
    ):
        if truth.get(field) is not False:
            errors.append(f"{source}: truth_boundary.{field} must be false")
    if truth.get("human_review_required_for_truth") is not True:
        errors.append(f"{source}: truth_boundary.human_review_required_for_truth must be true")
    return errors


def validate_node_capability_record(
    payload: Any,
    source: str,
    *,
    matrix_ids: set[str] | None = None,
) -> list[str]:
    data = _mapping(payload)
    errors: list[str] = []
    if data.get("schema_version") != "node_capability.v0":
        errors.append(f"{source}: schema_version must be node_capability.v0")
    errors.extend(_missing_items(data, _required_fields(), f"{source}: top-level"))
    capability_id = str(data.get("capability_id", ""))
    if matrix_ids is not None and capability_id not in matrix_ids:
        errors.append(f"{source}: capability_id {capability_id!r} is not present in capability matrix")

    status = str(data.get("capability_status", ""))
    family = str(data.get("capability_family", ""))
    side_effect = str(data.get("side_effect_class", ""))
    if status not in ALLOWED_STATUSES:
        errors.append(f"{source}: capability_status {status!r} is not allowed")
    if family not in ALLOWED_FAMILIES:
        errors.append(f"{source}: capability_family {family!r} is not allowed")
    if side_effect not in ALLOWED_SIDE_EFFECTS:
        errors.append(f"{source}: side_effect_class {side_effect!r} is not allowed")
    if status in CURRENT_STATUSES and side_effect not in CURRENT_SIDE_EFFECTS:
        errors.append(f"{source}: current capability cannot use side_effect_class {side_effect!r}")

    errors.extend(_unknown_items(set(_string_items(data.get("allowed_node_modes"))), ALLOWED_MODES, f"{source}: allowed_node_modes"))
    errors.extend(_unknown_items(set(_string_items(data.get("forbidden_node_modes"))), ALLOWED_MODES, f"{source}: forbidden_node_modes"))
    for ref in _string_items(data.get("required_node_policy_refs")):
        if not (REPO_ROOT / ref).is_file():
            errors.append(f"{source}: required_node_policy_ref does not exist: {ref}")
    errors.extend(_unknown_items(set(_string_items(data.get("required_review_gates"))), REVIEW_GATES, f"{source}: required_review_gates"))

    inputs = _mapping(data.get("input_categories"))
    outputs = _mapping(data.get("output_categories"))
    errors.extend(_unknown_items(set(_string_items(inputs.get("allowed"))), ALLOWED_INPUTS, f"{source}: input_categories.allowed"))
    errors.extend(_unknown_items(set(_string_items(inputs.get("forbidden"))), FORBIDDEN_INPUTS, f"{source}: input_categories.forbidden"))
    errors.extend(_missing_items(inputs.get("forbidden"), FORBIDDEN_INPUTS, f"{source}: input_categories.forbidden"))
    errors.extend(_unknown_items(set(_string_items(outputs.get("allowed"))), ALLOWED_OUTPUTS, f"{source}: output_categories.allowed"))
    errors.extend(_unknown_items(set(_string_items(outputs.get("forbidden"))), FORBIDDEN_OUTPUTS, f"{source}: output_categories.forbidden"))
    errors.extend(_missing_items(outputs.get("forbidden"), FORBIDDEN_OUTPUTS, f"{source}: output_categories.forbidden"))

    errors.extend(_validate_requirements(data, source, status))
    errors.extend(_false_field_errors(_mapping(data.get("truth_boundary")), TRUTH_FALSE_FIELDS, f"{source}: truth_boundary"))
    errors.extend(_boundary_false_errors(_mapping(data.get("product_boundary")), source))
    safety = _mapping(data.get("safety_boundary"))
    if safety.get("no_runtime_permission") is not True:
        errors.append(f"{source}: safety_boundary.no_runtime_permission must be true")
    errors.extend(_sensitive_key_errors(data, source))
    errors.extend(_private_path_errors(data, source))
    errors.extend(_forbidden_text_claim_errors(data, source))
    return errors


def _validate_matrix_record(record: Mapping[str, Any], capability_id: str, source: str, mode_ids: set[str]) -> list[str]:
    errors: list[str] = []
    status = str(record.get("capability_status", ""))
    side_effect = str(record.get("side_effect_class", ""))
    family = str(record.get("capability_family", ""))
    if status not in ALLOWED_STATUSES:
        errors.append(f"{source}: capability {capability_id} status {status!r} is not allowed")
    if family not in ALLOWED_FAMILIES:
        errors.append(f"{source}: capability {capability_id} family {family!r} is not allowed")
    if side_effect not in ALLOWED_SIDE_EFFECTS:
        errors.append(f"{source}: capability {capability_id} side_effect_class {side_effect!r} is not allowed")
    if status in CURRENT_STATUSES and side_effect not in CURRENT_SIDE_EFFECTS:
        errors.append(f"{source}: current capability {capability_id} cannot use side_effect_class {side_effect!r}")
    errors.extend(_unknown_items(set(_string_items(record.get("allowed_node_modes"))), mode_ids, f"{source}: capability {capability_id} allowed_node_modes"))
    errors.extend(_unknown_items(set(_string_items(record.get("forbidden_node_modes"))), mode_ids, f"{source}: capability {capability_id} forbidden_node_modes"))
    errors.extend(_unknown_items(set(_string_items(record.get("allowed_inputs"))), ALLOWED_INPUTS, f"{source}: capability {capability_id} allowed_inputs"))
    errors.extend(_unknown_items(set(_string_items(record.get("allowed_outputs"))), ALLOWED_OUTPUTS, f"{source}: capability {capability_id} allowed_outputs"))
    errors.extend(_unknown_items(set(_string_items(record.get("required_review_gates"))), REVIEW_GATES, f"{source}: capability {capability_id} required_review_gates"))
    errors.extend(_unknown_items(set(_string_items(record.get("dependencies"))), DEPENDENCY_TYPES, f"{source}: capability {capability_id} dependencies"))
    reqs = {
        "network_required": bool(record.get("network_required")),
        "source_access_required": bool(record.get("source_access_required")),
        "model_provider_required": bool(record.get("model_provider_required")),
        "credentials_required": bool(record.get("credentials_required")),
        "local_state_required": bool(record.get("local_state_required")),
    }
    if status in CURRENT_STATUSES and any(reqs.values()):
        true_fields = ", ".join(sorted(field for field, value in reqs.items() if value))
        errors.append(f"{source}: current capability {capability_id} must not require {true_fields}")
    if status not in FUTURE_OR_GATED_STATUSES and any(reqs.values()):
        errors.append(f"{source}: capability {capability_id} requires future/gated status for requirements")
    gates = set(_string_items(record.get("required_review_gates")))
    if any(reqs.values()) and "human_review_required" not in gates:
        errors.append(f"{source}: capability {capability_id} requirements require human_review_required")
    if (reqs["network_required"] or reqs["source_access_required"]) and "source_policy_review_required" not in gates:
        errors.append(f"{source}: capability {capability_id} source/network requirements require source_policy_review_required")
    if (reqs["network_required"] or reqs["model_provider_required"] or reqs["credentials_required"]) and "operator_approval_required_for_network" not in gates:
        errors.append(f"{source}: capability {capability_id} requirements require operator_approval_required_for_network")
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
    if status in CURRENT_STATUSES and any(required_flags.values()):
        true_sections = ", ".join(sorted(section for section, value in required_flags.items() if value))
        errors.append(f"{source}: current capability must not require {true_sections}")
    if any(required_flags.values()) and status not in FUTURE_OR_GATED_STATUSES:
        errors.append(f"{source}: capability with network/source/model/credential/local-state requirement must be future or gated")

    gates = set(_string_items(data.get("required_review_gates")))
    network = _mapping(data.get("network_requirement"))
    source_access = _mapping(data.get("source_access_requirement"))
    model = _mapping(data.get("model_provider_requirement"))
    credential = _mapping(data.get("credential_requirement"))
    local_state = _mapping(data.get("local_state_requirement"))
    if network.get("network_required") is True:
        for field in ("operator_approval_required", "source_policy_required", "kill_switch_required", "rate_or_budget_policy_required"):
            if network.get(field) is not True:
                errors.append(f"{source}: network_requirement.{field} must be true when network_required is true")
        if "operator_approval_required_for_network" not in gates:
            errors.append(f"{source}: network requirement requires operator_approval_required_for_network gate")
    if source_access.get("source_access_required") is True:
        if source_access.get("source_policy_required") is not True:
            errors.append(f"{source}: source_access_requirement.source_policy_required must be true when source access is required")
        if source_access.get("human_review_required") is not True:
            errors.append(f"{source}: source_access_requirement.human_review_required must be true when source access is required")
        if "source_policy_review_required" not in gates:
            errors.append(f"{source}: source access requirement requires source_policy_review_required gate")
    if model.get("model_provider_required") is True:
        if model.get("operator_approval_required") is not True:
            errors.append(f"{source}: model_provider_requirement.operator_approval_required must be true when model provider is required")
        if model.get("budget_policy_required") is not True:
            errors.append(f"{source}: model_provider_requirement.budget_policy_required must be true when model provider is required")
        if "operator_approval_required_for_network" not in gates:
            errors.append(f"{source}: model provider requirement requires operator_approval_required_for_network gate")
    if credential.get("credentials_required") is True and credential.get("operator_approval_required") is not True:
        errors.append(f"{source}: credential_requirement.operator_approval_required must be true when credentials are required")
    if local_state.get("local_state_required") is True and local_state.get("operator_approval_required") is not True:
        errors.append(f"{source}: local_state_requirement.operator_approval_required must be true when local state is required")
    return errors


def _format_plain(report: Mapping[str, Any]) -> str:
    lines = [f"validate_eureka_node_capability: {report['status']}"]
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


def _load_json(path: Path, errors: list[str]) -> Any:
    if not path.is_file():
        errors.append(f"{_relative(REPO_ROOT, path)}: missing file")
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"{_relative(REPO_ROOT, path)}: invalid JSON: {exc}")
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
        "capability_id",
        "capability_label",
        "capability_status",
        "capability_family",
        "description",
        "allowed_node_modes",
        "forbidden_node_modes",
        "required_node_policy_refs",
        "required_source_policy_refs",
        "required_review_gates",
        "input_categories",
        "output_categories",
        "side_effect_class",
        "network_requirement",
        "source_access_requirement",
        "local_state_requirement",
        "model_provider_requirement",
        "credential_requirement",
        "budget_requirement_future",
        "safety_boundary",
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
