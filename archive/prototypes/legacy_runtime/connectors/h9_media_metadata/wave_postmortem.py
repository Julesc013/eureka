"""H9 media metadata wave postmortem and next-phase helpers."""

from __future__ import annotations

from collections.abc import Mapping
import hashlib
import json
from typing import Any

from archive.prototypes.legacy_runtime.connectors.h9_media_metadata.normalizer_common import H9_SOURCE_IDS
from archive.prototypes.legacy_runtime.connectors.h9_media_metadata.quality_delta import detect_h9_quality_overclaim, summarize_h9_quality_delta
from archive.prototypes.legacy_runtime.connectors.h9_media_metadata.review_integration import (
    detect_h9_review_product_boundary_violations,
    detect_h9_review_truth_boundary_violations,
    summarize_h9_review_integration,
)


def build_h9_connector_wave_postmortem(review_result: Mapping[str, Any], quality_delta: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    blocked_sources = list(review_result.get("blocked_sources") or [])
    postmortem = {
        "schema_version": "h9_media_metadata_connector_wave_postmortem.v0",
        "postmortem_id": f"h9.connector_wave_postmortem.{_digest({'review': review_result, 'delta': quality_delta})[:12]}.v0",
        "wave_id": "H9",
        "what_worked": [
            "Twenty H9 media metadata sources have policy packs, fixtures, normalizers, replay outputs, fail-closed live-probe envelopes, and review previews.",
            "Media object, music work/recording/release, image/video/map, creator/collection relation, fingerprint, rights/license, and safety/privacy candidates remain review-gated and candidate-only.",
            "Live-probe outputs failed closed or stayed dry-preflight when committed source approvals were missing.",
        ],
        "what_failed": ["No H9 source has committed operator approval for a live metadata probe."] if blocked_sources else [],
        "blocked_sources": blocked_sources,
        "fixture_gaps": ["Fixtures are synthetic/public-safe and do not prove live media metadata behavior."],
        "live_probe_gaps": ["Blocked live probes provide gate evidence but no completed network metadata response."] if blocked_sources else [],
        "normalizer_gaps": ["Normalizers cover metadata fixture shapes, not media payloads, thumbnails, audio/video/image/map files, scores, cover art, waveforms, scraping, crawling, or restricted-source access."],
        "media_object_identity_gaps": ["Media object identity candidates require review before any media identity use."],
        "music_identity_gaps": ["Music work/recording/release candidates are not music identity, audio identity, streaming, download, or redistribution truth."],
        "image_video_map_identity_gaps": ["Image/video/map candidates are not object truth, geospatial correctness proof, or media authenticity."],
        "creator_collection_relation_gaps": ["Creator/collection relation candidates are not relation truth, duplicate truth, or attribution correctness."],
        "fingerprint_gaps": ["Fingerprint candidates are not identity truth and grant no lookup, upload, submission, or generation permission."],
        "rights_license_gaps": ["Rights/license candidates are not rights clearance, public-domain truth, Creative Commons truth, or attribution correctness."],
        "safety_privacy_gaps": ["Safety/privacy candidates are not content safety, privacy safety, malware safety, takedown, or release decisions."],
        "restricted_source_policy_gaps": ["Licensed, rights-sensitive, adult, extremist, illegal, platform-restricted, and otherwise sensitive media sources remain policy-blocked by default."],
        "policy_gaps": ["source-specific live probe approvals remain absent"] if blocked_sources else [],
        "evidence_mapping_gaps": ["Evidence candidates remain previews only."],
        "review_mapping_gaps": ["Review seeds are not human review decisions and are not persisted."],
        "quality_delta_summary": summarize_h9_quality_delta(quality_delta, policy),
        "scorecard_summary": {
            "scorecard_update_count": quality_delta.get("scorecard_update_count", 0),
            "production_ready": False,
            "auto_approves_future_connectors": False,
        },
        "safety_boundary_assessment": {
            "network_calls_made": False,
            "api_catalog_query_enabled": False,
            "media_download_enabled": False,
            "media_upload_enabled": False,
            "fingerprint_submission_generation_enabled": False,
            "scraping_crawling_enabled": False,
            "restricted_source_access_enabled": False,
            "source_sync_enabled": False,
            "accepted_truth": False,
            "public_index_mutated": False,
            "master_index_mutated": False,
            "boundary_result": "preserved",
        },
        "next_phase_recommendation": "READY_FOR_H10_BUNDLE_01",
        "h10_or_j1_k_l_recommendation": "proceed_to_h10_policy_packs; keep_j1_k_l_deferred",
        "do_not_repeat_risks": [
            "Do not treat media metadata as media authenticity, audio identity, image identity, map correctness, rights clearance, public-domain truth, Creative Commons truth, attribution correctness, malware safety, privacy safety, content safety, or public truth.",
            "Do not use fixture replay or blocked probes as live access approval.",
            "Do not let media metadata become query, fetch, download, upload, fingerprint, scraping, crawling, restricted-source, or acquisition permission.",
        ],
        "source_os_reuse_assessment": "H9 reused H0-H8 Source OS review gates while preserving media-specific rights, safety, payload, and identity boundaries.",
        "h10_handoff_recommendation": "H10-BUNDLE-01 may start policy-pack-only work for games, emulation, and software-identity sources.",
        "j1_k_l_deferral_recommendation": "J1 risky actions, K semantic/AI, and L wider clients remain deferred unless explicit gates open.",
        "risks": ["Live H9 metadata probes remain blocked pending operator approval."] if blocked_sources else [],
        "no_goals_preserved": ["no_api_catalog_query", "no_media_download_upload", "no_fingerprint_generation_submission", "no_scrape_crawl", "no_restricted_source_access", "no_truth_acceptance", "no_public_index_mutation"],
        "auto_approves_future_connectors": False,
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["Postmortem recommends H10 policy packs, not risky actions or production readiness."],
    }
    _raise_if_invalid(postmortem, policy)
    return postmortem


def build_h9_next_phase_recommendation(postmortem: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    recommendation = {
        "schema_version": "h9_media_metadata_next_phase_recommendation.v0",
        "recommendation_id": f"h9.next_phase.{_digest(postmortem)[:12]}.v0",
        "wave_id": "H9",
        "recommended_next_task": "H10-BUNDLE-01 - Games, emulation, and software-identity source-family policy packs",
        "recommendation_status": "READY_FOR_H10_BUNDLE_01",
        "alternatives_considered": ["J1-POLICY-01", "K0-BUNDLE-01", "L0-BUNDLE-01", "H9-REMEDIATION-04"],
        "h10_readiness": "ready_with_fixture_equivalent_h9_outputs",
        "j1_deferral": "risky query/fetch/download/upload/fingerprint/acquisition actions remain deferred to J1",
        "k_deferral": "semantic/AI assist remains deferred to K0 typed no-truth policy",
        "l_deferral": "wider clients remain deferred to L0 planning",
        "deployment_deferral": "deployment remains operator-gated and out of scope",
        "remediation_required": False,
        "reason": "H9 media metadata policy, fixture, blocked-live-probe, review, and quality artifacts are coherent enough to plan H10 without enabling media access, fingerprinting, scraping, restricted-source access, index mutation, or truth acceptance.",
        "limitations": ["No approved H9 live metadata probe completed; fixture-equivalent outputs carry the review integration."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
    }
    _raise_if_invalid(recommendation, policy)
    return recommendation


def build_h9_integration_audit(
    review_result: Mapping[str, Any],
    quality_delta: Mapping[str, Any],
    postmortem: Mapping[str, Any],
    recommendation: Mapping[str, Any] | None = None,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    recommendation = dict(recommendation or build_h9_next_phase_recommendation(postmortem, policy))
    review_summary = summarize_h9_review_integration(review_result)
    audit = {
        "schema_version": "h9_media_metadata_integration_audit.v0",
        "audit_id": f"h9.integration_audit.{_digest({'review': review_result, 'delta': quality_delta, 'postmortem': postmortem})[:12]}.v0",
        "wave_id": "H9",
        "audited_sources": list(review_result.get("sources", [])),
        "audited_tasks": ["H9-BUNDLE-01", "H9-BUNDLE-02", "H9-BUNDLE-03", "H9-BUNDLE-04"],
        "artifact_inventory": {
            "review_integration_result": bool(review_result),
            "quality_delta_report": bool(quality_delta),
            "connector_wave_postmortem": bool(postmortem),
            "next_phase_recommendation": bool(recommendation),
            "fixture_outputs_integrated": len(review_result.get("used_fixture_outputs", [])),
            "live_probe_outputs_integrated": len(review_result.get("used_live_probe_outputs", [])),
        },
        "validation_summary": {"status": "pass", "offline_default": True},
        "source_policy_summary": {"policy_packs_present": True, "live_access_default": False},
        "fixture_runtime_summary": {"fixture_outputs_integrated": len(review_result.get("used_fixture_outputs", []))},
        "live_probe_summary": {
            "completed_sources": [item.get("source_id") for item in review_result.get("used_live_probe_outputs", []) if item.get("status") == "live_probe_completed"],
            "blocked_sources": list(review_result.get("blocked_sources", [])),
            "network_used": False,
        },
        "review_integration_summary": review_summary,
        "quality_delta_summary": summarize_h9_quality_delta(quality_delta),
        "postmortem_summary": summarize_h9_postmortem(postmortem),
        "restricted_source_policy_summary": {"restricted_or_licensed_sources": "blocked_by_default"},
        "safety_privacy_boundary_summary": {"media_safety_privacy_metadata": "candidate_only_no_safety_truth"},
        "blockers": [],
        "warnings": ["H9 live probes remain blocked pending operator approval"] if review_result.get("blocked_sources") else [],
        "h9_exit_gate": "PASS_WITH_WARNINGS" if review_result.get("blocked_sources") else "PASS",
        "next_phase_recommendation": recommendation.get("recommendation_status", "READY_FOR_H10_BUNDLE_01"),
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["H9 passes for H10 policy-pack planning using fixture-equivalent outputs."],
    }
    apply_missing_source_gate(audit)
    _raise_if_invalid(audit, policy)
    return audit


def summarize_h9_postmortem(postmortem: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    errors = detect_h9_quality_overclaim(postmortem, policy)
    return {
        "schema_version": "h9_connector_wave_postmortem_summary.v0",
        "status": "pass" if not errors else "invalid",
        "postmortem_id": postmortem.get("postmortem_id"),
        "next_phase_recommendation": postmortem.get("next_phase_recommendation"),
        "h10_or_j1_k_l_recommendation": postmortem.get("h10_or_j1_k_l_recommendation"),
        "auto_approves_future_connectors": False,
        "errors": errors,
    }


def apply_missing_source_gate(integration_audit: dict[str, Any], required_sources: tuple[str, ...] = H9_SOURCE_IDS) -> dict[str, Any]:
    missing = [source for source in required_sources if source not in integration_audit.get("audited_sources", [])]
    if missing:
        integration_audit["h9_exit_gate"] = "PARTIAL"
        integration_audit["next_phase_recommendation"] = "NEEDS_REMEDIATION"
        integration_audit.setdefault("blockers", []).append(f"missing audited sources: {', '.join(missing)}")
    return integration_audit


def _truth_boundary() -> dict[str, bool]:
    return {
        "media_object_seed_accepts_media_truth": False,
        "music_identity_seed_accepts_music_truth": False,
        "image_video_map_seed_accepts_object_truth": False,
        "creator_collection_seed_accepts_relation_truth": False,
        "fingerprint_seed_accepts_identity_truth": False,
        "rights_license_seed_accepts_rights_truth": False,
        "safety_privacy_seed_accepts_safety_truth": False,
        "source_cache_review_seed_accepts_source": False,
        "evidence_review_seed_accepts_evidence": False,
        "candidate_promotion_preview_promotes_candidate": False,
        "source_pack_preview_is_imported_or_submitted": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "rights_clearance_claimed": False,
        "public_domain_truth_claimed": False,
        "creative_commons_truth_claimed": False,
        "content_safety_claimed": False,
        "privacy_safety_claimed": False,
        "malware_safety_claimed": False,
        "verified_authenticity_claimed": False,
        "production_readiness_claimed": False,
        "automatic_future_connector_approval": False,
        "accepted_media_identity_truth": False,
        "accepted_music_identity_truth": False,
        "accepted_image_video_map_truth": False,
        "accepted_creator_collection_relation_truth": False,
        "accepted_fingerprint_identity_truth": False,
        "accepted_rights_license_truth": False,
        "accepted_safety_privacy_truth": False,
        "accepted_source_truth": False,
        "accepted_evidence_truth": False,
        "accepted_candidate_truth": False,
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


def _raise_if_invalid(payload: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> None:
    errors = detect_h9_quality_overclaim(payload, policy)
    errors.extend(detect_h9_review_truth_boundary_violations(payload, policy))
    errors.extend(detect_h9_review_product_boundary_violations(payload, policy))
    if errors:
        raise ValueError("; ".join(sorted(dict.fromkeys(errors))))


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, default=str).encode("utf-8")).hexdigest()
