"""Review seed previews for extraction candidate effects."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from runtime.extraction.guards import detect_truth_or_product_violations, stable_id


def extraction_search_truth_boundary() -> dict[str, bool]:
    return {
        "extraction_search_gap_is_public_truth": False,
        "review_seed_is_review_decision": False,
        "workunit_seed_executes_work": False,
        "evidence_preview_is_accepted_evidence": False,
        "candidate_preview_is_accepted_candidate": False,
        "public_search_mutated": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "rights_clearance_claimed": False,
        "malware_safety_claimed": False,
        "verified_installability_claimed": False,
        "production_quality_claimed": False,
    }


def extraction_search_product_boundary() -> dict[str, bool]:
    return {
        "changed_public_search_behavior": False,
        "enabled_hosting": False,
        "enabled_source_sync": False,
        "enabled_downloads": False,
        "enabled_execution": False,
        "enabled_uploads": False,
        "enabled_accounts": False,
        "enabled_telemetry": False,
        "mutated_public_index": False,
        "mutated_master_index": False,
    }


def build_extraction_source_cache_candidate_preview(
    candidate_effect: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    effect_id = str(candidate_effect.get("candidate_effect_id", "unknown_effect"))
    return {
        "source_cache_candidate_preview_id": stable_id("extraction.source_cache_candidate_preview", effect_id),
        "candidate_effect_ref": effect_id,
        "candidate_type": candidate_effect.get("candidate_type", "unknown"),
        "candidate_summary": candidate_effect.get("candidate_summary", "Extraction candidate preview."),
        "source_cache_mutated": False,
        "accepted_source_truth": False,
        "review_required": True,
        "limitations": ["Source-cache candidate preview only; no source cache write occurred."],
        "truth_boundary": extraction_search_truth_boundary(),
        "product_boundary": extraction_search_product_boundary(),
    }


def build_extraction_evidence_candidate_preview(
    candidate_effect: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    effect_id = str(candidate_effect.get("candidate_effect_id", "unknown_effect"))
    return {
        "evidence_candidate_preview_id": stable_id("extraction.evidence_candidate_preview", effect_id),
        "candidate_effect_ref": effect_id,
        "evidence_summary": candidate_effect.get("candidate_summary", "Extraction evidence preview."),
        "evidence_ledger_mutated": False,
        "evidence_preview_is_accepted_evidence": False,
        "review_required": True,
        "limitations": ["Evidence candidate preview only; no evidence ledger acceptance occurred."],
        "truth_boundary": extraction_search_truth_boundary(),
        "product_boundary": extraction_search_product_boundary(),
    }


def build_extraction_review_seed(
    candidate_effect: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    effect_id = str(candidate_effect.get("candidate_effect_id", "unknown_effect"))
    effect_type = str(candidate_effect.get("effect_type", "extraction_gap_candidate"))
    subject_type = {
        "member_candidate": "extraction_member_candidate",
        "manifest_candidate": "extraction_manifest_candidate",
        "extraction_gap_candidate": "extraction_policy_gap",
    }.get(effect_type, "extraction_candidate_effect")
    seed = {
        "schema_version": "extraction_review_seed.v0",
        "review_seed_id": stable_id("extraction.review_seed", {"effect": effect_id, "type": subject_type}),
        "review_seed_status": "fixture_preview",
        "subject_type": subject_type,
        "subject_ref": effect_id,
        "review_reason": f"Review {effect_type} before any downstream use.",
        "proposed_review_subject": {
            "effect_type": effect_type,
            "candidate_type": candidate_effect.get("candidate_type", "unknown"),
            "related_member_refs": list(candidate_effect.get("related_member_refs", [])),
            "related_manifest_refs": list(candidate_effect.get("related_manifest_refs", [])),
        },
        "evidence_candidate_preview": build_extraction_evidence_candidate_preview(candidate_effect, policy),
        "source_cache_candidate_preview": build_extraction_source_cache_candidate_preview(candidate_effect, policy),
        "missing_evidence": ["human_review", "source_context_review"],
        "blockers": [] if effect_type != "extraction_gap_candidate" else ["policy_blocked_extraction"],
        "limitations": ["Review seed is not a review decision and does not mutate the review queue."],
        "truth_boundary": extraction_search_truth_boundary(),
        "product_boundary": extraction_search_product_boundary(),
    }
    validate_extraction_review_seed(seed, policy)
    return seed


def validate_extraction_review_seed(seed: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> bool:
    violations = detect_truth_or_product_violations(seed)
    if violations:
        raise ValueError("; ".join(violations))
    if seed.get("truth_boundary", {}).get("review_seed_is_review_decision") is not False:
        raise ValueError("review_seed_is_review_decision must be false")
    return True
