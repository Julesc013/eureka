#!/usr/bin/env python3
"""Emit a dry-run Cross-Source Identity Resolution Assessment v0 JSON object.

The dry run writes nothing, performs no network calls, executes no connectors,
creates no identity cluster, merges no records, and mutates no indexes, source
cache, evidence ledger, candidate index, or master index.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Mapping, Sequence


RELATION_TYPES = {
    "exact_same_object",
    "likely_same_object",
    "possible_same_object",
    "variant_of",
    "version_of",
    "release_of",
    "representation_of",
    "member_of",
    "source_record_for",
    "package_record_for",
    "repository_record_for",
    "capture_of",
    "alias_of",
    "near_match",
    "different_object",
    "conflicting_identity",
    "unknown",
}


def build_assessment(left_label: str, right_label: str, relation_type: str) -> Mapping[str, Any]:
    strong_identifier = relation_type == "exact_same_object"
    identifier_evidence = []
    if strong_identifier:
        identifier_evidence.append(
            {
                "identifier_kind": "package_url",
                "identifier_value": "pkg:pypi/dry-run-example@0.0.0",
                "identifier_value_public_safe": True,
                "identifier_status": "exact_match",
                "strength": "intrinsic_strong",
                "source_refs": ["synthetic:dry-run:left", "synthetic:dry-run:right"],
                "evidence_refs": ["synthetic:dry-run:identifier"],
                "limitations": ["Synthetic dry-run identifier only."],
            }
        )
    return {
        "schema_version": "0.1.0",
        "assessment_id": "dry_run_identity_resolution_assessment_v0",
        "assessment_kind": "identity_resolution_assessment",
        "status": "dry_run_validated",
        "created_by_tool": "dry_run_identity_resolution_assessment.py",
        "assessment_scope": {
            "scope_kind": "object_identity",
            "assessment_basis": "synthetic_example",
            "relation_goal": "determine_same" if relation_type in {"exact_same_object", "likely_same_object", "possible_same_object"} else "preserve_uncertainty",
            "limitations": ["Dry-run stdout-only assessment; no persistence or runtime resolver."],
        },
        "subjects": [
            {
                "subject_ref": "synthetic:dry-run:left",
                "subject_kind": "synthetic_example",
                "subject_label": left_label,
                "subject_status": "candidate",
                "object_kind": "unknown",
                "source_family": "local_fixture",
                "package_family": "unknown",
                "repository_family": "unknown",
                "version": None,
                "platform": None,
                "architecture": None,
                "representation_kind": "metadata_record",
                "member_path_public_safe": None,
                "evidence_status": "candidate",
                "limitations": ["Synthetic public-safe dry-run subject."],
            },
            {
                "subject_ref": "synthetic:dry-run:right",
                "subject_kind": "synthetic_example",
                "subject_label": right_label,
                "subject_status": "review_required",
                "object_kind": "unknown",
                "source_family": "recorded_fixture",
                "package_family": "unknown",
                "repository_family": "unknown",
                "version": None,
                "platform": None,
                "architecture": None,
                "representation_kind": "metadata_record",
                "member_path_public_safe": None,
                "evidence_status": "review_required",
                "limitations": ["Synthetic public-safe dry-run subject."],
            },
        ],
        "asserted_relation": {
            "relation_type": relation_type,
            "relation_status": "candidate",
            "symmetric_relation": relation_type not in {"version_of", "release_of", "representation_of", "member_of"},
            "transitive_relation": relation_type in {"exact_same_object", "alias_of"},
            "relation_claim_not_truth": True,
            "global_merge_allowed": False,
            "limitations": ["Dry-run relation claim is not identity truth."],
        },
        "relation_evidence": [
            {
                "evidence_ref": "synthetic:dry-run:relation-note",
                "evidence_kind": "synthetic_metadata_note",
                "evidence_status": "candidate",
                "claim_summary": f"Dry-run relation label: {relation_type}",
                "confidence_not_truth": True,
                "limitations": ["No live source call or evidence ledger write."],
            }
        ],
        "identifier_evidence": identifier_evidence,
        "alias_name_evidence": {
            "names_compared": [left_label, right_label],
            "aliases_compared": [[], []],
            "normalized_names": [left_label.lower(), right_label.lower()],
            "normalization_steps": ["case_fold", "whitespace_fold"],
            "name_similarity_status": "weak_similarity",
            "name_match_strength": "weak",
            "name_match_not_sufficient_alone": True,
            "limitations": ["Names alone are not sufficient for identity resolution."],
        },
        "version_platform_architecture_evidence": {
            "version_relation": "unknown",
            "platform_relation": "unknown",
            "architecture_relation": "unknown",
            "version_evidence_refs": [],
            "platform_evidence_refs": [],
            "architecture_evidence_refs": [],
            "limitations": ["No version/platform/architecture evidence in dry run."],
        },
        "source_provenance_evidence": {
            "source_refs": ["synthetic:dry-run:left", "synthetic:dry-run:right"],
            "provenance_refs": [],
            "source_relation": "unknown",
            "provenance_status": "candidate",
            "source_trust_claimed": False,
            "provenance_not_truth": True,
            "limitations": ["Dry run makes no source trust claim."],
        },
        "hash_checksum_intrinsic_id_model": {
            "intrinsic_identifier_present": strong_identifier,
            "exact_hash_match_present": False,
            "checksum_conflict_present": False,
            "intrinsic_id_conflict_present": False,
            "collision_or_weak_hash_caution_required": True,
            "strongest_identifier_kind": "package_url" if strong_identifier else "unknown",
            "strongest_identifier_status": "exact_match" if strong_identifier else "unknown",
            "limitations": ["No real hash or intrinsic ID was computed."],
        },
        "package_repository_archive_capture_identity": {
            "package_identity": {
                "package_family": "unknown",
                "package_name": None,
                "package_version": None,
                "package_url": None,
                "package_name_review_required": True,
                "limitations": ["No package source was queried."],
            },
            "repository_identity": {
                "repository_family": "unknown",
                "owner_repo": None,
                "origin_url_public_safe": None,
                "SWHID": None,
                "repository_identity_review_required": True,
                "limitations": ["No repository source was queried."],
            },
            "archive_identity": {
                "archive_family": "unknown",
                "archive_identifier": None,
                "item_identifier_review_required": True,
                "limitations": ["No archive source was queried."],
            },
            "capture_identity": {
                "capture_family": "unknown",
                "uri_r_public_safe": None,
                "capture_timestamp": None,
                "URI_privacy_review_required": True,
                "limitations": ["No capture source was queried."],
            },
            "relation_summary": "Dry-run identity posture only.",
            "cautions": ["Cross-source identities can diverge."],
            "limitations": ["No live source calls."],
        },
        "representation_member_evidence": {
            "representation_relation": "unknown",
            "member_relation": "unknown",
            "container_relation": "unknown",
            "member_path_public_safe": None,
            "payload_included": False,
            "downloads_enabled": False,
            "limitations": ["No payload, member extraction, or download."],
        },
        "conflicts": {
            "conflict_status": "unknown",
            "conflicts": [],
            "disagreement_preserved": True,
            "destructive_merge_allowed": False,
            "limitations": ["Dry run preserves uncertainty."],
        },
        "confidence": {
            "confidence_class": "unknown" if not strong_identifier else "high",
            "confidence_basis": "unknown" if not strong_identifier else "package_url_match",
            "confidence_not_truth": True,
            "confidence_sufficient_for_merge_now": False,
            "limitations": ["Confidence is not identity truth."],
        },
        "review": {
            "review_status": "human_review_required",
            "required_reviews": ["human_review", "promotion_policy_review"],
            "promotion_policy_required": True,
            "destructive_merge_forbidden": True,
            "limitations": ["Review required before any promotion or merge planning."],
        },
        "promotion_and_merge_boundary": {
            "candidate_promotion_required": True,
            "master_index_review_required": True,
            "merge_runtime_implemented": False,
            "merge_allowed_now": False,
            "destructive_merge_allowed": False,
            "canonicalization_allowed_now": False,
            "public_index_update_allowed_now": False,
            "future_destinations": ["candidate_index_future", "master_index_review_queue_future", "public_index_future_after_review"],
            "limitations": ["Dry run performs no promotion, canonicalization, or merge."],
        },
        "public_projection": {
            "public_search_projection": "future caveated relation label only",
            "result_card_projection": "future identity badge only after review",
            "object_page_projection": "future object relation section",
            "source_page_projection": "future source relation section",
            "comparison_page_projection": "future comparison page relation input",
            "public_visibility": "public_safe_example",
            "user_visible_relation_label": relation_type.replace("_", " "),
            "caveats_required": ["dry-run relation", "not identity truth", "no destructive merge"],
            "limitations": ["No public search runtime mutation."],
        },
        "privacy": {
            "privacy_classification": "public_safe_example",
            "contains_private_path": False,
            "contains_secret": False,
            "contains_private_url": False,
            "contains_user_identifier": False,
            "contains_ip_address": False,
            "contains_raw_private_query": False,
            "contains_private_repository": False,
            "contains_private_package": False,
            "publishable": True,
            "public_aggregate_allowed": True,
            "reasons": ["Caller-supplied labels are treated as synthetic dry-run labels."],
        },
        "limitations": ["Dry run only.", "No runtime identity resolution, live source call, merge, promotion, or mutation."],
        "no_runtime_guarantees": {
            "runtime_identity_resolution_implemented": False,
            "persistent_identity_store_implemented": False,
            "live_source_called": False,
            "external_calls_performed": False,
            "telemetry_exported": False,
        },
        "no_mutation_guarantees": {
            "identity_cluster_created": False,
            "records_merged": False,
            "destructive_merge_performed": False,
            "candidate_promotion_performed": False,
            "master_index_mutated": False,
            "public_index_mutated": False,
            "local_index_mutated": False,
            "source_cache_mutated": False,
            "evidence_ledger_mutated": False,
            "candidate_index_mutated": False,
        },
        "notes": ["Dry-run stdout only.", "Identity confidence is not identity truth."],
        "runtime_identity_resolution_implemented": False,
        "persistent_identity_store_implemented": False,
        "identity_cluster_created": False,
        "records_merged": False,
        "destructive_merge_performed": False,
        "candidate_promotion_performed": False,
        "master_index_mutated": False,
        "public_index_mutated": False,
        "local_index_mutated": False,
        "source_cache_mutated": False,
        "evidence_ledger_mutated": False,
        "candidate_index_mutated": False,
        "live_source_called": False,
        "external_calls_performed": False,
        "telemetry_exported": False,
    }


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--left-label", required=True)
    parser.add_argument("--right-label", required=True)
    parser.add_argument("--relation-type", required=True, choices=sorted(RELATION_TYPES))
    parser.add_argument("--json", action="store_true", help="Emit JSON. This is the only supported output in v0.")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    assessment = build_assessment(args.left_label, args.right_label, args.relation_type)
    sys.stdout.write(json.dumps(assessment, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
