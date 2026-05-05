#!/usr/bin/env python3
"""Emit a dry-run Evidence-Weighted Ranking Assessment v0 to stdout only."""

from __future__ import annotations

import argparse
import hashlib
import json
from typing import Sequence


FALSES = {
    "runtime_ranking_implemented": False,
    "persistent_ranking_store_implemented": False,
    "ranking_applied_to_live_search": False,
    "public_search_order_changed": False,
    "result_suppressed": False,
    "hidden_suppression_performed": False,
    "candidate_promotion_performed": False,
    "records_merged": False,
    "master_index_mutated": False,
    "public_index_mutated": False,
    "local_index_mutated": False,
    "source_cache_mutated": False,
    "evidence_ledger_mutated": False,
    "candidate_index_mutated": False,
    "live_source_called": False,
    "external_calls_performed": False,
    "telemetry_exported": False,
    "popularity_signal_used": False,
    "user_profile_signal_used": False,
    "ad_signal_used": False,
    "model_call_performed": False,
    "downloads_enabled": False,
    "installs_enabled": False,
    "execution_enabled": False,
    "rights_clearance_claimed": False,
    "malware_safety_claimed": False,
}


def build(left_title: str, right_title: str) -> dict:
    basis = f"{left_title}|{right_title}|evidence_weighted_ranking_v0"
    digest = hashlib.sha256(basis.encode("utf-8")).hexdigest()
    return {
        "schema_version": "0.1.0",
        "ranking_assessment_id": f"dry_run_evidence_weighted_ranking_{digest[:12]}",
        "ranking_assessment_kind": "evidence_weighted_ranking_assessment",
        "status": "dry_run_validated",
        "created_by_tool": "dry_run_evidence_weighted_ranking.py",
        "ranking_scope": {
            "scope_kind": "synthetic_example",
            "ranking_mode": "dry_run_example",
            "current_runtime_order_preserved": True,
            "live_runtime_changed": False,
            "limitations": ["stdout only; no persistence"],
        },
        "ranked_items": [
            {
                "item_ref": "synthetic:dry-run:left",
                "item_kind": "synthetic_example",
                "item_label": left_title,
                "item_status": "evidence_backed",
                "proposed_rank": 1,
                "current_rank": 1,
                "rank_changed_now": False,
                "source_refs": ["synthetic:source:left"],
                "evidence_refs": ["synthetic:evidence:left"],
                "limitations": ["Dry-run only; no live search order changed."],
            },
            {
                "item_ref": "synthetic:dry-run:right",
                "item_kind": "synthetic_example",
                "item_label": right_title,
                "item_status": "review_required",
                "proposed_rank": 2,
                "current_rank": 2,
                "rank_changed_now": False,
                "source_refs": ["synthetic:source:right"],
                "evidence_refs": ["synthetic:evidence:right"],
                "limitations": ["Dry-run only; no live search order changed."],
            },
        ],
        "ranking_factors": [
            {
                "factor_id": "dry-run-evidence",
                "factor_type": "evidence_strength",
                "direction": "positive",
                "weight_policy": "descriptive_only",
                "score_applied_now": False,
                "evidence_refs": ["synthetic:evidence:left"],
                "limitations": ["No score is applied now."],
            }
        ],
        "evidence_strength": {
            "evidence_strength_class": "medium",
            "evidence_basis": "fixture_record",
            "evidence_refs": ["synthetic:evidence:left", "synthetic:evidence:right"],
            "evidence_count_policy": "example_count",
            "evidence_strength_not_truth": True,
            "limitations": ["Dry-run evidence is not truth."],
        },
        "provenance_strength": {
            "provenance_strength_class": "medium",
            "provenance_basis": "fixture",
            "provenance_refs": ["synthetic:provenance:dry-run"],
            "chain_complete": False,
            "chain_limitations": ["dry-run only"],
            "provenance_not_truth": True,
            "limitations": ["No source trust claim."],
        },
        "source_posture": {
            "source_posture_class": "active_fixture",
            "source_policy_status": "fixture_only",
            "connector_status": "fixture_only",
            "live_enabled": False,
            "source_trust_claimed": False,
            "source_refs": ["synthetic:source:left", "synthetic:source:right"],
            "limitations": ["No live source."],
        },
        "freshness": {
            "freshness_class": "current_fixture",
            "freshness_basis": "dry-run",
            "stale_penalty_future": False,
            "freshness_score_applied_now": False,
            "limitations": ["No score applied."],
        },
        "conflicts_and_uncertainty": {
            "conflict_status": "none_known",
            "uncertainty_status": "medium",
            "penalty_policy": "descriptive_only",
            "conflict_hidden": False,
            "conflict_suppresses_result_now": False,
            "uncertainty_explanation_required": True,
            "limitations": ["No hidden suppression."],
        },
        "candidate_status": {
            "candidate_class": "review_required",
            "candidate_penalty_future": True,
            "candidate_promotion_performed": False,
            "candidate_confidence_not_truth": True,
            "limitations": ["No candidate promotion."],
        },
        "absence_and_gaps": {
            "absence_status": "not_absent",
            "global_absence_claimed": False,
            "gaps": [],
            "gap_transparency_required": True,
            "absence_or_gap_suppresses_result_now": False,
            "limitations": ["No global absence claim."],
        },
        "action_safety": {
            "action_safety_class": "safe_metadata_actions_only",
            "allowed_actions": ["inspect_metadata", "view_sources", "view_evidence", "compare", "cite"],
            "disabled_actions": ["download", "install", "execute", "upload", "mirror", "arbitrary_url_fetch"],
            "risky_action_bonus_allowed": False,
            "risky_action_penalty_future": True,
            "downloads_enabled": False,
            "installs_enabled": False,
            "execution_enabled": False,
            "limitations": ["No risky action enabled."],
        },
        "rights_risk": {
            "rights_classification": "public_metadata_only",
            "risk_classification": "metadata_only",
            "rights_clearance_claimed": False,
            "malware_safety_claimed": False,
            "risk_caution_required": True,
            "rights_risk_affects_rank_future": True,
            "rights_risk_score_applied_now": False,
            "limitations": ["No rights or malware decision."],
        },
        "tie_breaks": {
            "tie_break_policy": "preserve_current_order_v0",
            "tie_break_factors": ["stable_id", "none"],
            "tie_break_applied_now": False,
            "random_tie_break_allowed": False,
            "limitations": ["Random tie breaks forbidden."],
        },
        "ranking_explanation_ref": None,
        "public_projection": {
            "result_card_projection": "dry-run",
            "result_merge_group_projection": "dry-run",
            "object_page_projection": "dry-run",
            "source_page_projection": "dry-run",
            "comparison_page_projection": "dry-run",
            "explanation_visibility": "user_visible_summary",
            "user_visible_ranking_reason_required": True,
            "ranking_score_publication_policy": "no_numeric_score_v0",
            "limitations": ["No runtime projection."],
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
            "reasons": ["Caller labels are synthetic dry-run labels."],
        },
        "limitations": ["Dry run only; no files written."],
        "no_runtime_guarantees": {
            "runtime_ranking_implemented": False,
            "persistent_ranking_store_implemented": False,
            "live_source_called": False,
            "external_calls_performed": False,
            "model_call_performed": False,
            "telemetry_exported": False,
        },
        "no_ranking_change_guarantees": {
            "ranking_applied_to_live_search": False,
            "public_search_order_changed": False,
            "result_suppressed": False,
            "hidden_suppression_performed": False,
            "popularity_signal_used": False,
            "user_profile_signal_used": False,
            "ad_signal_used": False,
        },
        "no_mutation_guarantees": {
            "candidate_promotion_performed": False,
            "records_merged": False,
            "master_index_mutated": False,
            "public_index_mutated": False,
            "local_index_mutated": False,
            "source_cache_mutated": False,
            "evidence_ledger_mutated": False,
            "candidate_index_mutated": False,
        },
        "notes": ["Dry-run stdout only.", "Ranking is not truth."],
        **FALSES,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--left-title", required=True)
    parser.add_argument("--right-title", required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    payload = build(args.left_title, args.right_title)
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"status: {payload['status']}")
        print(f"ranking_assessment_id: {payload['ranking_assessment_id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
