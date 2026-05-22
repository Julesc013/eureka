"""Offline H7 library/cultural/research quality delta helpers."""

from __future__ import annotations

from collections.abc import Mapping
import hashlib
import json
from typing import Any

from archive.prototypes.legacy_runtime.connectors.h7_library_research.normalizer_common import H7_SOURCE_IDS
from archive.prototypes.legacy_runtime.connectors.h7_library_research.review_integration import (
    detect_h7_review_product_boundary_violations,
    detect_h7_review_truth_boundary_violations,
)


FORBIDDEN_TRUE_KEYS = {
    "access_rights_verified",
    "automatic_future_connector_approval",
    "bibliographic_completeness_verified",
    "citation_correctness_verified",
    "cultural_object_truth_verified",
    "dataset_validity_verified",
    "exhaustive_global_coverage",
    "future_connector_auto_approval",
    "malware_safety",
    "malware_safety_claimed",
    "open_access_truth",
    "open_access_truth_claimed",
    "open_access_truth_verified",
    "patent_validity_verified",
    "privacy_safety",
    "privacy_safety_claimed",
    "production_library_research_coverage",
    "production_readiness_claimed",
    "production_search_quality",
    "research_work_identity_verified",
    "rights_clearance",
    "rights_clearance_claimed",
    "verified_availability",
    "verified_availability_claimed",
}


def build_h7_quality_delta(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    review = dict(inputs.get("review_integration_result") or inputs)
    sources = list(review.get("sources") or [])
    blocked_sources = list(review.get("blocked_sources") or [])
    fixture_outputs = list(review.get("used_fixture_outputs") or [])
    live_outputs = list(review.get("used_live_probe_outputs") or [])
    known_gaps = _known_gaps(review)
    metrics = {
        "source_count": len(sources) or len(H7_SOURCE_IDS),
        "fixture_sources_count": len({item.get("source_id") for item in fixture_outputs if item.get("source_id")}) or len(sources),
        "live_probe_sources_count": len({item.get("source_id") for item in live_outputs if item.get("status") == "live_probe_completed"}),
        "blocked_sources_count": len(blocked_sources),
        "normalized_record_count": len(review.get("source_cache_review_seeds", [])),
        "bibliographic_identity_candidate_count": len(review.get("bibliographic_identity_review_seeds", [])),
        "research_work_identity_candidate_count": len(review.get("research_work_identity_review_seeds", [])),
        "dataset_identity_candidate_count": len(review.get("dataset_identity_review_seeds", [])),
        "cultural_object_identity_candidate_count": len(review.get("cultural_object_identity_review_seeds", [])),
        "patent_identity_candidate_count": len(review.get("patent_identity_review_seeds", [])),
        "citation_relation_candidate_count": len(review.get("citation_relation_review_seeds", [])),
        "access_rights_availability_candidate_count": len(review.get("access_rights_availability_review_seeds", [])),
        "source_cache_candidate_count": len(review.get("source_cache_review_seeds", [])),
        "evidence_candidate_preview_count": len(review.get("evidence_candidate_review_seeds", [])),
        "review_seed_count": sum(len(review.get(key, [])) for key in (
            "bibliographic_identity_review_seeds",
            "research_work_identity_review_seeds",
            "dataset_identity_review_seeds",
            "cultural_object_identity_review_seeds",
            "patent_identity_review_seeds",
            "citation_relation_review_seeds",
            "access_rights_availability_review_seeds",
            "source_cache_review_seeds",
            "evidence_candidate_review_seeds",
        )),
        "coverage_preview_count": len(review.get("coverage_update_previews", [])),
        "scorecard_update_count": len(review.get("scorecard_updates", [])),
        "known_gap_count": len(known_gaps),
        "blocker_count": 0,
        "warning_count": len(review.get("warnings", [])) + (1 if blocked_sources else 0),
    }
    delta = {
        "schema_version": "h7_library_research_quality_delta_report.v0",
        "quality_delta_id": f"h7.quality_delta.{_digest(review)[:12]}.v0",
        "wave_id": "H7",
        "comparison_scope": "fixture_review_and_blocked_live_probe_evidence",
        **metrics,
        "per_source_deltas": [_per_source_delta(source_id, review, fixture_outputs, live_outputs, blocked_sources) for source_id in sorted(set(sources) or set(H7_SOURCE_IDS))],
        "limitations": [
            "Quality delta measures H7 review readiness only.",
            "Blocked live probes do not prove endpoint behavior.",
            "Library/cultural/research metadata is not bibliographic completeness, citation correctness, research work truth, dataset validity, cultural object truth, patent validity, access rights, rights clearance, open-access truth, privacy safety, malware safety, verified availability, or production coverage proof.",
        ],
        "forbidden_claims": [
            "production_search_quality",
            "production_library_research_coverage",
            "exhaustive_global_coverage",
            "bibliographic_completeness_verified",
            "research_work_identity_verified",
            "dataset_validity_verified",
            "cultural_object_truth_verified",
            "patent_validity_verified",
            "citation_correctness_verified",
            "access_rights_verified",
            "open_access_truth_verified",
            "rights_clearance",
            "privacy_safety",
            "malware_safety",
            "verified_availability",
            "automatic_future_connector_approval",
        ],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["H7 quality delta is operational review evidence only."],
    }
    errors = detect_h7_quality_overclaim(delta, policy)
    if errors:
        raise ValueError("; ".join(errors))
    return delta


def summarize_h7_quality_delta(delta: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    errors = detect_h7_quality_overclaim(delta, policy)
    return {
        "schema_version": "h7_quality_delta_summary.v0",
        "status": "pass" if not errors else "invalid",
        "quality_delta_id": delta.get("quality_delta_id"),
        "source_count": delta.get("source_count", 0),
        "fixture_sources_count": delta.get("fixture_sources_count", 0),
        "live_probe_sources_count": delta.get("live_probe_sources_count", 0),
        "blocked_sources_count": delta.get("blocked_sources_count", 0),
        "bibliographic_identity_candidate_count": delta.get("bibliographic_identity_candidate_count", 0),
        "research_work_identity_candidate_count": delta.get("research_work_identity_candidate_count", 0),
        "dataset_identity_candidate_count": delta.get("dataset_identity_candidate_count", 0),
        "cultural_object_identity_candidate_count": delta.get("cultural_object_identity_candidate_count", 0),
        "patent_identity_candidate_count": delta.get("patent_identity_candidate_count", 0),
        "citation_relation_candidate_count": delta.get("citation_relation_candidate_count", 0),
        "access_rights_availability_candidate_count": delta.get("access_rights_availability_candidate_count", 0),
        "review_seed_count": delta.get("review_seed_count", 0),
        "known_gap_count": delta.get("known_gap_count", 0),
        "blocker_count": delta.get("blocker_count", 0),
        "claims_bibliographic_completeness_verified": False,
        "claims_citation_correctness_verified": False,
        "claims_rights_clearance": False,
        "claims_open_access_truth": False,
        "claims_privacy_safety": False,
        "claims_malware_safety": False,
        "claims_verified_availability": False,
        "claims_production_readiness": False,
        "overclaim_errors": errors,
    }


def detect_h7_quality_overclaim(delta: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    errors = [f"quality overclaim: {path}=true" for path, key, value in _iter_key_values(delta) if key in FORBIDDEN_TRUE_KEYS and value is True]
    errors.extend(detect_h7_review_truth_boundary_violations(delta, policy))
    errors.extend(detect_h7_review_product_boundary_violations(delta, policy))
    return sorted(dict.fromkeys(errors))


def _per_source_delta(source_id: str, review: Mapping[str, Any], fixture_outputs: list[Mapping[str, Any]], live_outputs: list[Mapping[str, Any]], blocked_sources: list[str]) -> dict[str, Any]:
    represented = source_id in review.get("sources", [])
    return {
        "source_id": source_id,
        "fixture_output_integrated": any(item.get("source_id") == source_id for item in fixture_outputs) or represented,
        "live_probe_completed": any(item.get("source_id") == source_id and item.get("status") == "live_probe_completed" for item in live_outputs),
        "live_probe_blocked": source_id in blocked_sources,
        "bibliographic_identity_review_seed_created": represented,
        "research_work_identity_review_seed_created": represented,
        "dataset_identity_review_seed_created": represented,
        "cultural_object_identity_review_seed_created": represented,
        "patent_identity_review_seed_created": represented,
        "citation_relation_review_seed_created": represented,
        "access_rights_availability_review_seed_created": represented,
        "source_cache_review_seed_created": represented,
        "evidence_review_seed_created": represented,
        "limitations": ["Fixture/local review only; not accepted source, evidence, bibliographic, research work, dataset, cultural object, patent, citation, access-rights, rights, availability, or production proof."],
    }


def _known_gaps(review: Mapping[str, Any]) -> list[str]:
    gaps: list[str] = []
    if review.get("blocked_sources"):
        gaps.append("operator_approval_missing_for_live_metadata_probes")
    if len(review.get("source_cache_review_seeds", [])) < len(H7_SOURCE_IDS):
        gaps.append("not_all_sources_have_review_seeds")
    if not any(item.get("status") == "live_probe_completed" for item in review.get("used_live_probe_outputs", [])):
        gaps.append("approved_live_probe_outputs_not_available")
    return sorted(dict.fromkeys(gaps))


def _truth_boundary() -> dict[str, bool]:
    return {
        "quality_delta_is_public_truth": False,
        "production_search_quality": False,
        "production_library_research_coverage": False,
        "exhaustive_global_coverage": False,
        "bibliographic_completeness_verified": False,
        "research_work_identity_verified": False,
        "dataset_validity_verified": False,
        "cultural_object_truth_verified": False,
        "patent_validity_verified": False,
        "citation_correctness_verified": False,
        "access_rights_verified": False,
        "rights_clearance_claimed": False,
        "open_access_truth_claimed": False,
        "privacy_safety_claimed": False,
        "malware_safety_claimed": False,
        "verified_availability_claimed": False,
        "production_readiness_claimed": False,
        "automatic_future_connector_approval": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
    }


def _product_boundary() -> dict[str, bool]:
    return {
        "changed_public_search_behavior": False,
        "enabled_hosting": False,
        "enabled_source_sync": False,
        "enabled_harvesting": False,
        "enabled_downloads": False,
        "enabled_crawling": False,
        "enabled_uploads": False,
        "enabled_accounts": False,
        "enabled_telemetry": False,
        "mutated_public_index": False,
        "mutated_master_index": False,
    }


def _iter_key_values(value: Any, prefix: str = ""):
    if isinstance(value, Mapping):
        for key, inner in value.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            yield path, str(key), inner
            yield from _iter_key_values(inner, path)
    elif isinstance(value, list):
        for index, inner in enumerate(value):
            yield from _iter_key_values(inner, f"{prefix}[{index}]")


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, default=str).encode("utf-8")).hexdigest()
