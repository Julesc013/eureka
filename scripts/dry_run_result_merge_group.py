#!/usr/bin/env python3
"""Emit a dry-run Result Merge Group v0 JSON object.

The dry run writes nothing, performs no network calls, applies no runtime
grouping or deduplication, changes no ranking, and mutates no index/cache or
ledger state.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from typing import Any, Mapping, Sequence


RELATION_TYPES = {
    "exact_duplicate_result",
    "near_duplicate_result",
    "variant_result",
    "same_object_different_source",
    "same_object_different_representation",
    "same_version_different_representation",
    "same_source_duplicate",
    "parent_child_result",
    "member_of_result",
    "source_mirror_result",
    "conflicting_duplicate_claim",
    "not_duplicate",
    "unknown",
}
HARD_FALSE = {
    "runtime_result_merge_implemented",
    "persistent_merge_group_store_implemented",
    "public_search_runtime_grouping_enabled",
    "public_search_ranking_changed",
    "records_merged",
    "duplicates_deleted",
    "results_hidden_without_explanation",
    "destructive_merge_performed",
    "canonical_record_claimed_as_truth",
    "candidate_promotion_performed",
    "master_index_mutated",
    "public_index_mutated",
    "local_index_mutated",
    "source_cache_mutated",
    "evidence_ledger_mutated",
    "candidate_index_mutated",
    "live_source_called",
    "external_calls_performed",
    "downloads_enabled",
    "installs_enabled",
    "execution_enabled",
    "telemetry_exported",
}


def result(ref: str, title: str, source_family: str) -> Mapping[str, Any]:
    return {
        "result_ref": ref,
        "result_kind": "synthetic_example",
        "result_title": title,
        "result_status": "candidate",
        "source_id": f"synthetic:{source_family}",
        "source_family": source_family,
        "object_ref": None,
        "representation_ref": None,
        "member_ref": None,
        "evidence_refs": [f"synthetic:evidence:{ref.split(':')[-1]}"],
        "identity_resolution_refs": [],
        "limitations": ["Dry-run synthetic result only."],
    }


def build_group(left_title: str, right_title: str, relation_type: str) -> Mapping[str, Any]:
    exact = relation_type == "exact_duplicate_result"
    criteria = [
        {
            "criterion_id": "dry-run-title",
            "criterion_type": "normalized_title_match",
            "strength": "weak",
            "passed": True,
            "evidence_refs": ["synthetic:evidence:dry-run-title"],
            "limitations": ["Name similarity is weak and not enough for exact duplicates."],
        }
    ]
    if exact:
        criteria.append(
            {
                "criterion_id": "dry-run-package-url",
                "criterion_type": "package_url_match",
                "strength": "strong",
                "passed": True,
                "evidence_refs": ["synthetic:evidence:dry-run-package-url"],
                "limitations": ["Synthetic package URL only."],
            }
        )
    group = {
        "schema_version": "0.1.0",
        "result_merge_group_id": "dry_run_result_merge_group_v0",
        "result_merge_group_kind": "result_merge_group",
        "status": "dry_run_validated",
        "created_by_tool": "dry_run_result_merge_group.py",
        "merge_group_identity": {
            "merge_group_fingerprint": {
                "algorithm": "sha256",
                "normalized_basis": f"{left_title}|{right_title}|{relation_type}",
                "value": hashlib.sha256(f"{left_title}|{right_title}|{relation_type}".encode()).hexdigest(),
                "reversible": False,
            },
            "canonical_group_label": left_title,
            "group_label_policy": "synthetic_example",
            "group_label_not_truth": True,
            "duplicate_of": None,
            "supersedes": None,
            "limitations": ["Dry-run group label is not truth."],
        },
        "group_relation": {
            "relation_type": relation_type,
            "relation_status": "candidate",
            "relation_claim_not_truth": True,
            "destructive_merge_allowed": False,
            "limitations": ["Dry-run relation only."],
        },
        "grouped_results": [result("synthetic:dry-run:left", left_title, "local_fixture"), result("synthetic:dry-run:right", right_title, "recorded_fixture")],
        "canonical_display_record": {
            "selected_result_ref": "synthetic:dry-run:left",
            "selection_policy": "first_result_example",
            "selection_reason": "Dry-run display convenience only.",
            "canonical_record_claimed_as_truth": False,
            "alternative_results_preserved": True,
            "limitations": ["Canonical display is not truth."],
        },
        "collapsed_results": {
            "collapsed_count": 0,
            "collapsed_result_refs": [],
            "collapse_allowed_future": True,
            "collapse_applied_now": False,
            "user_expand_available_future": True,
            "hidden_without_explanation": False,
            "explanation_required": True,
            "conflict_results_must_not_be_hidden": True,
            "limitations": ["No result is hidden or collapsed now."],
        },
        "transparency": {
            "all_results_visible_now": True,
            "grouping_explanation_visible_future": True,
            "user_can_expand_future": True,
            "conflict_warning_visible_future": relation_type == "conflicting_duplicate_claim",
            "limitations": ["Dry-run transparency only."],
        },
        "grouping_criteria": criteria,
        "identity_resolution_refs": [
            {
                "identity_assessment_ref": "synthetic:dry-run:identity",
                "identity_cluster_ref": None,
                "relation_type": "possible_same_object",
                "relation_status": "candidate",
                "confidence": "unknown",
                "confidence_not_truth": True,
                "destructive_merge_allowed": False,
                "limitations": ["Identity evidence does not authorize merge."],
            }
        ],
        "source_evidence_provenance": {
            "source_refs": ["synthetic:source:left", "synthetic:source:right"],
            "evidence_refs": ["synthetic:evidence:dry-run-title"],
            "provenance_refs": [],
            "source_diversity_summary": "Dry-run synthetic sources preserved.",
            "evidence_strength_summary": "Dry-run criteria only.",
            "conflicts_preserved": True,
            "source_trust_claimed": False,
            "accepted_as_truth": False,
            "limitations": ["No source trust or evidence acceptance."],
        },
        "conflicts": {
            "conflict_status": "conflicting_duplicate_claim" if relation_type == "conflicting_duplicate_claim" else "none_known",
            "conflicts": [],
            "disagreement_preserved": True,
            "conflict_results_must_remain_expandable": True,
            "destructive_merge_allowed": False,
            "limitations": ["Conflicts remain expandable."],
        },
        "user_facing_behavior": {
            "display_mode": "conflict_group_future" if relation_type == "conflicting_duplicate_claim" else "expandable_group_future",
            "user_can_expand_group_future": True,
            "user_can_view_all_sources_future": True,
            "user_can_view_grouping_reason_future": True,
            "user_can_disable_grouping_future": True,
            "conflict_warning_required": relation_type == "conflicting_duplicate_claim",
            "uncertainty_notice_required": True,
            "limitations": ["No runtime UI behavior is enabled."],
        },
        "result_card_projection": {
            "result_card_contract_ref": "contracts/api/search_result_card.v0.json",
            "can_project_to_result_card_group": True,
            "group_badge_label": relation_type.replace("_", " "),
            "group_count_label": "2 related results",
            "canonical_title": left_title,
            "grouped_source_summary": "2 synthetic sources preserved",
            "evidence_summary": "Dry-run criteria only",
            "warning_summary": "Not identity truth",
            "limitations_summary": "No runtime grouping applied",
            "expand_link_future": "/api/v1/result-group/{group_id}",
            "object_page_refs": [],
            "source_page_refs": [],
            "comparison_page_refs": [],
            "limitations": ["Projection only."],
        },
        "api_projection": {
            "response_kind": "result_merge_group_response",
            "route_future": ["/api/v1/search", "/api/v1/result-group/{group_id}"],
            "implemented_now": False,
            "compatible_with_public_search_response": True,
            "included_sections": ["grouped_results", "grouping_criteria", "conflicts", "transparency"],
            "limitations": ["No route is implemented."],
        },
        "privacy": {
            "privacy_classification": "public_safe_example",
            "contains_private_path": False,
            "contains_secret": False,
            "contains_private_url": False,
            "contains_user_identifier": False,
            "contains_ip_address": False,
            "contains_raw_private_query": False,
            "publishable": True,
            "public_aggregate_allowed": True,
            "reasons": ["Caller-supplied labels are treated as synthetic dry-run labels."],
        },
        "limitations": ["Dry run only.", "No runtime grouping, ranking, suppression, merge, promotion, or mutation."],
        "no_destructive_merge_guarantees": {"records_merged": False, "duplicates_deleted": False, "destructive_merge_performed": False, "canonical_record_claimed_as_truth": False},
        "no_ranking_promotion_mutation_guarantees": {"public_search_ranking_changed": False, "candidate_promotion_performed": False, "master_index_mutated": False, "public_index_mutated": False, "local_index_mutated": False, "source_cache_mutated": False, "evidence_ledger_mutated": False, "candidate_index_mutated": False},
        "no_runtime_guarantees": {"runtime_result_merge_implemented": False, "persistent_merge_group_store_implemented": False, "public_search_runtime_grouping_enabled": False, "live_source_called": False, "external_calls_performed": False, "telemetry_exported": False},
        "notes": ["Dry-run stdout only.", "Grouping is not record merging."],
    }
    for key in HARD_FALSE:
        group[key] = False
    return group


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--left-title", required=True)
    parser.add_argument("--right-title", required=True)
    parser.add_argument("--relation-type", required=True, choices=sorted(RELATION_TYPES))
    parser.add_argument("--json", action="store_true", help="Emit JSON. This is the only supported output in v0.")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    group = build_group(args.left_title, args.right_title, args.relation_type)
    sys.stdout.write(json.dumps(group, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
