"""Offline H12 retro/community quality delta helpers."""

from __future__ import annotations

from collections.abc import Mapping
import hashlib
import json
from typing import Any

from control.prototypes.legacy_runtime.connectors.h12_retro_community.normalizer_common import H12_SOURCE_IDS
from control.prototypes.legacy_runtime.connectors.h12_retro_community.review_integration import (
    REVIEW_SEED_KEYS,
    detect_h12_review_product_boundary_violations,
    detect_h12_review_truth_boundary_violations,
)

FORBIDDEN_TRUE_KEYS = set(['abandonware_label_is_legal_permission', 'accepted_archive_item_member_truth', 'accepted_candidate_truth', 'accepted_community_review_truth', 'accepted_compatibility_install_truth', 'accepted_evidence_truth', 'accepted_gated_source_access_truth', 'accepted_hash_checksum_truth', 'accepted_ia_wayback_corroboration_truth', 'accepted_platform_version_truth', 'accepted_public_record', 'accepted_retro_software_identity_truth', 'accepted_rights_safety_truth', 'accepted_source_truth', 'accepts_archive_item_member_truth', 'accepts_candidate_truth', 'accepts_community_review_truth', 'accepts_compatibility_install_truth', 'accepts_evidence_truth', 'accepts_gated_source_access_truth', 'accepts_hash_checksum_truth', 'accepts_ia_wayback_corroboration_truth', 'accepts_platform_version_truth', 'accepts_retro_software_identity_truth', 'accepts_rights_safety_truth', 'accepts_source_truth', 'archive_item_member_seed_accepts_file_truth', 'archive_item_member_verified', 'archive_item_member_verified', 'archive_item_metadata_grants_download_or_extraction_permission', 'automatic_future_connector_approval', 'automatic_future_connector_approval', 'candidate_promotion_preview_promotes_candidate', 'checksum_correctness_verified', 'checksum_correctness_verified', 'community_download_metadata_grants_acquisition_permission', 'community_reputation_claimed', 'community_reputation_verified', 'community_reputation_verified', 'community_review_comment_seed_accepts_truth', 'compatibility_correctness_verified', 'compatibility_correctness_verified', 'compatibility_install_note_seed_accepts_compatibility_truth', 'content_safety', 'content_safety', 'content_safety_claimed', 'evidence_review_seed_accepts_evidence', 'exhaustive_global_coverage', 'exhaustive_global_coverage', 'file_authenticity_verified', 'file_authenticity_verified', 'future_connector_auto_approval', 'gated_source_boundary_seed_grants_access_permission', 'hash_checksum_seed_accepts_hash_truth', 'ia_wayback_seed_accepts_corroboration_truth', 'installability_verified', 'installability_verified', 'legal_acquisition_verified', 'legal_acquisition_verified', 'malware_safety', 'malware_safety', 'malware_safety_claimed', 'master_index_mutated', 'mutated_master_index', 'mutated_public_index', 'platform_version_seed_accepts_version_truth', 'platform_version_verified', 'platform_version_verified', 'playability_verified', 'playability_verified', 'privacy_safety', 'privacy_safety', 'privacy_safety_claimed', 'production_readiness_claim', 'production_readiness_claimed', 'production_retro_archive_coverage', 'production_retro_archive_coverage', 'production_search_quality', 'production_search_quality', 'public_index_mutated', 'retro_software_identity_seed_accepts_software_truth', 'retro_software_identity_verified', 'retro_software_identity_verified', 'review_seed_is_review_decision', 'rights_clearance', 'rights_clearance', 'rights_clearance_claimed', 'rights_safety_seed_accepts_rights_safety_truth', 'source_cache_review_seed_accepts_source', 'source_pack_accepted', 'source_pack_imported', 'source_pack_preview_is_imported_or_submitted', 'source_pack_submitted', 'verified_authenticity', 'verified_authenticity', 'verified_authenticity_claimed'])


def build_h12_quality_delta(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    review = dict(inputs.get("review_integration_result") or inputs)
    sources = list(review.get("sources") or [])
    blocked_sources = list(review.get("blocked_sources") or [])
    fixture_outputs = list(review.get("used_fixture_outputs") or [])
    live_outputs = list(review.get("used_live_probe_outputs") or [])
    known_gaps = _known_gaps(review)
    metrics = {
        "source_count": len(sources) or len(H12_SOURCE_IDS),
        "fixture_sources_count": len({item.get("source_id") for item in fixture_outputs if item.get("source_id")}) or len(sources),
        "live_probe_sources_count": len({item.get("source_id") for item in live_outputs if item.get("status") == "live_probe_completed"}),
        "blocked_sources_count": len(blocked_sources),
        "normalized_record_count": len(review.get("source_cache_review_seeds", [])),
        "retro_software_identity_candidate_count": len(review.get("retro_software_identity_review_seeds", [])),
        "platform_version_edition_candidate_count": len(review.get("platform_version_edition_review_seeds", [])),
        "archive_item_member_candidate_count": len(review.get("archive_item_member_review_seeds", [])),
        "compatibility_install_note_candidate_count": len(review.get("compatibility_install_note_review_seeds", [])),
        "community_review_comment_candidate_count": len(review.get("community_review_comment_review_seeds", [])),
        "hash_checksum_candidate_count": len(review.get("hash_checksum_review_seeds", [])),
        "ia_wayback_corroboration_candidate_count": len(review.get("ia_wayback_corroboration_review_seeds", [])),
        "gated_source_boundary_candidate_count": len(review.get("gated_source_boundary_review_seeds", [])),
        "retro_rights_safety_candidate_count": len(review.get("retro_rights_safety_review_seeds", [])),
        "source_cache_candidate_count": len(review.get("source_cache_review_seeds", [])),
        "evidence_candidate_preview_count": len(review.get("evidence_candidate_review_seeds", [])),
        "review_seed_count": sum(len(review.get(key, [])) for key in REVIEW_SEED_KEYS),
        "coverage_preview_count": len(review.get("coverage_update_previews", [])),
        "scorecard_update_count": len(review.get("scorecard_updates", [])),
        "known_gap_count": len(known_gaps),
        "blocker_count": 0,
        "warning_count": len(review.get("warnings", [])) + (1 if blocked_sources else 0),
    }
    delta = {
        "schema_version": "h12_retro_community_quality_delta_report.v0",
        "quality_delta_id": f"h12.quality_delta.{_digest(review)[:12]}.v0",
        "wave_id": "H12",
        "comparison_scope": "fixture_review_and_blocked_live_probe_evidence",
        **metrics,
        "per_source_deltas": [_per_source_delta(source_id, review, fixture_outputs, live_outputs, blocked_sources) for source_id in sorted(set(sources) or set(H12_SOURCE_IDS))],
        "limitations": [
            "Quality delta measures H12 review readiness only.",
            "Blocked live probes do not prove endpoint behavior.",
            "Retro/community metadata is not retro software identity truth, platform/version/edition truth, archive item/member truth, file authenticity, checksum correctness, compatibility correctness, installability, playability, legal acquisition, rights clearance, malware safety, content safety, privacy safety, community reputation, production coverage, or production quality proof.",
        ],
        "forbidden_claims": ['production_search_quality', 'production_retro_archive_coverage', 'exhaustive_global_coverage', 'retro_software_identity_verified', 'platform_version_verified', 'archive_item_member_verified', 'file_authenticity_verified', 'checksum_correctness_verified', 'compatibility_correctness_verified', 'installability_verified', 'playability_verified', 'legal_acquisition_verified', 'rights_clearance', 'malware_safety', 'content_safety', 'privacy_safety', 'community_reputation_verified', 'verified_authenticity', 'automatic_future_connector_approval'],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["H12 quality delta is operational review evidence only."],
    }
    errors = detect_h12_quality_overclaim(delta, policy)
    if errors:
        raise ValueError("; ".join(errors))
    return delta


def summarize_h12_quality_delta(delta: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    errors = detect_h12_quality_overclaim(delta, policy)
    return {
        "schema_version": "h12_quality_delta_summary.v0",
        "status": "pass" if not errors else "invalid",
        "quality_delta_id": delta.get("quality_delta_id"),
        "source_count": delta.get("source_count", 0),
        "fixture_sources_count": delta.get("fixture_sources_count", 0),
        "live_probe_sources_count": delta.get("live_probe_sources_count", 0),
        "blocked_sources_count": delta.get("blocked_sources_count", 0),
        "retro_software_identity_candidate_count": delta.get("retro_software_identity_candidate_count", 0),
        "platform_version_edition_candidate_count": delta.get("platform_version_edition_candidate_count", 0),
        "archive_item_member_candidate_count": delta.get("archive_item_member_candidate_count", 0),
        "compatibility_install_note_candidate_count": delta.get("compatibility_install_note_candidate_count", 0),
        "community_review_comment_candidate_count": delta.get("community_review_comment_candidate_count", 0),
        "hash_checksum_candidate_count": delta.get("hash_checksum_candidate_count", 0),
        "ia_wayback_corroboration_candidate_count": delta.get("ia_wayback_corroboration_candidate_count", 0),
        "gated_source_boundary_candidate_count": delta.get("gated_source_boundary_candidate_count", 0),
        "retro_rights_safety_candidate_count": delta.get("retro_rights_safety_candidate_count", 0),
        "review_seed_count": delta.get("review_seed_count", 0),
        "known_gap_count": delta.get("known_gap_count", 0),
        "blocker_count": delta.get("blocker_count", 0),
        "claims_retro_software_identity_verified": False,
        "claims_platform_version_verified": False,
        "claims_archive_item_member_verified": False,
        "claims_file_authenticity_verified": False,
        "claims_checksum_correctness_verified": False,
        "claims_compatibility_correctness": False,
        "claims_installability": False,
        "claims_playability": False,
        "claims_legal_acquisition": False,
        "claims_rights_clearance": False,
        "claims_malware_safety": False,
        "claims_content_safety": False,
        "claims_privacy_safety": False,
        "claims_community_reputation": False,
        "claims_verified_authenticity": False,
        "claims_production_readiness": False,
        "overclaim_errors": errors,
    }


def detect_h12_quality_overclaim(delta: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    errors = [f"quality overclaim: {path}=true" for path, key, value in _iter_key_values(delta) if key in FORBIDDEN_TRUE_KEYS and value is True]
    errors.extend(detect_h12_review_truth_boundary_violations(delta, policy))
    errors.extend(detect_h12_review_product_boundary_violations(delta, policy))
    return sorted(dict.fromkeys(errors))


def _per_source_delta(source_id: str, review: Mapping[str, Any], fixture_outputs: list[Mapping[str, Any]], live_outputs: list[Mapping[str, Any]], blocked_sources: list[str]) -> dict[str, Any]:
    represented = source_id in review.get("sources", [])
    return {
        "source_id": source_id,
        "fixture_output_integrated": any(item.get("source_id") == source_id for item in fixture_outputs) or represented,
        "live_probe_completed": any(item.get("source_id") == source_id and item.get("status") == "live_probe_completed" for item in live_outputs),
        "live_probe_blocked": source_id in blocked_sources,
        "retro_software_identity_review_seed_created": represented,
        "platform_version_edition_review_seed_created": represented,
        "archive_item_member_review_seed_created": represented,
        "compatibility_install_note_review_seed_created": represented,
        "community_review_comment_review_seed_created": represented,
        "hash_checksum_review_seed_created": represented,
        "ia_wayback_corroboration_review_seed_created": represented,
        "gated_source_boundary_review_seed_created": represented,
        "retro_rights_safety_review_seed_created": represented,
        "source_cache_review_seed_created": represented,
        "evidence_review_seed_created": represented,
        "limitations": ["Fixture/local review only; not accepted source, evidence, candidate, retro software identity, platform/version, archive item/member, compatibility, community review, hash, IA/Wayback, gated-source, rights/safety, public, or production proof."],
    }


def _known_gaps(review: Mapping[str, Any]) -> list[str]:
    gaps: list[str] = []
    if review.get("blocked_sources"):
        gaps.append("operator_approval_missing_for_live_metadata_probes")
    if len(review.get("source_cache_review_seeds", [])) < len(H12_SOURCE_IDS):
        gaps.append("not_all_sources_have_review_seeds")
    if not any(item.get("status") == "live_probe_completed" for item in review.get("used_live_probe_outputs", [])):
        gaps.append("approved_live_probe_outputs_not_available")
    return sorted(dict.fromkeys(gaps))


def _truth_boundary() -> dict[str, bool]:
    return {key: False for key in FORBIDDEN_TRUE_KEYS}


def _product_boundary() -> dict[str, bool]:
    return {key: False for key in ['acquisition_action_used', 'acquisition_permission', 'api_calls_made', 'bypass_or_automation_used', 'catalog_fetch_used', 'changed_public_search_behavior', 'crawling_used', 'download_used', 'enabled_accounts', 'enabled_acquisition_actions', 'enabled_crawling', 'enabled_downloads', 'enabled_execution', 'enabled_extraction', 'enabled_hosting', 'enabled_live_probes', 'enabled_source_sync', 'enabled_telemetry', 'enabled_uploads', 'enables_acquisition_actions', 'enables_api_catalog_sync', 'enables_downloads', 'enables_execution', 'enables_extraction', 'enables_forum_or_gated_fetch', 'enables_hash_submission', 'enables_restricted_source_access', 'enables_scraping_crawling', 'enables_uploads', 'execution_used', 'extraction_used', 'forum_comment_fetch_used', 'gated_source_access_used', 'hash_submission_used', 'mutated_master_index', 'mutated_public_index', 'mutates_master_index', 'mutates_public_index', 'network_calls_made', 'query_fetch_download_extract_execute_acquire_upload', 'restricted_source_access', 'restricted_source_access_used', 'scraping_used', 'upload_used']}


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
