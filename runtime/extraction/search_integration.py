"""Fixture-only extraction search integration previews."""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from typing import Any

from runtime.extraction.candidate_effects import build_extraction_candidate_effects
from runtime.extraction.guards import detect_truth_or_product_violations, load_json, stable_id
from runtime.extraction.review_bridge import (
    build_extraction_evidence_candidate_preview,
    build_extraction_review_seed,
    build_extraction_source_cache_candidate_preview,
    extraction_search_product_boundary,
    extraction_search_truth_boundary,
)
from runtime.extraction.workunit_seeds import build_extraction_workunit_seed


def load_extraction_search_policy(root: Any | None = None) -> dict[str, Any]:
    from runtime.extraction.guards import REPO_ROOT

    repo_root = REPO_ROOT if root is None else root
    policy_root = repo_root / "control" / "inventory" / "extraction"
    names = [
        "extraction_search_integration_policy",
        "extraction_search_gap_policy",
        "extraction_review_seed_policy",
        "extraction_workunit_seed_policy",
        "extraction_candidate_effect_policy",
        "extraction_search_output_policy",
        "extraction_search_truth_policy",
        "extraction_to_track_g_handoff_policy",
    ]
    bundle = {name: load_json(policy_root / f"{name}.json") for name in names}
    integration_policy = bundle["extraction_search_integration_policy"]
    return {
        "schema_version": "extraction_search_policy_bundle.v0",
        **bundle,
        "allowed_input_roots": integration_policy.get("allowed_input_roots", ["examples/extraction/results", "explicit temp test directory"]),
        "allowed_output_roots": integration_policy.get("allowed_output_roots", []),
        "forbidden_output_roots": integration_policy.get("forbidden_output_roots", []),
    }


def build_extraction_search_gap(extraction_result: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    gaps: list[dict[str, Any]] = []
    members = [item for item in extraction_result.get("member_listing", []) if isinstance(item, Mapping) and not item.get("blocked")]
    blocked_members = [item for item in extraction_result.get("blocked_members", []) if isinstance(item, Mapping)]
    manifests = [item for item in extraction_result.get("manifest_candidates", []) if isinstance(item, Mapping)]
    if extraction_result.get("extraction_status", "").startswith("blocked"):
        gaps.append(_gap("policy_blocked_extraction_gap", extraction_result, blocked_members, [], "Policy blocked extraction details; review policy before deeper work."))
    if manifests:
        gaps.append(_gap("manifest_not_indexed", extraction_result, [], manifests[:8], "Manifest-like fixture metadata can seed reviewable search gaps."))
    if members:
        gaps.append(_gap("hidden_member_not_indexed", extraction_result, members[:8], [], "Member listing reveals fixture members not visible from outer metadata."))
    if not gaps:
        gaps.append(_gap("archive_outer_metadata_insufficient", extraction_result, [], [], "Outer metadata alone does not explain member-level relevance."))
    for gap in gaps:
        detect_search_integration_truth_boundary_violations(gap, policy)
    return gaps


def build_local_search_preview_from_extraction(extraction_result: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    member_names = [
        str(item.get("normalized_member_path"))
        for item in extraction_result.get("member_listing", [])
        if isinstance(item, Mapping) and item.get("normalized_member_path") and not item.get("blocked")
    ]
    manifest_names = [
        str(item.get("manifest_name"))
        for item in extraction_result.get("manifest_candidates", [])
        if isinstance(item, Mapping) and item.get("manifest_name")
    ]
    return {
        "schema_version": "extraction_local_search_preview.v0",
        "preview_id": stable_id("extraction.local_search_preview", extraction_result.get("extraction_result_id")),
        "extraction_result_ref": extraction_result.get("extraction_result_id"),
        "preview_terms": sorted(set(member_names + manifest_names)),
        "search_gap_count": len(build_extraction_search_gap(extraction_result, policy)),
        "public_search_mutated": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "limitations": ["Local search preview is not wired into public search behavior."],
        "truth_boundary": extraction_search_truth_boundary(),
        "product_boundary": extraction_search_product_boundary(),
    }


def build_extraction_search_integration(
    extraction_results: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    results = [dict(item) for item in extraction_results]
    candidate_effects = [
        effect
        for result in results
        for effect in (result.get("candidate_effects") or build_extraction_candidate_effects(result, policy))
        if isinstance(effect, Mapping)
    ]
    search_gaps = [gap for result in results for gap in build_extraction_search_gap(result, policy)]
    review_seeds = [build_extraction_review_seed(effect, policy) for effect in candidate_effects]
    workunit_seeds = _workunit_seeds(results, policy)
    source_cache_previews = [build_extraction_source_cache_candidate_preview(effect, policy) for effect in candidate_effects]
    evidence_previews = [build_extraction_evidence_candidate_preview(effect, policy) for effect in candidate_effects]
    local_previews = [build_local_search_preview_from_extraction(result, policy) for result in results]
    status = "local_dry_run" if results else "not_evaluable"
    if results and all(str(item.get("extraction_status", "")).startswith("blocked") for item in results):
        status = "blocked_by_policy"
    integration = {
        "schema_version": "extraction_search_integration.v0",
        "integration_id": stable_id("extraction.search_integration", [item.get("extraction_result_id") for item in results]),
        "integration_status": status,
        "extraction_result_refs": [item.get("extraction_result_id") for item in results],
        "candidate_effect_refs": [item.get("candidate_effect_id") for item in candidate_effects],
        "search_gap_refs": [item.get("search_gap_id") for item in search_gaps],
        "search_gaps": search_gaps,
        "review_seed_refs": [item.get("review_seed_id") for item in review_seeds],
        "review_seeds": review_seeds,
        "workunit_seed_refs": [item.get("workunit_seed_id") for item in workunit_seeds],
        "workunit_seeds": workunit_seeds,
        "source_cache_candidate_previews": source_cache_previews,
        "evidence_candidate_previews": evidence_previews,
        "local_search_preview": {
            "previews": local_previews,
            "public_search_mutated": False,
            "public_index_mutated": False,
            "master_index_mutated": False,
        },
        "limitations": ["Integration is an offline fixture dry-run and does not mutate search or review stores."],
        "review_gates": {
            "human_review_required": True,
            "candidate_store_review_required": True,
            "evidence_review_required": True,
            "public_index_review_required": True,
            "master_index_review_required": True,
        },
        "truth_boundary": {
            **extraction_search_truth_boundary(),
            "integration_mutates_public_search": False,
            "integration_mutates_public_index": False,
            "integration_mutates_master_index": False,
            "integration_accepts_evidence": False,
            "integration_accepts_candidates": False,
        },
        "product_boundary": extraction_search_product_boundary(),
        "notes": ["Extraction search integration creates reviewable gaps and seeds only."],
    }
    detect_search_integration_truth_boundary_violations(integration, policy)
    return integration


def detect_search_integration_truth_boundary_violations(record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    violations = detect_truth_or_product_violations(record)
    if violations:
        raise ValueError("; ".join(violations))
    return []


def summarize_extraction_search_integration(record: Mapping[str, Any]) -> dict[str, Any]:
    gap_types = Counter(str(item.get("gap_type", "unknown")) for item in record.get("search_gaps", []))
    return {
        "schema_version": "extraction_search_integration_summary.v0",
        "integration_id": record.get("integration_id"),
        "integration_status": record.get("integration_status"),
        "extraction_result_count": len(record.get("extraction_result_refs", [])),
        "candidate_effect_count": len(record.get("candidate_effect_refs", [])),
        "search_gap_count": len(record.get("search_gap_refs", [])),
        "review_seed_count": len(record.get("review_seed_refs", [])),
        "workunit_seed_count": len(record.get("workunit_seed_refs", [])),
        "gap_type_counts": dict(sorted(gap_types.items())),
        "public_search_mutated": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
    }


def _gap(
    gap_type: str,
    extraction_result: Mapping[str, Any],
    members: Sequence[Mapping[str, Any]],
    manifests: Sequence[Mapping[str, Any]],
    why: str,
) -> dict[str, Any]:
    result_ref = str(extraction_result.get("extraction_result_id", "unknown_result"))
    member_refs = [str(item.get("normalized_member_path") or item.get("member_ref")) for item in members if item]
    manifest_refs = [str(item.get("manifest_candidate_id") or item.get("manifest_name")) for item in manifests if item]
    return {
        "schema_version": "extraction_search_gap.v0",
        "search_gap_id": stable_id("extraction.search_gap", {"result": result_ref, "type": gap_type, "members": member_refs, "manifests": manifest_refs}),
        "search_gap_status": "fixture_preview" if gap_type != "policy_blocked_extraction_gap" else "policy_blocked",
        "related_search_need_refs": ["search_need.extraction_visibility.fixture.v0"],
        "related_query_observation_refs": [],
        "related_search_miss_refs": [],
        "extraction_result_ref": result_ref,
        "member_refs": member_refs,
        "manifest_refs": manifest_refs,
        "gap_type": gap_type,
        "gap_summary": f"{gap_type} from {extraction_result.get('target_ref', result_ref)}",
        "why_extraction_matters": why,
        "candidate_resolution_path": "human_review_then_future_search_gap_resolution",
        "recommended_next_action": "request_human_review" if gap_type != "policy_blocked_extraction_gap" else "policy_review_future",
        "limitations": [
            "Search gap is a fixture-only preview.",
            "No exhaustive absence or public search quality claim is made.",
        ],
        "truth_boundary": extraction_search_truth_boundary(),
        "product_boundary": extraction_search_product_boundary(),
    }


def _workunit_seeds(results: Sequence[Mapping[str, Any]], policy: Mapping[str, Any] | None) -> list[dict[str, Any]]:
    seeds: list[dict[str, Any]] = []
    for result in results:
        if str(result.get("extraction_status", "")).startswith("blocked"):
            seeds.append(build_extraction_workunit_seed(result, None, policy))
        elif not result.get("member_listing") and not result.get("manifest_candidates"):
            seeds.append(build_extraction_workunit_seed(result, None, policy))
        for manifest in result.get("manifest_candidates", []):
            if isinstance(manifest, Mapping):
                seeds.append(build_extraction_workunit_seed(result, manifest, policy))
        for member in result.get("member_listing", []):
            if isinstance(member, Mapping) and not member.get("blocked"):
                seeds.append(build_extraction_workunit_seed(result, member, policy))
    return seeds
