from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_VERSION = "0.1.0"

PACK_CONTRACT_PATH = "contracts/view/pages/pack_page.v0.json"
TASK_CONTRACT_PATH = "contracts/view/pages/task_page.v0.json"
REVIEW_CONTRACT_PATH = "contracts/view/pages/review_page.v0.json"
PACK_POLICY_INVENTORY = "control/inventory/publication/pack_page_view_model_policy.json"
TASK_POLICY_INVENTORY = "control/inventory/publication/task_page_view_model_policy.json"
REVIEW_POLICY_INVENTORY = "control/inventory/publication/review_page_view_model_policy.json"
REPRESENTATION_INVENTORY = "control/inventory/publication/representation_profiles.json"
SEMANTIC_PARITY_INVENTORY = "control/inventory/publication/semantic_renderer_parity_policy.json"
ROUTE_MATRIX_INVENTORY = "control/inventory/publication/route_view_representation_matrix.json"

PACK_EXAMPLE_PATHS = [
    "examples/view_models/pack_page/contribution_pack_page_v0.json",
    "examples/view_models/pack_page/evidence_pack_page_v0.json",
    "examples/view_models/pack_page/minimal_pack_page_v0.json",
    "examples/view_models/pack_page/source_pack_page_v0.json",
]
TASK_EXAMPLE_PATHS = [
    "examples/view_models/task_page/minimal_task_page_v0.json",
    "examples/view_models/task_page/policy_blocked_task_page_v0.json",
    "examples/view_models/task_page/search_need_task_page_future_v0.json",
    "examples/view_models/task_page/source_lead_task_page_future_v0.json",
]
REVIEW_EXAMPLE_PATHS = [
    "examples/view_models/review_page/defer_review_page_v0.json",
    "examples/view_models/review_page/minimal_review_page_v0.json",
    "examples/view_models/review_page/promotion_requirements_review_page_v0.json",
    "examples/view_models/review_page/reject_review_page_v0.json",
]

REQUIRED_SCHEMA_FIELDS = {"$schema", "$id", "title", "description", "type", "required", "properties"}
PACK_VIEW_FIELDS = {
    "schema_version", "view_model_id", "view_family", "route_family", "canonical_route", "page_title",
    "page_status", "pack", "pack_identity", "pack_type", "pack_status", "pack_validation_summary",
    "pack_contents_summary", "referenced_sources", "referenced_evidence", "referenced_index_records",
    "referenced_contribution_items", "related_candidate_refs", "related_need_refs", "related_review_refs",
    "related_object_refs", "related_source_refs", "import_summary", "quarantine_summary", "review_summary",
    "rights_summary", "risk_summary", "privacy_summary", "provenance_summary", "action_summary", "actions",
    "blocked_actions", "limitations", "warnings", "representation_hints", "semantic_requirements",
    "generated_from", "no_goals", "notes",
}
TASK_VIEW_FIELDS = {
    "schema_version", "view_model_id", "view_family", "route_family", "canonical_route", "page_title",
    "page_status", "task", "task_identity", "task_type", "task_status", "task_scope", "input_summary",
    "allowed_actions", "forbidden_actions", "output_contract", "expected_outputs", "related_need_refs",
    "related_candidate_refs", "related_source_refs", "related_pack_refs", "related_review_refs",
    "node_policy_summary_future", "capability_requirements_future", "execution_summary", "evidence_summary",
    "rights_summary", "risk_summary", "privacy_summary", "action_summary", "actions", "blocked_actions",
    "limitations", "warnings", "representation_hints", "semantic_requirements", "generated_from", "no_goals",
    "notes",
}
REVIEW_VIEW_FIELDS = {
    "schema_version", "view_model_id", "view_family", "route_family", "canonical_route", "page_title",
    "page_status", "review", "review_identity", "review_type", "review_status", "queue_entry_summary",
    "review_decision_summary", "subject_refs", "candidate_refs", "pack_refs", "evidence_refs", "source_refs",
    "need_refs", "object_refs", "validation_summary", "acceptance_requirements", "rejection_summary",
    "deferral_summary", "conflict_summary", "rights_summary", "risk_summary", "privacy_summary",
    "provenance_summary", "master_index_summary", "action_summary", "actions", "blocked_actions",
    "limitations", "warnings", "representation_hints", "semantic_requirements", "generated_from", "no_goals",
    "notes",
}

PACK_POLICY_FIELDS = {
    "schema_version", "policy_id", "contract_ref", "label", "description", "status", "stability",
    "created_by_slice", "canonical_view_family", "supported_route_families", "required_semantic_parity_policy",
    "allowed_representation_profiles", "allowed_pack_types", "allowed_pack_statuses", "allowed_validation_statuses",
    "allowed_import_statuses", "allowed_quarantine_statuses", "allowed_action_names", "required_blocked_actions",
    "required_product_boundary_booleans", "required_safety_claim_booleans", "required_representation_hints",
    "required_semantic_requirements", "current_no_goals", "future_deferred_fields", "notes",
}
TASK_POLICY_FIELDS = {
    "schema_version", "policy_id", "contract_ref", "label", "description", "status", "stability",
    "created_by_slice", "canonical_view_family", "supported_route_families", "required_semantic_parity_policy",
    "allowed_representation_profiles", "allowed_task_types", "allowed_task_statuses", "allowed_action_names",
    "required_forbidden_action_names", "required_blocked_actions", "required_product_boundary_booleans",
    "required_safety_claim_booleans", "required_representation_hints", "required_semantic_requirements",
    "current_no_goals", "future_deferred_fields", "notes",
}
REVIEW_POLICY_FIELDS = {
    "schema_version", "policy_id", "contract_ref", "label", "description", "status", "stability",
    "created_by_slice", "canonical_view_family", "supported_route_families", "required_semantic_parity_policy",
    "allowed_representation_profiles", "allowed_review_statuses", "allowed_review_decisions",
    "allowed_promotion_states", "allowed_action_names", "required_blocked_actions",
    "required_product_boundary_booleans", "required_safety_claim_booleans", "required_representation_hints",
    "required_semantic_requirements", "current_no_goals", "future_deferred_fields", "notes",
}

PACK_IDENTITY_FIELDS = {
    "pack_id", "pack_slug", "pack_type", "canonical_route", "pack_label", "pack_schema_version",
    "pack_format_version", "source_pack_refs", "evidence_pack_refs", "index_pack_refs",
    "contribution_pack_refs", "review_queue_refs", "checksum_or_digest_refs", "signature_status",
    "producer_or_submitter_posture", "pack_confidence", "pack_limitations", "notes",
}
TASK_IDENTITY_FIELDS = {
    "task_id", "task_slug", "task_type", "canonical_route", "task_label", "task_origin", "task_confidence",
    "task_limitations", "notes",
}
REVIEW_IDENTITY_FIELDS = {
    "review_id", "review_slug", "review_type", "canonical_route", "review_label", "subject_ref",
    "queue_entry_ref", "review_confidence", "review_limitations", "notes",
}
PACK_VALIDATION_FIELDS = {
    "validation_status", "validator_refs", "validation_report_refs", "checksum_status", "schema_status",
    "issue_count", "issue_summary", "warnings", "notes",
}
PACK_IMPORT_FIELDS = {
    "import_status", "import_runtime_enabled", "staging_runtime_enabled", "quarantine_status", "local_only",
    "public_search_impact", "master_index_impact", "upload_status", "moderation_status",
    "automatic_acceptance_status",
}
REVIEW_MASTER_INDEX_FIELDS = {
    "master_index_mutation_allowed", "accepted_public_status", "promotion_requirements_met",
    "promotion_requirements_missing", "review_required", "conflict_preservation_required", "publication_policy",
}

REQUIRED_REPRESENTATION_HINTS = {
    "api_json", "file_tree", "html32", "lite_html", "manifest_json", "native_card_future", "print",
    "relay_future", "snapshot_future", "standard_html", "terminal_future", "text",
}
PACK_TYPES = {
    "alias_pack_future", "compatibility_pack_future", "contribution_pack", "evidence_pack",
    "extraction_pack_future", "hash_pack_future", "index_pack", "query_need_pack_future",
    "review_pack_future", "snapshot_pack_future", "source_pack",
}
PACK_STATUSES = {
    "accepted_public_future", "deferred_future", "example_only", "policy_blocked", "quarantined_future",
    "rejected_future", "rights_blocked", "risk_blocked", "staged_future", "submitted_future",
    "superseded_future", "under_review_future", "validate_only", "validated", "validation_failed",
}
PACK_VALIDATION_STATUSES = {"not_run", "pass", "pass_with_warnings", "policy_blocked", "validate_only", "validation_failed"}
PACK_IMPORT_STATUSES = {"future_deferred", "policy_blocked", "unavailable", "validate_only"}
PACK_QUARANTINE_STATUSES = {"not_applicable", "not_quarantined", "policy_blocked", "quarantined_future"}
PACK_ACTIONS = {
    "copy_citation_hint", "copy_pack_id", "open_manifest_future", "view_pack_contents", "view_pack_lineage",
    "view_pack_policy", "view_related_candidates", "view_related_reviews", "view_validation_report",
}
PACK_BLOCKED_ACTIONS = {
    "account_unavailable", "automatic_acceptance_unavailable", "download_unavailable", "execute_unavailable",
    "hosted_backend_unavailable", "import_runtime_unavailable", "install_unavailable", "live_probe_unavailable",
    "malware_safety_unavailable", "master_index_mutation_unavailable", "moderation_runtime_unavailable",
    "pack_import_unavailable", "public_truth_unavailable", "rights_clearance_unavailable",
    "source_sync_unavailable", "telemetry_unavailable", "upload_unavailable", "verified_installability_unavailable",
}
PACK_PRODUCT_FLAGS = {
    "accounts_enabled", "automatic_acceptance_enabled", "downloads_enabled", "hosted_backend_claimed",
    "import_runtime_enabled", "live_probes_enabled", "master_index_mutation_allowed", "moderation_runtime_enabled",
    "pack_import_runtime_enabled", "public_search_impact", "public_truth_claimed", "source_sync_runtime_enabled",
    "staging_runtime_enabled", "telemetry_enabled", "uploads_enabled",
}
PACK_SEMANTICS = {
    "actions_and_blocked_actions_preserved", "canonical_pack_identity_preserved", "import_upload_acceptance_disabled",
    "limitations_and_gaps_visible", "no_master_index_mutation", "no_public_truth_from_packs",
    "pack_contents_not_truth_preserved", "pack_validation_status_preserved", "provenance_and_lineage_preserved",
    "rights_risk_privacy_posture_preserved",
}

TASK_TYPES = {
    "ai_assisted_drafting_future", "approved_metadata_sync_future", "candidate_dedup",
    "compatibility_evidence_review", "container_deepening_future", "contribution_pack_drafting",
    "discussion_to_evidence_future", "evidence_pack_drafting", "hash_verification_future",
    "search_need_review", "source_lead_inspection", "wayback_metadata_trace_future",
}
TASK_STATUSES = {
    "approval_gated", "completed_future", "deferred", "dry_run_only", "future", "human_operated",
    "operator_gated", "permission_needed", "planned", "policy_blocked", "ready_for_manual_review",
    "rejected_future",
}
TASK_ACTIONS = {
    "copy_citation_hint", "copy_task_id", "export_task_bundle_future", "inspect_task", "view_policy",
    "view_related_candidate", "view_related_need", "view_related_pack", "view_related_source",
}
TASK_FORBIDDEN_ACTIONS = {
    "account_required_action_forbidden", "arbitrary_url_fetch_forbidden", "crawling_forbidden",
    "download_forbidden", "execute_forbidden", "install_forbidden", "live_probe_forbidden",
    "master_index_mutation_forbidden", "model_call_forbidden", "provider_call_forbidden",
    "public_truth_mutation_forbidden", "scraping_forbidden", "telemetry_forbidden", "upload_forbidden",
}
TASK_BLOCKED_ACTIONS = {
    "account_unavailable", "autonomous_runtime_unavailable", "download_unavailable", "execute_unavailable",
    "hosted_backend_unavailable", "install_unavailable", "live_probe_unavailable", "malware_safety_unavailable",
    "master_index_mutation_unavailable", "model_call_unavailable", "node_runtime_unavailable",
    "provider_call_unavailable", "public_submission_unavailable", "public_truth_unavailable",
    "rights_clearance_unavailable", "source_sync_unavailable", "telemetry_unavailable", "upload_unavailable",
    "verified_installability_unavailable",
}
TASK_PRODUCT_FLAGS = {
    "accounts_enabled", "autonomous_execution_enabled", "downloads_enabled", "hosted_backend_claimed",
    "live_probes_enabled", "master_index_mutation_allowed", "model_calls_enabled", "node_runtime_enabled",
    "provider_calls_enabled", "public_submission_runtime_enabled", "public_truth_mutation_enabled",
    "source_sync_runtime_enabled", "telemetry_enabled", "uploads_enabled",
}
TASK_EXECUTION_FLAGS = TASK_PRODUCT_FLAGS | {"live_source_access_enabled"}
TASK_SEMANTICS = {
    "actions_and_blocked_actions_preserved", "canonical_task_identity_preserved", "forbidden_actions_preserved",
    "limitations_and_gaps_visible", "no_autonomous_runtime", "no_live_source_or_model_calls",
    "no_master_index_mutation", "no_public_truth_from_tasks", "rights_risk_privacy_posture_preserved",
    "task_status_and_scope_preserved",
}

REVIEW_STATUSES = {
    "accepted_public_future", "conflict_preserved", "deferred", "needs_review", "policy_checked",
    "queue_entry", "rejected", "rights_blocked", "risk_blocked", "superseded", "takedown_pending_future",
    "under_review_future", "validation_failed", "validation_passed", "withdrawn_future",
}
REVIEW_DECISIONS = {
    "accept_future", "defer", "mark_duplicate", "policy_block", "preserve_conflict", "reject",
    "request_more_evidence", "rights_block", "risk_block", "supersede_future", "withdraw_future",
}
PROMOTION_STATES = {"blocked", "future_only", "missing_requirements", "not_allowed", "not_applicable", "review_required"}
REVIEW_ACTIONS = {
    "copy_citation_hint", "copy_review_id", "view_conflicts", "view_evidence", "view_policy_checks",
    "view_promotion_requirements", "view_review_decision", "view_subject", "view_validation_summary",
}
REVIEW_BLOCKED_ACTIONS = {
    "account_unavailable", "accept_public_unavailable", "download_unavailable", "execute_unavailable",
    "hosted_backend_unavailable", "hosted_moderation_unavailable", "install_unavailable",
    "live_probe_unavailable", "malware_safety_unavailable", "master_index_mutation_unavailable",
    "public_submission_unavailable", "public_truth_unavailable", "rights_clearance_unavailable",
    "source_sync_unavailable", "telemetry_unavailable", "upload_unavailable", "verified_installability_unavailable",
    "write_route_unavailable",
}
REVIEW_PRODUCT_FLAGS = {
    "accounts_enabled", "accepted_public_status", "downloads_enabled", "hosted_backend_claimed",
    "hosted_moderation_enabled", "live_probes_enabled", "master_index_mutation_allowed",
    "public_submission_runtime_enabled", "public_truth_claimed", "review_runtime_enabled",
    "source_sync_runtime_enabled", "telemetry_enabled", "uploads_enabled", "write_routes_enabled",
}
REVIEW_SEMANTICS = {
    "actions_and_blocked_actions_preserved", "canonical_review_identity_preserved", "conflicts_preserved",
    "limitations_and_gaps_visible", "master_index_boundary_preserved", "no_public_truth_from_reviews",
    "promotion_requirements_preserved", "review_decision_posture_preserved", "review_status_preserved",
    "rights_risk_privacy_posture_preserved",
}

FLAG_TO_BLOCKED_ACTION = {
    "accepted_public_status": "accept_public_unavailable",
    "accounts_enabled": "account_unavailable",
    "automatic_acceptance_enabled": "automatic_acceptance_unavailable",
    "autonomous_execution_enabled": "autonomous_runtime_unavailable",
    "downloads_enabled": "download_unavailable",
    "hosted_backend_claimed": "hosted_backend_unavailable",
    "hosted_moderation_enabled": "hosted_moderation_unavailable",
    "import_runtime_enabled": "import_runtime_unavailable",
    "live_probes_enabled": "live_probe_unavailable",
    "master_index_mutation_allowed": "master_index_mutation_unavailable",
    "model_calls_enabled": "model_call_unavailable",
    "moderation_runtime_enabled": "moderation_runtime_unavailable",
    "node_runtime_enabled": "node_runtime_unavailable",
    "pack_import_runtime_enabled": "pack_import_unavailable",
    "provider_calls_enabled": "provider_call_unavailable",
    "public_submission_runtime_enabled": "public_submission_unavailable",
    "public_truth_claimed": "public_truth_unavailable",
    "public_truth_mutation_enabled": "public_truth_unavailable",
    "review_runtime_enabled": "hosted_moderation_unavailable",
    "source_sync_runtime_enabled": "source_sync_unavailable",
    "staging_runtime_enabled": "import_runtime_unavailable",
    "telemetry_enabled": "telemetry_unavailable",
    "uploads_enabled": "upload_unavailable",
    "write_routes_enabled": "write_route_unavailable",
}
TRUTH_BOUNDARY_FALSE_FIELDS = {
    "source_observation_accepted_as_truth": "source observation must not be marked accepted truth",
    "evidence_candidate_accepted_as_truth": "evidence candidate must not be marked accepted truth",
    "contribution_items_accepted_public": "contribution item must not be marked accepted public record",
    "ai_draft_marked_evidence_truth": "AI draft must not be marked evidence truth",
    "demand_signal_used_as_object_truth": "demand signal must not be object truth",
    "pack_contents_public_truth_claimed": "pack contents must not be public truth",
    "public_truth_claimed": "public truth must not be claimed",
    "public_acceptance_claimed": "public acceptance must not be claimed",
}
SAFETY_FALSE_FIELDS = {
    "authorized_bulk_access_claimed": "authorized bulk access",
    "authorized_download_claimed": "authorized download",
    "malware_safety_claimed": "malware safety",
    "production_suitability_claimed": "production suitability",
    "rights_clearance_claimed": "rights clearance",
    "safe_execution_claimed": "safe execution",
    "verified_installability_claimed": "verified installability",
}
UNSAFE_EXAMPLE_PATTERNS = [
    re.compile(r"sk-(?:proj|live|svcacct)-[A-Za-z0-9_-]{20,}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"\bapi[_-]?key\s*[:=]", re.IGNORECASE),
    re.compile(r"\bauth[_-]?token\s*[:=]", re.IGNORECASE),
    re.compile(r"\b[A-Za-z]:\\"),
    re.compile(r"(^|[\"' ])/(home|Users|var|etc|root)/"),
    re.compile(r"\b\S+\.(exe|msi|dmg|pkg|deb|rpm|zip|tar\.gz)\b", re.IGNORECASE),
]


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate Eureka PackPage, TaskPage, and ReviewPage view-model schemas, policies, and examples."
    )
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help="Repository root to validate.")
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_pack_task_review_page_view_models(Path(args.repo_root))
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


def validate_pack_task_review_page_view_models(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    root = repo_root.resolve()
    errors: list[str] = []
    warnings: list[str] = []

    for path, expected_fields in (
        (PACK_CONTRACT_PATH, PACK_VIEW_FIELDS),
        (TASK_CONTRACT_PATH, TASK_VIEW_FIELDS),
        (REVIEW_CONTRACT_PATH, REVIEW_VIEW_FIELDS),
    ):
        contract = _load_json(root / path, errors, root)
        if isinstance(contract, Mapping):
            _validate_schema(path, contract, expected_fields, errors)

    pack_policy = _load_json(root / PACK_POLICY_INVENTORY, errors, root)
    task_policy = _load_json(root / TASK_POLICY_INVENTORY, errors, root)
    review_policy = _load_json(root / REVIEW_POLICY_INVENTORY, errors, root)
    representations = _load_json(root / REPRESENTATION_INVENTORY, errors, root)
    semantic = _load_json(root / SEMANTIC_PARITY_INVENTORY, errors, root)
    route_matrix = _load_json(root / ROUTE_MATRIX_INVENTORY, errors, root)
    pack_examples = [_load_json(root / path, errors, root) for path in PACK_EXAMPLE_PATHS]
    task_examples = [_load_json(root / path, errors, root) for path in TASK_EXAMPLE_PATHS]
    review_examples = [_load_json(root / path, errors, root) for path in REVIEW_EXAMPLE_PATHS]
    pack_payloads = [item for item in pack_examples if isinstance(item, Mapping)]
    task_payloads = [item for item in task_examples if isinstance(item, Mapping)]
    review_payloads = [item for item in review_examples if isinstance(item, Mapping)]

    if (
        isinstance(pack_policy, Mapping)
        and isinstance(task_policy, Mapping)
        and isinstance(review_policy, Mapping)
        and isinstance(representations, Mapping)
        and isinstance(semantic, Mapping)
        and isinstance(route_matrix, Mapping)
    ):
        errors.extend(
            validate_payloads(
                pack_policy,
                task_policy,
                review_policy,
                representations,
                semantic,
                route_matrix,
                pack_payloads,
                task_payloads,
                review_payloads,
                source_label="pack_task_review_page_view_models",
            )
        )

    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "validate_pack_task_review_page_view_models",
        "schema_version": SCHEMA_VERSION,
        "contracts_checked": sorted([PACK_CONTRACT_PATH, TASK_CONTRACT_PATH, REVIEW_CONTRACT_PATH]),
        "policies_checked": sorted([PACK_POLICY_INVENTORY, TASK_POLICY_INVENTORY, REVIEW_POLICY_INVENTORY]),
        "pack_examples_checked": sorted(PACK_EXAMPLE_PATHS),
        "task_examples_checked": sorted(TASK_EXAMPLE_PATHS),
        "review_examples_checked": sorted(REVIEW_EXAMPLE_PATHS),
        "pack_example_count": len(pack_payloads),
        "task_example_count": len(task_payloads),
        "review_example_count": len(review_payloads),
        "errors": sorted(errors),
        "warnings": sorted(warnings),
    }


def validate_payloads(
    pack_policy: Mapping[str, Any],
    task_policy: Mapping[str, Any],
    review_policy: Mapping[str, Any],
    representation_inventory: Mapping[str, Any],
    semantic_inventory: Mapping[str, Any],
    route_matrix: Mapping[str, Any],
    pack_examples: Sequence[Mapping[str, Any]],
    task_examples: Sequence[Mapping[str, Any]],
    review_examples: Sequence[Mapping[str, Any]],
    *,
    source_label: str,
) -> list[str]:
    errors: list[str] = []
    representation_ids = _representation_ids(representation_inventory)
    semantic_policy_ids = _semantic_policy_ids(semantic_inventory)
    route_records = _route_records(route_matrix)

    errors.extend(_validate_pack_policy(pack_policy, representation_ids, semantic_policy_ids, route_records))
    errors.extend(_validate_task_policy(task_policy, representation_ids, semantic_policy_ids, route_records))
    errors.extend(_validate_review_policy(review_policy, representation_ids, semantic_policy_ids, route_records))

    pack_context = _policy_context(pack_policy)
    task_context = _policy_context(task_policy)
    review_context = _policy_context(review_policy)
    for index, example in enumerate(pack_examples):
        label = str(example.get("view_model_id") or f"pack_example[{index}]")
        errors.extend(_validate_pack_example(label, example, pack_context, representation_ids, route_records))
    for index, example in enumerate(task_examples):
        label = str(example.get("view_model_id") or f"task_example[{index}]")
        errors.extend(_validate_task_example(label, example, task_context, representation_ids, route_records))
    for index, example in enumerate(review_examples):
        label = str(example.get("view_model_id") or f"review_example[{index}]")
        errors.extend(_validate_review_example(label, example, review_context, representation_ids, route_records))
    if not pack_examples:
        errors.append(f"{source_label}: at least one PackPageView example is required")
    if not task_examples:
        errors.append(f"{source_label}: at least one TaskPageView example is required")
    if not review_examples:
        errors.append(f"{source_label}: at least one ReviewPageView example is required")
    return sorted(errors)


def _validate_schema(path: str, contract: Mapping[str, Any], expected_fields: set[str], errors: list[str]) -> None:
    missing = REQUIRED_SCHEMA_FIELDS - set(contract)
    if missing:
        errors.append(f"{path}: missing schema fields {sorted(missing)}")
    if contract.get("type") != "object":
        errors.append(f"{path}: schema type must be object")
    if contract.get("properties", {}).get("schema_version", {}).get("const") != SCHEMA_VERSION:
        errors.append(f"{path}: schema_version const must be {SCHEMA_VERSION}")
    required = set(_string_items(contract.get("required")))
    missing_required = expected_fields - required
    if missing_required:
        errors.append(f"{path}: required list missing {sorted(missing_required)}")
    properties = contract.get("properties")
    if isinstance(properties, Mapping):
        missing_properties = expected_fields - set(properties)
        if missing_properties:
            errors.append(f"{path}: properties missing {sorted(missing_properties)}")
    else:
        errors.append(f"{path}: properties must be an object")


def _validate_pack_policy(
    policy: Mapping[str, Any],
    representation_ids: set[str],
    semantic_policy_ids: set[str],
    route_records: Mapping[str, Mapping[str, Any]],
) -> list[str]:
    errors = _validate_common_policy(
        policy, PACK_POLICY_FIELDS, PACK_POLICY_INVENTORY, PACK_CONTRACT_PATH, "PackPageView",
        "pack_page_future", "pack_page_future_parity_v0", PACK_BLOCKED_ACTIONS, PACK_PRODUCT_FLAGS,
        PACK_SEMANTICS, representation_ids, semantic_policy_ids, route_records,
    )
    errors.extend(_require_policy_vocab(PACK_POLICY_INVENTORY, policy, "allowed_pack_types", PACK_TYPES))
    errors.extend(_require_policy_vocab(PACK_POLICY_INVENTORY, policy, "allowed_pack_statuses", PACK_STATUSES))
    errors.extend(_require_policy_vocab(PACK_POLICY_INVENTORY, policy, "allowed_validation_statuses", PACK_VALIDATION_STATUSES))
    errors.extend(_require_policy_vocab(PACK_POLICY_INVENTORY, policy, "allowed_import_statuses", PACK_IMPORT_STATUSES))
    errors.extend(_require_policy_vocab(PACK_POLICY_INVENTORY, policy, "allowed_quarantine_statuses", PACK_QUARANTINE_STATUSES))
    errors.extend(_require_policy_vocab(PACK_POLICY_INVENTORY, policy, "allowed_action_names", PACK_ACTIONS))
    return errors


def _validate_task_policy(
    policy: Mapping[str, Any],
    representation_ids: set[str],
    semantic_policy_ids: set[str],
    route_records: Mapping[str, Mapping[str, Any]],
) -> list[str]:
    errors = _validate_common_policy(
        policy, TASK_POLICY_FIELDS, TASK_POLICY_INVENTORY, TASK_CONTRACT_PATH, "TaskPageView",
        "task_page_future", "task_page_future_parity_v0", TASK_BLOCKED_ACTIONS, TASK_PRODUCT_FLAGS,
        TASK_SEMANTICS, representation_ids, semantic_policy_ids, route_records,
    )
    errors.extend(_require_policy_vocab(TASK_POLICY_INVENTORY, policy, "allowed_task_types", TASK_TYPES))
    errors.extend(_require_policy_vocab(TASK_POLICY_INVENTORY, policy, "allowed_task_statuses", TASK_STATUSES))
    errors.extend(_require_policy_vocab(TASK_POLICY_INVENTORY, policy, "allowed_action_names", TASK_ACTIONS))
    errors.extend(_require_policy_vocab(TASK_POLICY_INVENTORY, policy, "required_forbidden_action_names", TASK_FORBIDDEN_ACTIONS))
    return errors


def _validate_review_policy(
    policy: Mapping[str, Any],
    representation_ids: set[str],
    semantic_policy_ids: set[str],
    route_records: Mapping[str, Mapping[str, Any]],
) -> list[str]:
    errors = _validate_common_policy(
        policy, REVIEW_POLICY_FIELDS, REVIEW_POLICY_INVENTORY, REVIEW_CONTRACT_PATH, "ReviewPageView",
        "review_page_future", "review_page_future_parity_v0", REVIEW_BLOCKED_ACTIONS, REVIEW_PRODUCT_FLAGS,
        REVIEW_SEMANTICS, representation_ids, semantic_policy_ids, route_records,
    )
    errors.extend(_require_policy_vocab(REVIEW_POLICY_INVENTORY, policy, "allowed_review_statuses", REVIEW_STATUSES))
    errors.extend(_require_policy_vocab(REVIEW_POLICY_INVENTORY, policy, "allowed_review_decisions", REVIEW_DECISIONS))
    errors.extend(_require_policy_vocab(REVIEW_POLICY_INVENTORY, policy, "allowed_promotion_states", PROMOTION_STATES))
    errors.extend(_require_policy_vocab(REVIEW_POLICY_INVENTORY, policy, "allowed_action_names", REVIEW_ACTIONS))
    return errors


def _validate_common_policy(
    policy: Mapping[str, Any],
    policy_fields: set[str],
    policy_path: str,
    contract_path: str,
    view_family: str,
    required_route: str,
    required_parity: str,
    required_blocked: set[str],
    required_flags: set[str],
    required_semantics: set[str],
    representation_ids: set[str],
    semantic_policy_ids: set[str],
    route_records: Mapping[str, Mapping[str, Any]],
) -> list[str]:
    errors: list[str] = []
    missing = policy_fields - set(policy)
    if missing:
        errors.append(f"{policy_path}: missing policy fields {sorted(missing)}")
    if policy.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"{policy_path}: schema_version must be {SCHEMA_VERSION}")
    if policy.get("contract_ref") != contract_path:
        errors.append(f"{policy_path}: contract_ref must be {contract_path}")
    if policy.get("canonical_view_family") != view_family:
        errors.append(f"{policy_path}: canonical_view_family must be {view_family}")
    supported_routes = set(_string_items(policy.get("supported_route_families")))
    if required_route not in supported_routes:
        errors.append(f"{policy_path}: supported_route_families must include {required_route}")
    unknown_routes = supported_routes - set(route_records)
    if unknown_routes:
        errors.append(f"{policy_path}: unsupported route family refs {sorted(unknown_routes)}")
    for route_id in sorted(supported_routes & set(route_records)):
        if route_records[route_id].get("canonical_view_family") != view_family:
            errors.append(f"{policy_path}: {route_id} does not bind to {view_family}")
    if policy.get("required_semantic_parity_policy") != required_parity:
        errors.append(f"{policy_path}: required_semantic_parity_policy must be {required_parity}")
    if required_parity not in semantic_policy_ids:
        errors.append(f"{policy_path}: semantic parity policy ref {required_parity!r} does not exist")
    representations = set(_string_items(policy.get("allowed_representation_profiles")))
    missing_representations = representations - representation_ids
    if missing_representations:
        errors.append(f"{policy_path}: unknown representation profile refs {sorted(missing_representations)}")
    if not REQUIRED_REPRESENTATION_HINTS <= representations:
        errors.append(
            f"{policy_path}: allowed_representation_profiles missing {sorted(REQUIRED_REPRESENTATION_HINTS - representations)}"
        )
    hints = set(_string_items(policy.get("required_representation_hints")))
    if not REQUIRED_REPRESENTATION_HINTS <= hints:
        errors.append(f"{policy_path}: required_representation_hints missing {sorted(REQUIRED_REPRESENTATION_HINTS - hints)}")
    blocked = set(_string_items(policy.get("required_blocked_actions")))
    if not required_blocked <= blocked:
        errors.append(f"{policy_path}: required_blocked_actions missing {sorted(required_blocked - blocked)}")
    flags = set(_string_items(policy.get("required_product_boundary_booleans")))
    if not required_flags <= flags:
        errors.append(f"{policy_path}: required_product_boundary_booleans missing {sorted(required_flags - flags)}")
    safety = set(_string_items(policy.get("required_safety_claim_booleans")))
    if not set(SAFETY_FALSE_FIELDS) <= safety:
        errors.append(f"{policy_path}: required_safety_claim_booleans missing {sorted(set(SAFETY_FALSE_FIELDS) - safety)}")
    semantics = set(_string_items(policy.get("required_semantic_requirements")))
    if not required_semantics <= semantics:
        errors.append(f"{policy_path}: required_semantic_requirements missing {sorted(required_semantics - semantics)}")
    return errors


def _require_policy_vocab(path: str, policy: Mapping[str, Any], key: str, required: set[str]) -> list[str]:
    actual = set(_string_items(policy.get(key)))
    missing = required - actual
    return [f"{path}: {key} missing {sorted(missing)}"] if missing else []


def _policy_context(policy: Mapping[str, Any]) -> dict[str, set[str] | str]:
    return {
        "routes": set(_string_items(policy.get("supported_route_families"))),
        "representations": set(_string_items(policy.get("allowed_representation_profiles"))),
        "hints": set(_string_items(policy.get("required_representation_hints"))),
        "semantics": set(_string_items(policy.get("required_semantic_requirements"))),
        "blocked": set(_string_items(policy.get("required_blocked_actions"))),
        "actions": set(_string_items(policy.get("allowed_action_names"))),
        "pack_types": set(_string_items(policy.get("allowed_pack_types"))),
        "pack_statuses": set(_string_items(policy.get("allowed_pack_statuses"))),
        "validation_statuses": set(_string_items(policy.get("allowed_validation_statuses"))),
        "import_statuses": set(_string_items(policy.get("allowed_import_statuses"))),
        "quarantine_statuses": set(_string_items(policy.get("allowed_quarantine_statuses"))),
        "task_types": set(_string_items(policy.get("allowed_task_types"))),
        "task_statuses": set(_string_items(policy.get("allowed_task_statuses"))),
        "forbidden_actions": set(_string_items(policy.get("required_forbidden_action_names"))),
        "review_statuses": set(_string_items(policy.get("allowed_review_statuses"))),
        "review_decisions": set(_string_items(policy.get("allowed_review_decisions"))),
        "promotion_states": set(_string_items(policy.get("allowed_promotion_states"))),
        "semantic_ref": str(policy.get("required_semantic_parity_policy") or ""),
    }


def _validate_pack_example(
    label: str,
    example: Mapping[str, Any],
    context: Mapping[str, set[str] | str],
    representation_ids: set[str],
    route_records: Mapping[str, Mapping[str, Any]],
) -> list[str]:
    errors: list[str] = []
    missing = PACK_VIEW_FIELDS - set(example)
    if missing:
        return [f"{label}: missing required PackPageView top-level fields {sorted(missing)}"]
    errors.extend(_validate_basic_example(label, example, "PackPageView", context, route_records))

    identity = _mapping(example.get("pack_identity"))
    errors.extend(_require_object_fields(label, "pack_identity", identity, PACK_IDENTITY_FIELDS))
    if not identity.get("pack_id"):
        errors.append(f"{label}: canonical pack identity pack_id is required")
    if not identity.get("canonical_route"):
        errors.append(f"{label}: canonical pack identity canonical_route is required")
    if identity.get("pack_type") not in context["pack_types"]:
        errors.append(f"{label}: pack_identity.pack_type {identity.get('pack_type')!r} is not allowed")
    if example.get("pack_type") not in context["pack_types"]:
        errors.append(f"{label}: pack_type {example.get('pack_type')!r} is not allowed")
    if example.get("pack_status") not in context["pack_statuses"]:
        errors.append(f"{label}: pack_status {example.get('pack_status')!r} is not allowed")
    if example.get("pack_status") == "accepted_public_future":
        errors.append(f"{label}: current pack example must not be accepted public future")

    validation = _mapping(example.get("pack_validation_summary"))
    errors.extend(_require_object_fields(label, "pack_validation_summary", validation, PACK_VALIDATION_FIELDS))
    if validation.get("validation_status") not in context["validation_statuses"]:
        errors.append(f"{label}: validation_status {validation.get('validation_status')!r} is not allowed")

    import_summary = _mapping(example.get("import_summary"))
    combined_import = dict(import_summary)
    combined_import.update(_mapping(example.get("quarantine_summary")))
    errors.extend(_require_object_fields(label, "import_summary", combined_import, PACK_IMPORT_FIELDS))
    if import_summary.get("import_status") not in context["import_statuses"]:
        errors.append(f"{label}: import_status {import_summary.get('import_status')!r} is not allowed")
    if _mapping(example.get("quarantine_summary")).get("quarantine_status") not in context["quarantine_statuses"]:
        errors.append(f"{label}: quarantine_status is not allowed")
    for key in ("import_runtime_enabled", "staging_runtime_enabled", "pack_import_runtime_enabled", "public_search_impact", "master_index_impact", "automatic_acceptance_enabled", "master_index_mutation_allowed"):
        if import_summary.get(key) is not False:
            errors.append(f"{label}: import_summary.{key} must be false")
    for key, expected in (("upload_status", "unavailable"), ("automatic_acceptance_status", "unavailable")):
        if import_summary.get(key) != expected:
            errors.append(f"{label}: import_summary.{key} must be {expected!r}")

    errors.extend(_validate_truth_boundaries(label, example, ("pack_contents_summary", "provenance_summary", "review_summary", "import_summary")))
    errors.extend(_validate_safety_claims(label, example))
    errors.extend(_validate_action_boundary(label, example, PACK_PRODUCT_FLAGS, PACK_BLOCKED_ACTIONS, context["blocked"], context["actions"]))
    errors.extend(_validate_hints(label, example, representation_ids, context["representations"], context["hints"]))
    errors.extend(_validate_semantics(label, example, PACK_SEMANTICS, context["semantics"]))
    errors.extend(_validate_generated_from(label, example, str(context["semantic_ref"])))
    errors.extend(_validate_unsafe_patterns(label, example))
    return sorted(errors)


def _validate_task_example(
    label: str,
    example: Mapping[str, Any],
    context: Mapping[str, set[str] | str],
    representation_ids: set[str],
    route_records: Mapping[str, Mapping[str, Any]],
) -> list[str]:
    errors: list[str] = []
    missing = TASK_VIEW_FIELDS - set(example)
    if missing:
        return [f"{label}: missing required TaskPageView top-level fields {sorted(missing)}"]
    errors.extend(_validate_basic_example(label, example, "TaskPageView", context, route_records))

    identity = _mapping(example.get("task_identity"))
    errors.extend(_require_object_fields(label, "task_identity", identity, TASK_IDENTITY_FIELDS))
    if not identity.get("task_id"):
        errors.append(f"{label}: canonical task identity task_id is required")
    if not identity.get("canonical_route"):
        errors.append(f"{label}: canonical task identity canonical_route is required")
    if identity.get("task_type") not in context["task_types"]:
        errors.append(f"{label}: task_identity.task_type {identity.get('task_type')!r} is not allowed")
    if example.get("task_type") not in context["task_types"]:
        errors.append(f"{label}: task_type {example.get('task_type')!r} is not allowed")
    if example.get("task_status") not in context["task_statuses"]:
        errors.append(f"{label}: task_status {example.get('task_status')!r} is not allowed")

    forbidden = _action_ids(example.get("forbidden_actions"))
    missing_forbidden = (TASK_FORBIDDEN_ACTIONS | (context["forbidden_actions"] if isinstance(context["forbidden_actions"], set) else set())) - forbidden
    if missing_forbidden:
        errors.append(f"{label}: forbidden_actions missing {sorted(missing_forbidden)}")
    execution = _mapping(example.get("execution_summary"))
    for key in sorted(TASK_EXECUTION_FLAGS):
        if execution.get(key) is not False:
            errors.append(f"{label}: execution_summary.{key} must be false")
    output = _mapping(example.get("output_contract"))
    if output.get("accepted_public_status") is not False:
        errors.append(f"{label}: output_contract.accepted_public_status must be false")
    if output.get("master_index_mutation_allowed") is not False:
        errors.append(f"{label}: output_contract.master_index_mutation_allowed must be false")

    errors.extend(_validate_truth_boundaries(label, example, ("input_summary", "evidence_summary", "output_contract")))
    errors.extend(_validate_safety_claims(label, example))
    errors.extend(_validate_action_boundary(label, example, TASK_PRODUCT_FLAGS, TASK_BLOCKED_ACTIONS, context["blocked"], context["actions"]))
    errors.extend(_validate_hints(label, example, representation_ids, context["representations"], context["hints"]))
    errors.extend(_validate_semantics(label, example, TASK_SEMANTICS, context["semantics"]))
    errors.extend(_validate_generated_from(label, example, str(context["semantic_ref"])))
    errors.extend(_validate_unsafe_patterns(label, example))
    return sorted(errors)


def _validate_review_example(
    label: str,
    example: Mapping[str, Any],
    context: Mapping[str, set[str] | str],
    representation_ids: set[str],
    route_records: Mapping[str, Mapping[str, Any]],
) -> list[str]:
    errors: list[str] = []
    missing = REVIEW_VIEW_FIELDS - set(example)
    if missing:
        return [f"{label}: missing required ReviewPageView top-level fields {sorted(missing)}"]
    errors.extend(_validate_basic_example(label, example, "ReviewPageView", context, route_records))

    identity = _mapping(example.get("review_identity"))
    errors.extend(_require_object_fields(label, "review_identity", identity, REVIEW_IDENTITY_FIELDS))
    if not identity.get("review_id"):
        errors.append(f"{label}: canonical review identity review_id is required")
    if not identity.get("canonical_route"):
        errors.append(f"{label}: canonical review identity canonical_route is required")
    if example.get("review_status") not in context["review_statuses"]:
        errors.append(f"{label}: review_status {example.get('review_status')!r} is not allowed")
    if example.get("review_status") == "accepted_public_future":
        errors.append(f"{label}: current review example must not be accepted public future")

    decision = _mapping(example.get("review_decision_summary"))
    if decision.get("review_decision") not in context["review_decisions"]:
        errors.append(f"{label}: review_decision {decision.get('review_decision')!r} is not allowed")
    for key in ("master_index_mutation_allowed", "accepted_public_status", "public_acceptance_claimed"):
        if decision.get(key) is not False:
            errors.append(f"{label}: review_decision_summary.{key} must be false")
    if decision.get("review_required") is not True:
        errors.append(f"{label}: review_decision_summary.review_required must be true")

    master_index = _mapping(example.get("master_index_summary"))
    missing_master = REVIEW_MASTER_INDEX_FIELDS - set(master_index)
    if missing_master:
        errors.append(f"{label}: master_index_summary missing {sorted(missing_master)}")
    for key in ("master_index_mutation_allowed", "accepted_public_status", "hosted_moderation_enabled", "accounts_enabled", "write_routes_enabled", "public_submission_runtime_enabled", "review_runtime_enabled", "public_truth_claimed"):
        if master_index.get(key) is not False:
            errors.append(f"{label}: master_index_summary.{key} must be false")
    if master_index.get("review_required") is not True:
        errors.append(f"{label}: master_index_summary.review_required must be true")
    if master_index.get("promotion_requirements_met") is not False:
        errors.append(f"{label}: master_index_summary.promotion_requirements_met must be false")
    queue = _mapping(example.get("queue_entry_summary"))
    for key in ("hosted_moderation_enabled", "accounts_enabled", "write_routes_enabled", "public_submission_runtime_enabled", "accepted_public_status"):
        if queue.get(key) is not False:
            errors.append(f"{label}: queue_entry_summary.{key} must be false")

    errors.extend(_validate_truth_boundaries(label, example, ("validation_summary", "provenance_summary", "queue_entry_summary", "review_decision_summary", "master_index_summary")))
    errors.extend(_validate_safety_claims(label, example))
    errors.extend(_validate_action_boundary(label, example, REVIEW_PRODUCT_FLAGS, REVIEW_BLOCKED_ACTIONS, context["blocked"], context["actions"]))
    errors.extend(_validate_hints(label, example, representation_ids, context["representations"], context["hints"]))
    errors.extend(_validate_semantics(label, example, REVIEW_SEMANTICS, context["semantics"]))
    errors.extend(_validate_generated_from(label, example, str(context["semantic_ref"])))
    errors.extend(_validate_unsafe_patterns(label, example))
    return sorted(errors)


def _validate_basic_example(
    label: str,
    example: Mapping[str, Any],
    view_family: str,
    context: Mapping[str, set[str] | str],
    route_records: Mapping[str, Mapping[str, Any]],
) -> list[str]:
    errors: list[str] = []
    if example.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"{label}: schema_version must be {SCHEMA_VERSION}")
    if example.get("view_family") != view_family:
        errors.append(f"{label}: view_family must be {view_family}")
    errors.extend(_validate_route(label, example, view_family, context["routes"], route_records))
    return errors


def _validate_route(
    label: str,
    example: Mapping[str, Any],
    view_family: str,
    allowed_routes: object,
    route_records: Mapping[str, Mapping[str, Any]],
) -> list[str]:
    routes = allowed_routes if isinstance(allowed_routes, set) else set()
    route_family = example.get("route_family")
    errors: list[str] = []
    if route_family not in routes:
        errors.append(f"{label}: route_family {route_family!r} is not allowed by policy")
    if route_family not in route_records:
        errors.append(f"{label}: route_family {route_family!r} is not in route matrix")
    elif route_records[route_family].get("canonical_view_family") != view_family:
        errors.append(f"{label}: route_family {route_family!r} does not bind to {view_family}")
    return errors


def _validate_action_boundary(
    label: str,
    example: Mapping[str, Any],
    product_flags: set[str],
    required_blocked: set[str],
    policy_blocked: object,
    policy_actions: object,
) -> list[str]:
    errors: list[str] = []
    blocked = _action_ids(example.get("blocked_actions"))
    summary = _mapping(example.get("action_summary"))
    missing_blocked = (required_blocked | (policy_blocked if isinstance(policy_blocked, set) else set())) - blocked
    if missing_blocked:
        errors.append(f"{label}: blocked_actions missing {sorted(missing_blocked)}")
    summary_blocked = set(_string_items(summary.get("blocked_actions")))
    summary_missing = required_blocked - summary_blocked
    if summary_missing:
        errors.append(f"{label}: action_summary.blocked_actions missing {sorted(summary_missing)}")
    actions = _action_ids(example.get("actions"))
    allowed_actions = policy_actions if isinstance(policy_actions, set) else set()
    unknown_actions = actions - allowed_actions
    if unknown_actions:
        errors.append(f"{label}: actions contain unknown action ids {sorted(unknown_actions)}")
    summary_actions = set(_string_items(summary.get("allowed_actions")))
    unknown_summary_actions = summary_actions - allowed_actions
    if unknown_summary_actions:
        errors.append(f"{label}: action_summary contains unknown actions {sorted(unknown_summary_actions)}")
    for flag in sorted(product_flags):
        if summary.get(flag) is not False:
            errors.append(f"{label}: {flag} must be false for current examples")
        blocked_action = FLAG_TO_BLOCKED_ACTION.get(flag)
        if blocked_action and blocked_action not in blocked:
            errors.append(f"{label}: missing blocked action {blocked_action} for false {flag}")
    return errors


def _validate_safety_claims(label: str, example: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    for object_name in ("rights_summary", "risk_summary", "privacy_summary"):
        payload = _mapping(example.get(object_name))
        for key, phrase in SAFETY_FALSE_FIELDS.items():
            if payload.get(key) is not False and key in payload:
                errors.append(f"{label}: {phrase} must not be claimed")
    return errors


def _validate_truth_boundaries(label: str, example: Mapping[str, Any], object_names: Sequence[str]) -> list[str]:
    errors: list[str] = []
    for object_name in object_names:
        payload = _mapping(example.get(object_name))
        for key, message in TRUTH_BOUNDARY_FALSE_FIELDS.items():
            if key in payload and payload.get(key) is not False:
                errors.append(f"{label}: {message}")
    return errors


def _validate_hints(
    label: str,
    example: Mapping[str, Any],
    representation_ids: set[str],
    policy_representations: object,
    policy_required_hints: object,
) -> list[str]:
    errors: list[str] = []
    hints = example.get("representation_hints")
    if not isinstance(hints, Mapping):
        return [f"{label}: representation_hints must be an object"]
    hint_ids = set(hints)
    policy_reps = policy_representations if isinstance(policy_representations, set) else set()
    required_hints = policy_required_hints if isinstance(policy_required_hints, set) else set()
    unknown_hints = hint_ids - representation_ids
    if unknown_hints:
        errors.append(f"{label}: representation_hints reference unknown profiles {sorted(unknown_hints)}")
    missing_hints = (required_hints | REQUIRED_REPRESENTATION_HINTS) - hint_ids
    if missing_hints:
        errors.append(f"{label}: representation_hints missing {sorted(missing_hints)}")
    disallowed = hint_ids - policy_reps
    if disallowed:
        errors.append(f"{label}: representation_hints include profiles outside policy {sorted(disallowed)}")
    for hint_id in sorted(hint_ids):
        hint = hints[hint_id]
        if not isinstance(hint, Mapping):
            errors.append(f"{label}: representation hint {hint_id} must be an object")
        elif hint.get("semantic_meaning_changes_allowed") is not False:
            errors.append(f"{label}: {hint_id} must not allow semantic meaning changes")
    return errors


def _validate_semantics(
    label: str,
    example: Mapping[str, Any],
    required_semantics: set[str],
    policy_semantics: object,
) -> list[str]:
    semantics = set(_string_items(example.get("semantic_requirements")))
    policy_required = policy_semantics if isinstance(policy_semantics, set) else set()
    missing = (required_semantics | policy_required) - semantics
    if not semantics:
        return [f"{label}: semantic_requirements must be non-empty"]
    if missing:
        return [f"{label}: semantic_requirements missing {sorted(missing)}"]
    return []


def _validate_generated_from(label: str, example: Mapping[str, Any], semantic_ref: str) -> list[str]:
    generated_from = example.get("generated_from")
    if not isinstance(generated_from, Mapping):
        return [f"{label}: generated_from must be an object"]
    if generated_from.get("semantic_parity_policy") != semantic_ref:
        return [f"{label}: generated_from semantic_parity_policy must be {semantic_ref!r}"]
    return []


def _validate_unsafe_patterns(label: str, example: Mapping[str, Any]) -> list[str]:
    raw = json.dumps(example, sort_keys=True)
    return [
        f"{label}: example contains unsafe/private pattern {pattern.pattern}"
        for pattern in UNSAFE_EXAMPLE_PATTERNS
        if pattern.search(raw)
    ]


def _require_object_fields(label: str, object_name: str, payload: Mapping[str, Any], required: set[str]) -> list[str]:
    missing = required - set(payload)
    return [f"{label}: {object_name} missing {sorted(missing)}"] if missing else []


def _load_json(path: Path, errors: list[str], repo_root: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"{_rel(path, repo_root)}: file not found")
    except json.JSONDecodeError as exc:
        errors.append(f"{_rel(path, repo_root)}: invalid JSON at line {exc.lineno}: {exc.msg}")
    return None


def _representation_ids(inventory: Mapping[str, Any]) -> set[str]:
    profiles = inventory.get("profiles")
    if not isinstance(profiles, Sequence) or isinstance(profiles, (str, bytes)):
        return set()
    return {
        str(profile["representation_profile_id"])
        for profile in profiles
        if isinstance(profile, Mapping) and isinstance(profile.get("representation_profile_id"), str)
    }


def _semantic_policy_ids(inventory: Mapping[str, Any]) -> set[str]:
    policies = inventory.get("policies")
    if not isinstance(policies, Sequence) or isinstance(policies, (str, bytes)):
        return set()
    return {
        str(policy["parity_policy_id"])
        for policy in policies
        if isinstance(policy, Mapping) and isinstance(policy.get("parity_policy_id"), str)
    }


def _route_records(matrix: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    routes = matrix.get("route_families")
    if not isinstance(routes, Sequence) or isinstance(routes, (str, bytes)):
        return {}
    return {
        str(route["route_family_id"]): route
        for route in routes
        if isinstance(route, Mapping) and isinstance(route.get("route_family_id"), str)
    }


def _string_items(value: Any) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [item for item in value if isinstance(item, str)]


def _action_ids(actions: Any) -> set[str]:
    if not isinstance(actions, Sequence) or isinstance(actions, (str, bytes)):
        return set()
    return {
        action["action_id"]
        for action in actions
        if isinstance(action, Mapping) and isinstance(action.get("action_id"), str)
    }


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _rel(path: Path, repo_root: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return str(path)


def _format_plain(report: Mapping[str, Any]) -> str:
    lines = [
        f"validate_pack_task_review_page_view_models: {report['status']}",
        f"schema_version: {report['schema_version']}",
        f"pack_examples: {report['pack_example_count']}",
        f"task_examples: {report['task_example_count']}",
        f"review_examples: {report['review_example_count']}",
    ]
    errors = report.get("errors", [])
    if errors:
        lines.append("errors:")
        lines.extend(f"- {error}" for error in errors)
    warnings = report.get("warnings", [])
    if warnings:
        lines.append("warnings:")
        lines.extend(f"- {warning}" for warning in warnings)
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
