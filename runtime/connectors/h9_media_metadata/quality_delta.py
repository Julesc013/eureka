"""Offline H9 media metadata quality delta helpers."""

from __future__ import annotations

from collections.abc import Mapping
import hashlib
import json
from typing import Any

from runtime.connectors.h9_media_metadata.normalizer_common import H9_SOURCE_IDS
from runtime.connectors.h9_media_metadata.review_integration import (
    detect_h9_review_product_boundary_violations,
    detect_h9_review_truth_boundary_violations,
)

FORBIDDEN_TRUE_KEYS = {
    "attribution_correctness_verified", "audio_identity_verified",
    "automatic_future_connector_approval", "content_safety_verified",
    "creative_commons_truth_verified", "exhaustive_global_coverage",
    "fingerprint_identity_verified", "future_connector_auto_approval",
    "image_identity_verified", "license_correctness_verified",
    "malware_safety", "malware_safety_claimed", "media_authenticity_verified",
    "privacy_safety_verified", "production_media_coverage",
    "production_readiness_claimed", "production_search_quality",
    "public_domain_truth_verified", "rights_clearance", "rights_clearance_claimed",
    "verified_authenticity", "verified_authenticity_claimed",
}


def build_h9_quality_delta(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    review = dict(inputs.get("review_integration_result") or inputs)
    sources = list(review.get("sources") or [])
    blocked_sources = list(review.get("blocked_sources") or [])
    fixture_outputs = list(review.get("used_fixture_outputs") or [])
    live_outputs = list(review.get("used_live_probe_outputs") or [])
    known_gaps = _known_gaps(review)
    metrics = {
        "source_count": len(sources) or len(H9_SOURCE_IDS),
        "fixture_sources_count": len({item.get("source_id") for item in fixture_outputs if item.get("source_id")}) or len(sources),
        "live_probe_sources_count": len({item.get("source_id") for item in live_outputs if item.get("status") == "live_probe_completed"}),
        "blocked_sources_count": len(blocked_sources),
        "normalized_record_count": len(review.get("source_cache_review_seeds", [])),
        "media_object_identity_candidate_count": len(review.get("media_object_identity_review_seeds", [])),
        "music_work_recording_release_candidate_count": len(review.get("music_work_recording_release_review_seeds", [])),
        "image_video_map_identity_candidate_count": len(review.get("image_video_map_identity_review_seeds", [])),
        "creator_collection_relation_candidate_count": len(review.get("media_creator_collection_relation_review_seeds", [])),
        "fingerprint_candidate_count": len(review.get("media_fingerprint_review_seeds", [])),
        "rights_license_candidate_count": len(review.get("media_rights_license_review_seeds", [])),
        "safety_privacy_candidate_count": len(review.get("media_safety_privacy_review_seeds", [])),
        "source_cache_candidate_count": len(review.get("source_cache_review_seeds", [])),
        "evidence_candidate_preview_count": len(review.get("evidence_candidate_review_seeds", [])),
        "review_seed_count": sum(len(review.get(key, [])) for key in (
            "media_object_identity_review_seeds", "music_work_recording_release_review_seeds",
            "image_video_map_identity_review_seeds", "media_creator_collection_relation_review_seeds",
            "media_fingerprint_review_seeds", "media_rights_license_review_seeds",
            "media_safety_privacy_review_seeds", "source_cache_review_seeds",
            "evidence_candidate_review_seeds",
        )),
        "coverage_preview_count": len(review.get("coverage_update_previews", [])),
        "scorecard_update_count": len(review.get("scorecard_updates", [])),
        "known_gap_count": len(known_gaps),
        "blocker_count": 0,
        "warning_count": len(review.get("warnings", [])) + (1 if blocked_sources else 0),
    }
    delta = {
        "schema_version": "h9_media_metadata_quality_delta_report.v0",
        "quality_delta_id": f"h9.quality_delta.{_digest(review)[:12]}.v0",
        "wave_id": "H9",
        "comparison_scope": "fixture_review_and_blocked_live_probe_evidence",
        **metrics,
        "per_source_deltas": [_per_source_delta(source_id, review, fixture_outputs, live_outputs, blocked_sources) for source_id in sorted(set(sources) or set(H9_SOURCE_IDS))],
        "limitations": [
            "Quality delta measures H9 review readiness only.",
            "Blocked live probes do not prove endpoint behavior.",
            "Media metadata is not media authenticity, audio identity, image identity, map correctness, rights clearance, public-domain truth, Creative Commons truth, attribution correctness, malware safety, privacy safety, content safety, production coverage, or production quality proof.",
        ],
        "forbidden_claims": [
            "production_search_quality", "production_media_coverage", "exhaustive_global_coverage",
            "media_authenticity_verified", "audio_identity_verified", "image_identity_verified",
            "fingerprint_identity_verified", "rights_clearance", "public_domain_truth_verified",
            "creative_commons_truth_verified", "license_correctness_verified",
            "attribution_correctness_verified", "content_safety_verified", "privacy_safety_verified",
            "malware_safety", "verified_authenticity", "automatic_future_connector_approval",
        ],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["H9 quality delta is operational review evidence only."],
    }
    errors = detect_h9_quality_overclaim(delta, policy)
    if errors:
        raise ValueError("; ".join(errors))
    return delta


def summarize_h9_quality_delta(delta: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    errors = detect_h9_quality_overclaim(delta, policy)
    return {
        "schema_version": "h9_quality_delta_summary.v0",
        "status": "pass" if not errors else "invalid",
        "quality_delta_id": delta.get("quality_delta_id"),
        "source_count": delta.get("source_count", 0),
        "fixture_sources_count": delta.get("fixture_sources_count", 0),
        "live_probe_sources_count": delta.get("live_probe_sources_count", 0),
        "blocked_sources_count": delta.get("blocked_sources_count", 0),
        "media_object_identity_candidate_count": delta.get("media_object_identity_candidate_count", 0),
        "music_work_recording_release_candidate_count": delta.get("music_work_recording_release_candidate_count", 0),
        "image_video_map_identity_candidate_count": delta.get("image_video_map_identity_candidate_count", 0),
        "creator_collection_relation_candidate_count": delta.get("creator_collection_relation_candidate_count", 0),
        "fingerprint_candidate_count": delta.get("fingerprint_candidate_count", 0),
        "rights_license_candidate_count": delta.get("rights_license_candidate_count", 0),
        "safety_privacy_candidate_count": delta.get("safety_privacy_candidate_count", 0),
        "review_seed_count": delta.get("review_seed_count", 0),
        "known_gap_count": delta.get("known_gap_count", 0),
        "blocker_count": delta.get("blocker_count", 0),
        "claims_media_authenticity_verified": False,
        "claims_audio_identity_verified": False,
        "claims_image_identity_verified": False,
        "claims_fingerprint_identity_verified": False,
        "claims_rights_clearance": False,
        "claims_public_domain_truth": False,
        "claims_creative_commons_truth": False,
        "claims_content_safety": False,
        "claims_privacy_safety": False,
        "claims_malware_safety": False,
        "claims_verified_authenticity": False,
        "claims_production_readiness": False,
        "overclaim_errors": errors,
    }


def detect_h9_quality_overclaim(delta: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    errors = [f"quality overclaim: {path}=true" for path, key, value in _iter_key_values(delta) if key in FORBIDDEN_TRUE_KEYS and value is True]
    errors.extend(detect_h9_review_truth_boundary_violations(delta, policy))
    errors.extend(detect_h9_review_product_boundary_violations(delta, policy))
    return sorted(dict.fromkeys(errors))


def _per_source_delta(source_id: str, review: Mapping[str, Any], fixture_outputs: list[Mapping[str, Any]], live_outputs: list[Mapping[str, Any]], blocked_sources: list[str]) -> dict[str, Any]:
    represented = source_id in review.get("sources", [])
    return {
        "source_id": source_id,
        "fixture_output_integrated": any(item.get("source_id") == source_id for item in fixture_outputs) or represented,
        "live_probe_completed": any(item.get("source_id") == source_id and item.get("status") == "live_probe_completed" for item in live_outputs),
        "live_probe_blocked": source_id in blocked_sources,
        "media_object_identity_review_seed_created": represented,
        "music_work_recording_release_review_seed_created": represented,
        "image_video_map_identity_review_seed_created": represented,
        "creator_collection_relation_review_seed_created": represented,
        "fingerprint_review_seed_created": represented,
        "rights_license_review_seed_created": represented,
        "safety_privacy_review_seed_created": represented,
        "source_cache_review_seed_created": represented,
        "evidence_review_seed_created": represented,
        "limitations": ["Fixture/local review only; not accepted source, evidence, candidate, media, music, image/video/map, relation, fingerprint, rights/license, safety/privacy, or production proof."],
    }


def _known_gaps(review: Mapping[str, Any]) -> list[str]:
    gaps: list[str] = []
    if review.get("blocked_sources"):
        gaps.append("operator_approval_missing_for_live_metadata_probes")
    if len(review.get("source_cache_review_seeds", [])) < len(H9_SOURCE_IDS):
        gaps.append("not_all_sources_have_review_seeds")
    if not any(item.get("status") == "live_probe_completed" for item in review.get("used_live_probe_outputs", [])):
        gaps.append("approved_live_probe_outputs_not_available")
    return sorted(dict.fromkeys(gaps))


def _truth_boundary() -> dict[str, bool]:
    return {
        "quality_delta_is_public_truth": False,
        "production_search_quality": False,
        "production_media_coverage": False,
        "exhaustive_global_coverage": False,
        "media_authenticity_verified": False,
        "audio_identity_verified": False,
        "image_identity_verified": False,
        "fingerprint_identity_verified": False,
        "rights_clearance_claimed": False,
        "public_domain_truth_claimed": False,
        "creative_commons_truth_claimed": False,
        "content_safety_claimed": False,
        "privacy_safety_claimed": False,
        "malware_safety_claimed": False,
        "verified_authenticity_claimed": False,
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
        "enabled_downloads": False,
        "enabled_uploads": False,
        "enabled_fingerprinting": False,
        "enabled_crawling": False,
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
