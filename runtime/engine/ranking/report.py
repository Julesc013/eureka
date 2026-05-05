from __future__ import annotations

import json
from typing import Any

from runtime.engine.ranking.models import RankingDryRunReport, RankingDryRunResultSet
from runtime.engine.ranking.policy import HARD_BOOLEANS


EVAL_GATE_SUMMARY = {
    "archive_resolution_eval_status": "passed at P97/P106 verification; rerun in P107 verification",
    "search_usefulness_audit_status": "passed at P97/P106 verification; rerun in P107 verification",
    "external_baseline_comparison_status": "comparison_not_eligible_for_production_claims",
    "manual_observation_batch_0_status": "0 observed / 39 pending in P102/P106 evidence",
    "production_quality_claims_eligible": False,
    "local_dry_run_allowed": True,
    "known_counts": {
        "covered": 5,
        "partial": 40,
        "source_gap": 10,
        "capability_gap": 7,
        "unknown": 2,
    },
}


def build_report(input_roots: list[str], result_sets: list[RankingDryRunResultSet], errors: list[str]) -> RankingDryRunReport:
    valid_sets = [item for item in result_sets if not item.errors]
    invalid_count = len(result_sets) - len(valid_sets) + len(errors)
    factors = []
    result_summaries = []
    explanations = []
    current_order = {}
    proposed_order = {}
    fallback_order = {}
    conflict_gap = {"conflict_visible": 0, "gap_visible": 0, "fallback_used": 0}
    factor_summary: dict[str, int] = {}
    for result_set in result_sets:
        payload = result_set.to_dict()
        current_order[result_set.result_set_id] = payload["current_order"]
        proposed_order[result_set.result_set_id] = payload["proposed_dry_run_order"]
        fallback_order[result_set.result_set_id] = payload["fallback_order"]
        if result_set.fallback_used:
            conflict_gap["fallback_used"] += 1
        for summary in result_set.result_summaries:
            result_summaries.append(
                {
                    "result_set_id": result_set.result_set_id,
                    "result_id": summary.result_id,
                    "title": summary.title,
                    "current_rank": summary.current_rank,
                    "policy_status": summary.policy_status,
                }
            )
            for factor in summary.factors:
                factor_dict = factor.to_dict()
                factor_dict["result_set_id"] = result_set.result_set_id
                factor_dict["result_id"] = summary.result_id
                factors.append(factor_dict)
                factor_summary[factor.factor_type] = factor_summary.get(factor.factor_type, 0) + 1
                if factor.factor_type == "conflict_penalty" and factor.category_value != "absent":
                    conflict_gap["conflict_visible"] += 1
                if factor.factor_type == "absence_gap_transparency" and factor.category_value != "absent":
                    conflict_gap["gap_visible"] += 1
        for explanation in result_set.explanation_summaries:
            explanation_dict = explanation.to_dict()
            explanation_dict["result_set_id"] = result_set.result_set_id
            explanations.append(explanation_dict)
    return RankingDryRunReport(
        report_id="public_search_ranking_local_dry_run_report",
        mode="local_dry_run",
        input_roots=tuple(input_roots),
        result_sets_seen=len(result_sets),
        result_sets_valid=len(valid_sets),
        result_sets_invalid=invalid_count,
        result_summaries=tuple(result_summaries),
        current_order=current_order,
        proposed_dry_run_order=proposed_order,
        fallback_order=fallback_order,
        ranking_factors=tuple(factors),
        factor_summary=dict(sorted(factor_summary.items())),
        explanation_summaries=tuple(explanations),
        conflict_gap_visibility_summary=conflict_gap,
        privacy_status_counts={"public_safe": len(result_sets), "rejected_sensitive": len(errors)},
        public_safety_status_counts={"public_safe": len(valid_sets), "rejected": invalid_count},
        eval_gate_summary=EVAL_GATE_SUMMARY,
        warnings=tuple(warning for result_set in result_sets for warning in result_set.warnings),
        errors=tuple(errors + [error for result_set in result_sets for error in result_set.errors]),
        hard_booleans=dict(HARD_BOOLEANS),
    )


def report_to_json(report: RankingDryRunReport) -> str:
    return json.dumps(report.to_dict(), indent=2, sort_keys=True) + "\n"


def summarize_report(report: RankingDryRunReport) -> str:
    data = report.to_dict()
    return (
        f"mode: {data['mode']}\n"
        f"result_sets_seen: {data['result_sets_seen']}\n"
        f"result_sets_valid: {data['result_sets_valid']}\n"
        f"result_sets_invalid: {data['result_sets_invalid']}\n"
        f"public_search_order_changed: {data['hard_booleans']['public_search_order_changed']}\n"
    )

