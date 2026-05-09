"""Candidate-effect previews from extraction results."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from runtime.extraction.guards import product_boundary, stable_id, truth_boundary


def build_extraction_candidate_effects(result: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    effects: list[dict[str, Any]] = []
    members = [item for item in result.get("member_listing", []) if isinstance(item, Mapping) and not item.get("blocked")]
    manifests = [item for item in result.get("manifest_candidates", []) if isinstance(item, Mapping)]
    if members:
        effects.append(_effect("member_candidate", "container_member_listing", result, members[:8], []))
    if manifests:
        effects.append(_effect("manifest_candidate", "manifest_metadata", result, [], manifests[:8]))
    if result.get("extraction_status", "").startswith("blocked"):
        effects.append(_effect("extraction_gap_candidate", "policy_blocked_extraction_gap", result, result.get("blocked_members", []), []))
    return effects


def _effect(
    effect_type: str,
    candidate_type: str,
    result: Mapping[str, Any],
    members: list[Any],
    manifests: list[Any],
) -> dict[str, Any]:
    target_ref = result.get("target_ref", "unknown_target")
    effect_id = stable_id("extraction.candidate_effect", {"effect_type": effect_type, "target": target_ref})
    return {
        "schema_version": "extraction_candidate_effect.v0",
        "candidate_effect_id": effect_id,
        "extraction_result_ref": result.get("extraction_result_id"),
        "effect_type": effect_type,
        "candidate_type": candidate_type,
        "candidate_summary": f"{effect_type} preview for {target_ref}",
        "related_member_refs": [item.get("normalized_member_path", item.get("member_ref")) for item in members if isinstance(item, Mapping)],
        "related_manifest_refs": [item.get("manifest_candidate_id") for item in manifests if isinstance(item, Mapping)],
        "source_cache_candidate_preview": {
            "candidate_id": stable_id("extraction.source_cache_preview", effect_id),
            "accepted_source_truth": False,
            "source_cache_mutated": False,
        },
        "evidence_candidate_preview": {
            "evidence_preview_id": stable_id("extraction.evidence_preview", effect_id),
            "accepted_evidence": False,
            "evidence_ledger_mutated": False,
        },
        "review_seed_preview": {
            "review_seed_id": stable_id("extraction.review_seed", effect_id),
            "review_required": True,
            "review_queue_mutated": False,
            "review_decision": False,
        },
        "limitations": ["Candidate effect is a preview only and does not accept a candidate."],
        "truth_boundary": truth_boundary(),
        "product_boundary": product_boundary(),
    }
