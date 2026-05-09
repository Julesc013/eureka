"""Near-miss explanation helpers."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from runtime.extraction.guards import detect_truth_or_product_violations, stable_id
from runtime.search_quality.explanation import explanation_product_boundary, explanation_truth_boundary


ALLOWED_MISMATCH_TYPES = {
    "wrong_version",
    "wrong_platform",
    "wrong_architecture",
    "wrong_format",
    "wrong_source_lane",
    "source_only",
    "evidence_too_weak",
    "compatibility_uncertain",
    "rights_or_risk_blocked",
    "extraction_needed",
    "identity_uncertain",
    "not_evaluable",
}


def classify_near_miss_mismatch(result: Mapping[str, Any], query_or_need: Mapping[str, Any] | None = None, policy: Mapping[str, Any] | None = None) -> str:
    declared = result.get("mismatch_type") or result.get("reason")
    if declared in ALLOWED_MISMATCH_TYPES:
        return str(declared)
    text = " ".join(str(value) for value in result.values()).casefold()
    if "version" in text:
        return "wrong_version"
    if "platform" in text:
        return "wrong_platform"
    if "source only" in text or "source_only" in text:
        return "source_only"
    if "extract" in text or "member" in text:
        return "extraction_needed"
    if "evidence" in text:
        return "evidence_too_weak"
    return "not_evaluable"


def build_near_miss_explanation(result: Mapping[str, Any], query_or_need: Mapping[str, Any] | None = None, policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    mismatch = classify_near_miss_mismatch(result, query_or_need, policy)
    result_ref = str(result.get("result_ref") or result.get("candidate_id") or result.get("source_ref") or "near_miss.unknown.v0")
    query_ref = str((query_or_need or {}).get("search_need_id") or (query_or_need or {}).get("query_ref") or "query.fixture.v0")
    record = {
        "schema_version": "near_miss_explanation.v0",
        "near_miss_id": stable_id("search.near_miss", {"query": query_ref, "result": result_ref, "mismatch": mismatch}),
        "near_miss_status": "fixture_only",
        "query_ref": query_ref,
        "near_miss_result_ref": result_ref,
        "mismatch_type": mismatch,
        "matched_fields": list(result.get("matched_fields", ["name_or_topic"])) if isinstance(result.get("matched_fields", []), list) else [],
        "mismatched_fields": list(result.get("mismatched_fields", [mismatch])) if isinstance(result.get("mismatched_fields", []), list) else [mismatch],
        "why_not_exact": result.get("why_not_exact") or f"Fixture result is a near miss because of {mismatch}.",
        "useful_followup": result.get("useful_followup") or "Review or seed a future WorkUnit before downstream use.",
        "suggested_workunit_seed_future": {
            "proposed_workunit_type": "check_member_relevance_future" if mismatch == "extraction_needed" else "policy_review_future",
            "created": False,
            "review_required": True,
        },
        "limitations": ["Near miss does not reject, merge, or accept a result."],
        "truth_boundary": explanation_truth_boundary(),
        "product_boundary": explanation_product_boundary(),
    }
    return validate_near_miss_explanation(record, policy)


def validate_near_miss_explanation(record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    violations = detect_truth_or_product_violations(record)
    if violations:
        raise ValueError("; ".join(violations))
    if record.get("mismatch_type") not in ALLOWED_MISMATCH_TYPES:
        raise ValueError("near miss mismatch_type is not allowed")
    if not record.get("why_not_exact"):
        raise ValueError("near miss requires why_not_exact")
    if record.get("suggested_workunit_seed_future", {}).get("created") is not False:
        raise ValueError("near miss must not create or execute a WorkUnit")
    return dict(record)
