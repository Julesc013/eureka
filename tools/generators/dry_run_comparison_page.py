#!/usr/bin/env python3
"""Emit a hypothetical Comparison Page v0 JSON payload to stdout only."""

from __future__ import annotations

import argparse
import json
import re
import sys
from typing import Sequence, TextIO


ALLOWED_COMPARISON_TYPES = {
    "object_identity_comparison",
    "version_comparison",
    "source_coverage_comparison",
    "representation_comparison",
    "member_comparison",
    "compatibility_comparison",
    "evidence_strength_comparison",
    "provenance_comparison",
    "rights_risk_action_comparison",
    "conflict_comparison",
    "absence_near_miss_comparison",
    "candidate_review_comparison",
    "unknown",
}
SAFE_LABEL_RE = re.compile(r"^[A-Za-z0-9 ._()/-]{1,120}$")
HARD_FALSE_FIELDS = {
    "runtime_comparison_page_implemented": False,
    "persistent_comparison_page_store_implemented": False,
    "comparison_page_generated_from_live_source": False,
    "comparison_winner_claimed": False,
    "live_source_called": False,
    "external_calls_performed": False,
    "source_sync_worker_executed": False,
    "source_cache_mutated": False,
    "evidence_ledger_mutated": False,
    "candidate_index_mutated": False,
    "candidate_promotion_performed": False,
    "public_index_mutated": False,
    "local_index_mutated": False,
    "master_index_mutated": False,
    "downloads_enabled": False,
    "uploads_enabled": False,
    "installs_enabled": False,
    "execution_enabled": False,
    "arbitrary_url_fetch_enabled": False,
    "rights_clearance_claimed": False,
    "malware_safety_claimed": False,
    "source_trust_claimed": False,
    "telemetry_exported": False,
}


def build_page(label: str, comparison_type: str) -> dict:
    safe_slug = re.sub(r"[^A-Za-z0-9]+", "_", label).strip("_").lower()[:64] or "comparison"
    subjects = [
        {
            "subject_ref": f"synthetic:dry-run:{safe_slug}:a",
            "subject_kind": "synthetic_example",
            "subject_label": f"{label} A",
            "subject_status": "candidate",
            "object_kind": "software_version",
            "source_family": None,
            "version": "unknown",
            "platform": "Windows 7",
            "representation_kind": "metadata_record",
            "evidence_status": "candidate",
            "limitations": ["Dry-run synthetic subject only."],
        },
        {
            "subject_ref": f"synthetic:dry-run:{safe_slug}:b",
            "subject_kind": "synthetic_example",
            "subject_label": f"{label} B",
            "subject_status": "review_required",
            "object_kind": "software_version",
            "source_family": None,
            "version": "unknown",
            "platform": "Windows 7",
            "representation_kind": "metadata_record",
            "evidence_status": "review_required",
            "limitations": ["Dry-run synthetic subject only."],
        },
    ]
    page = {
        "schema_version": "0.1.0",
        "comparison_page_id": f"comparison_page_dry_run_{safe_slug}",
        "comparison_page_kind": "comparison_page",
        "status": "dry_run_validated",
        "created_by_tool": "dry_run_comparison_page_v0",
        "comparison_identity": {
            "comparison_id": f"dry_run_{safe_slug}",
            "canonical_label": label,
            "comparison_scope": "object_to_object",
            "comparison_basis": "synthetic_example",
            "limitations": ["Dry-run payload emitted to stdout only."],
        },
        "comparison_type": {
            "type": comparison_type,
            "comparison_goal": "explain_same_or_different",
            "winner_allowed": False,
            "scoped_recommendation_allowed": False,
            "limitations": ["No winner claim."],
        },
        "subjects": subjects,
        "criteria": [
            {
                "criterion_id": "identity",
                "criterion_type": "identity_match",
                "criterion_label": "Identity relation",
                "required": True,
                "scoring_policy": "categorical",
                "evidence_required": True,
                "limitations": ["Descriptive only."],
            },
            {
                "criterion_id": "evidence",
                "criterion_type": "evidence_strength",
                "criterion_label": "Evidence support",
                "required": True,
                "scoring_policy": "descriptive_only",
                "evidence_required": True,
                "limitations": ["Evidence confidence is not truth."],
            },
        ],
        "comparison_matrix": {
            "matrix_kind": "descriptive",
            "rows": [{"row_id": subject["subject_ref"], "subject_ref": subject["subject_ref"]} for subject in subjects],
            "columns": [{"criterion_id": "identity", "criterion_label": "Identity relation"}, {"criterion_id": "evidence", "criterion_label": "Evidence support"}],
            "cells": [
                {
                    "row_id": f"{subject['subject_ref']}:identity",
                    "subject_ref": subject["subject_ref"],
                    "criterion_id": "identity",
                    "value": "unknown",
                    "status": "unknown",
                    "evidence_refs": [],
                    "source_refs": [],
                    "confidence": "unknown",
                    "confidence_not_truth": True,
                    "limitations": ["No source was called."],
                }
                for subject in subjects
            ],
            "scoring_used_now": False,
            "ranking_used_now": False,
            "winner_selected_now": False,
            "limitations": ["No ranking or winner selection."],
        },
        "identity_comparison": {
            "identity_relation": "unknown",
            "identity_evidence_refs": [],
            "identity_conflicts": [],
            "duplicate_policy": "preserve_separate",
            "destructive_merge_allowed": False,
            "limitations": ["No merge decision."],
        },
        "version_state_release_comparison": {
            "versions_compared": [
                {"subject_ref": subject["subject_ref"], "version_label": "unknown", "version_status": "unknown", "source_refs": [], "evidence_refs": [], "limitations": ["No version evidence."]}
                for subject in subjects
            ],
            "release_dates_compared": "unknown",
            "platform_architecture_compared": "Windows 7 query label only.",
            "lifecycle_status_compared": "unknown",
            "newer_older_claim_scoped": True,
            "version_conflicts": [],
            "limitations": ["Dry-run only."],
        },
        "representation_member_comparison": {
            "representations_compared": [
                {"subject_ref": subject["subject_ref"], "representation_kind": "metadata_record", "availability_status": "metadata_only", "checksum_refs": [], "source_refs": [], "evidence_refs": [], "limitations": ["No payload included."]}
                for subject in subjects
            ],
            "members_compared": [],
            "representation_availability_summary": "metadata-only",
            "member_access_summary": "not checked",
            "payload_included": False,
            "downloads_enabled": False,
            "limitations": ["No downloads."],
        },
        "source_evidence_provenance_comparison": {
            "sources_compared": [
                {"subject_ref": subject["subject_ref"], "source_id": "synthetic-dry-run", "source_family": "local_fixture", "source_status": "fixture", "source_role": "supporting", "source_trust_claimed": False, "limitations": ["No source trust claim."]}
                for subject in subjects
            ],
            "evidence_compared": [
                {"subject_ref": subject["subject_ref"], "evidence_ref": "synthetic:dry-run:evidence", "evidence_kind": "metadata_note", "evidence_status": "fixture", "confidence": "low", "confidence_not_truth": True, "limitations": ["Synthetic evidence only."]}
                for subject in subjects
            ],
            "provenance_compared": [],
            "evidence_strength_summary": "insufficient for authoritative comparison",
            "provenance_limitations": ["No source cache or evidence ledger record."],
            "accepted_as_truth": False,
            "limitations": ["Dry-run only."],
        },
        "compatibility_comparison": {
            "compatibility_subjects": [subject["subject_ref"] for subject in subjects],
            "operating_systems": ["Windows 7"],
            "architectures": ["unknown"],
            "runtime_requirements": ["unknown"],
            "compatibility_relation": "unknown",
            "compatibility_evidence_refs": [],
            "compatibility_claim_scoped": True,
            "limitations": ["No compatibility truth claim."],
        },
        "rights_risk_action_comparison": {
            "rights_comparison": "review required",
            "risk_comparison": "metadata only",
            "action_comparison": [
                {"subject_ref": subject["subject_ref"], "allowed_actions": ["inspect_metadata", "view_sources", "view_evidence", "compare", "cite"], "disabled_actions": ["download", "install", "execute", "upload", "mirror", "arbitrary_url_fetch"], "limitations": ["Inspect-only."]}
                for subject in subjects
            ],
            "safe_action_summary": "Inspect metadata only.",
            "disabled_action_summary": "Download, install, execute, upload, mirror, and arbitrary URL fetch disabled.",
            "rights_clearance_claimed": False,
            "malware_safety_claimed": False,
            "downloads_enabled": False,
            "installs_enabled": False,
            "execution_enabled": False,
            "uploads_enabled": False,
            "mirroring_enabled": False,
            "arbitrary_url_fetch_enabled": False,
            "limitations": ["No rights or malware safety claim."],
        },
        "conflicts_and_disagreements": {
            "conflict_status": "none_known",
            "conflicts": [],
            "disagreement_preserved": True,
            "destructive_merge_allowed": False,
            "resolution_status": "not_needed",
            "limitations": ["No destructive merge."],
        },
        "absence_near_miss_gap_comparison": {
            "absence_status": "unknown",
            "global_absence_claimed": False,
            "near_misses_compared": [],
            "gaps_compared": [
                {"subject_ref": subject["subject_ref"], "gap_type": "source_cache_missing", "explanation": "Dry-run has no source cache record.", "limitations": ["No mutation."]}
                for subject in subjects
            ],
            "checked_scope_summary": "dry-run only",
            "not_checked_scope_summary": "live sources, source cache, evidence ledger",
            "limitations": ["No global absence claim."],
        },
        "result_card_object_source_projection": {
            "public_search_result_card_refs": [],
            "object_page_refs": [],
            "source_page_refs": [],
            "can_project_to_result_card": True,
            "can_project_to_object_page": True,
            "can_project_to_source_page": True,
            "projection_status": "contract_only",
            "limitations": ["No public search mutation."],
        },
        "api_projection": {
            "response_kind": "comparison_page_response",
            "route_future": ["/compare", "/comparison/{comparison_id}", "/api/v1/compare", "/api/v1/comparison/{comparison_id}"],
            "implemented_now": False,
            "compatible_with_public_search_response": True,
            "included_sections": ["subjects", "criteria", "comparison_matrix"],
            "limitations": ["No runtime route."],
        },
        "static_projection": {
            "static_demo_available": False,
            "generated_static_artifact": False,
            "no_js_required": True,
            "base_path_safe": True,
            "old_client_safe": True,
            "limitations": ["No static artifact written."],
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
            "reasons": ["Synthetic dry-run data only."],
        },
        "limitations": ["Dry-run only.", "No persistence."],
        "no_winner_without_evidence_guarantees": {"winner_allowed": False, "comparison_winner_claimed": False, "winner_selected_now": False, "scoped_recommendation_requires_evidence": True, "limitations": ["No winner."]},
        "no_runtime_guarantees": {"runtime_comparison_page_implemented": False, "persistent_comparison_page_store_implemented": False, "comparison_page_generated_from_live_source": False, "live_source_called": False, "external_calls_performed": False, "source_sync_worker_executed": False},
        "no_mutation_guarantees": {"source_cache_mutated": False, "evidence_ledger_mutated": False, "candidate_index_mutated": False, "candidate_promotion_performed": False, "public_index_mutated": False, "local_index_mutated": False, "master_index_mutated": False},
        "notes": ["stdout only"],
    }
    page.update(HARD_FALSE_FIELDS)
    return page


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Emit a dry-run Comparison Page v0 payload to stdout.")
    parser.add_argument("--label", default="Synthetic comparison", help="Public-safe label for the dry-run comparison.")
    parser.add_argument("--comparison-type", default="object_identity_comparison", help="Comparison type.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    return parser


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    args = build_parser().parse_args(argv)
    if args.comparison_type not in ALLOWED_COMPARISON_TYPES:
        stderr.write(f"unsupported comparison type: {args.comparison_type}\n")
        return 2
    if not SAFE_LABEL_RE.match(args.label) or "\\" in args.label:
        stderr.write("label must be public-safe ASCII without private path markers\n")
        return 2
    page = build_page(args.label, args.comparison_type)
    if args.json:
        json.dump(page, stdout, indent=2, sort_keys=True)
        stdout.write("\n")
    else:
        stdout.write(f"comparison_page_id: {page['comparison_page_id']}\n")
        stdout.write("status: dry_run_validated\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
