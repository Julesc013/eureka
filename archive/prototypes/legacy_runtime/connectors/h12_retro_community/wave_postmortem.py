"""H12 retro/community wave postmortem and next-phase helpers."""

from __future__ import annotations

from collections.abc import Mapping
import hashlib
import json
from typing import Any

from archive.prototypes.legacy_runtime.connectors.h12_retro_community.normalizer_common import H12_SOURCE_IDS
from archive.prototypes.legacy_runtime.connectors.h12_retro_community.quality_delta import detect_h12_quality_overclaim, summarize_h12_quality_delta
from archive.prototypes.legacy_runtime.connectors.h12_retro_community.review_integration import (
    detect_h12_review_product_boundary_violations,
    detect_h12_review_truth_boundary_violations,
    summarize_h12_review_integration,
)


def build_h12_connector_wave_postmortem(review_result: Mapping[str, Any], quality_delta: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    blocked_sources = list(review_result.get("blocked_sources") or [])
    postmortem = {
        "schema_version": "h12_retro_community_connector_wave_postmortem.v0",
        "postmortem_id": f"h12.connector_wave_postmortem.{_digest({'review': review_result, 'delta': quality_delta})[:12]}.v0",
        "wave_id": "H12",
        "what_worked": [
            "Thirteen H12 retro/community sources have policy packs, fixtures, normalizers, replay outputs, fail-closed live-probe envelopes, and review previews.",
            "Retro software identity, platform/version/edition, archive item/member, compatibility/install-note, community review/comment, hash/checksum, IA/Wayback, gated-source boundary, and rights/safety candidates remain review-gated and candidate-only.",
            "Live-probe outputs failed closed or stayed dry-preflight when committed source approvals were missing.",
        ],
        "what_failed": ["No H12 source has committed operator approval for a live metadata probe."] if blocked_sources else [],
        "blocked_sources": blocked_sources,
        "fixture_gaps": ["Fixtures are synthetic/public-safe and do not prove live retro/community archive metadata behavior."],
        "live_probe_gaps": ["Blocked live probes provide gate evidence but no completed network metadata response."] if blocked_sources else [],
        "normalizer_gaps": ["Normalizers cover metadata fixture shapes, not catalog/forum/gated fetching, payload downloads, extraction, execution, accounts, scraping, crawling, bypass, or restricted-source access."],
        "retro_software_identity_gaps": ["Retro software identity candidates require review before any identity use."],
        "platform_version_edition_gaps": ["Platform/version/edition candidates are not version truth, compatibility proof, installability proof, or acquisition proof."],
        "archive_item_member_gaps": ["Archive item/member candidates are not file truth, authenticity proof, checksum proof, or download/extraction permission."],
        "compatibility_install_note_gaps": ["Compatibility/install-note candidates are not compatibility correctness, installability, playability, or execution permission."],
        "community_review_comment_gaps": ["Community review/comment candidates are not accepted claim truth or community reputation truth."],
        "hash_checksum_gaps": ["Hash/checksum candidates are not identity truth, authenticity proof, checksum correctness, or malware safety."],
        "ia_wayback_corroboration_gaps": ["IA/Wayback corroboration candidates are not accepted truth, acquisition permission, rights proof, or authenticity proof."],
        "gated_source_boundary_gaps": ["Gated-source boundary candidates grant no account, invitation, forum, private, or restricted-source access."],
        "rights_safety_gaps": ["Rights/safety candidates are not rights clearance, legal acquisition truth, malware safety, content safety, privacy safety, or production readiness."],
        "restricted_source_policy_gaps": ["Rights-sensitive, gated, private, piracy-adjacent, crack/key/serial, leaked/proprietary, account-locked, and restricted retro/community sources remain policy-blocked by default."],
        "community_lane_trust_gaps": ["Community-lane metadata remains candidate evidence only and requires review before any downstream use."],
        "policy_gaps": ["source-specific live probe approvals remain absent"] if blocked_sources else [],
        "evidence_mapping_gaps": ["Evidence candidates remain previews only."],
        "review_mapping_gaps": ["Review seeds are not human review decisions and are not persisted."],
        "quality_delta_summary": summarize_h12_quality_delta(quality_delta, policy),
        "scorecard_summary": {
            "scorecard_update_count": quality_delta.get("scorecard_update_count", 0),
            "production_ready": False,
            "auto_approves_future_connectors": False,
        },
        "safety_boundary_assessment": {
            "network_calls_made": False,
            "api_catalog_query_enabled": False,
            "forum_or_gated_fetch_enabled": False,
            "downloads_enabled": False,
            "extraction_enabled": False,
            "execution_enabled": False,
            "acquisition_actions_enabled": False,
            "uploads_enabled": False,
            "hash_submission_enabled": False,
            "scraping_crawling_enabled": False,
            "restricted_source_access_enabled": False,
            "source_sync_enabled": False,
            "accepted_truth": False,
            "public_index_mutated": False,
            "master_index_mutated": False,
            "boundary_result": "preserved",
        },
        "next_phase_recommendation": "READY_FOR_H13_BUNDLE_01",
        "h13_or_j1_k_l_recommendation": "proceed_to_h13_policy_packs; keep_j1_k_l_deferred",
        "do_not_repeat_risks": [
            "Do not treat retro/community metadata as identity, platform/version, archive item/member, compatibility, community-review, hash, IA/Wayback, gated-source, rights/safety, or public truth.",
            "Do not use fixture replay or blocked probes as live access approval.",
            "Do not let retro/community metadata become query, fetch, download, extraction, execution, acquisition, upload, hash submission, gated-source, restricted-source, source-sync, or action permission.",
        ],
        "source_os_reuse_assessment": "H12 reused H0-H11 Source OS review gates while preserving retro/community-specific rights, payload, gated-source, hash, compatibility, and safety boundaries.",
        "h13_handoff_recommendation": "H13-BUNDLE-01 may start policy-pack-only work for local, private, user-supplied, and restricted-source source families.",
        "j1_k_l_deferral_recommendation": "J1 risky actions, K semantic/AI, and L wider clients remain deferred unless explicit gates open.",
        "risks": ["Live H12 metadata probes remain blocked pending operator approval."] if blocked_sources else [],
        "no_goals_preserved": ["no_api_catalog_query", "no_forum_or_gated_fetch", "no_download_extract_execute_acquire_upload", "no_hash_submission", "no_scrape_crawl", "no_restricted_source_access", "no_truth_acceptance", "no_public_index_mutation"],
        "auto_approves_future_connectors": False,
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["Postmortem recommends H13 policy packs, not risky actions or production readiness."],
    }
    _raise_if_invalid(postmortem, policy)
    return postmortem


def build_h12_next_phase_recommendation(postmortem: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    recommendation = {
        "schema_version": "h12_retro_community_next_phase_recommendation.v0",
        "recommendation_id": f"h12.next_phase.{_digest(postmortem)[:12]}.v0",
        "wave_id": "H12",
        "recommended_next_task": "H13-BUNDLE-01 - Local, private, user-supplied, and restricted-source policy packs",
        "recommendation_status": "READY_FOR_H13_BUNDLE_01",
        "alternatives_considered": ["J1-POLICY-01", "K0-BUNDLE-01", "L0-BUNDLE-01", "H12-REMEDIATION-04"],
        "h13_readiness": "ready_with_fixture_equivalent_h12_outputs",
        "j1_deferral": "risky query/fetch/download/extract/execute/acquire/upload/hash-submit actions remain deferred to J1",
        "k_deferral": "semantic/AI assist remains deferred to K0 typed no-truth policy",
        "l_deferral": "wider clients remain deferred to L0 planning",
        "deployment_deferral": "deployment remains operator-gated and out of scope",
        "remediation_required": False,
        "reason": "H12 retro/community policy, fixture, blocked-live-probe, review, and quality artifacts are coherent enough to plan H13 without enabling live access, downloads, extraction, execution, acquisition actions, uploads, hash submissions, scraping, crawling, restricted-source access, source sync, index mutation, or truth acceptance.",
        "limitations": ["No approved H12 live metadata probe completed; fixture-equivalent outputs carry the review integration."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
    }
    _raise_if_invalid(recommendation, policy)
    return recommendation


def build_h12_integration_audit(
    review_result: Mapping[str, Any],
    quality_delta: Mapping[str, Any],
    postmortem: Mapping[str, Any],
    recommendation: Mapping[str, Any] | None = None,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    recommendation = dict(recommendation or build_h12_next_phase_recommendation(postmortem, policy))
    review_summary = summarize_h12_review_integration(review_result)
    audit = {
        "schema_version": "h12_retro_community_integration_audit.v0",
        "audit_id": f"h12.integration_audit.{_digest({'review': review_result, 'delta': quality_delta, 'postmortem': postmortem})[:12]}.v0",
        "wave_id": "H12",
        "audited_sources": list(review_result.get("sources", [])),
        "audited_tasks": ["H12-BUNDLE-01", "H12-BUNDLE-02", "H12-BUNDLE-03", "H12-BUNDLE-04"],
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
        "quality_delta_summary": summarize_h12_quality_delta(quality_delta),
        "postmortem_summary": summarize_h12_postmortem(postmortem),
        "community_lane_summary": {"community_lane_metadata": "candidate_evidence_only"},
        "gated_source_boundary_summary": {"gated_source_access": "blocked_current"},
        "restricted_source_policy_summary": {"restricted_or_rights_sensitive_retro_community_sources": "blocked_by_default"},
        "blockers": [],
        "warnings": ["H12 live probes remain blocked pending operator approval"] if review_result.get("blocked_sources") else [],
        "h12_exit_gate": "PASS_WITH_WARNINGS" if review_result.get("blocked_sources") else "PASS",
        "next_phase_recommendation": recommendation.get("recommendation_status", "READY_FOR_H13_BUNDLE_01"),
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["H12 passes for H13 policy-pack planning using fixture-equivalent outputs."],
    }
    apply_missing_source_gate(audit)
    _raise_if_invalid(audit, policy)
    return audit


def summarize_h12_postmortem(postmortem: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    errors = detect_h12_quality_overclaim(postmortem, policy)
    return {
        "schema_version": "h12_connector_wave_postmortem_summary.v0",
        "status": "pass" if not errors else "invalid",
        "postmortem_id": postmortem.get("postmortem_id"),
        "next_phase_recommendation": postmortem.get("next_phase_recommendation"),
        "h13_or_j1_k_l_recommendation": postmortem.get("h13_or_j1_k_l_recommendation"),
        "auto_approves_future_connectors": False,
        "errors": errors,
    }


def apply_missing_source_gate(integration_audit: dict[str, Any], required_sources: tuple[str, ...] = H12_SOURCE_IDS) -> dict[str, Any]:
    missing = [source for source in required_sources if source not in integration_audit.get("audited_sources", [])]
    if missing:
        integration_audit["h12_exit_gate"] = "PARTIAL"
        integration_audit["next_phase_recommendation"] = "NEEDS_REMEDIATION"
        integration_audit.setdefault("blockers", []).append(f"missing audited sources: {', '.join(missing)}")
    return integration_audit


def _truth_boundary() -> dict[str, bool]:
    return {
        "retro_software_identity_seed_accepts_software_truth": False,
        "platform_version_seed_accepts_version_truth": False,
        "archive_item_member_seed_accepts_file_truth": False,
        "compatibility_install_note_seed_accepts_compatibility_truth": False,
        "community_review_comment_seed_accepts_truth": False,
        "hash_checksum_seed_accepts_hash_truth": False,
        "ia_wayback_seed_accepts_corroboration_truth": False,
        "gated_source_boundary_seed_grants_access_permission": False,
        "rights_safety_seed_accepts_rights_safety_truth": False,
        "source_cache_review_seed_accepts_source": False,
        "evidence_review_seed_accepts_evidence": False,
        "candidate_promotion_preview_promotes_candidate": False,
        "source_pack_preview_is_imported_or_submitted": False,
        "review_seed_is_review_decision": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "rights_clearance_claimed": False,
        "legal_acquisition_claimed": False,
        "file_authenticity_claimed": False,
        "checksum_correctness_claimed": False,
        "compatibility_correctness_claimed": False,
        "installability_claimed": False,
        "playability_claimed": False,
        "malware_safety_claimed": False,
        "content_safety_claimed": False,
        "privacy_safety_claimed": False,
        "community_reputation_claimed": False,
        "verified_authenticity_claimed": False,
        "production_readiness_claimed": False,
        "automatic_future_connector_approval": False,
        "accepted_retro_software_identity_truth": False,
        "accepted_platform_version_truth": False,
        "accepted_archive_item_member_truth": False,
        "accepted_compatibility_install_truth": False,
        "accepted_community_review_truth": False,
        "accepted_hash_checksum_truth": False,
        "accepted_ia_wayback_corroboration_truth": False,
        "accepted_gated_source_access_truth": False,
        "accepted_rights_safety_truth": False,
        "accepted_source_truth": False,
        "accepted_evidence_truth": False,
        "accepted_candidate_truth": False,
        "abandonware_label_is_legal_permission": False,
        "community_download_metadata_grants_acquisition_permission": False,
    }


def _product_boundary() -> dict[str, bool]:
    return {
        "changed_public_search_behavior": False,
        "enabled_hosting": False,
        "enabled_live_probes": False,
        "enabled_source_sync": False,
        "enabled_downloads": False,
        "enabled_extraction": False,
        "enabled_execution": False,
        "enabled_acquisition_actions": False,
        "enabled_accounts": False,
        "enabled_uploads": False,
        "enabled_crawling": False,
        "enabled_telemetry": False,
        "network_calls_made": False,
        "api_calls_made": False,
        "catalog_fetch_used": False,
        "forum_comment_fetch_used": False,
        "gated_source_access_used": False,
        "download_used": False,
        "extraction_used": False,
        "execution_used": False,
        "acquisition_action_used": False,
        "upload_used": False,
        "hash_submission_used": False,
        "scraping_used": False,
        "crawling_used": False,
        "restricted_source_access_used": False,
        "bypass_or_automation_used": False,
        "mutated_public_index": False,
        "mutated_master_index": False,
    }


def _raise_if_invalid(payload: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> None:
    errors = detect_h12_quality_overclaim(payload, policy)
    errors.extend(detect_h12_review_truth_boundary_violations(payload, policy))
    errors.extend(detect_h12_review_product_boundary_violations(payload, policy))
    if errors:
        raise ValueError("; ".join(sorted(dict.fromkeys(errors))))


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, default=str).encode("utf-8")).hexdigest()
