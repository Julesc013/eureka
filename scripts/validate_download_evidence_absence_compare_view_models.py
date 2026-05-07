from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_VERSION = "0.1.0"

DOWNLOAD_CONTRACT_PATH = "contracts/views/download_manifest_page.v0.json"
EVIDENCE_CONTRACT_PATH = "contracts/views/evidence_page.v0.json"
ABSENCE_CONTRACT_PATH = "contracts/views/absence_page.v0.json"
COMPARE_CONTRACT_PATH = "contracts/views/compare_page.v0.json"
DOWNLOAD_POLICY_INVENTORY = "control/inventory/publication/download_manifest_view_model_policy.json"
EVIDENCE_POLICY_INVENTORY = "control/inventory/publication/evidence_page_view_model_policy.json"
ABSENCE_POLICY_INVENTORY = "control/inventory/publication/absence_page_view_model_policy.json"
COMPARE_POLICY_INVENTORY = "control/inventory/publication/compare_page_view_model_policy.json"
REPRESENTATION_INVENTORY = "control/inventory/publication/representation_profiles.json"
SEMANTIC_PARITY_INVENTORY = "control/inventory/publication/semantic_renderer_parity_policy.json"
ROUTE_MATRIX_INVENTORY = "control/inventory/publication/route_view_representation_matrix.json"

DOWNLOAD_EXAMPLE_PATHS = [
    "examples/view_models/download_manifest/blocked_download_manifest_v0.json",
    "examples/view_models/download_manifest/minimal_download_manifest_v0.json",
    "examples/view_models/download_manifest/native_handoff_future_manifest_v0.json",
]
EVIDENCE_EXAMPLE_PATHS = [
    "examples/view_models/evidence_page/conflicting_evidence_page_v0.json",
    "examples/view_models/evidence_page/evidence_candidate_page_v0.json",
    "examples/view_models/evidence_page/minimal_evidence_page_v0.json",
    "examples/view_models/evidence_page/source_observation_evidence_page_v0.json",
]
ABSENCE_EXAMPLE_PATHS = [
    "examples/view_models/absence_page/minimal_absence_page_v0.json",
    "examples/view_models/absence_page/near_match_absence_page_v0.json",
    "examples/view_models/absence_page/policy_blocked_absence_page_v0.json",
    "examples/view_models/absence_page/source_gap_absence_page_v0.json",
]
COMPARE_EXAMPLE_PATHS = [
    "examples/view_models/compare_page/candidate_compare_page_v0.json",
    "examples/view_models/compare_page/minimal_compare_page_v0.json",
    "examples/view_models/compare_page/object_version_compare_page_v0.json",
    "examples/view_models/compare_page/source_conflict_compare_page_v0.json",
]

REQUIRED_SCHEMA_FIELDS = {"$schema", "$id", "title", "description", "type", "required", "properties"}
DOWNLOAD_VIEW_FIELDS = {
    "schema_version", "view_model_id", "view_family", "route_family", "canonical_route", "page_title",
    "page_status", "manifest", "manifest_identity", "target_object_summary",
    "target_representation_summary", "source_summary", "access_path_summary", "file_summary",
    "checksum_summary", "signature_summary", "rights_summary", "risk_summary", "privacy_summary",
    "safety_summary", "action_summary", "actions", "blocked_actions", "native_handoff_summary_future",
    "relay_handoff_summary_future", "snapshot_summary_future", "limitations", "warnings",
    "representation_hints", "semantic_requirements", "generated_from", "no_goals", "notes",
}
EVIDENCE_VIEW_FIELDS = {
    "schema_version", "view_model_id", "view_family", "route_family", "canonical_route", "page_title",
    "page_status", "evidence", "evidence_identity", "evidence_type", "evidence_status",
    "claim_summary", "observation_summary", "source_locator_summary", "snippet_summary",
    "provenance_summary", "related_source_refs", "related_object_refs", "related_candidate_refs",
    "related_pack_refs", "related_review_refs", "confidence_or_uncertainty", "conflict_summary",
    "review_summary", "rights_summary", "risk_summary", "privacy_summary", "action_summary",
    "actions", "blocked_actions", "limitations", "warnings", "representation_hints",
    "semantic_requirements", "generated_from", "no_goals", "notes",
}
ABSENCE_VIEW_FIELDS = {
    "schema_version", "view_model_id", "view_family", "route_family", "canonical_route", "page_title",
    "page_status", "absence", "absence_identity", "absence_status", "query_summary",
    "interpreted_intent", "searched_scope", "sources_checked", "sources_not_checked",
    "source_gap_summary", "capability_gap_summary", "near_match_summary", "rejected_match_summary",
    "candidate_summary", "policy_block_summary", "evidence_summary", "related_need_refs",
    "related_candidate_refs", "related_source_refs", "related_task_refs_future", "next_safe_actions",
    "rights_summary", "risk_summary", "privacy_summary", "action_summary", "actions",
    "blocked_actions", "limitations", "warnings", "representation_hints", "semantic_requirements",
    "generated_from", "no_goals", "notes",
}
COMPARE_VIEW_FIELDS = {
    "schema_version", "view_model_id", "view_family", "route_family", "canonical_route", "page_title",
    "page_status", "comparison", "comparison_identity", "comparison_type", "comparison_status",
    "compared_subjects", "comparison_axes", "shared_fields", "differing_fields", "conflict_summary",
    "evidence_summary", "source_summary", "compatibility_summary", "representation_summary",
    "rights_summary", "risk_summary", "review_summary", "deduplication_summary",
    "identity_resolution_summary", "action_summary", "actions", "blocked_actions", "limitations",
    "warnings", "representation_hints", "semantic_requirements", "generated_from", "no_goals", "notes",
}

DOWNLOAD_POLICY_FIELDS = {
    "schema_version", "policy_id", "contract_ref", "label", "description", "status", "stability",
    "created_by_slice", "canonical_view_family", "supported_route_families", "required_semantic_parity_policy",
    "allowed_representation_profiles", "allowed_manifest_types", "allowed_manifest_statuses",
    "allowed_access_statuses", "allowed_action_names", "required_blocked_actions",
    "required_product_boundary_booleans", "required_safety_claim_booleans", "required_representation_hints",
    "required_semantic_requirements", "current_no_goals", "future_deferred_fields", "notes",
}
EVIDENCE_POLICY_FIELDS = {
    "schema_version", "policy_id", "contract_ref", "label", "description", "status", "stability",
    "created_by_slice", "canonical_view_family", "supported_route_families", "required_semantic_parity_policy",
    "allowed_representation_profiles", "allowed_evidence_types", "allowed_evidence_statuses",
    "allowed_claim_types", "allowed_observation_types", "allowed_action_names",
    "required_blocked_actions", "required_review_truth_boundary_fields", "required_product_boundary_booleans",
    "required_safety_claim_booleans", "required_representation_hints", "required_semantic_requirements",
    "current_no_goals", "future_deferred_fields", "notes",
}
ABSENCE_POLICY_FIELDS = {
    "schema_version", "policy_id", "contract_ref", "label", "description", "status", "stability",
    "created_by_slice", "canonical_view_family", "supported_route_families", "required_semantic_parity_policy",
    "allowed_representation_profiles", "allowed_absence_statuses", "allowed_absence_scopes",
    "allowed_next_safe_action_names", "allowed_action_names", "required_blocked_actions",
    "required_no_exhaustive_global_search_fields", "required_product_boundary_booleans",
    "required_safety_claim_booleans", "required_representation_hints", "required_semantic_requirements",
    "current_no_goals", "future_deferred_fields", "notes",
}
COMPARE_POLICY_FIELDS = {
    "schema_version", "policy_id", "contract_ref", "label", "description", "status", "stability",
    "created_by_slice", "canonical_view_family", "supported_route_families", "required_semantic_parity_policy",
    "allowed_representation_profiles", "allowed_comparison_types", "allowed_comparison_statuses",
    "allowed_comparison_axes", "allowed_action_names", "required_blocked_actions",
    "required_no_auto_merge_no_auto_promotion_fields", "required_product_boundary_booleans",
    "required_safety_claim_booleans", "required_representation_hints", "required_semantic_requirements",
    "current_no_goals", "future_deferred_fields", "notes",
}

DOWNLOAD_IDENTITY_FIELDS = {
    "manifest_id", "manifest_slug", "manifest_type", "canonical_route", "manifest_schema_version",
    "target_object_id", "target_representation_id", "target_source_id", "target_pack_refs",
    "checksum_or_digest_refs", "signature_status", "manifest_status", "manifest_limitations", "notes",
}
EVIDENCE_IDENTITY_FIELDS = {
    "evidence_id", "evidence_slug", "evidence_type", "canonical_route", "source_id", "source_locator",
    "claim_type", "observation_type", "evidence_pack_ref", "contribution_pack_ref", "candidate_ref",
    "review_ref", "evidence_confidence", "evidence_limitations", "notes",
}
ABSENCE_IDENTITY_FIELDS = {
    "absence_id", "absence_slug", "canonical_route", "related_query", "related_need_id",
    "related_search_run_ref", "absence_scope", "absence_confidence", "absence_limitations", "notes",
}
COMPARE_IDENTITY_FIELDS = {
    "comparison_id", "comparison_slug", "comparison_type", "canonical_route", "comparison_label",
    "subject_refs", "comparison_confidence", "comparison_limitations", "notes",
}

REQUIRED_REPRESENTATION_HINTS = {
    "api_json", "file_tree", "html32", "lite_html", "manifest_json", "native_card_future", "print",
    "relay_future", "snapshot_future", "standard_html", "terminal_future", "text",
}

MANIFEST_TYPES = {
    "acquisition_manifest", "citation_manifest", "download_manifest", "export_manifest",
    "install_recipe_future", "native_handoff_manifest_future", "relay_manifest_future",
    "replay_recipe_future", "snapshot_manifest_future",
}
MANIFEST_STATUSES = {
    "blocked", "example_only", "future_deferred", "manifest_only", "policy_blocked",
    "rights_blocked", "risk_blocked", "validate_only",
}
ACCESS_STATUSES = {"future_deferred", "metadata_only", "policy_blocked", "unavailable"}
DOWNLOAD_ACTIONS = {
    "copy_checksum", "copy_manifest_id", "export_manifest_future", "open_relay_future",
    "open_snapshot_future", "view_evidence", "view_manifest", "view_object", "view_rights_risk",
    "view_source",
}
DOWNLOAD_BLOCKED_ACTIONS = {
    "account_unavailable", "direct_download_unavailable", "download_unavailable", "execute_unavailable",
    "hosted_backend_unavailable", "install_unavailable", "live_probe_unavailable",
    "malware_safety_unavailable", "native_handoff_unavailable", "package_manager_unavailable",
    "relay_unavailable", "rights_clearance_unavailable", "source_sync_unavailable",
    "telemetry_unavailable", "upload_unavailable",
}
DOWNLOAD_PRODUCT_FLAGS = {
    "accounts_enabled", "downloads_enabled", "execution_enabled", "hosted_backend_claimed",
    "installers_enabled", "live_probes_enabled", "native_handoff_enabled", "package_manager_enabled",
    "relay_enabled", "source_sync_runtime_enabled", "telemetry_enabled", "uploads_enabled",
}
DOWNLOAD_SEMANTICS = {
    "actions_and_blocked_actions_preserved", "canonical_manifest_identity_preserved",
    "download_install_execution_disabled", "limitations_and_gaps_visible",
    "manifest_metadata_not_download_grant", "rights_risk_safety_posture_preserved",
    "source_and_target_relationships_preserved",
}

EVIDENCE_TYPES = {
    "ai_draft_future", "checksum_claim", "compatibility_claim", "contribution_claim",
    "discussion_derived_future", "filename_or_member_claim", "identity_claim", "manual_observation",
    "metadata_claim", "pack_claim", "snippet", "source_locator", "source_observation",
}
EVIDENCE_STATUSES = {
    "accepted_public_future", "candidate", "conflicting", "deferred", "evidence_needed",
    "needs_review", "normalized", "observed", "policy_blocked", "rejected", "rights_blocked",
    "risk_blocked", "superseded",
}
CLAIM_TYPES = {
    "checksum_claim", "compatibility_claim", "filename_or_member_claim", "identity_claim",
    "metadata_claim", "source_locator_claim",
}
OBSERVATION_TYPES = {
    "manual_observation", "pack_observation", "snippet_observation", "source_locator",
    "source_observation",
}
EVIDENCE_ACTIONS = {
    "copy_citation_hint", "copy_evidence_id", "view_candidate", "view_conflicts", "view_evidence",
    "view_object", "view_pack", "view_review_requirements", "view_source",
}
EVIDENCE_BLOCKED_ACTIONS = {
    "accept_public_unavailable", "account_unavailable", "download_unavailable",
    "hosted_backend_unavailable", "live_probe_unavailable", "malware_safety_unavailable",
    "master_index_mutation_unavailable", "rights_clearance_unavailable", "source_sync_unavailable",
    "telemetry_unavailable", "upload_unavailable",
}
EVIDENCE_PRODUCT_FLAGS = {
    "accepted_public_status", "accounts_enabled", "downloads_enabled", "hosted_backend_claimed",
    "live_probes_enabled", "master_index_mutation_allowed", "public_truth_claimed",
    "source_sync_runtime_enabled", "telemetry_enabled", "uploads_enabled",
}
EVIDENCE_SEMANTICS = {
    "actions_and_blocked_actions_preserved", "canonical_evidence_identity_preserved",
    "claim_observation_review_status_preserved", "conflicts_preserved", "evidence_candidate_not_truth",
    "limitations_and_gaps_visible", "rights_risk_privacy_posture_preserved",
    "source_locator_and_provenance_preserved",
}

ABSENCE_STATUSES = {
    "candidate_available", "capability_gap", "deferred", "manual_observation_pending",
    "near_match_only", "no_verified_result", "not_yet_searched", "policy_blocked",
    "resolved_future", "source_gap", "weak_result_only",
}
ABSENCE_SCOPES = {
    "capability_scope", "fixture_scope", "local_index_scope", "policy_scope", "query_scope",
    "source_scope",
}
ABSENCE_ACTIONS = {
    "copy_absence_id", "copy_citation_hint", "export_work_unit_future", "refine_query",
    "run_node_task_future", "submit_evidence_future", "suggest_source_future", "view_candidates",
    "view_capability_gaps", "view_manual_observation_instructions", "view_near_matches",
    "view_source_gaps", "view_sources_checked", "view_sources_not_checked",
}
ABSENCE_BLOCKED_ACTIONS = {
    "account_unavailable", "crawling_unavailable", "download_unavailable",
    "hosted_backend_unavailable", "live_probe_unavailable", "master_index_mutation_unavailable",
    "node_task_unavailable", "public_submission_unavailable", "scraping_unavailable",
    "source_sync_unavailable", "telemetry_unavailable", "upload_unavailable",
}
ABSENCE_PRODUCT_FLAGS = {
    "accounts_enabled", "downloads_enabled", "exhaustive_global_search_claimed",
    "hosted_backend_claimed", "live_probes_enabled", "master_index_mutation_allowed",
    "node_task_enabled", "public_submission_runtime_enabled", "source_sync_runtime_enabled",
    "telemetry_enabled", "uploads_enabled",
}
ABSENCE_SEMANTICS = {
    "actions_and_blocked_actions_preserved", "absence_scope_preserved",
    "canonical_absence_identity_preserved", "limitations_and_gaps_visible",
    "near_matches_and_gaps_preserved", "no_exhaustive_global_search",
    "sources_checked_and_not_checked_preserved",
}

COMPARISON_TYPES = {
    "absence_near_match_compare", "candidate_compare", "compatibility_compare", "evidence_compare",
    "identity_cluster_compare", "object_version_compare", "pack_compare", "representation_compare",
    "source_record_compare",
}
COMPARISON_STATUSES = {
    "candidate_only", "conflict_detected", "deferred", "duplicate_possible", "evidence_needed",
    "identity_uncertain", "informational", "policy_blocked", "reviewed_future",
}
COMPARISON_AXES = {
    "candidate_state", "compatibility", "evidence", "identity", "representation", "rights",
    "risk", "source", "version",
}
COMPARE_ACTIONS = {
    "copy_citation_hint", "copy_comparison_id", "mark_duplicate_future", "preserve_conflict_future",
    "request_review_future", "view_candidate", "view_conflicts", "view_evidence",
    "view_review_requirements", "view_source", "view_subject",
}
COMPARE_BLOCKED_ACTIONS = {
    "accept_public_unavailable", "account_unavailable", "automatic_dedup_unavailable",
    "automatic_merge_unavailable", "download_unavailable", "hosted_backend_unavailable",
    "install_unavailable", "live_probe_unavailable", "master_index_mutation_unavailable",
    "telemetry_unavailable", "upload_unavailable",
}
COMPARE_PRODUCT_FLAGS = {
    "accepted_public_status", "accounts_enabled", "automatic_dedup_enabled",
    "automatic_merge_enabled", "automatic_promotion_enabled", "downloads_enabled",
    "hosted_backend_claimed", "live_probes_enabled", "master_index_mutation_allowed",
    "telemetry_enabled", "uploads_enabled",
}
COMPARE_SEMANTICS = {
    "actions_and_blocked_actions_preserved", "canonical_comparison_identity_preserved",
    "disagreements_preserved", "limitations_and_gaps_visible", "no_automatic_merge_or_promotion",
    "rights_risk_posture_preserved", "source_evidence_conflict_posture_preserved",
    "subject_relationships_preserved",
}

FLAG_TO_BLOCKED_ACTION = {
    "accepted_public_status": "accept_public_unavailable",
    "accounts_enabled": "account_unavailable",
    "automatic_dedup_enabled": "automatic_dedup_unavailable",
    "automatic_merge_enabled": "automatic_merge_unavailable",
    "automatic_promotion_enabled": "accept_public_unavailable",
    "downloads_enabled": "download_unavailable",
    "execution_enabled": "execute_unavailable",
    "exhaustive_global_search_claimed": "live_probe_unavailable",
    "hosted_backend_claimed": "hosted_backend_unavailable",
    "installers_enabled": "install_unavailable",
    "live_probes_enabled": "live_probe_unavailable",
    "master_index_mutation_allowed": "master_index_mutation_unavailable",
    "native_handoff_enabled": "native_handoff_unavailable",
    "node_task_enabled": "node_task_unavailable",
    "package_manager_enabled": "package_manager_unavailable",
    "public_submission_runtime_enabled": "public_submission_unavailable",
    "public_truth_claimed": "accept_public_unavailable",
    "relay_enabled": "relay_unavailable",
    "source_sync_runtime_enabled": "source_sync_unavailable",
    "telemetry_enabled": "telemetry_unavailable",
    "uploads_enabled": "upload_unavailable",
}
TRUTH_BOUNDARY_FALSE_FIELDS = {
    "absence_public_truth_claimed": "absence must not be public truth",
    "ai_draft_marked_evidence_truth": "AI draft must not be marked evidence truth",
    "checksum_claim_authenticity_proof": "checksum claim must not be authenticity proof",
    "comparison_output_accepted_as_truth": "comparison output must not be accepted truth",
    "contribution_claim_accepted_public": "contribution claim must not be accepted public record",
    "discussion_comment_marked_compatibility_truth": "discussion comment must not be compatibility truth",
    "evidence_candidate_accepted_as_truth": "evidence candidate must not be accepted truth",
    "evidence_page_master_index_mutation": "evidence page must not mutate the master index",
    "global_absence_claimed": "absence must not claim global absence",
    "manual_observation_completed_external_baseline": "manual observation placeholder must not be completed baseline",
    "metadata_claim_rights_clearance": "metadata claim must not be rights clearance",
    "source_observation_accepted_as_truth": "source observation must not be accepted truth",
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
        description="Validate Eureka DownloadManifest, EvidencePage, AbsencePage, and ComparePage view-model contracts."
    )
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help="Repository root to validate.")
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_download_evidence_absence_compare_view_models(Path(args.repo_root))
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


def validate_download_evidence_absence_compare_view_models(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    root = repo_root.resolve()
    errors: list[str] = []
    warnings: list[str] = []

    for path, expected_fields in (
        (DOWNLOAD_CONTRACT_PATH, DOWNLOAD_VIEW_FIELDS),
        (EVIDENCE_CONTRACT_PATH, EVIDENCE_VIEW_FIELDS),
        (ABSENCE_CONTRACT_PATH, ABSENCE_VIEW_FIELDS),
        (COMPARE_CONTRACT_PATH, COMPARE_VIEW_FIELDS),
    ):
        contract = _load_json(root / path, errors, root)
        if isinstance(contract, Mapping):
            _validate_schema(path, contract, expected_fields, errors)

    download_policy = _load_json(root / DOWNLOAD_POLICY_INVENTORY, errors, root)
    evidence_policy = _load_json(root / EVIDENCE_POLICY_INVENTORY, errors, root)
    absence_policy = _load_json(root / ABSENCE_POLICY_INVENTORY, errors, root)
    compare_policy = _load_json(root / COMPARE_POLICY_INVENTORY, errors, root)
    representations = _load_json(root / REPRESENTATION_INVENTORY, errors, root)
    semantic = _load_json(root / SEMANTIC_PARITY_INVENTORY, errors, root)
    route_matrix = _load_json(root / ROUTE_MATRIX_INVENTORY, errors, root)

    downloads = [_load_json(root / path, errors, root) for path in DOWNLOAD_EXAMPLE_PATHS]
    evidences = [_load_json(root / path, errors, root) for path in EVIDENCE_EXAMPLE_PATHS]
    absences = [_load_json(root / path, errors, root) for path in ABSENCE_EXAMPLE_PATHS]
    compares = [_load_json(root / path, errors, root) for path in COMPARE_EXAMPLE_PATHS]

    if all(
        isinstance(payload, Mapping)
        for payload in (download_policy, evidence_policy, absence_policy, compare_policy, representations, semantic, route_matrix)
    ) and all(isinstance(payload, Mapping) for payload in downloads + evidences + absences + compares):
        errors.extend(
            validate_payloads(
                download_policy,
                evidence_policy,
                absence_policy,
                compare_policy,
                representations,
                semantic,
                route_matrix,
                downloads,
                evidences,
                absences,
                compares,
                source_label="files",
            )
        )

    errors = sorted(set(errors))
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "valid" if not errors else "invalid",
        "errors": errors,
        "warnings": sorted(set(warnings)),
        "download_example_count": len(DOWNLOAD_EXAMPLE_PATHS),
        "evidence_example_count": len(EVIDENCE_EXAMPLE_PATHS),
        "absence_example_count": len(ABSENCE_EXAMPLE_PATHS),
        "compare_example_count": len(COMPARE_EXAMPLE_PATHS),
    }


def validate_payloads(
    download_policy: Mapping[str, Any],
    evidence_policy: Mapping[str, Any],
    absence_policy: Mapping[str, Any],
    compare_policy: Mapping[str, Any],
    representations: Mapping[str, Any],
    semantic: Mapping[str, Any],
    route_matrix: Mapping[str, Any],
    download_examples: Sequence[Mapping[str, Any]],
    evidence_examples: Sequence[Mapping[str, Any]],
    absence_examples: Sequence[Mapping[str, Any]],
    compare_examples: Sequence[Mapping[str, Any]],
    *,
    source_label: str = "payloads",
) -> list[str]:
    errors: list[str] = []
    representation_ids = _representation_ids(representations)
    semantic_ids = _semantic_policy_ids(semantic)
    route_records = _route_records(route_matrix)

    contexts = {
        "download": _policy_context(download_policy),
        "evidence": _policy_context(evidence_policy),
        "absence": _policy_context(absence_policy),
        "compare": _policy_context(compare_policy),
    }
    policy_specs = (
        ("download policy", download_policy, DOWNLOAD_POLICY_FIELDS, "DownloadManifestView", "download_manifest_future", DOWNLOAD_CONTRACT_PATH, DOWNLOAD_SEMANTICS, MANIFEST_TYPES, "allowed_manifest_types", MANIFEST_STATUSES, "allowed_manifest_statuses"),
        ("evidence policy", evidence_policy, EVIDENCE_POLICY_FIELDS, "EvidencePageView", "evidence_page_future", EVIDENCE_CONTRACT_PATH, EVIDENCE_SEMANTICS, EVIDENCE_TYPES, "allowed_evidence_types", EVIDENCE_STATUSES, "allowed_evidence_statuses"),
        ("absence policy", absence_policy, ABSENCE_POLICY_FIELDS, "AbsencePageView", "absence_page_future", ABSENCE_CONTRACT_PATH, ABSENCE_SEMANTICS, ABSENCE_STATUSES, "allowed_absence_statuses", ABSENCE_SCOPES, "allowed_absence_scopes"),
        ("compare policy", compare_policy, COMPARE_POLICY_FIELDS, "ComparePageView", "compare_page_future", COMPARE_CONTRACT_PATH, COMPARE_SEMANTICS, COMPARISON_TYPES, "allowed_comparison_types", COMPARISON_STATUSES, "allowed_comparison_statuses"),
    )
    for label, policy, fields, view, route, contract_ref, semantics, expected_vocab_a, vocab_key_a, expected_vocab_b, vocab_key_b in policy_specs:
        errors.extend(_validate_policy(label, policy, fields, view, route, contract_ref, semantics, expected_vocab_a, vocab_key_a, expected_vocab_b, vocab_key_b, representation_ids, semantic_ids, route_records))

    for index, example in enumerate(download_examples):
        errors.extend(_validate_download_example(f"{source_label}: download example {index}", example, contexts["download"], representation_ids, route_records))
    for index, example in enumerate(evidence_examples):
        errors.extend(_validate_evidence_example(f"{source_label}: evidence example {index}", example, contexts["evidence"], representation_ids, route_records))
    for index, example in enumerate(absence_examples):
        errors.extend(_validate_absence_example(f"{source_label}: absence example {index}", example, contexts["absence"], representation_ids, route_records))
    for index, example in enumerate(compare_examples):
        errors.extend(_validate_compare_example(f"{source_label}: compare example {index}", example, contexts["compare"], representation_ids, route_records))

    return sorted(errors)


def _validate_schema(path: str, schema: Mapping[str, Any], expected_fields: set[str], errors: list[str]) -> None:
    missing = REQUIRED_SCHEMA_FIELDS - set(schema)
    if missing:
        errors.append(f"{path}: schema missing top-level fields {sorted(missing)}")
    properties = schema.get("properties")
    required = schema.get("required")
    if not isinstance(properties, Mapping):
        errors.append(f"{path}: properties must be an object")
        return
    if not isinstance(required, Sequence) or isinstance(required, (str, bytes)):
        errors.append(f"{path}: required must be an array")
        return
    required_set = {item for item in required if isinstance(item, str)}
    missing_required = expected_fields - required_set
    missing_properties = expected_fields - set(properties)
    if missing_required:
        errors.append(f"{path}: required missing {sorted(missing_required)}")
    if missing_properties:
        errors.append(f"{path}: properties missing {sorted(missing_properties)}")
    version = _mapping(properties.get("schema_version")).get("const")
    if version != SCHEMA_VERSION:
        errors.append(f"{path}: schema_version const must be {SCHEMA_VERSION!r}")


def _validate_policy(
    label: str,
    policy: Mapping[str, Any],
    required_fields: set[str],
    view_family: str,
    route_family: str,
    contract_ref: str,
    required_semantics: set[str],
    expected_vocab_a: set[str],
    vocab_key_a: str,
    expected_vocab_b: set[str],
    vocab_key_b: str,
    representation_ids: set[str],
    semantic_ids: set[str],
    route_records: Mapping[str, Mapping[str, Any]],
) -> list[str]:
    errors: list[str] = []
    missing = required_fields - set(policy)
    if missing:
        errors.append(f"{label}: missing policy fields {sorted(missing)}")
    if policy.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"{label}: schema_version must be {SCHEMA_VERSION}")
    if policy.get("contract_ref") != contract_ref:
        errors.append(f"{label}: contract_ref must be {contract_ref!r}")
    if policy.get("canonical_view_family") != view_family:
        errors.append(f"{label}: canonical_view_family must be {view_family}")
    routes = set(_string_items(policy.get("supported_route_families")))
    if route_family not in routes:
        errors.append(f"{label}: supported_route_families must include {route_family}")
    if route_family not in route_records:
        errors.append(f"{label}: route {route_family!r} is missing from route matrix")
    elif route_records[route_family].get("canonical_view_family") != view_family:
        errors.append(f"{label}: route {route_family!r} does not bind to {view_family}")
    semantic_ref = policy.get("required_semantic_parity_policy")
    if semantic_ref not in semantic_ids:
        errors.append(f"{label}: required_semantic_parity_policy {semantic_ref!r} does not exist")
    profiles = set(_string_items(policy.get("allowed_representation_profiles")))
    missing_profiles = profiles - representation_ids
    if missing_profiles:
        errors.append(f"{label}: unknown representation profiles {sorted(missing_profiles)}")
    missing_required_hints = REQUIRED_REPRESENTATION_HINTS - set(_string_items(policy.get("required_representation_hints")))
    if missing_required_hints:
        errors.append(f"{label}: required_representation_hints missing {sorted(missing_required_hints)}")
    missing_semantics = required_semantics - set(_string_items(policy.get("required_semantic_requirements")))
    if missing_semantics:
        errors.append(f"{label}: required_semantic_requirements missing {sorted(missing_semantics)}")
    missing_vocab_a = expected_vocab_a - set(_string_items(policy.get(vocab_key_a)))
    missing_vocab_b = expected_vocab_b - set(_string_items(policy.get(vocab_key_b)))
    if missing_vocab_a:
        errors.append(f"{label}: {vocab_key_a} missing {sorted(missing_vocab_a)}")
    if missing_vocab_b:
        errors.append(f"{label}: {vocab_key_b} missing {sorted(missing_vocab_b)}")
    return errors


def _validate_download_example(
    label: str,
    example: Mapping[str, Any],
    context: Mapping[str, Any],
    representation_ids: set[str],
    route_records: Mapping[str, Mapping[str, Any]],
) -> list[str]:
    errors = _validate_common_example(label, example, "DownloadManifestView", DOWNLOAD_VIEW_FIELDS, context, representation_ids, route_records, DOWNLOAD_SEMANTICS)
    identity = _mapping(example.get("manifest_identity"))
    errors.extend(_require_object_fields(label, "manifest_identity", identity, DOWNLOAD_IDENTITY_FIELDS))
    if not identity.get("manifest_id"):
        errors.append(f"{label}: canonical manifest identity manifest_id is required")
    if not identity.get("canonical_route"):
        errors.append(f"{label}: canonical manifest identity canonical_route is required")
    if identity.get("manifest_type") not in context["manifest_types"] or identity.get("manifest_type") not in MANIFEST_TYPES:
        errors.append(f"{label}: manifest_type {identity.get('manifest_type')!r} is not allowed")
    if identity.get("manifest_status") not in context["manifest_statuses"]:
        errors.append(f"{label}: manifest_status {identity.get('manifest_status')!r} is not allowed")
    access = _mapping(example.get("access_path_summary"))
    for key in ("access_status", "direct_download_status", "mirror_status", "install_status", "execution_status", "package_manager_status", "rights_clearance_status", "malware_safety_status"):
        value = access.get(key)
        if value not in context["access_statuses"] and key == "access_status":
            errors.append(f"{label}: access_status {value!r} is not allowed")
    for key in ("direct_download_status", "install_status", "execution_status", "package_manager_status", "rights_clearance_status", "malware_safety_status"):
        if access.get(key) != "unavailable":
            errors.append(f"{label}: access_path_summary.{key} must be 'unavailable'")
    errors.extend(_validate_false_fields_recursive(label, example, DOWNLOAD_PRODUCT_FLAGS | set(SAFETY_FALSE_FIELDS) | set(TRUTH_BOUNDARY_FALSE_FIELDS)))
    errors.extend(_validate_action_boundary(label, example, DOWNLOAD_PRODUCT_FLAGS, DOWNLOAD_BLOCKED_ACTIONS, context["blocked"], context["actions"]))
    errors.extend(_validate_unsafe_patterns(label, example))
    return sorted(errors)


def _validate_evidence_example(
    label: str,
    example: Mapping[str, Any],
    context: Mapping[str, Any],
    representation_ids: set[str],
    route_records: Mapping[str, Mapping[str, Any]],
) -> list[str]:
    errors = _validate_common_example(label, example, "EvidencePageView", EVIDENCE_VIEW_FIELDS, context, representation_ids, route_records, EVIDENCE_SEMANTICS)
    identity = _mapping(example.get("evidence_identity"))
    errors.extend(_require_object_fields(label, "evidence_identity", identity, EVIDENCE_IDENTITY_FIELDS))
    if not identity.get("evidence_id"):
        errors.append(f"{label}: canonical evidence identity evidence_id is required")
    if not identity.get("canonical_route"):
        errors.append(f"{label}: canonical evidence identity canonical_route is required")
    if example.get("evidence_type") not in context["evidence_types"]:
        errors.append(f"{label}: evidence_type {example.get('evidence_type')!r} is not allowed")
    if example.get("evidence_status") not in context["evidence_statuses"]:
        errors.append(f"{label}: evidence_status {example.get('evidence_status')!r} is not allowed")
    if example.get("evidence_status") == "accepted_public_future":
        errors.append(f"{label}: current evidence example must not be accepted public future")
    if identity.get("claim_type") not in context["claim_types"]:
        errors.append(f"{label}: claim_type {identity.get('claim_type')!r} is not allowed")
    if identity.get("observation_type") not in context["observation_types"]:
        errors.append(f"{label}: observation_type {identity.get('observation_type')!r} is not allowed")
    review = _mapping(example.get("review_summary"))
    if review.get("review_required") is not True:
        errors.append(f"{label}: review_summary.review_required must be true")
    for key in ("accepted_public_status", "master_index_mutation_allowed"):
        if review.get(key) is not False:
            errors.append(f"{label}: review_summary.{key} must be false")
    errors.extend(_validate_false_fields_recursive(label, example, EVIDENCE_PRODUCT_FLAGS | set(SAFETY_FALSE_FIELDS) | set(TRUTH_BOUNDARY_FALSE_FIELDS)))
    errors.extend(_validate_action_boundary(label, example, EVIDENCE_PRODUCT_FLAGS, EVIDENCE_BLOCKED_ACTIONS, context["blocked"], context["actions"]))
    errors.extend(_validate_unsafe_patterns(label, example))
    return sorted(errors)


def _validate_absence_example(
    label: str,
    example: Mapping[str, Any],
    context: Mapping[str, Any],
    representation_ids: set[str],
    route_records: Mapping[str, Mapping[str, Any]],
) -> list[str]:
    errors = _validate_common_example(label, example, "AbsencePageView", ABSENCE_VIEW_FIELDS, context, representation_ids, route_records, ABSENCE_SEMANTICS)
    identity = _mapping(example.get("absence_identity"))
    errors.extend(_require_object_fields(label, "absence_identity", identity, ABSENCE_IDENTITY_FIELDS))
    if not identity.get("absence_id"):
        errors.append(f"{label}: canonical absence identity absence_id is required")
    if not identity.get("canonical_route"):
        errors.append(f"{label}: canonical absence identity canonical_route is required")
    if example.get("absence_status") not in context["absence_statuses"]:
        errors.append(f"{label}: absence_status {example.get('absence_status')!r} is not allowed")
    if identity.get("absence_scope") not in context["absence_scopes"]:
        errors.append(f"{label}: absence_scope {identity.get('absence_scope')!r} is not allowed")
    errors.extend(_validate_false_fields_recursive(label, example, ABSENCE_PRODUCT_FLAGS | set(SAFETY_FALSE_FIELDS) | set(TRUTH_BOUNDARY_FALSE_FIELDS)))
    errors.extend(_validate_action_boundary(label, example, ABSENCE_PRODUCT_FLAGS, ABSENCE_BLOCKED_ACTIONS, context["blocked"], context["actions"]))
    errors.extend(_validate_unsafe_patterns(label, example))
    return sorted(errors)


def _validate_compare_example(
    label: str,
    example: Mapping[str, Any],
    context: Mapping[str, Any],
    representation_ids: set[str],
    route_records: Mapping[str, Mapping[str, Any]],
) -> list[str]:
    errors = _validate_common_example(label, example, "ComparePageView", COMPARE_VIEW_FIELDS, context, representation_ids, route_records, COMPARE_SEMANTICS)
    identity = _mapping(example.get("comparison_identity"))
    errors.extend(_require_object_fields(label, "comparison_identity", identity, COMPARE_IDENTITY_FIELDS))
    if not identity.get("comparison_id"):
        errors.append(f"{label}: canonical comparison identity comparison_id is required")
    if not identity.get("canonical_route"):
        errors.append(f"{label}: canonical comparison identity canonical_route is required")
    if example.get("comparison_type") not in context["comparison_types"]:
        errors.append(f"{label}: comparison_type {example.get('comparison_type')!r} is not allowed")
    if example.get("comparison_status") not in context["comparison_statuses"]:
        errors.append(f"{label}: comparison_status {example.get('comparison_status')!r} is not allowed")
    axes = set(_string_items(example.get("comparison_axes")))
    unknown_axes = axes - context["comparison_axes"]
    if unknown_axes:
        errors.append(f"{label}: comparison_axes contain unknown axes {sorted(unknown_axes)}")
    errors.extend(_validate_false_fields_recursive(label, example, COMPARE_PRODUCT_FLAGS | set(SAFETY_FALSE_FIELDS) | set(TRUTH_BOUNDARY_FALSE_FIELDS)))
    errors.extend(_validate_action_boundary(label, example, COMPARE_PRODUCT_FLAGS, COMPARE_BLOCKED_ACTIONS, context["blocked"], context["actions"]))
    errors.extend(_validate_unsafe_patterns(label, example))
    return sorted(errors)


def _validate_common_example(
    label: str,
    example: Mapping[str, Any],
    view_family: str,
    required_fields: set[str],
    context: Mapping[str, Any],
    representation_ids: set[str],
    route_records: Mapping[str, Mapping[str, Any]],
    required_semantics: set[str],
) -> list[str]:
    errors: list[str] = []
    missing = required_fields - set(example)
    if missing:
        errors.append(f"{label}: missing required {view_family} top-level fields {sorted(missing)}")
        return errors
    if example.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"{label}: schema_version must be {SCHEMA_VERSION}")
    if example.get("view_family") != view_family:
        errors.append(f"{label}: view_family must be {view_family}")
    errors.extend(_validate_route(label, example, view_family, context["routes"], route_records))
    errors.extend(_validate_hints(label, example, representation_ids, context["representations"], context["hints"]))
    errors.extend(_validate_semantics(label, example, required_semantics, context["semantics"]))
    errors.extend(_validate_generated_from(label, example, str(context["semantic_ref"])))
    return errors


def _validate_route(label: str, example: Mapping[str, Any], view_family: str, allowed_routes: set[str], route_records: Mapping[str, Mapping[str, Any]]) -> list[str]:
    errors: list[str] = []
    route_family = example.get("route_family")
    if route_family not in allowed_routes:
        errors.append(f"{label}: route_family {route_family!r} is not allowed by policy")
    if route_family not in route_records:
        errors.append(f"{label}: route_family {route_family!r} is not in route matrix")
    elif route_records[route_family].get("canonical_view_family") != view_family:
        errors.append(f"{label}: route_family {route_family!r} does not bind to {view_family}")
    return errors


def _validate_action_boundary(label: str, example: Mapping[str, Any], product_flags: set[str], required_blocked: set[str], policy_blocked: set[str], policy_actions: set[str]) -> list[str]:
    errors: list[str] = []
    blocked = _action_ids(example.get("blocked_actions"))
    summary = _mapping(example.get("action_summary"))
    missing_blocked = (required_blocked | policy_blocked) - blocked
    if missing_blocked:
        errors.append(f"{label}: blocked_actions missing {sorted(missing_blocked)}")
    summary_blocked = set(_string_items(summary.get("blocked_actions")))
    summary_missing = (required_blocked | policy_blocked) - summary_blocked
    if summary_missing:
        errors.append(f"{label}: action_summary.blocked_actions missing {sorted(summary_missing)}")
    actions = _action_ids(example.get("actions"))
    unknown_actions = actions - policy_actions
    if unknown_actions:
        errors.append(f"{label}: actions contain unknown action ids {sorted(unknown_actions)}")
    summary_actions = set(_string_items(summary.get("allowed_actions")))
    unknown_summary_actions = summary_actions - policy_actions
    if unknown_summary_actions:
        errors.append(f"{label}: action_summary contains unknown actions {sorted(unknown_summary_actions)}")
    for flag in sorted(product_flags):
        if summary.get(flag) is not False:
            errors.append(f"{label}: {flag} must be false for current examples")
        blocked_action = FLAG_TO_BLOCKED_ACTION.get(flag)
        if blocked_action and blocked_action not in blocked:
            errors.append(f"{label}: missing blocked action {blocked_action} for false {flag}")
    return errors


def _validate_false_fields_recursive(label: str, value: Any, field_names: set[str], path: str = "$") -> list[str]:
    errors: list[str] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key in field_names and child is not False:
                phrase = SAFETY_FALSE_FIELDS.get(key) or TRUTH_BOUNDARY_FALSE_FIELDS.get(key) or key
                errors.append(f"{label}: {child_path} must be false ({phrase})")
            errors.extend(_validate_false_fields_recursive(label, child, field_names, child_path))
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for index, child in enumerate(value):
            errors.extend(_validate_false_fields_recursive(label, child, field_names, f"{path}[{index}]"))
    return errors


def _validate_hints(label: str, example: Mapping[str, Any], representation_ids: set[str], policy_representations: set[str], policy_required_hints: set[str]) -> list[str]:
    errors: list[str] = []
    hints = example.get("representation_hints")
    if not isinstance(hints, Mapping):
        return [f"{label}: representation_hints must be an object"]
    hint_ids = set(hints)
    unknown_hints = hint_ids - representation_ids
    if unknown_hints:
        errors.append(f"{label}: representation_hints reference unknown profiles {sorted(unknown_hints)}")
    missing_hints = (policy_required_hints | REQUIRED_REPRESENTATION_HINTS) - hint_ids
    if missing_hints:
        errors.append(f"{label}: representation_hints missing {sorted(missing_hints)}")
    disallowed = hint_ids - policy_representations
    if disallowed:
        errors.append(f"{label}: representation_hints include profiles outside policy {sorted(disallowed)}")
    for hint_id in sorted(hint_ids):
        hint = hints[hint_id]
        if not isinstance(hint, Mapping):
            errors.append(f"{label}: representation hint {hint_id} must be an object")
        elif hint.get("semantic_meaning_changes_allowed") is not False:
            errors.append(f"{label}: {hint_id} must not allow semantic meaning changes")
    return errors


def _validate_semantics(label: str, example: Mapping[str, Any], required_semantics: set[str], policy_semantics: set[str]) -> list[str]:
    semantics = set(_string_items(example.get("semantic_requirements")))
    missing = (required_semantics | policy_semantics) - semantics
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


def _policy_context(policy: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "routes": set(_string_items(policy.get("supported_route_families"))),
        "semantic_ref": str(policy.get("required_semantic_parity_policy", "")),
        "representations": set(_string_items(policy.get("allowed_representation_profiles"))),
        "hints": set(_string_items(policy.get("required_representation_hints"))),
        "semantics": set(_string_items(policy.get("required_semantic_requirements"))),
        "blocked": set(_string_items(policy.get("required_blocked_actions"))),
        "actions": set(_string_items(policy.get("allowed_action_names"))),
        "manifest_types": set(_string_items(policy.get("allowed_manifest_types"))),
        "manifest_statuses": set(_string_items(policy.get("allowed_manifest_statuses"))),
        "access_statuses": set(_string_items(policy.get("allowed_access_statuses"))),
        "evidence_types": set(_string_items(policy.get("allowed_evidence_types"))),
        "evidence_statuses": set(_string_items(policy.get("allowed_evidence_statuses"))),
        "claim_types": set(_string_items(policy.get("allowed_claim_types"))),
        "observation_types": set(_string_items(policy.get("allowed_observation_types"))),
        "absence_statuses": set(_string_items(policy.get("allowed_absence_statuses"))),
        "absence_scopes": set(_string_items(policy.get("allowed_absence_scopes"))),
        "comparison_types": set(_string_items(policy.get("allowed_comparison_types"))),
        "comparison_statuses": set(_string_items(policy.get("allowed_comparison_statuses"))),
        "comparison_axes": set(_string_items(policy.get("allowed_comparison_axes"))),
    }


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
        f"validate_download_evidence_absence_compare_view_models: {report['status']}",
        f"schema_version: {report['schema_version']}",
        f"download_examples: {report['download_example_count']}",
        f"evidence_examples: {report['evidence_example_count']}",
        f"absence_examples: {report['absence_example_count']}",
        f"compare_examples: {report['compare_example_count']}",
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
