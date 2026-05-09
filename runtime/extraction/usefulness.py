"""Usefulness and Track G handoff summaries for extraction integration."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from runtime.extraction.guards import detect_truth_or_product_violations, stable_id
from runtime.extraction.review_bridge import extraction_search_product_boundary, extraction_search_truth_boundary


def build_extraction_quality_delta_preview(
    integration_records: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    integrations = list(integration_records)
    return {
        "schema_version": "extraction_quality_delta_preview.v0",
        "quality_delta_preview_id": stable_id("extraction.quality_delta_preview", [item.get("integration_id") for item in integrations]),
        "comparison_scope": "fixture_search_gap_visibility_only",
        "before_state": "outer_metadata_only",
        "after_state": "member_and_manifest_gap_previews",
        "search_gap_count": sum(len(item.get("search_gap_refs", [])) for item in integrations),
        "review_seed_count": sum(len(item.get("review_seed_refs", [])) for item in integrations),
        "workunit_seed_count": sum(len(item.get("workunit_seed_refs", [])) for item in integrations),
        "claims_production_quality": False,
        "limitations": ["Quality delta is a fixture preview and not production search quality proof."],
        "truth_boundary": extraction_search_truth_boundary(),
        "product_boundary": extraction_search_product_boundary(),
    }


def build_extraction_usefulness_report(
    integration_records: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    integrations = list(integration_records)
    search_gap_count = sum(len(item.get("search_gap_refs", [])) for item in integrations)
    review_seed_count = sum(len(item.get("review_seed_refs", [])) for item in integrations)
    workunit_seed_count = sum(len(item.get("workunit_seed_refs", [])) for item in integrations)
    blocked_count = sum(
        1
        for item in integrations
        for gap in item.get("search_gaps", [])
        if isinstance(gap, Mapping) and gap.get("gap_type") == "policy_blocked_extraction_gap"
    )
    report = {
        "schema_version": "extraction_usefulness_report.v0",
        "usefulness_report_id": stable_id("extraction.usefulness_report", [item.get("integration_id") for item in integrations]),
        "extraction_result_count": sum(len(item.get("extraction_result_refs", [])) for item in integrations),
        "member_candidate_count": sum(len(item.get("candidate_effect_refs", [])) for item in integrations),
        "manifest_candidate_count": sum(
            1
            for item in integrations
            for gap in item.get("search_gaps", [])
            if isinstance(gap, Mapping) and gap.get("gap_type") == "manifest_not_indexed"
        ),
        "search_gap_count": search_gap_count,
        "review_seed_count": review_seed_count,
        "workunit_seed_count": workunit_seed_count,
        "blocked_count": blocked_count,
        "useful_query_classes": [
            "hidden_member_lookup",
            "manifest_metadata_lookup",
            "future_deepening_decision",
        ],
        "limitations": ["Usefulness report does not claim production search quality or exhaustive coverage."],
        "quality_delta_preview": build_extraction_quality_delta_preview(integrations, policy),
        "next_phase_recommendation": "READY_FOR_G_BUNDLE_01" if search_gap_count and review_seed_count else "NEEDS_REMEDIATION",
        "truth_boundary": extraction_search_truth_boundary(),
        "product_boundary": extraction_search_product_boundary(),
    }
    detect_extraction_usefulness_overclaim(report, policy)
    return report


def build_track_g_readiness_recommendation(
    usefulness_report: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    readiness = usefulness_report.get("next_phase_recommendation", "NEEDS_REMEDIATION")
    return {
        "schema_version": "extraction_to_track_g_handoff.v0",
        "handoff_id": stable_id("extraction.track_g_handoff", usefulness_report.get("usefulness_report_id")),
        "track_g_readiness": readiness,
        "recommended_next_task": "G-BUNDLE-01 - Result explanations, near misses, and known absence"
        if readiness == "READY_FOR_G_BUNDLE_01"
        else "F-REMEDIATION-01 - Complete extraction search integration gaps",
        "basis": {
            "search_gap_count": usefulness_report.get("search_gap_count", 0),
            "review_seed_count": usefulness_report.get("review_seed_count", 0),
            "workunit_seed_count": usefulness_report.get("workunit_seed_count", 0),
        },
        "limitations": ["Track G handoff consumes fixture previews only."],
        "truth_boundary": extraction_search_truth_boundary(),
        "product_boundary": extraction_search_product_boundary(),
    }


def detect_extraction_usefulness_overclaim(report: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    violations = detect_truth_or_product_violations(report)
    if report.get("claims_production_quality") is True:
        violations.append("claims_production_quality=true is forbidden")
    if violations:
        raise ValueError("; ".join(violations))
    return []
