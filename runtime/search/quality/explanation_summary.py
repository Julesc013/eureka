"""Output bundles and summaries for fixture explanations."""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from typing import Any

from runtime.extraction.guards import detect_truth_or_product_violations, stable_id
from runtime.search.quality.explanation import (
    build_search_result_explanation,
    explanation_product_boundary,
    explanation_truth_boundary,
)
from runtime.search.quality.gap_explanation import build_search_gap_explanation
from runtime.search.quality.known_absence import build_known_absence_record
from runtime.search.quality.near_miss import build_near_miss_explanation


def build_explanation_output_bundle(inputs: Mapping[str, Any] | Sequence[Mapping[str, Any]], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    input_bundle = _merge_inputs(inputs)
    result_explanations = _result_explanations(input_bundle, policy)
    near_misses = [
        build_near_miss_explanation(item, {"query_ref": _query_ref(input_bundle)}, policy)
        for item in input_bundle.get("near_miss_inputs", [])
        if isinstance(item, Mapping)
    ]
    known_absence = build_known_absence_record(input_bundle, policy)
    gap_explanations = [
        build_search_gap_explanation(item, policy)
        for item in input_bundle.get("extraction_search_gaps", [])
        if isinstance(item, Mapping)
    ]
    bundle = {
        "schema_version": "explanation_output_bundle.v0",
        "output_bundle_id": stable_id("search.explanation_output", input_bundle.get("input_bundle_id", "input")),
        "output_status": "local_dry_run",
        "input_bundle_ref": input_bundle.get("input_bundle_id"),
        "result_explanations": result_explanations,
        "near_miss_explanations": near_misses,
        "known_absence_records": [known_absence],
        "search_gap_explanations": gap_explanations,
        "review_seed_previews": list(input_bundle.get("review_seed_previews", [])),
        "workunit_seed_previews_future": list(input_bundle.get("workunit_seed_previews_future", [])),
        "limitations": ["Explanation bundle is fixture-only and does not mutate ranking or public search."],
        "no_claims": {
            "ranking_changed": False,
            "public_search_changed": False,
            "evidence_accepted": False,
            "candidate_accepted": False,
            "global_absence_claimed": False,
        },
        "truth_boundary": explanation_truth_boundary(),
        "product_boundary": explanation_product_boundary(),
    }
    violations = detect_truth_or_product_violations(bundle)
    if violations:
        raise ValueError("; ".join(violations))
    return bundle


def summarize_explanation_output_bundle(bundle: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    near_types = Counter(str(item.get("mismatch_type", "unknown")) for item in bundle.get("near_miss_explanations", []))
    absence_statuses = Counter(str(item.get("absence_status", "unknown")) for item in bundle.get("known_absence_records", []))
    gap_types = Counter(str(item.get("gap_type", "unknown")) for item in bundle.get("search_gap_explanations", []))
    return {
        "schema_version": "search_explanation_summary.v0",
        "output_bundle_id": bundle.get("output_bundle_id"),
        "output_status": bundle.get("output_status"),
        "result_explanation_count": len(bundle.get("result_explanations", [])),
        "near_miss_count": len(bundle.get("near_miss_explanations", [])),
        "known_absence_count": len(bundle.get("known_absence_records", [])),
        "search_gap_explanation_count": len(bundle.get("search_gap_explanations", [])),
        "near_miss_type_counts": dict(sorted(near_types.items())),
        "absence_status_counts": dict(sorted(absence_statuses.items())),
        "gap_type_counts": dict(sorted(gap_types.items())),
        "public_search_mutated": False,
        "ranking_mutated": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
    }


def _result_explanations(input_bundle: Mapping[str, Any], policy: Mapping[str, Any] | None) -> list[dict[str, Any]]:
    explanations: list[dict[str, Any]] = []
    for key in ("candidate_records", "source_cache_records", "evidence_records", "extraction_search_gaps"):
        for item in input_bundle.get(key, []):
            if not isinstance(item, Mapping):
                continue
            scoped = dict(input_bundle)
            scoped["candidate_records"] = [item] if key == "candidate_records" else []
            scoped["source_cache_records"] = [item] if key == "source_cache_records" else []
            scoped["evidence_records"] = [item] if key == "evidence_records" else []
            scoped["extraction_search_gaps"] = [item] if key == "extraction_search_gaps" else []
            explanations.append(build_search_result_explanation(scoped, policy))
    if not explanations:
        explanations.append(build_search_result_explanation(input_bundle, policy))
    return explanations


def _merge_inputs(inputs: Mapping[str, Any] | Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    if isinstance(inputs, Mapping):
        return dict(inputs)
    merged: dict[str, Any] = {
        "schema_version": "explanation_input_bundle.v0",
        "input_bundle_id": "explanation.input.merged.v0",
        "bundle_status": "local_dry_run",
        "query_observation_refs": [],
        "search_miss_refs": [],
        "search_need_refs": [],
        "candidate_refs": [],
        "source_cache_refs": [],
        "evidence_refs": [],
        "review_refs": [],
        "extraction_result_refs": [],
        "extraction_search_gap_refs": [],
        "local_fixture_result_refs": [],
        "candidate_records": [],
        "source_cache_records": [],
        "evidence_records": [],
        "extraction_search_gaps": [],
        "near_miss_inputs": [],
        "truth_boundary": explanation_truth_boundary(),
        "product_boundary": explanation_product_boundary(),
        "limitations": ["Merged explicit input records."],
    }
    for item in inputs:
        if not isinstance(item, Mapping):
            continue
        schema = item.get("schema_version")
        if schema == "candidate_record.v0":
            merged["candidate_records"].append(item)
            merged["candidate_refs"].append(item.get("candidate_id"))
        elif schema == "local_evidence_ledger_record.v0":
            merged["evidence_records"].append(item)
            merged["evidence_refs"].append(item.get("evidence_record_id"))
        elif schema == "extraction_search_gap.v0":
            merged["extraction_search_gaps"].append(item)
            merged["extraction_search_gap_refs"].append(item.get("search_gap_id"))
        else:
            merged["local_fixture_result_refs"].append(item.get("schema_version", "unknown"))
    return merged


def _query_ref(input_bundle: Mapping[str, Any]) -> str:
    refs = input_bundle.get("search_need_refs") or input_bundle.get("query_observation_refs") or input_bundle.get("search_miss_refs") or []
    return str(refs[0]) if isinstance(refs, list) and refs else str(input_bundle.get("input_bundle_id", "query.fixture.v0"))
