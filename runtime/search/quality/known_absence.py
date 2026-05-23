"""Known-absence records with explicit non-global scope."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from runtime.extraction.guards import detect_truth_or_product_violations, stable_id
from runtime.search.quality.explanation import explanation_product_boundary, explanation_truth_boundary


OVERCLAIM_PHRASES = {
    "global absence",
    "exhaustive web",
    "does not exist anywhere",
    "whole web",
    "all sources checked",
}


def build_known_absence_record(input_bundle: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    gaps = [item for item in input_bundle.get("extraction_search_gaps", []) if isinstance(item, Mapping)]
    near_misses = [item for item in input_bundle.get("near_miss_inputs", []) if isinstance(item, Mapping)]
    status = str(input_bundle.get("absence_status_hint") or "no_reviewed_result")
    if status not in {"no_reviewed_result", "source_gap", "extraction_needed", "policy_blocked", "local_fixture_absence", "example_only", "not_evaluable"}:
        status = "no_reviewed_result"
    if any(item.get("gap_type") == "policy_blocked_extraction_gap" for item in gaps):
        status = "policy_blocked"
    elif any(item.get("gap_type") in {"future_deep_extraction_needed", "hidden_member_not_indexed", "manifest_not_indexed"} for item in gaps):
        status = "extraction_needed"
    sources_checked = list(input_bundle.get("sources_checked", ["local_fixture_index"]))
    sources_not_checked = list(input_bundle.get("sources_not_checked", ["live_web", "external_sources", "public_query_fanout"]))
    record = {
        "schema_version": "known_absence_record.v0",
        "known_absence_id": stable_id("search.known_absence", {"bundle": input_bundle.get("input_bundle_id"), "status": status}),
        "absence_status": status,
        "query_ref": _query_ref(input_bundle),
        "search_need_refs": list(input_bundle.get("search_need_refs", [])),
        "sources_checked": sources_checked,
        "sources_not_checked": sources_not_checked,
        "local_index_scope": "fixture_and_local_examples_only",
        "fixture_scope": "examples/search/quality and referenced fixture records",
        "reviewed_records_scope": "no accepted reviewed public records in this bundle",
        "near_miss_refs": [str(item.get("result_ref") or item.get("near_miss_result_ref")) for item in near_misses],
        "search_gap_refs": [str(item.get("search_gap_id")) for item in gaps if item.get("search_gap_id")],
        "extraction_gap_refs": [str(item.get("search_gap_id")) for item in gaps if item.get("search_gap_id")],
        "blocked_source_refs": [str(item.get("search_gap_id")) for item in gaps if item.get("gap_type") == "policy_blocked_extraction_gap"],
        "remaining_work": ["human_review", "source_policy_review", "future_workunit_review"],
        "absence_summary": "No reviewed exact result is present in the fixture scope; this is not a global absence claim.",
        "no_claims": {
            "global_absence_claimed": False,
            "exhaustive_web_search_claimed": False,
            "all_sources_checked": False,
            "public_truth_created": False,
        },
        "limitations": ["Known absence is scoped to explicit local fixture inputs."],
        "truth_boundary": explanation_truth_boundary(),
        "product_boundary": explanation_product_boundary(),
        "notes": ["Known absence preserves sources-not-checked and remaining-work lists."],
    }
    return validate_known_absence_record(record, policy)


def summarize_known_absence(record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return {
        "known_absence_id": record.get("known_absence_id"),
        "absence_status": record.get("absence_status"),
        "sources_checked_count": len(record.get("sources_checked", [])),
        "sources_not_checked_count": len(record.get("sources_not_checked", [])),
        "remaining_work_count": len(record.get("remaining_work", [])),
        "global_absence_claimed": False,
    }


def validate_known_absence_record(record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    violations = detect_truth_or_product_violations(record)
    if violations:
        raise ValueError("; ".join(violations))
    if not record.get("sources_checked"):
        raise ValueError("known absence requires sources_checked")
    if not record.get("sources_not_checked"):
        raise ValueError("known absence requires sources_not_checked")
    if not record.get("remaining_work"):
        raise ValueError("known absence requires remaining_work")
    if detect_absence_overclaim(record, policy):
        raise ValueError("known absence must not claim global or exhaustive absence")
    return dict(record)


def detect_absence_overclaim(record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> bool:
    no_claims = record.get("no_claims", {})
    if isinstance(no_claims, Mapping):
        if no_claims.get("global_absence_claimed") is True or no_claims.get("exhaustive_web_search_claimed") is True:
            return True
    if record.get("truth_boundary", {}).get("known_absence_claims_global_absence") is True:
        return True
    text = _record_text(record).casefold()
    return any(phrase in text for phrase in OVERCLAIM_PHRASES if phrase not in {"global absence"})


def _query_ref(input_bundle: Mapping[str, Any]) -> str:
    refs = input_bundle.get("search_need_refs") or input_bundle.get("query_observation_refs") or input_bundle.get("search_miss_refs") or []
    return str(refs[0]) if isinstance(refs, list) and refs else str(input_bundle.get("input_bundle_id", "query.fixture.v0"))


def _record_text(value: Any) -> str:
    values: list[str] = []

    def walk(item: Any) -> None:
        if isinstance(item, str):
            values.append(item)
        elif isinstance(item, Mapping):
            for child in item.values():
                walk(child)
        elif isinstance(item, list):
            for child in item:
                walk(child)

    walk(value)
    return "\n".join(values)
