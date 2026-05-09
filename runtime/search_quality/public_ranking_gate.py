"""Public-ranking gate reports for shadow ranking."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from runtime.extraction.guards import detect_truth_or_product_violations, stable_id
from runtime.search_quality.ranking_shadow import ranking_product_boundary, ranking_truth_boundary


def build_public_ranking_gate(regression_reports: Sequence[Mapping[str, Any]], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    blockers = ["public_ranking_blocked_current"]
    if any(report.get("blockers") for report in regression_reports):
        blockers.append("regression_blockers_present")
    gate = {
        "schema_version": "public_ranking_gate.v0",
        "public_ranking_gate_id": stable_id("public_ranking.gate", [report.get("regression_report_id") for report in regression_reports]),
        "gate_status": "blocked_current",
        "required_inputs": [
            "reviewed_regression_report",
            "human_ranking_review",
            "public_search_change_approval",
        ],
        "regression_report_refs": [report.get("regression_report_id") for report in regression_reports],
        "review_refs": [],
        "blockers": blockers,
        "allowed_next_actions": ["review_shadow_results_future", "expand_fixture_query_sets_future"],
        "forbidden_next_actions": [
            "public_ranking_change",
            "public_search_runtime_change",
            "public_index_mutation",
            "master_index_mutation",
        ],
        "limitations": ["Public ranking remains blocked in G-BUNDLE-02."],
        "truth_boundary": ranking_truth_boundary(),
        "product_boundary": ranking_product_boundary(),
    }
    return validate_public_ranking_gate(gate, policy)


def validate_public_ranking_gate(gate: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    violations = detect_truth_or_product_violations(gate)
    if violations:
        raise ValueError("; ".join(violations))
    if gate.get("gate_status") not in {"blocked_current", "not_ready", "ready_for_review_future", "ready_for_public_alpha_future", "policy_blocked", "not_evaluable"}:
        raise ValueError("invalid public ranking gate status")
    if gate.get("gate_status") not in {"blocked_current", "ready_for_review_future"}:
        raise ValueError("G-BUNDLE-02 may only be blocked current or future-review")
    return dict(gate)


def summarize_public_ranking_gate(gate: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return {
        "schema_version": "public_ranking_gate_summary.v0",
        "public_ranking_gate_id": gate.get("public_ranking_gate_id"),
        "gate_status": gate.get("gate_status"),
        "blocker_count": len(gate.get("blockers", [])),
        "public_ranking_mutated": False,
        "public_search_mutated": False,
    }
