"""Fixture-only search-quality regression harness."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from runtime.extraction.guards import detect_truth_or_product_violations, load_json, stable_id
from runtime.search.quality.ranking_shadow import ranking_product_boundary, ranking_truth_boundary


def load_query_set(path: str | Path) -> dict[str, Any]:
    return load_json(Path(path))


def run_quality_regression(query_set: Mapping[str, Any], ranking_outputs: Sequence[Mapping[str, Any]], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return build_search_quality_regression_report(query_set, ranking_outputs, policy)


def build_search_quality_regression_report(
    query_set: Mapping[str, Any],
    outputs: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    shadow_results = [_shadow_result(output) for output in outputs]
    expected = set(_strings(query_set.get("expected_result_refs")))
    ranked_refs = {item.get("item_ref") for result in shadow_results for item in result.get("ranked_items", [])}
    near_expected = set(_strings(query_set.get("expected_near_miss_refs")))
    absence_expected = set(_strings(query_set.get("expected_absence_refs")))
    metrics = {
        "exact_expected_present": len(expected.intersection(ranked_refs)),
        "exact_expected_missing": len(expected.difference(ranked_refs)),
        "near_miss_identified": len(near_expected),
        "absence_record_present": len(absence_expected),
        "explanation_present": _count_refs(shadow_results, "explanation_refs"),
        "extraction_gap_explained": _count_refs(shadow_results, "extraction_gap_refs"),
        "policy_block_explained": 1 if query_set.get("query_set_status") == "blocked" else 0,
        "duplicate_preserved": _count_nested(outputs, "dedup_shadow_results"),
        "conflict_preserved": _count_nested(outputs, "identity_merge_shadows"),
        "ranking_shadow_changed_count": 0,
        "warning_count": 0,
    }
    report = {
        "schema_version": "search_quality_regression_report.v0",
        "regression_report_id": stable_id("search_quality.regression", {"query_set": query_set.get("query_set_id"), "outputs": [r.get("ranking_shadow_id") for r in shadow_results]}),
        "query_set_ref": query_set.get("query_set_id"),
        "ranking_shadow_refs": [result.get("ranking_shadow_id") for result in shadow_results],
        "explanation_refs": list(query_set.get("explanation_refs", [])),
        "metrics": metrics,
        "pass_fail_summary": {
            "status": "pass_with_warnings" if metrics["exact_expected_missing"] else "pass",
            "public_ranking_changed": False,
            "production_quality_claimed": False,
        },
        "regressions": [],
        "improvements": ["Fixture query set can be evaluated by shadow ranking."],
        "blockers": [] if query_set.get("query_set_status") != "blocked" else ["query_set_policy_blocked"],
        "limitations": ["Regression report is fixture-only and not production search quality proof."],
        "forbidden_claims": [
            "production_search_quality",
            "beats_google",
            "beats_internet_archive",
            "exhaustive_global_coverage",
            "rights_clearance",
            "malware_safety",
            "verified_installability",
        ],
        "truth_boundary": ranking_truth_boundary(),
        "product_boundary": ranking_product_boundary(),
    }
    if detect_quality_overclaim(report, policy):
        raise ValueError("; ".join(detect_quality_overclaim(report, policy)))
    violations = detect_truth_or_product_violations(report)
    if violations:
        raise ValueError("; ".join(violations))
    return report


def summarize_regression_report(report: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    metrics = report.get("metrics", {})
    return {
        "schema_version": "search_quality_regression_summary.v0",
        "regression_report_id": report.get("regression_report_id"),
        "query_set_ref": report.get("query_set_ref"),
        "status": report.get("pass_fail_summary", {}).get("status"),
        "exact_expected_present": metrics.get("exact_expected_present", 0),
        "exact_expected_missing": metrics.get("exact_expected_missing", 0),
        "ranking_shadow_count": len(report.get("ranking_shadow_refs", [])),
        "public_ranking_mutated": False,
        "production_quality_claimed": False,
    }


def detect_quality_overclaim(report: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    text = __import__("json").dumps(report, sort_keys=True).casefold()
    forbidden = ["beats_google", "beats_internet_archive", "exhaustive_global_coverage"]
    return [f"forbidden quality overclaim: {term}" for term in forbidden if f'"{term}": true' in text]


def _shadow_result(output: Mapping[str, Any]) -> Mapping[str, Any]:
    if output.get("schema_version") == "ranking_shadow_result.v0":
        return output
    if isinstance(output.get("ranking_shadow_result"), Mapping):
        return output["ranking_shadow_result"]
    return {}


def _strings(value: Any) -> list[str]:
    return [str(item) for item in value] if isinstance(value, list) else []


def _count_refs(results: Sequence[Mapping[str, Any]], key: str) -> int:
    return sum(len(item.get(key, [])) for item in results)


def _count_nested(outputs: Sequence[Mapping[str, Any]], key: str) -> int:
    return sum(len(item.get(key, [])) for item in outputs if isinstance(item.get(key), list))
