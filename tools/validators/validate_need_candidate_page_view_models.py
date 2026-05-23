from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_VERSION = "0.1.0"

NEED_CONTRACT_PATH = "contracts/view/pages/need_page.v0.json"
CANDIDATE_CONTRACT_PATH = "contracts/view/pages/candidate_page.v0.json"
NEED_POLICY_INVENTORY = "control/inventory/publication/need_page_view_model_policy.json"
CANDIDATE_POLICY_INVENTORY = "control/inventory/publication/candidate_page_view_model_policy.json"
REPRESENTATION_INVENTORY = "control/inventory/publication/representation_profiles.json"
SEMANTIC_PARITY_INVENTORY = "control/inventory/publication/semantic_renderer_parity_policy.json"
ROUTE_MATRIX_INVENTORY = "control/inventory/publication/route_view_representation_matrix.json"

NEED_EXAMPLE_PATHS = [
    "examples/view_models/need_page/known_absence_need_page_v0.json",
    "examples/view_models/need_page/minimal_need_page_v0.json",
    "examples/view_models/need_page/source_gap_need_page_v0.json",
    "examples/view_models/need_page/work_unit_future_need_page_v0.json",
]
CANDIDATE_EXAMPLE_PATHS = [
    "examples/view_models/candidate_page/evidence_candidate_page_v0.json",
    "examples/view_models/candidate_page/minimal_candidate_page_v0.json",
    "examples/view_models/candidate_page/policy_blocked_candidate_page_v0.json",
    "examples/view_models/candidate_page/source_observed_candidate_page_v0.json",
]

REQUIRED_SCHEMA_FIELDS = {"$schema", "$id", "title", "description", "type", "required", "properties"}
NEED_VIEW_FIELDS = {
    "schema_version",
    "view_model_id",
    "view_family",
    "route_family",
    "canonical_route",
    "page_title",
    "page_status",
    "need",
    "need_identity",
    "need_status",
    "need_scope",
    "query_summary",
    "interpreted_intent",
    "demand_summary",
    "absence_summary",
    "searched_scope",
    "sources_checked",
    "sources_not_checked",
    "source_gap_summary",
    "near_match_summary",
    "candidate_summary",
    "evidence_summary",
    "work_unit_summary_future",
    "contribution_summary_future",
    "privacy_summary",
    "poisoning_guard_summary",
    "rights_summary",
    "risk_summary",
    "action_summary",
    "actions",
    "blocked_actions",
    "limitations",
    "warnings",
    "representation_hints",
    "semantic_requirements",
    "generated_from",
    "no_goals",
    "notes",
}
CANDIDATE_VIEW_FIELDS = {
    "schema_version",
    "view_model_id",
    "view_family",
    "route_family",
    "canonical_route",
    "page_title",
    "page_status",
    "candidate",
    "candidate_identity",
    "candidate_status",
    "candidate_type",
    "candidate_source",
    "proposed_object_summary",
    "proposed_state_summary",
    "evidence_summary",
    "source_summary",
    "provenance_summary",
    "compatibility_summary",
    "rights_summary",
    "risk_summary",
    "review_summary",
    "conflict_summary",
    "deduplication_summary",
    "related_need_refs",
    "related_object_refs",
    "related_source_refs",
    "related_pack_refs",
    "related_work_unit_refs_future",
    "action_summary",
    "actions",
    "blocked_actions",
    "limitations",
    "warnings",
    "representation_hints",
    "semantic_requirements",
    "generated_from",
    "no_goals",
    "notes",
}
NEED_POLICY_FIELDS = {
    "schema_version",
    "policy_id",
    "contract_ref",
    "label",
    "description",
    "status",
    "stability",
    "created_by_slice",
    "canonical_view_family",
    "supported_route_families",
    "required_semantic_parity_policy",
    "allowed_representation_profiles",
    "allowed_need_statuses",
    "allowed_demand_fields",
    "allowed_absence_states",
    "allowed_action_names",
    "required_blocked_actions",
    "required_product_boundary_booleans",
    "required_representation_hints",
    "required_semantic_requirements",
    "current_no_goals",
    "future_deferred_fields",
    "notes",
}
CANDIDATE_POLICY_FIELDS = {
    "schema_version",
    "policy_id",
    "contract_ref",
    "label",
    "description",
    "status",
    "stability",
    "created_by_slice",
    "canonical_view_family",
    "supported_route_families",
    "required_semantic_parity_policy",
    "allowed_representation_profiles",
    "allowed_candidate_statuses",
    "allowed_candidate_origins",
    "allowed_candidate_types",
    "allowed_review_states",
    "allowed_action_names",
    "required_blocked_actions",
    "required_product_boundary_booleans",
    "required_safety_claim_booleans",
    "required_representation_hints",
    "required_semantic_requirements",
    "current_no_goals",
    "future_deferred_fields",
    "notes",
}
NEED_IDENTITY_FIELDS = {
    "need_id",
    "need_slug",
    "canonical_route",
    "canonical_need_label",
    "object_family",
    "product_or_topic",
    "version_or_state",
    "platform_or_context",
    "artifact_type",
    "desired_user_action",
    "aliases",
    "related_queries",
    "related_need_refs",
    "identity_confidence",
    "identity_limitations",
    "notes",
}
CANDIDATE_IDENTITY_FIELDS = {
    "candidate_id",
    "candidate_slug",
    "candidate_type",
    "canonical_route",
    "proposed_title",
    "proposed_object_id_future",
    "proposed_source_id",
    "candidate_origin",
    "candidate_origin_ref",
    "candidate_confidence",
    "candidate_limitations",
    "notes",
}
DEMAND_FIELDS = {
    "aggregate_only",
    "demand_score",
    "demand_score_available",
    "demand_score_limitations",
    "demand_status",
    "first_seen_or_recorded_when_available",
    "last_seen_or_recorded_when_available",
    "observation_count",
    "poisoning_guarded",
    "privacy_filtered",
    "raw_query_retention",
}
ABSENCE_FIELDS = {
    "absence_status",
    "searched_scope",
    "sources_checked",
    "sources_not_checked",
    "near_matches",
    "rejected_matches",
    "known_gaps",
    "capability_gaps",
    "policy_blocked_sources",
    "next_safe_actions",
    "work_unit_refs_future",
    "limitations",
    "notes",
}
CANDIDATE_REVIEW_FIELDS = {
    "review_status",
    "review_required",
    "reviewer_role_required",
    "acceptance_requirements",
    "rejection_reason",
    "deferral_reason",
    "conflict_preservation_required",
    "master_index_mutation_allowed",
    "accepted_public_status",
    "notes",
}

REQUIRED_REPRESENTATION_HINTS = {
    "api_json",
    "file_tree",
    "html32",
    "lite_html",
    "manifest_json",
    "native_card_future",
    "print",
    "relay_future",
    "snapshot_future",
    "standard_html",
    "terminal_future",
    "text",
}
NEED_STATUSES = {
    "accepted_result_available_future",
    "candidate_available",
    "capability_gap",
    "deferred",
    "evidence_needed",
    "partially_resolved",
    "policy_blocked",
    "review_pending",
    "source_gap",
    "superseded",
    "unresolved",
    "weakly_resolved",
}
ABSENCE_STATES = {
    "candidate_exists",
    "capability_gap_exists",
    "near_miss_exists",
    "no_verified_result",
    "not_searched_yet",
    "policy_blocked",
    "scoped_known_absence",
    "source_gap_exists",
}
CANDIDATE_STATUSES = {
    "accepted_public_future",
    "candidate",
    "conflict_detected",
    "deferred",
    "duplicate_possible",
    "evidence_needed",
    "needs_review",
    "normalized",
    "observed",
    "policy_blocked",
    "rejected",
    "rights_blocked",
    "risk_blocked",
    "superseded",
}
CANDIDATE_ORIGINS = {
    "ai_draft_future",
    "contribution_pack",
    "deep_extraction_future",
    "discussion_to_evidence_future",
    "evidence_pack",
    "index_pack",
    "manual_observation",
    "node_work_unit_future",
    "search_need",
    "source_cache_record",
    "source_observation",
}
CANDIDATE_TYPES = {
    "compatibility_claim",
    "duplicate_lead",
    "evidence_lead",
    "file_member_lead",
    "object_lead",
    "policy_blocked_lead",
    "source_lead",
    "version_lead",
}
REVIEW_STATES = {
    "deferred",
    "needs_evidence",
    "needs_human_review",
    "policy_blocked",
    "rejected",
    "review_required",
}
NEED_ACTIONS = {
    "copy_citation_hint",
    "copy_need_id",
    "export_work_unit_future",
    "refine_query",
    "run_node_task_future",
    "submit_evidence_future",
    "suggest_source_future",
    "view_absence_scope",
    "view_candidates",
    "view_manual_observation_instructions",
    "view_near_matches",
    "view_source_gaps",
    "view_sources_checked",
    "watch_need_future",
}
CANDIDATE_ACTIONS = {
    "copy_candidate_id",
    "copy_citation_hint",
    "defer_future",
    "mark_duplicate_future",
    "reject_future",
    "request_more_evidence_future",
    "submit_review_future",
    "view_candidate_summary",
    "view_conflicts",
    "view_evidence",
    "view_related_need",
    "view_related_pack",
    "view_review_requirements",
    "view_source",
}
NEED_BLOCKED_ACTIONS = {
    "account_unavailable",
    "arbitrary_url_fetch_unavailable",
    "crawling_unavailable",
    "download_unavailable",
    "hosted_backend_unavailable",
    "install_unavailable",
    "live_probe_unavailable",
    "master_index_mutation_unavailable",
    "node_task_unavailable",
    "public_submission_unavailable",
    "scraping_unavailable",
    "source_sync_unavailable",
    "telemetry_unavailable",
    "upload_unavailable",
}
CANDIDATE_BLOCKED_ACTIONS = {
    "accept_public_unavailable",
    "account_unavailable",
    "download_unavailable",
    "execute_unavailable",
    "hosted_backend_unavailable",
    "install_unavailable",
    "live_probe_unavailable",
    "malware_safety_unavailable",
    "master_index_mutation_unavailable",
    "rights_clearance_unavailable",
    "source_sync_unavailable",
    "telemetry_unavailable",
    "upload_unavailable",
    "verified_installability_unavailable",
}
NEED_PRODUCT_FLAGS = {
    "accounts_enabled",
    "downloads_enabled",
    "hosted_backend_claimed",
    "live_probes_enabled",
    "node_task_runtime_enabled",
    "public_submissions_enabled",
    "source_sync_runtime_enabled",
    "telemetry_enabled",
    "uploads_enabled",
}
CANDIDATE_PRODUCT_FLAGS = {
    "accept_public_enabled",
    "accounts_enabled",
    "downloads_enabled",
    "hosted_backend_claimed",
    "live_probes_enabled",
    "master_index_mutation_allowed",
    "source_sync_runtime_enabled",
    "telemetry_enabled",
    "uploads_enabled",
}
FLAG_TO_BLOCKED_ACTION = {
    "accept_public_enabled": "accept_public_unavailable",
    "accounts_enabled": "account_unavailable",
    "downloads_enabled": "download_unavailable",
    "hosted_backend_claimed": "hosted_backend_unavailable",
    "live_probes_enabled": "live_probe_unavailable",
    "master_index_mutation_allowed": "master_index_mutation_unavailable",
    "node_task_runtime_enabled": "node_task_unavailable",
    "public_submissions_enabled": "public_submission_unavailable",
    "source_sync_runtime_enabled": "source_sync_unavailable",
    "telemetry_enabled": "telemetry_unavailable",
    "uploads_enabled": "upload_unavailable",
}
NEED_SEMANTICS = {
    "absence_scope_preserved",
    "actions_and_blocked_actions_preserved",
    "canonical_need_identity_preserved",
    "candidate_state_preserved",
    "demand_privacy_posture_preserved",
    "evidence_posture_preserved",
    "limitations_and_gaps_visible",
    "no_exhaustive_global_search_claims",
    "no_public_truth_from_demand",
    "query_intent_posture_preserved",
    "rights_risk_privacy_posture_preserved",
    "source_gap_posture_preserved",
}
CANDIDATE_SEMANTICS = {
    "actions_and_blocked_actions_preserved",
    "candidate_origin_preserved",
    "candidate_review_state_preserved",
    "canonical_candidate_identity_preserved",
    "conflicts_and_deduplication_preserved",
    "evidence_posture_preserved",
    "limitations_and_gaps_visible",
    "no_public_truth_from_candidates",
    "provisional_status_preserved",
    "rights_risk_privacy_posture_preserved",
    "source_observation_not_truth_preserved",
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
        description="Validate Eureka NeedPage and CandidatePage view-model schemas, policies, and examples."
    )
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help="Repository root to validate.")
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_need_candidate_page_view_models(Path(args.repo_root))
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


def validate_need_candidate_page_view_models(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    root = repo_root.resolve()
    errors: list[str] = []
    warnings: list[str] = []

    need_contract = _load_json(root / NEED_CONTRACT_PATH, errors, root)
    candidate_contract = _load_json(root / CANDIDATE_CONTRACT_PATH, errors, root)
    if isinstance(need_contract, Mapping):
        _validate_schema(NEED_CONTRACT_PATH, need_contract, NEED_VIEW_FIELDS, errors)
    if isinstance(candidate_contract, Mapping):
        _validate_schema(CANDIDATE_CONTRACT_PATH, candidate_contract, CANDIDATE_VIEW_FIELDS, errors)

    need_policy = _load_json(root / NEED_POLICY_INVENTORY, errors, root)
    candidate_policy = _load_json(root / CANDIDATE_POLICY_INVENTORY, errors, root)
    representations = _load_json(root / REPRESENTATION_INVENTORY, errors, root)
    semantic = _load_json(root / SEMANTIC_PARITY_INVENTORY, errors, root)
    route_matrix = _load_json(root / ROUTE_MATRIX_INVENTORY, errors, root)
    need_examples = [_load_json(root / path, errors, root) for path in NEED_EXAMPLE_PATHS]
    candidate_examples = [_load_json(root / path, errors, root) for path in CANDIDATE_EXAMPLE_PATHS]
    need_payloads = [item for item in need_examples if isinstance(item, Mapping)]
    candidate_payloads = [item for item in candidate_examples if isinstance(item, Mapping)]

    if (
        isinstance(need_policy, Mapping)
        and isinstance(candidate_policy, Mapping)
        and isinstance(representations, Mapping)
        and isinstance(semantic, Mapping)
        and isinstance(route_matrix, Mapping)
    ):
        errors.extend(
            validate_payloads(
                need_policy,
                candidate_policy,
                representations,
                semantic,
                route_matrix,
                need_payloads,
                candidate_payloads,
                source_label="need_candidate_page_view_models",
            )
        )

    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "validate_need_candidate_page_view_models",
        "schema_version": SCHEMA_VERSION,
        "contracts_checked": sorted([NEED_CONTRACT_PATH, CANDIDATE_CONTRACT_PATH]),
        "policies_checked": sorted([NEED_POLICY_INVENTORY, CANDIDATE_POLICY_INVENTORY]),
        "need_examples_checked": sorted(NEED_EXAMPLE_PATHS),
        "candidate_examples_checked": sorted(CANDIDATE_EXAMPLE_PATHS),
        "need_example_count": len(need_payloads),
        "candidate_example_count": len(candidate_payloads),
        "errors": sorted(errors),
        "warnings": sorted(warnings),
    }


def validate_payloads(
    need_policy: Mapping[str, Any],
    candidate_policy: Mapping[str, Any],
    representation_inventory: Mapping[str, Any],
    semantic_inventory: Mapping[str, Any],
    route_matrix: Mapping[str, Any],
    need_examples: Sequence[Mapping[str, Any]],
    candidate_examples: Sequence[Mapping[str, Any]],
    *,
    source_label: str,
) -> list[str]:
    errors: list[str] = []
    representation_ids = _representation_ids(representation_inventory)
    semantic_policy_ids = _semantic_policy_ids(semantic_inventory)
    route_records = _route_records(route_matrix)

    errors.extend(_validate_need_policy(need_policy, representation_ids, semantic_policy_ids, route_records))
    errors.extend(_validate_candidate_policy(candidate_policy, representation_ids, semantic_policy_ids, route_records))

    need_policy_context = _policy_context(need_policy)
    candidate_policy_context = _policy_context(candidate_policy)
    for index, example in enumerate(need_examples):
        label = str(example.get("view_model_id") or f"need_example[{index}]")
        errors.extend(_validate_need_example(label, example, need_policy_context, representation_ids, route_records))
    for index, example in enumerate(candidate_examples):
        label = str(example.get("view_model_id") or f"candidate_example[{index}]")
        errors.extend(
            _validate_candidate_example(label, example, candidate_policy_context, representation_ids, route_records)
        )
    if not need_examples:
        errors.append(f"{source_label}: at least one NeedPageView example is required")
    if not candidate_examples:
        errors.append(f"{source_label}: at least one CandidatePageView example is required")
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


def _validate_need_policy(
    policy: Mapping[str, Any],
    representation_ids: set[str],
    semantic_policy_ids: set[str],
    route_records: Mapping[str, Mapping[str, Any]],
) -> list[str]:
    errors: list[str] = []
    errors.extend(
        _validate_common_policy(
            policy,
            NEED_POLICY_FIELDS,
            NEED_POLICY_INVENTORY,
            NEED_CONTRACT_PATH,
            "NeedPageView",
            "need_page_future",
            "need_page_future_parity_v0",
            NEED_BLOCKED_ACTIONS,
            NEED_PRODUCT_FLAGS,
            NEED_SEMANTICS,
            representation_ids,
            semantic_policy_ids,
            route_records,
        )
    )
    if not NEED_STATUSES <= set(_string_items(policy.get("allowed_need_statuses"))):
        errors.append(
            f"{NEED_POLICY_INVENTORY}: allowed_need_statuses missing {sorted(NEED_STATUSES - set(_string_items(policy.get('allowed_need_statuses'))))}"
        )
    if not DEMAND_FIELDS <= set(_string_items(policy.get("allowed_demand_fields"))):
        errors.append(
            f"{NEED_POLICY_INVENTORY}: allowed_demand_fields missing {sorted(DEMAND_FIELDS - set(_string_items(policy.get('allowed_demand_fields'))))}"
        )
    if not ABSENCE_STATES <= set(_string_items(policy.get("allowed_absence_states"))):
        errors.append(
            f"{NEED_POLICY_INVENTORY}: allowed_absence_states missing {sorted(ABSENCE_STATES - set(_string_items(policy.get('allowed_absence_states'))))}"
        )
    if not NEED_ACTIONS <= set(_string_items(policy.get("allowed_action_names"))):
        errors.append(
            f"{NEED_POLICY_INVENTORY}: allowed_action_names missing {sorted(NEED_ACTIONS - set(_string_items(policy.get('allowed_action_names'))))}"
        )
    return errors


def _validate_candidate_policy(
    policy: Mapping[str, Any],
    representation_ids: set[str],
    semantic_policy_ids: set[str],
    route_records: Mapping[str, Mapping[str, Any]],
) -> list[str]:
    errors: list[str] = []
    errors.extend(
        _validate_common_policy(
            policy,
            CANDIDATE_POLICY_FIELDS,
            CANDIDATE_POLICY_INVENTORY,
            CANDIDATE_CONTRACT_PATH,
            "CandidatePageView",
            "candidate_page_future",
            "candidate_page_future_parity_v0",
            CANDIDATE_BLOCKED_ACTIONS,
            CANDIDATE_PRODUCT_FLAGS,
            CANDIDATE_SEMANTICS,
            representation_ids,
            semantic_policy_ids,
            route_records,
        )
    )
    if not CANDIDATE_STATUSES <= set(_string_items(policy.get("allowed_candidate_statuses"))):
        errors.append(
            f"{CANDIDATE_POLICY_INVENTORY}: allowed_candidate_statuses missing {sorted(CANDIDATE_STATUSES - set(_string_items(policy.get('allowed_candidate_statuses'))))}"
        )
    if not CANDIDATE_ORIGINS <= set(_string_items(policy.get("allowed_candidate_origins"))):
        errors.append(
            f"{CANDIDATE_POLICY_INVENTORY}: allowed_candidate_origins missing {sorted(CANDIDATE_ORIGINS - set(_string_items(policy.get('allowed_candidate_origins'))))}"
        )
    if not CANDIDATE_TYPES <= set(_string_items(policy.get("allowed_candidate_types"))):
        errors.append(
            f"{CANDIDATE_POLICY_INVENTORY}: allowed_candidate_types missing {sorted(CANDIDATE_TYPES - set(_string_items(policy.get('allowed_candidate_types'))))}"
        )
    if not REVIEW_STATES <= set(_string_items(policy.get("allowed_review_states"))):
        errors.append(
            f"{CANDIDATE_POLICY_INVENTORY}: allowed_review_states missing {sorted(REVIEW_STATES - set(_string_items(policy.get('allowed_review_states'))))}"
        )
    if not CANDIDATE_ACTIONS <= set(_string_items(policy.get("allowed_action_names"))):
        errors.append(
            f"{CANDIDATE_POLICY_INVENTORY}: allowed_action_names missing {sorted(CANDIDATE_ACTIONS - set(_string_items(policy.get('allowed_action_names'))))}"
        )
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
    semantics = set(_string_items(policy.get("required_semantic_requirements")))
    if not required_semantics <= semantics:
        errors.append(f"{policy_path}: required_semantic_requirements missing {sorted(required_semantics - semantics)}")
    return errors


def _policy_context(policy: Mapping[str, Any]) -> dict[str, set[str] | str]:
    return {
        "routes": set(_string_items(policy.get("supported_route_families"))),
        "representations": set(_string_items(policy.get("allowed_representation_profiles"))),
        "hints": set(_string_items(policy.get("required_representation_hints"))),
        "semantics": set(_string_items(policy.get("required_semantic_requirements"))),
        "blocked": set(_string_items(policy.get("required_blocked_actions"))),
        "actions": set(_string_items(policy.get("allowed_action_names"))),
        "need_statuses": set(_string_items(policy.get("allowed_need_statuses"))),
        "absence_states": set(_string_items(policy.get("allowed_absence_states"))),
        "candidate_statuses": set(_string_items(policy.get("allowed_candidate_statuses"))),
        "candidate_origins": set(_string_items(policy.get("allowed_candidate_origins"))),
        "candidate_types": set(_string_items(policy.get("allowed_candidate_types"))),
        "review_states": set(_string_items(policy.get("allowed_review_states"))),
        "semantic_ref": str(policy.get("required_semantic_parity_policy") or ""),
    }


def _validate_need_example(
    label: str,
    example: Mapping[str, Any],
    context: Mapping[str, set[str] | str],
    representation_ids: set[str],
    route_records: Mapping[str, Mapping[str, Any]],
) -> list[str]:
    errors: list[str] = []
    missing = NEED_VIEW_FIELDS - set(example)
    if missing:
        return [f"{label}: missing required NeedPageView top-level fields {sorted(missing)}"]
    if example.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"{label}: schema_version must be {SCHEMA_VERSION}")
    if example.get("view_family") != "NeedPageView":
        errors.append(f"{label}: view_family must be NeedPageView")
    errors.extend(_validate_route(label, example, "NeedPageView", context["routes"], route_records))

    identity = _mapping(example.get("need_identity"))
    missing_identity = NEED_IDENTITY_FIELDS - set(identity)
    if missing_identity:
        errors.append(f"{label}: need_identity missing {sorted(missing_identity)}")
    if not identity.get("need_id"):
        errors.append(f"{label}: canonical need identity need_id is required")
    if not identity.get("canonical_route"):
        errors.append(f"{label}: canonical need identity canonical_route is required")

    if example.get("need_status") not in context["need_statuses"]:
        errors.append(f"{label}: need_status {example.get('need_status')!r} is not allowed")

    demand = _mapping(example.get("demand_summary"))
    demand_missing = DEMAND_FIELDS - set(demand)
    if demand_missing:
        errors.append(f"{label}: demand_summary missing {sorted(demand_missing)}")
    if demand.get("aggregate_only") is not True:
        errors.append(f"{label}: demand_summary.aggregate_only must be true")
    if demand.get("raw_query_retention") not in {"none", "aggregate_only"}:
        errors.append(f"{label}: raw_query_retention must not imply raw public query storage")
    for key in ("raw_user_tracking_claimed", "account_identity_used", "public_raw_query_storage", "telemetry_enabled"):
        if demand.get(key) is not False:
            errors.append(f"{label}: demand_summary.{key} must be false")
    if demand.get("privacy_filtered") is not True:
        errors.append(f"{label}: demand_summary.privacy_filtered must be true")

    absence = _mapping(example.get("absence_summary"))
    absence_missing = ABSENCE_FIELDS - set(absence)
    if absence_missing:
        errors.append(f"{label}: absence_summary missing {sorted(absence_missing)}")
    if absence.get("absence_status") not in context["absence_states"]:
        errors.append(f"{label}: absence_status {absence.get('absence_status')!r} is not allowed")
    if absence.get("global_absence_claimed") is not False:
        errors.append(f"{label}: absence must not claim global absence")
    if absence.get("exhaustive_global_search_claimed") is not False:
        errors.append(f"{label}: absence must not claim exhaustive global search")
    searched_scope = _mapping(example.get("searched_scope"))
    if searched_scope.get("global_scope_claimed") is not False:
        errors.append(f"{label}: searched_scope must not claim global scope")
    if searched_scope.get("exhaustive_global_search_claimed") is not False:
        errors.append(f"{label}: searched_scope must not claim exhaustive global search")

    evidence = _mapping(example.get("evidence_summary"))
    for key, message in (
        ("source_observation_accepted_as_truth", "source observation must not be marked accepted truth"),
        ("evidence_candidate_accepted_as_truth", "evidence candidate must not be marked accepted truth"),
        ("ai_draft_marked_evidence_truth", "AI draft must not be marked evidence truth"),
    ):
        if evidence.get(key) is not False:
            errors.append(f"{label}: {message}")
    candidate = _mapping(example.get("candidate_summary"))
    if candidate.get("candidate_public_truth_claimed") is not False:
        errors.append(f"{label}: candidate summary must not claim public truth")

    errors.extend(_validate_action_boundary(label, example, NEED_PRODUCT_FLAGS, NEED_BLOCKED_ACTIONS, context["blocked"], context["actions"]))
    errors.extend(_validate_need_rights_risk(label, example))
    errors.extend(_validate_hints(label, example, representation_ids, context["representations"], context["hints"]))
    errors.extend(_validate_semantics(label, example, NEED_SEMANTICS, context["semantics"]))
    errors.extend(_validate_generated_from(label, example, str(context["semantic_ref"])))
    errors.extend(_validate_unsafe_patterns(label, example))
    return sorted(errors)


def _validate_candidate_example(
    label: str,
    example: Mapping[str, Any],
    context: Mapping[str, set[str] | str],
    representation_ids: set[str],
    route_records: Mapping[str, Mapping[str, Any]],
) -> list[str]:
    errors: list[str] = []
    missing = CANDIDATE_VIEW_FIELDS - set(example)
    if missing:
        return [f"{label}: missing required CandidatePageView top-level fields {sorted(missing)}"]
    if example.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"{label}: schema_version must be {SCHEMA_VERSION}")
    if example.get("view_family") != "CandidatePageView":
        errors.append(f"{label}: view_family must be CandidatePageView")
    errors.extend(_validate_route(label, example, "CandidatePageView", context["routes"], route_records))

    identity = _mapping(example.get("candidate_identity"))
    missing_identity = CANDIDATE_IDENTITY_FIELDS - set(identity)
    if missing_identity:
        errors.append(f"{label}: candidate_identity missing {sorted(missing_identity)}")
    if not identity.get("candidate_id"):
        errors.append(f"{label}: canonical candidate identity candidate_id is required")
    if not identity.get("canonical_route"):
        errors.append(f"{label}: canonical candidate identity canonical_route is required")
    if identity.get("candidate_origin") not in context["candidate_origins"]:
        errors.append(f"{label}: candidate_origin {identity.get('candidate_origin')!r} is not allowed")
    if identity.get("candidate_type") not in context["candidate_types"]:
        errors.append(f"{label}: candidate_type {identity.get('candidate_type')!r} is not allowed")
    if example.get("candidate_status") not in context["candidate_statuses"]:
        errors.append(f"{label}: candidate_status {example.get('candidate_status')!r} is not allowed")
    if example.get("candidate_status") == "accepted_public_future":
        errors.append(f"{label}: current candidate example must not be accepted public future")

    review = _mapping(example.get("review_summary"))
    review_missing = CANDIDATE_REVIEW_FIELDS - set(review)
    if review_missing:
        errors.append(f"{label}: review_summary missing {sorted(review_missing)}")
    if review.get("review_status") not in context["review_states"]:
        errors.append(f"{label}: review_status {review.get('review_status')!r} is not allowed")
    if review.get("review_required") is not True:
        errors.append(f"{label}: review_required must be true")
    if review.get("master_index_mutation_allowed") is not False:
        errors.append(f"{label}: master_index_mutation_allowed must be false")
    if review.get("accepted_public_status") is not False:
        errors.append(f"{label}: accepted public truth must not be claimed")
    if review.get("public_acceptance_claimed") is not False:
        errors.append(f"{label}: public acceptance must not be claimed")

    proposed = _mapping(example.get("proposed_object_summary"))
    if proposed.get("accepted_public_truth") is not False:
        errors.append(f"{label}: proposed object must not be accepted public truth")
    if proposed.get("demand_signal_used_as_object_truth") is not False:
        errors.append(f"{label}: demand signal must not be object truth")

    evidence = _mapping(example.get("evidence_summary"))
    if evidence.get("evidence_candidate_accepted_as_truth") is not False:
        errors.append(f"{label}: evidence candidate must not be marked accepted truth")
    if evidence.get("ai_draft_marked_evidence_truth") is not False:
        errors.append(f"{label}: AI draft must not be marked evidence truth")
    if evidence.get("discussion_comment_marked_compatibility_truth") is not False:
        errors.append(f"{label}: discussion-derived field must not be compatibility truth")
    source = _mapping(example.get("source_summary"))
    if source.get("source_observation_accepted_as_truth") is not False:
        errors.append(f"{label}: source observation must not be marked accepted truth")
    provenance = _mapping(example.get("provenance_summary"))
    if provenance.get("source_observation_accepted_as_truth") is not False:
        errors.append(f"{label}: source observation must not be marked accepted truth")

    compatibility = _mapping(example.get("compatibility_summary"))
    if compatibility.get("discussion_derived_compatibility_truth_claimed") is not False:
        errors.append(f"{label}: discussion-derived compatibility truth must not be claimed")
    if compatibility.get("verified_installability_claimed") is not False:
        errors.append(f"{label}: verified installability must not be claimed")
    errors.extend(_validate_candidate_rights_risk(label, example))
    errors.extend(
        _validate_action_boundary(
            label,
            example,
            CANDIDATE_PRODUCT_FLAGS,
            CANDIDATE_BLOCKED_ACTIONS,
            context["blocked"],
            context["actions"],
        )
    )
    errors.extend(_validate_hints(label, example, representation_ids, context["representations"], context["hints"]))
    errors.extend(_validate_semantics(label, example, CANDIDATE_SEMANTICS, context["semantics"]))
    errors.extend(_validate_generated_from(label, example, str(context["semantic_ref"])))
    errors.extend(_validate_unsafe_patterns(label, example))
    return sorted(errors)


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


def _validate_need_rights_risk(label: str, example: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    rights = _mapping(example.get("rights_summary"))
    if rights.get("rights_clearance_claimed") is not False:
        errors.append(f"{label}: rights clearance must not be claimed")
    risk = _mapping(example.get("risk_summary"))
    for key, phrase in (
        ("malware_safety_claimed", "malware safety"),
        ("safe_execution_claimed", "safe execution"),
        ("verified_installability_claimed", "verified installability"),
    ):
        if risk.get(key) is not False:
            errors.append(f"{label}: {phrase} must not be claimed")
    return errors


def _validate_candidate_rights_risk(label: str, example: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    rights = _mapping(example.get("rights_summary"))
    if rights.get("rights_clearance_claimed") is not False:
        errors.append(f"{label}: rights clearance must not be claimed")
    if rights.get("authorized_download_claimed") is not False:
        errors.append(f"{label}: authorized download must not be claimed")
    risk = _mapping(example.get("risk_summary"))
    for key, phrase in (
        ("malware_safety_claimed", "malware safety"),
        ("safe_execution_claimed", "safe execution"),
        ("verified_installability_claimed", "verified installability"),
    ):
        if risk.get(key) is not False:
            errors.append(f"{label}: {phrase} must not be claimed")
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
        f"validate_need_candidate_page_view_models: {report['status']}",
        f"schema_version: {report['schema_version']}",
        f"need_examples: {report['need_example_count']}",
        f"candidate_examples: {report['candidate_example_count']}",
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
