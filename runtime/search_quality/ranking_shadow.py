"""Shadow-only ranking proposals over explicit fixture records."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from runtime.extraction.guards import REPO_ROOT, detect_truth_or_product_violations, load_json, stable_id
from runtime.search_quality.explanation import explanation_product_boundary
from runtime.search_quality.ranking_factors import FACTOR_SCORERS


RANKING_POLICY_NAMES = [
    "ranking_shadow_policy",
    "ranking_factor_policy",
    "identity_merge_shadow_policy",
    "dedup_shadow_policy",
    "search_quality_query_set_policy",
    "search_quality_regression_policy",
    "public_ranking_gate_policy",
    "ranking_output_policy",
    "ranking_path_policy",
    "ranking_truth_policy",
]


def load_ranking_policy(root=None) -> dict[str, Any]:
    repo_root = REPO_ROOT if root is None else root
    policy_root = repo_root / "control" / "inventory" / "search_quality"
    bundle = {name: load_json(policy_root / f"{name}.json") for name in RANKING_POLICY_NAMES}
    path_policy = bundle["ranking_path_policy"]
    return {
        "schema_version": "ranking_policy_bundle.v0",
        **bundle,
        "allowed_input_roots": path_policy.get("allowed_input_roots", []),
        "allowed_output_roots": path_policy.get("allowed_output_roots", []),
        "forbidden_output_roots": path_policy.get("forbidden_output_roots", []),
    }


def ranking_truth_boundary() -> dict[str, bool]:
    return {
        "ranking_shadow_accepts_result_as_truth": False,
        "ranking_shadow_accepts_evidence": False,
        "ranking_shadow_accepts_candidate": False,
        "ranking_shadow_accepts_candidates": False,
        "ranking_shadow_mutates_public_ranking": False,
        "ranking_shadow_mutates_public_search": False,
        "ranking_shadow_mutates_public_index": False,
        "ranking_shadow_mutates_master_index": False,
        "identity_shadow_creates_canonical_identity": False,
        "dedup_shadow_merges_or_deletes": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "rights_clearance_claimed": False,
        "malware_safety_claimed": False,
        "verified_installability_claimed": False,
        "production_quality_claimed": False,
        "external_superiority_claimed": False,
    }


def ranking_product_boundary() -> dict[str, bool]:
    boundary = explanation_product_boundary()
    boundary.update(
        {
            "changed_public_search_behavior": False,
            "changed_ranking_behavior": False,
            "mutated_public_index": False,
            "mutated_master_index": False,
        }
    )
    return boundary


def build_ranking_shadow(input_bundle: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    policy = policy or {}
    context = input_bundle.get("query_context", {})
    items = [item for item in input_bundle.get("items", []) if isinstance(item, Mapping)]
    factor_policy = policy.get("ranking_factor_policy", {})
    scored = []
    factor_results = []
    for item in items:
        item_factors = build_factor_results(item, factor_policy, context)
        total = round(sum(float(result["score"]) * float(result.get("weight", 1.0)) for result in item_factors), 6)
        item_ref = str(item.get("item_ref") or item.get("candidate_id") or stable_id("ranking.item", item))
        scored.append((total, item_ref, item, item_factors))
        factor_results.extend(item_factors)
    ranked_items = []
    for rank, (score, item_ref, item, item_factors) in enumerate(sorted(scored, key=lambda entry: (-entry[0], entry[1])), start=1):
        ranked_items.append(
            {
                "shadow_rank": rank,
                "item_ref": item_ref,
                "item_kind": item.get("item_kind", "fixture_candidate"),
                "shadow_score": score,
                "factor_result_refs": [result["factor_result_id"] for result in item_factors],
                "explanation_refs": list(item.get("explanation_refs", [])),
                "near_miss_refs": list(item.get("near_miss_refs", [])),
                "known_absence_refs": list(item.get("known_absence_refs", [])),
                "review_required_before_public_use": True,
            }
        )
    status = "blocked_by_policy" if input_bundle.get("ranking_shadow_status") == "blocked_by_policy" else "local_shadow"
    result = {
        "schema_version": "ranking_shadow_result.v0",
        "ranking_shadow_id": stable_id("ranking.shadow", {"input": input_bundle.get("ranking_input_bundle_id"), "items": [item[1] for item in scored]}),
        "ranking_shadow_status": status,
        "input_bundle_ref": input_bundle.get("ranking_input_bundle_id"),
        "query_ref": input_bundle.get("query_ref"),
        "ranked_items": ranked_items,
        "factor_results": factor_results,
        "explanation_refs": list(input_bundle.get("explanation_refs", [])),
        "near_miss_refs": list(input_bundle.get("near_miss_refs", [])),
        "known_absence_refs": list(input_bundle.get("known_absence_refs", [])),
        "extraction_gap_refs": list(input_bundle.get("extraction_gap_refs", [])),
        "identity_shadow_refs": [],
        "dedup_shadow_refs": [],
        "limitations": ["Ranking is shadow-only and does not publish or mutate order."],
        "review_gates": {
            "review_required_before_public_ranking_use": True,
            "public_ranking_mutation_allowed": False,
            "automatic_acceptance_allowed": False,
        },
        "truth_boundary": ranking_truth_boundary(),
        "product_boundary": ranking_product_boundary(),
        "notes": ["Shadow score is a deterministic fixture proposal, not authority."],
    }
    return validate_ranking_shadow_result(result, policy)


def score_ranking_item(item: Mapping[str, Any], factor_policy: Mapping[str, Any] | None = None, context: Mapping[str, Any] | None = None) -> float:
    return round(sum(result["score"] * result.get("weight", 1.0) for result in build_factor_results(item, factor_policy, context)), 6)


def build_factor_results(item: Mapping[str, Any], factor_policy: Mapping[str, Any] | None = None, context: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    enabled = (factor_policy or {}).get("enabled_factor_families") or list(FACTOR_SCORERS)
    weights = (factor_policy or {}).get("factor_weights", {})
    item_ref = str(item.get("item_ref") or item.get("candidate_id") or stable_id("ranking.item", item))
    results: list[dict[str, Any]] = []
    for family in enabled:
        scorer = FACTOR_SCORERS.get(str(family))
        if scorer is None:
            continue
        score = float(scorer(item, context or {}))
        weight = float(weights.get(family, 1.0))
        results.append(
            {
                "schema_version": "ranking_factor_result.v0",
                "factor_result_id": stable_id("ranking.factor_result", {"item": item_ref, "family": family, "score": score, "weight": weight}),
                "item_ref": item_ref,
                "factor_family": family,
                "score": round(score, 6),
                "weight": weight,
                "weighted_score": round(score * weight, 6),
                "deterministic": True,
                "review_required_before_public_use": True,
            }
        )
    return results


def build_ranking_output_bundle(
    input_bundle: Mapping[str, Any],
    ranking_shadow: Mapping[str, Any],
    identity_shadow: Mapping[str, Any],
    dedup_shadow: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    bundle = {
        "schema_version": "ranking_output_bundle.v0",
        "ranking_output_bundle_id": stable_id("ranking.output", ranking_shadow.get("ranking_shadow_id")),
        "output_status": "local_shadow",
        "input_bundle_ref": input_bundle.get("ranking_input_bundle_id"),
        "ranking_shadow_result": dict(ranking_shadow),
        "factor_results": list(ranking_shadow.get("factor_results", [])),
        "identity_merge_shadows": [dict(identity_shadow)],
        "dedup_shadow_results": [dict(dedup_shadow)],
        "explanation_refs": list(input_bundle.get("explanation_refs", [])),
        "quality_regression_refs": [],
        "public_ranking_gate_refs": [],
        "no_claims": {
            "public_ranking_changed": False,
            "public_search_changed": False,
            "evidence_accepted": False,
            "candidate_accepted": False,
            "production_quality_claimed": False,
        },
        "truth_boundary": ranking_truth_boundary(),
        "product_boundary": ranking_product_boundary(),
        "limitations": ["Ranking output bundle is fixture-only and shadow-only."],
    }
    violations = detect_truth_or_product_violations(bundle)
    if violations:
        raise ValueError("; ".join(violations))
    return bundle


def validate_ranking_shadow_result(result: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    violations = detect_ranking_truth_boundary_violations(result, policy)
    if violations:
        raise ValueError("; ".join(violations))
    return dict(result)


def summarize_ranking_shadow(result: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return {
        "schema_version": "ranking_shadow_summary.v0",
        "ranking_shadow_id": result.get("ranking_shadow_id"),
        "ranking_shadow_status": result.get("ranking_shadow_status"),
        "ranked_item_count": len(result.get("ranked_items", [])),
        "factor_result_count": len(result.get("factor_results", [])),
        "top_item_ref": (result.get("ranked_items") or [{}])[0].get("item_ref"),
        "public_ranking_mutated": False,
        "public_search_mutated": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
    }


def detect_ranking_truth_boundary_violations(result: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    return detect_truth_or_product_violations(result)
