"""Fixture-only result explanations.

The helpers in this package build explanation records from explicit local
fixtures. They do not mutate ranking, search runtime, indexes, stores, or
truth state.
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from runtime.extraction.guards import REPO_ROOT, detect_truth_or_product_violations, load_json, stable_id


POLICY_ROOT = REPO_ROOT / "control" / "inventory" / "search_quality"


def load_search_quality_policy(root: Path | None = None) -> dict[str, Any]:
    repo_root = REPO_ROOT if root is None else root
    policy_root = repo_root / "control" / "inventory" / "search_quality"
    names = [
        "search_explanation_policy",
        "near_miss_policy",
        "known_absence_policy",
        "search_gap_explanation_policy",
        "explanation_output_policy",
        "explanation_path_policy",
        "explanation_truth_policy",
        "explanation_review_policy",
    ]
    bundle = {name: load_json(policy_root / f"{name}.json") for name in names}
    path_policy = bundle["explanation_path_policy"]
    return {
        "schema_version": "search_quality_policy_bundle.v0",
        **bundle,
        "allowed_input_roots": path_policy.get("allowed_input_roots", []),
        "allowed_output_roots": path_policy.get("allowed_output_roots", []),
        "forbidden_output_roots": path_policy.get("forbidden_output_roots", []),
    }


def explanation_truth_boundary() -> dict[str, bool]:
    return {
        "explanation_accepts_result_as_truth": False,
        "explanation_accepts_evidence": False,
        "explanation_accepts_candidate": False,
        "explanation_mutates_ranking": False,
        "explanation_mutates_public_search": False,
        "explanation_mutates_public_index": False,
        "explanation_mutates_master_index": False,
        "known_absence_claims_global_absence": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "rights_clearance_claimed": False,
        "malware_safety_claimed": False,
        "verified_installability_claimed": False,
        "production_quality_claimed": False,
    }


def explanation_product_boundary() -> dict[str, bool]:
    return {
        "changed_public_search_behavior": False,
        "changed_ranking_behavior": False,
        "enabled_hosting": False,
        "enabled_source_sync": False,
        "enabled_downloads": False,
        "enabled_uploads": False,
        "enabled_accounts": False,
        "enabled_telemetry": False,
        "enabled_model_provider_calls": False,
        "mutated_public_index": False,
        "mutated_master_index": False,
    }


def build_search_result_explanation(input_bundle: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    candidates = _records(input_bundle, "candidate_records")
    source_cache = _records(input_bundle, "source_cache_records")
    evidence = _records(input_bundle, "evidence_records")
    gaps = _records(input_bundle, "extraction_search_gaps")
    if candidates:
        return explain_candidate_result(candidates[0], input_bundle, policy)
    if source_cache:
        return explain_source_cache_supported_result(source_cache[0], input_bundle, policy)
    if evidence:
        return explain_evidence_supported_result(evidence[0], input_bundle, policy)
    if gaps:
        return explain_extraction_member_result(gaps[0], input_bundle, policy)
    explanation = _base_explanation(
        "not_evaluable",
        _query_ref(input_bundle),
        "none",
        "not_evaluable",
        "No explicit fixture result was present to explain.",
    )
    explanation["limitation_reasons"].append("Input bundle did not include candidate, source-cache, evidence, or extraction-gap records.")
    return validate_search_result_explanation(explanation, policy)


def explain_candidate_result(candidate: Mapping[str, Any], input_bundle: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    result_ref = str(candidate.get("candidate_id", "candidate.unknown.v0"))
    summary = candidate.get("candidate_label") or candidate.get("candidate_summary") or "Candidate fixture result is reviewable."
    explanation = _base_explanation(
        "local_dry_run",
        _query_ref(input_bundle),
        result_ref,
        "candidate_record",
        f"Candidate appears because the fixture candidate matches the requested object fields: {summary}",
    )
    proposed = candidate.get("proposed_object_summary", {})
    explanation["match_reasons"] = _object_match_reasons(proposed)
    explanation["candidate_reasons"] = [
        {
            "candidate_ref": result_ref,
            "candidate_status": candidate.get("candidate_status", "candidate"),
            "reason": "Candidate is included as a provisional fixture result only.",
        }
    ]
    explanation["missing_evidence"] = ["accepted_evidence_review", "human_candidate_review"]
    explanation["confidence_or_uncertainty"] = candidate.get("confidence_or_uncertainty", "low_confidence_review_required")
    return validate_search_result_explanation(explanation, policy)


def explain_source_cache_supported_result(source_cache_record: Mapping[str, Any], input_bundle: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    result_ref = str(source_cache_record.get("source_cache_record_id") or source_cache_record.get("source_cache_id") or "source_cache.unknown.v0")
    explanation = _base_explanation(
        "local_dry_run",
        _query_ref(input_bundle),
        result_ref,
        "source_cache_record",
        "Source-cache fixture metadata can explain why this local result is visible.",
    )
    explanation["source_reasons"] = [
        {
            "source_cache_ref": result_ref,
            "reason": source_cache_record.get("input_summary") or source_cache_record.get("observation_summary") or "Fixture source metadata is present.",
        }
    ]
    explanation["missing_evidence"] = ["source_cache_review", "evidence_acceptance_review"]
    return validate_search_result_explanation(explanation, policy)


def explain_evidence_supported_result(evidence_record: Mapping[str, Any], input_bundle: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    result_ref = str(evidence_record.get("evidence_record_id", "evidence.unknown.v0"))
    explanation = _base_explanation(
        "evidence_supported_candidate",
        _query_ref(input_bundle),
        result_ref,
        "evidence_record",
        "Evidence fixture can support a candidate explanation after review, but is not accepted evidence here.",
    )
    explanation["evidence_reasons"] = [
        {
            "evidence_ref": result_ref,
            "claim_type": evidence_record.get("claim_type", "metadata"),
            "reason": evidence_record.get("claim_summary") or evidence_record.get("observation_summary") or "Fixture evidence record is present.",
        }
    ]
    explanation["missing_evidence"] = ["human_evidence_review", "conflict_review"]
    return validate_search_result_explanation(explanation, policy)


def explain_extraction_member_result(extraction_gap: Mapping[str, Any], input_bundle: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    result_ref = str(extraction_gap.get("search_gap_id", "extraction.search_gap.unknown.v0"))
    status = "policy_blocked" if extraction_gap.get("gap_type") == "policy_blocked_extraction_gap" else "local_dry_run"
    explanation = _base_explanation(
        status,
        _query_ref(input_bundle),
        result_ref,
        "extraction_search_gap",
        "Extraction-derived gap explains why member or manifest visibility may affect the local result set.",
    )
    explanation["extraction_reasons"] = [
        {
            "search_gap_ref": result_ref,
            "gap_type": extraction_gap.get("gap_type", "not_evaluable"),
            "why_extraction_matters": extraction_gap.get("why_extraction_matters", "Extraction gap needs review."),
        }
    ]
    explanation["missing_evidence"] = ["member_relevance_review", "future_deepening_policy_review"]
    return validate_search_result_explanation(explanation, policy)


def validate_search_result_explanation(explanation: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    violations = detect_explanation_truth_boundary_violations(explanation, policy)
    if violations:
        raise ValueError("; ".join(violations))
    required_false = [
        "explanation_accepts_result_as_truth",
        "explanation_accepts_evidence",
        "explanation_accepts_candidate",
        "explanation_mutates_ranking",
        "explanation_mutates_public_search",
        "explanation_mutates_public_index",
        "explanation_mutates_master_index",
    ]
    boundary = explanation.get("truth_boundary", {})
    for key in required_false:
        if boundary.get(key) is not False:
            raise ValueError(f"truth_boundary.{key} must be false")
    return dict(explanation)


def detect_explanation_truth_boundary_violations(explanation: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    return detect_truth_or_product_violations(explanation)


def _base_explanation(status: str, query_ref: str, result_ref: str, result_kind: str, summary: str) -> dict[str, Any]:
    return {
        "schema_version": "search_result_explanation.v0",
        "explanation_id": stable_id("search.explanation", {"query": query_ref, "result": result_ref, "kind": result_kind, "status": status}),
        "explanation_status": status,
        "query_ref": query_ref,
        "result_ref": result_ref,
        "result_kind": result_kind,
        "explanation_summary": summary,
        "match_reasons": [],
        "source_reasons": [],
        "evidence_reasons": [],
        "candidate_reasons": [],
        "extraction_reasons": [],
        "compatibility_reasons": [{"known": False, "reason": "Compatibility requires review before use."}],
        "risk_rights_reasons": [{"known": False, "reason": "Risk and rights posture are unknown until review."}],
        "limitation_reasons": ["Explanation is fixture-only and does not change ranking or search behavior."],
        "missing_evidence": [],
        "review_posture": {
            "human_review_required": True,
            "ranking_use_requires_review": True,
            "public_display_claim_requires_review": True,
        },
        "confidence_or_uncertainty": "low_confidence_review_required",
        "forbidden_claims": [
            "accepted_truth",
            "accepted_evidence",
            "accepted_candidate",
            "rights_clearance",
            "malware_safety",
            "verified_installability",
            "global_absence",
            "production_quality",
        ],
        "truth_boundary": explanation_truth_boundary(),
        "product_boundary": explanation_product_boundary(),
        "notes": ["Explanation is evidence-linked reasoning, not authority."],
    }


def _query_ref(input_bundle: Mapping[str, Any]) -> str:
    refs = input_bundle.get("search_need_refs") or input_bundle.get("query_observation_refs") or input_bundle.get("search_miss_refs") or []
    if isinstance(refs, list) and refs:
        return str(refs[0])
    return str(input_bundle.get("input_bundle_id", "query.fixture.unknown.v0"))


def _records(input_bundle: Mapping[str, Any], key: str) -> list[Mapping[str, Any]]:
    values = input_bundle.get(key, [])
    return [item for item in values if isinstance(item, Mapping)] if isinstance(values, list) else []


def _object_match_reasons(proposed: Any) -> list[dict[str, Any]]:
    if not isinstance(proposed, Mapping):
        return []
    keys = ["object_family", "product_or_topic", "version_or_state", "platform_or_context", "artifact_type"]
    return [
        {"field": key, "value": proposed.get(key), "reason": "Fixture field contributes to local explanation."}
        for key in keys
        if proposed.get(key)
    ]
