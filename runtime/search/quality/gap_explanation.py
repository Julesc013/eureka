"""Search-gap explanation helpers."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from runtime.extraction.guards import detect_truth_or_product_violations, stable_id
from runtime.search.quality.explanation import explanation_product_boundary, explanation_truth_boundary


def build_search_gap_explanation(search_gap: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    gap_ref = str(search_gap.get("search_gap_id", "search_gap.unknown.v0"))
    gap_type = str(search_gap.get("gap_type", "not_evaluable"))
    record = {
        "schema_version": "search_gap_explanation.v0",
        "search_gap_explanation_id": stable_id("search.gap_explanation", {"gap": gap_ref, "type": gap_type}),
        "gap_type": gap_type,
        "related_search_gap_refs": [gap_ref],
        "related_extraction_gap_refs": [gap_ref] if gap_type in {"hidden_member_not_indexed", "manifest_not_indexed", "policy_blocked_extraction_gap", "future_deep_extraction_needed"} else [],
        "why_gap_exists": search_gap.get("why_extraction_matters") or search_gap.get("gap_summary") or "Gap requires fixture review.",
        "what_would_close_gap": "Human review plus future policy-approved WorkUnit output.",
        "suggested_next_actions": [search_gap.get("recommended_next_action", "request_human_review")],
        "suggested_workunit_seed_refs": ["workunit_seed_future.review_required.v0"],
        "limitations": ["Gap explanation is a fixture-only planning artifact."],
        "truth_boundary": explanation_truth_boundary(),
        "product_boundary": explanation_product_boundary(),
    }
    return validate_search_gap_explanation(record, policy)


def build_extraction_gap_explanation(extraction_gap: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return build_search_gap_explanation(extraction_gap, policy)


def validate_search_gap_explanation(record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    violations = detect_truth_or_product_violations(record)
    if violations:
        raise ValueError("; ".join(violations))
    if record.get("truth_boundary", {}).get("explanation_mutates_public_search") is not False:
        raise ValueError("gap explanation must not mutate public search")
    return dict(record)
