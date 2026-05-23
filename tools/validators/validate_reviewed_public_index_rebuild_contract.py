#!/usr/bin/env python3
"""Validate the reviewed public-index rebuild contract milestone."""

from __future__ import annotations

from copy import deepcopy
import json
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping


REPO_ROOT = Path(__file__).resolve().parents[2]

CONTRACT_PATHS = [
    "contracts/index/master/reviewed_public_index_rebuild.v0.json",
    "contracts/index/master/reviewed_public_record_proposal.v0.json",
]

POLICY_PATHS = [
    "control/inventory/review/reviewed_public_index_rebuild_policy.json",
    "control/inventory/review/reviewed_public_index_input_policy.json",
    "control/inventory/review/reviewed_public_index_output_policy.json",
    "control/inventory/review/reviewed_public_index_record_policy.json",
    "control/inventory/review/reviewed_public_index_path_policy.json",
    "control/inventory/review/reviewed_public_index_truth_policy.json",
]

DOC_PATHS = [
    "docs/reference/REVIEWED_PUBLIC_INDEX_REBUILD_CONTRACT.md",
    "docs/reference/REVIEWED_PUBLIC_RECORD_PROPOSAL_CONTRACT.md",
    "docs/architecture/REVIEWED_PUBLIC_INDEX_REBUILD_MODEL.md",
    "docs/operations/REVIEWED_PUBLIC_INDEX_REBUILD_REVIEW.md",
]

EXAMPLE_REBUILD_PATHS = [
    "examples/index/reviewed_public_rebuilds/minimal_rebuild_contract_v0.json",
    "examples/index/reviewed_public_rebuilds/ready_candidate_rebuild_input_v0.json",
    "examples/index/reviewed_public_rebuilds/missing_evidence_rebuild_blocked_v0.json",
    "examples/index/reviewed_public_rebuilds/policy_blocked_rebuild_v0.json",
]

EXAMPLE_PROPOSAL_PATHS = [
    "examples/index/reviewed_public_records/minimal_reviewed_public_record_proposal_v0.json",
    "examples/index/reviewed_public_records/software_candidate_record_proposal_v0.json",
    "examples/index/reviewed_public_records/source_record_proposal_v0.json",
    "examples/index/reviewed_public_records/need_record_proposal_v0.json",
    "examples/index/reviewed_public_records/policy_blocked_record_proposal_v0.json",
]

AUDIT_PATHS = [
    "control/audits/track-b-20-reviewed-public-index-rebuild-contract-v0/README.md",
    "control/audits/track-b-20-reviewed-public-index-rebuild-contract-v0/track_b_20_report.json",
    "control/audits/track-b-20-reviewed-public-index-rebuild-contract-v0/reviewed_public_index_rebuild_readiness.md",
    "control/audits/track-b-20-reviewed-public-index-rebuild-contract-v0/validation.md",
]

ALLOWED_REBUILD_STATUSES = [
    "example_only",
    "contract_only",
    "planning_only",
    "ready_for_future_dry_run",
    "blocked_missing_evidence",
    "blocked_missing_review",
    "blocked_policy",
    "blocked_rights",
    "blocked_risk",
    "blocked_conflict",
    "blocked_duplicate_uncertain",
    "deferred",
    "not_evaluable",
    "future_runtime",
]

CURRENT_REBUILD_STATUSES = [status for status in ALLOWED_REBUILD_STATUSES if status != "future_runtime"]

ALLOWED_PROPOSAL_STATUSES = [
    "example_only",
    "proposed",
    "ready_for_review",
    "ready_for_future_rebuild_dry_run",
    "blocked_missing_evidence",
    "blocked_missing_review",
    "blocked_policy",
    "blocked_rights",
    "blocked_risk",
    "blocked_conflict",
    "blocked_duplicate_uncertain",
    "rejected",
    "deferred",
    "accepted_public_future",
]

CURRENT_PROPOSAL_STATUSES = [status for status in ALLOWED_PROPOSAL_STATUSES if status != "accepted_public_future"]

ALLOWED_PROPOSAL_TYPES = [
    "object_public_record",
    "source_public_record",
    "need_public_record",
    "candidate_public_record_future",
    "evidence_summary_public_record",
    "compatibility_public_record",
    "representation_public_record",
    "absence_public_record",
    "pack_public_record_future",
    "policy_blocked_record",
    "not_evaluable_record",
]

ALLOWED_INPUT_TYPES = [
    "candidate_promotion_dry_run",
    "local_review_queue_entry",
    "candidate_record",
    "evidence_ledger_record",
    "source_cache_record",
    "source_cache_to_evidence_bridge_result",
    "search_need_record",
    "search_miss_record",
    "query_observation_record",
    "source_pack_future",
    "evidence_pack_future",
    "contribution_pack_future",
    "review_pack_future",
]

FORBIDDEN_INPUT_TYPES = [
    "unreviewed_candidate",
    "unreviewed_evidence_candidate",
    "unreviewed_source_observation",
    "unreviewed_source_cache_record",
    "unreviewed_AI_draft",
    "scraped_result",
    "unapproved_live_source_result",
    "private_user_file",
    "secret_or_credential",
    "executable_download",
    "installer_payload",
    "account_session_data",
    "telemetry_stream",
]

ALLOWED_OUTPUT_TYPES = [
    "reviewed_public_record_proposal",
    "public_search_card_candidate",
    "public_index_rebuild_manifest_future",
    "public_index_delta_preview_future",
    "public_limitations_report",
    "public_no_claim_summary",
    "review_blocker_report",
    "rebuild_audit_report",
]

FORBIDDEN_OUTPUT_TYPES = [
    "public_index_mutation_current",
    "master_index_mutation",
    "accepted_evidence_truth_without_review",
    "accepted_candidate_truth_without_review",
    "rights_clearance",
    "malware_safety",
    "verified_installability",
    "exhaustive_global_search_proof",
    "production_readiness_claim",
]

REBUILD_TRUTH_FALSE_FIELDS = [
    "rebuild_contract_is_public_truth",
    "record_proposal_is_accepted_truth",
    "record_proposal_is_accepted_evidence",
    "public_index_mutation_allowed_current",
    "master_index_mutation_allowed_current",
]

REBUILD_TRUTH_TRUE_FIELDS = ["human_review_required_for_actual_rebuild"]

PROPOSAL_TRUTH_FALSE_FIELDS = [
    "record_proposal_is_public_truth",
    "record_proposal_is_accepted_truth",
    "record_proposal_is_accepted_evidence",
    "record_proposal_mutates_public_index_current",
    "record_proposal_mutates_master_index_current",
    "record_proposal_can_claim_rights_clearance",
    "record_proposal_can_claim_malware_safety",
    "record_proposal_can_claim_verified_installability",
]

PROPOSAL_TRUTH_TRUE_FIELDS = ["human_review_required_for_actual_publication"]

REBUILD_PRODUCT_FALSE_FIELDS = [
    "implemented_public_index_rebuild_runtime",
    "implemented_master_index_mutation",
    "implemented_hosted_review_runtime",
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
    "enabled_model_provider_calls",
    "mutated_public_index",
    "mutated_master_index",
    "claimed_rights_clearance",
    "claimed_malware_safety",
    "claimed_verified_installability",
    "claimed_exhaustive_global_search",
    "claimed_production_readiness",
]

PROPOSAL_PRODUCT_FALSE_FIELDS = [
    "implemented_public_index_rebuild_runtime",
    "created_public_record_current",
    "mutated_public_index",
    "mutated_master_index",
    "claimed_rights_clearance",
    "claimed_malware_safety",
    "claimed_verified_installability",
    "claimed_exhaustive_global_search",
    "claimed_production_readiness",
]

REQUIRED_PUBLIC_RECORD_FIELDS = [
    "record_id",
    "record_kind",
    "display_label",
    "review_status",
    "public_search_effect_status",
]

REQUIRED_SOURCE_SUMMARY_FIELDS = ["source_refs", "source_posture", "source_limitations"]
REQUIRED_EVIDENCE_SUMMARY_FIELDS = ["evidence_refs", "evidence_posture", "evidence_limitations"]
REQUIRED_RIGHTS_RISK_FIELDS = [
    "rights_clearance_claimed",
    "malware_safety_claimed",
    "verified_installability_claimed",
    "review_required",
]
REQUIRED_LIMITATION_FIELDS = ["limitations", "no_claims"]


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def require_files(paths: Iterable[str], errors: list[str]) -> None:
    for raw_path in paths:
        if not (REPO_ROOT / raw_path).exists():
            errors.append(f"missing required file: {raw_path}")


def require_values(label: str, actual: Iterable[str], expected: Iterable[str], errors: list[str]) -> None:
    actual_set = set(actual)
    expected_set = set(expected)
    missing = sorted(expected_set - actual_set)
    extra = sorted(actual_set - expected_set)
    if missing:
        errors.append(f"{label} missing values: {missing}")
    if extra:
        errors.append(f"{label} has unexpected values: {extra}")


def expect_false(mapping: Mapping[str, Any], field: str, label: str, errors: list[str]) -> None:
    if mapping.get(field) is not False:
        errors.append(f"{label}.{field} must be false")


def expect_true(mapping: Mapping[str, Any], field: str, label: str, errors: list[str]) -> None:
    if mapping.get(field) is not True:
        errors.append(f"{label}.{field} must be true")


def require_keys(mapping: Mapping[str, Any], keys: Iterable[str], label: str, errors: list[str]) -> None:
    for key in keys:
        if key not in mapping:
            errors.append(f"{label} missing required key: {key}")


def list_values(values: Any) -> list[str]:
    if isinstance(values, list):
        return [str(value) for value in values]
    return []


def validate_contract_payload(payload: Mapping[str, Any], label: str) -> list[str]:
    errors: list[str] = []
    if payload.get("type") != "object":
        errors.append(f"{label} must be an object schema")
    for key in ["$schema", "$id", "title", "required", "properties", "x-contract_only", "x-no_public_index_mutation", "x-no_master_index_mutation", "x-no_auto_acceptance"]:
        if key not in payload:
            errors.append(f"{label} missing contract key: {key}")
    for key in ["x-contract_only", "x-no_public_index_mutation", "x-no_master_index_mutation", "x-no_auto_acceptance"]:
        expect_true(payload, key, label, errors)
    if "reviewed_public_index_rebuild" in str(payload.get("$id", "")):
        if payload.get("x-no_runtime_implemented") is not True:
            errors.append(f"{label}.x-no_runtime_implemented must be true")
    return errors


def validate_rebuild_payload(payload: Mapping[str, Any], label: str, repo_root: Path = REPO_ROOT) -> list[str]:
    del repo_root
    errors: list[str] = []
    required = [
        "schema_version",
        "rebuild_contract_id",
        "rebuild_status",
        "rebuild_input_policy",
        "rebuild_output_policy",
        "reviewed_input_refs",
        "blocked_input_refs",
        "evidence_requirements",
        "review_requirements",
        "conflict_policy",
        "duplicate_policy",
        "public_index_mutation_policy",
        "master_index_mutation_policy",
        "truth_boundary",
        "product_boundary",
    ]
    require_keys(payload, required, label, errors)
    if payload.get("schema_version") != "reviewed_public_index_rebuild.v0":
        errors.append(f"{label}.schema_version must be reviewed_public_index_rebuild.v0")
    status = str(payload.get("rebuild_status", ""))
    if status not in CURRENT_REBUILD_STATUSES:
        errors.append(f"{label}.rebuild_status is not allowed for current examples: {status}")

    input_policy = payload.get("rebuild_input_policy", {})
    if isinstance(input_policy, Mapping):
        allowed_inputs = list_values(input_policy.get("allowed_input_types"))
        for input_type in allowed_inputs:
            if input_type in FORBIDDEN_INPUT_TYPES:
                errors.append(f"{label} allowed forbidden input type: {input_type}")
            elif input_type not in ALLOWED_INPUT_TYPES:
                errors.append(f"{label} has unknown allowed input type: {input_type}")

    output_policy = payload.get("rebuild_output_policy", {})
    if isinstance(output_policy, Mapping):
        allowed_outputs = list_values(output_policy.get("allowed_output_types"))
        for output_type in allowed_outputs:
            if output_type in FORBIDDEN_OUTPUT_TYPES:
                errors.append(f"{label} allowed forbidden output type: {output_type}")
            elif output_type not in ALLOWED_OUTPUT_TYPES:
                errors.append(f"{label} has unknown allowed output type: {output_type}")

    reviewed_inputs = payload.get("reviewed_input_refs", [])
    blocked_inputs = payload.get("blocked_input_refs", [])
    for index, entry in enumerate(reviewed_inputs if isinstance(reviewed_inputs, list) else []):
        if not isinstance(entry, Mapping):
            errors.append(f"{label}.reviewed_input_refs[{index}] must be object")
            continue
        input_type = str(entry.get("input_type", ""))
        if input_type in FORBIDDEN_INPUT_TYPES:
            errors.append(f"{label}.reviewed_input_refs[{index}] uses forbidden input type: {input_type}")
        if input_type not in ALLOWED_INPUT_TYPES:
            errors.append(f"{label}.reviewed_input_refs[{index}] has unknown input type: {input_type}")
        if not entry.get("evidence_refs") and not entry.get("limitations"):
            errors.append(f"{label}.reviewed_input_refs[{index}] must preserve evidence refs or limitations")

    for index, entry in enumerate(blocked_inputs if isinstance(blocked_inputs, list) else []):
        if not isinstance(entry, Mapping):
            errors.append(f"{label}.blocked_input_refs[{index}] must be object")
            continue
        if str(entry.get("input_type", "")) in FORBIDDEN_INPUT_TYPES:
            errors.append(f"{label}.blocked_input_refs[{index}] uses forbidden input type")
        if not entry.get("limitations"):
            errors.append(f"{label}.blocked_input_refs[{index}] must preserve limitations")

    if status == "ready_for_future_dry_run":
        if not reviewed_inputs:
            errors.append(f"{label} ready rebuild must include reviewed inputs")
        if not payload.get("proposed_public_records"):
            errors.append(f"{label} ready rebuild must include proposed public record refs")
        evidence_present = bool(payload.get("evidence_requirements", {}).get("evidence_refs_present"))
        review_present = bool(payload.get("review_requirements", {}).get("review_refs_present"))
        if not evidence_present:
            errors.append(f"{label} ready rebuild must have evidence refs present")
        if not review_present:
            errors.append(f"{label} ready rebuild must have review refs present")
        if blocked_inputs or payload.get("blocked_records"):
            errors.append(f"{label} ready rebuild cannot include blocked inputs or records")

    if status == "blocked_missing_evidence" and not payload.get("blocked_records"):
        errors.append(f"{label} missing evidence status must include blocked_records")
    if status in {"blocked_policy", "blocked_rights", "blocked_risk"} and not blocked_inputs:
        errors.append(f"{label} blocked status must include blocked_input_refs")

    conflict_policy = payload.get("conflict_policy", {})
    if isinstance(conflict_policy, Mapping):
        expect_true(conflict_policy, "conflict_preservation_required", f"{label}.conflict_policy", errors)
        expect_false(conflict_policy, "automatic_conflict_resolution_allowed", f"{label}.conflict_policy", errors)
        if conflict_policy.get("conflict_status") == "conflict_detected" and status != "blocked_conflict":
            errors.append(f"{label} conflict_detected must use blocked_conflict status")

    duplicate_policy = payload.get("duplicate_policy", {})
    if isinstance(duplicate_policy, Mapping):
        expect_true(duplicate_policy, "duplicate_preservation_required", f"{label}.duplicate_policy", errors)
        expect_false(duplicate_policy, "automatic_merge_allowed", f"{label}.duplicate_policy", errors)
        expect_false(duplicate_policy, "automatic_delete_allowed", f"{label}.duplicate_policy", errors)
        if duplicate_policy.get("duplicate_status") == "duplicate_possible" and status != "blocked_duplicate_uncertain":
            errors.append(f"{label} duplicate_possible must use blocked_duplicate_uncertain status")

    for field in ["public_index_mutation_allowed_current"]:
        expect_false(payload.get("public_index_mutation_policy", {}), field, f"{label}.public_index_mutation_policy", errors)
    for field in ["master_index_mutation_allowed_current"]:
        expect_false(payload.get("master_index_mutation_policy", {}), field, f"{label}.master_index_mutation_policy", errors)
    for field in REBUILD_TRUTH_FALSE_FIELDS:
        expect_false(payload.get("truth_boundary", {}), field, f"{label}.truth_boundary", errors)
    for field in REBUILD_TRUTH_TRUE_FIELDS:
        expect_true(payload.get("truth_boundary", {}), field, f"{label}.truth_boundary", errors)
    for field in REBUILD_PRODUCT_FALSE_FIELDS:
        expect_false(payload.get("product_boundary", {}), field, f"{label}.product_boundary", errors)
    return errors


def validate_proposal_payload(payload: Mapping[str, Any], label: str, repo_root: Path = REPO_ROOT) -> list[str]:
    del repo_root
    errors: list[str] = []
    required = [
        "schema_version",
        "reviewed_public_record_proposal_id",
        "proposal_status",
        "proposal_type",
        "proposed_public_record",
        "source_summary",
        "evidence_summary",
        "rights_summary",
        "risk_summary",
        "limitation_summary",
        "review_summary",
        "conflict_summary",
        "duplicate_summary",
        "publication_constraints",
        "truth_boundary",
        "product_boundary",
    ]
    require_keys(payload, required, label, errors)
    if payload.get("schema_version") != "reviewed_public_record_proposal.v0":
        errors.append(f"{label}.schema_version must be reviewed_public_record_proposal.v0")
    status = str(payload.get("proposal_status", ""))
    proposal_type = str(payload.get("proposal_type", ""))
    if status not in CURRENT_PROPOSAL_STATUSES:
        errors.append(f"{label}.proposal_status is not allowed for current examples: {status}")
    if proposal_type not in ALLOWED_PROPOSAL_TYPES:
        errors.append(f"{label}.proposal_type is not allowed: {proposal_type}")

    require_keys(payload.get("proposed_public_record", {}), REQUIRED_PUBLIC_RECORD_FIELDS, f"{label}.proposed_public_record", errors)
    require_keys(payload.get("source_summary", {}), REQUIRED_SOURCE_SUMMARY_FIELDS, f"{label}.source_summary", errors)
    require_keys(payload.get("evidence_summary", {}), REQUIRED_EVIDENCE_SUMMARY_FIELDS, f"{label}.evidence_summary", errors)
    require_keys(payload.get("limitation_summary", {}), REQUIRED_LIMITATION_FIELDS, f"{label}.limitation_summary", errors)

    rights_summary = payload.get("rights_summary", {})
    risk_summary = payload.get("risk_summary", {})
    combined_rights_risk = {
        "rights_clearance_claimed": rights_summary.get("rights_clearance_claimed") if isinstance(rights_summary, Mapping) else None,
        "malware_safety_claimed": risk_summary.get("malware_safety_claimed") if isinstance(risk_summary, Mapping) else None,
        "verified_installability_claimed": risk_summary.get("verified_installability_claimed") if isinstance(risk_summary, Mapping) else None,
        "review_required": bool(
            isinstance(rights_summary, Mapping)
            and isinstance(risk_summary, Mapping)
            and rights_summary.get("review_required") is True
            and risk_summary.get("review_required") is True
        ),
    }
    require_keys(combined_rights_risk, REQUIRED_RIGHTS_RISK_FIELDS, f"{label}.rights_risk", errors)
    expect_false(combined_rights_risk, "rights_clearance_claimed", f"{label}.rights_risk", errors)
    expect_false(combined_rights_risk, "malware_safety_claimed", f"{label}.rights_risk", errors)
    expect_false(combined_rights_risk, "verified_installability_claimed", f"{label}.rights_risk", errors)
    expect_true(combined_rights_risk, "review_required", f"{label}.rights_risk", errors)

    if status == "ready_for_future_rebuild_dry_run":
        if not payload.get("source_evidence_refs"):
            errors.append(f"{label} ready proposal must include source_evidence_refs")
        if not payload.get("source_review_refs"):
            errors.append(f"{label} ready proposal must include source_review_refs")
    if status.startswith("blocked_") and payload.get("publication_constraints", {}).get("public_index_mutation_allowed_current") is not False:
        errors.append(f"{label} blocked proposal must not allow public index mutation")

    conflict_summary = payload.get("conflict_summary", {})
    if isinstance(conflict_summary, Mapping):
        expect_true(conflict_summary, "conflict_preserved", f"{label}.conflict_summary", errors)
        expect_false(conflict_summary, "automatic_resolution_allowed", f"{label}.conflict_summary", errors)
        if conflict_summary.get("conflict_status") == "conflict_detected" and status != "blocked_conflict":
            errors.append(f"{label} conflict_detected must use blocked_conflict status")

    duplicate_summary = payload.get("duplicate_summary", {})
    if isinstance(duplicate_summary, Mapping):
        expect_true(duplicate_summary, "duplicate_preserved", f"{label}.duplicate_summary", errors)
        expect_false(duplicate_summary, "automatic_merge_allowed", f"{label}.duplicate_summary", errors)
        expect_false(duplicate_summary, "automatic_delete_allowed", f"{label}.duplicate_summary", errors)
        if duplicate_summary.get("duplicate_status") == "duplicate_possible" and status != "blocked_duplicate_uncertain":
            errors.append(f"{label} duplicate_possible must use blocked_duplicate_uncertain status")

    expect_false(payload.get("publication_constraints", {}), "public_index_mutation_allowed_current", f"{label}.publication_constraints", errors)
    expect_false(payload.get("publication_constraints", {}), "master_index_mutation_allowed_current", f"{label}.publication_constraints", errors)
    for field in PROPOSAL_TRUTH_FALSE_FIELDS:
        expect_false(payload.get("truth_boundary", {}), field, f"{label}.truth_boundary", errors)
    for field in PROPOSAL_TRUTH_TRUE_FIELDS:
        expect_true(payload.get("truth_boundary", {}), field, f"{label}.truth_boundary", errors)
    for field in PROPOSAL_PRODUCT_FALSE_FIELDS:
        expect_false(payload.get("product_boundary", {}), field, f"{label}.product_boundary", errors)
    return errors


def validate_path_policy_payload(payload: Mapping[str, Any], label: str = "path_policy") -> list[str]:
    errors: list[str] = []
    allowed = list_values(payload.get("allowed_output_roots_current"))
    forbidden = list_values(payload.get("forbidden_output_roots"))
    for required in [
        "examples/index/reviewed_public_rebuilds/",
        "examples/index/reviewed_public_records/",
        "control/audits/**/",
        "explicit temp test directory",
    ]:
        if required not in allowed:
            errors.append(f"{label} must allow {required}")
    for root in [
        "site/dist/",
        "site/dist/data/public_index/",
        "runtime/",
        "contracts/",
        "control/inventory/publication/",
        "master-index production roots",
        "public-index production roots",
        ".aide.local/",
        ".local/eureka/",
        ".cache/eureka/",
    ]:
        if root not in forbidden:
            errors.append(f"{label} must forbid {root}")
        if root in allowed:
            errors.append(f"{label} must not allow forbidden root {root}")
    for field in ["current_task_writes_public_index_artifacts", "current_task_writes_site_dist", "current_task_writes_data_public_index"]:
        expect_false(payload, field, label, errors)
    return errors


def validate_truth_policy_payload(payload: Mapping[str, Any], label: str = "truth_policy") -> list[str]:
    errors: list[str] = []
    for field in [
        "automatic_candidate_acceptance_allowed",
        "automatic_evidence_acceptance_allowed",
        "automatic_public_record_creation_allowed",
        "automatic_public_index_mutation_allowed",
        "automatic_master_index_mutation_allowed",
        "automatic_rights_clearance_allowed",
        "automatic_malware_safety_allowed",
        "automatic_installability_verification_allowed",
    ]:
        expect_false(payload, field, label, errors)
    for field in ["public_record_requires_review", "evidence_summary_requires_review", "source_summary_requires_review"]:
        expect_true(payload, field, label, errors)
    truth = payload.get("truth_boundary", {})
    for field in REBUILD_TRUTH_FALSE_FIELDS:
        expect_false(truth, field, f"{label}.truth_boundary", errors)
    for field in REBUILD_TRUTH_TRUE_FIELDS:
        expect_true(truth, field, f"{label}.truth_boundary", errors)
    return errors


def validate_policies(errors: list[str]) -> None:
    policies: dict[str, Any] = {}
    for raw_path in POLICY_PATHS:
        try:
            policies[raw_path] = load_json(REPO_ROOT / raw_path)
        except json.JSONDecodeError as exc:
            errors.append(f"{raw_path} is not valid JSON: {exc}")

    rebuild_policy = policies.get(POLICY_PATHS[0], {})
    require_values("rebuild_policy.allowed_rebuild_statuses", rebuild_policy.get("allowed_rebuild_statuses", []), ALLOWED_REBUILD_STATUSES, errors)
    require_values("rebuild_policy.current_example_rebuild_statuses", rebuild_policy.get("current_example_rebuild_statuses", []), CURRENT_REBUILD_STATUSES, errors)
    for field in ["current_rebuild_runtime_enabled", "current_public_index_mutation_enabled", "current_master_index_mutation_enabled"]:
        expect_false(rebuild_policy, field, "rebuild_policy", errors)
    expect_true(rebuild_policy, "future_dry_run_allowed", "rebuild_policy", errors)
    expect_true(rebuild_policy, "future_actual_rebuild_requires_operator_approval", "rebuild_policy", errors)

    input_policy = policies.get(POLICY_PATHS[1], {})
    require_values("input_policy.allowed_future_input_types", input_policy.get("allowed_future_input_types", []), ALLOWED_INPUT_TYPES, errors)
    require_values("input_policy.forbidden_input_types", input_policy.get("forbidden_input_types", []), FORBIDDEN_INPUT_TYPES, errors)
    for field in [
        "all_input_records_must_preserve_review_refs_or_limitations",
        "evidence_backed_records_must_have_source_or_provenance_refs_where_available",
        "unresolved_conflicts_must_be_preserved",
        "duplicate_uncertainty_must_be_preserved",
        "missing_evidence_must_block_or_defer",
        "rights_risk_blocks_must_block_or_defer",
    ]:
        expect_true(input_policy.get("requirements", {}), field, "input_policy.requirements", errors)

    output_policy = policies.get(POLICY_PATHS[2], {})
    require_values("output_policy.allowed_future_output_types", output_policy.get("allowed_future_output_types", []), ALLOWED_OUTPUT_TYPES, errors)
    require_values("output_policy.forbidden_output_types", output_policy.get("forbidden_output_types", []), FORBIDDEN_OUTPUT_TYPES, errors)
    for field in ["writes_public_index_current", "writes_master_index_current", "creates_public_truth_current"]:
        expect_false(output_policy, field, "output_policy", errors)
    expect_true(output_policy, "requires_review_for_public_record_proposal", "output_policy", errors)

    record_policy = policies.get(POLICY_PATHS[3], {})
    require_values("record_policy.allowed_proposal_types", record_policy.get("allowed_proposal_types", []), ALLOWED_PROPOSAL_TYPES, errors)
    require_values("record_policy.allowed_proposal_statuses", record_policy.get("allowed_proposal_statuses", []), ALLOWED_PROPOSAL_STATUSES, errors)
    require_values("record_policy.current_example_proposal_statuses", record_policy.get("current_example_proposal_statuses", []), CURRENT_PROPOSAL_STATUSES, errors)
    require_values("record_policy.required_public_record_fields", record_policy.get("required_public_record_fields", []), REQUIRED_PUBLIC_RECORD_FIELDS, errors)
    require_values("record_policy.required_source_summary_fields", record_policy.get("required_source_summary_fields", []), REQUIRED_SOURCE_SUMMARY_FIELDS, errors)
    require_values("record_policy.required_evidence_summary_fields", record_policy.get("required_evidence_summary_fields", []), REQUIRED_EVIDENCE_SUMMARY_FIELDS, errors)
    require_values("record_policy.required_rights_risk_fields", record_policy.get("required_rights_risk_fields", []), REQUIRED_RIGHTS_RISK_FIELDS, errors)
    require_values("record_policy.required_limitation_fields", record_policy.get("required_limitation_fields", []), REQUIRED_LIMITATION_FIELDS, errors)
    expect_true(record_policy, "conflict_preservation_required", "record_policy", errors)
    expect_true(record_policy, "duplicate_preservation_required", "record_policy", errors)

    errors.extend(validate_path_policy_payload(policies.get(POLICY_PATHS[4], {})))
    errors.extend(validate_truth_policy_payload(policies.get(POLICY_PATHS[5], {})))


def validate_examples(errors: list[str]) -> tuple[int, int]:
    rebuild_count = 0
    proposal_count = 0
    ids: set[str] = set()
    for raw_path in EXAMPLE_REBUILD_PATHS:
        payload = load_json(REPO_ROOT / raw_path)
        item_errors = validate_rebuild_payload(payload, raw_path, REPO_ROOT)
        if item_errors:
            errors.extend(item_errors)
        rebuild_id = str(payload.get("rebuild_contract_id", ""))
        if rebuild_id in ids:
            errors.append(f"duplicate rebuild_contract_id: {rebuild_id}")
        ids.add(rebuild_id)
        rebuild_count += 1
    for raw_path in EXAMPLE_PROPOSAL_PATHS:
        payload = load_json(REPO_ROOT / raw_path)
        item_errors = validate_proposal_payload(payload, raw_path, REPO_ROOT)
        if item_errors:
            errors.extend(item_errors)
        proposal_id = str(payload.get("reviewed_public_record_proposal_id", ""))
        if proposal_id in ids:
            errors.append(f"duplicate proposal id: {proposal_id}")
        ids.add(proposal_id)
        proposal_count += 1
    return rebuild_count, proposal_count


def validate_boundary_guards(errors: list[str]) -> None:
    rebuild = load_json(REPO_ROOT / EXAMPLE_REBUILD_PATHS[0])
    proposal = load_json(REPO_ROOT / EXAMPLE_PROPOSAL_PATHS[0])
    for field in REBUILD_TRUTH_FALSE_FIELDS:
        mutated = deepcopy(rebuild)
        mutated.setdefault("truth_boundary", {})[field] = True
        if not validate_rebuild_payload(mutated, f"mutated.{field}", REPO_ROOT):
            errors.append(f"rebuild truth-boundary mutation accepted: {field}")
    for field in REBUILD_PRODUCT_FALSE_FIELDS:
        mutated = deepcopy(rebuild)
        mutated.setdefault("product_boundary", {})[field] = True
        if not validate_rebuild_payload(mutated, f"mutated.{field}", REPO_ROOT):
            errors.append(f"rebuild product-boundary mutation accepted: {field}")
            break
    for field in PROPOSAL_TRUTH_FALSE_FIELDS:
        mutated = deepcopy(proposal)
        mutated.setdefault("truth_boundary", {})[field] = True
        if not validate_proposal_payload(mutated, f"mutated.{field}", REPO_ROOT):
            errors.append(f"proposal truth-boundary mutation accepted: {field}")
    for field in PROPOSAL_PRODUCT_FALSE_FIELDS:
        mutated = deepcopy(proposal)
        mutated.setdefault("product_boundary", {})[field] = True
        if not validate_proposal_payload(mutated, f"mutated.{field}", REPO_ROOT):
            errors.append(f"proposal product-boundary mutation accepted: {field}")
            break


def validate_no_public_artifact_writes(errors: list[str]) -> None:
    b20_roots = [
        "contracts/index/master/reviewed_public_index_rebuild.v0.json",
        "contracts/index/master/reviewed_public_record_proposal.v0.json",
        "examples/index/reviewed_public_rebuilds",
        "examples/index/reviewed_public_records",
        "control/audits/track-b-20-reviewed-public-index-rebuild-contract-v0",
    ]
    for raw_path in b20_roots:
        path = REPO_ROOT / raw_path
        if "site/dist" in path.as_posix() or "site/dist/data/public_index" in path.as_posix():
            errors.append(f"B20 artifact is under forbidden public-index output root: {raw_path}")


def validate_reviewed_public_index_rebuild_contract(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    if repo_root != REPO_ROOT:
        raise ValueError("validator expects the repository root")
    errors: list[str] = []
    require_files(CONTRACT_PATHS, errors)
    require_files(POLICY_PATHS, errors)
    require_files(DOC_PATHS, errors)
    require_files(EXAMPLE_REBUILD_PATHS, errors)
    require_files(EXAMPLE_PROPOSAL_PATHS, errors)
    require_files(AUDIT_PATHS, errors)

    for raw_path in CONTRACT_PATHS:
        if (REPO_ROOT / raw_path).exists():
            payload = load_json(REPO_ROOT / raw_path)
            errors.extend(validate_contract_payload(payload, raw_path))

    validate_policies(errors)
    rebuild_count, proposal_count = validate_examples(errors)
    validate_boundary_guards(errors)
    validate_no_public_artifact_writes(errors)
    return {
        "schema_version": "reviewed_public_index_rebuild_validation.v0",
        "status": "pass" if not errors else "fail",
        "checked_files": {
            "contracts": sorted(CONTRACT_PATHS),
            "policies": sorted(POLICY_PATHS),
            "docs": sorted(DOC_PATHS),
            "rebuild_examples": sorted(EXAMPLE_REBUILD_PATHS),
            "proposal_examples": sorted(EXAMPLE_PROPOSAL_PATHS),
            "audit": sorted(AUDIT_PATHS),
        },
        "rebuild_example_count": rebuild_count,
        "proposal_example_count": proposal_count,
        "error_count": len(errors),
        "errors": sorted(errors),
    }


def main() -> int:
    report = validate_reviewed_public_index_rebuild_contract()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
