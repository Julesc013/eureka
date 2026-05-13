"""H11 storefront wave postmortem and next-phase helpers."""

from __future__ import annotations

from collections.abc import Mapping
import hashlib
import json
from typing import Any

from control.prototypes.legacy_runtime.connectors.h11_storefront.normalizer_common import H11_SOURCE_IDS
from control.prototypes.legacy_runtime.connectors.h11_storefront.quality_delta import detect_h11_quality_overclaim, summarize_h11_quality_delta
from control.prototypes.legacy_runtime.connectors.h11_storefront.review_integration import (
    detect_h11_review_product_boundary_violations,
    detect_h11_review_truth_boundary_violations,
    summarize_h11_review_integration,
)


def build_h11_connector_wave_postmortem(review_result: Mapping[str, Any], quality_delta: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    blocked_sources = list(review_result.get("blocked_sources") or [])
    postmortem = {
        "schema_version": "h11_storefront_connector_wave_postmortem.v0",
        "postmortem_id": f"h11.connector_wave_postmortem.{_digest({'review': review_result, 'delta': quality_delta})[:12]}.v0",
        "wave_id": "H11",
        "what_worked": [
            "Sixteen H11 storefront/app-store sources have policy packs, fixtures, normalizers, replay outputs, fail-closed live-probe envelopes, and review previews.",
            "Listing identity, app/product identity, version/release/channel, price/availability/region, acquisition path, review/rating, account/entitlement, and rights/safety candidates remain review-gated and candidate-only.",
            "Live-probe outputs failed closed or stayed dry-preflight when committed source approvals were missing.",
        ],
        "what_failed": ["No H11 source has committed operator approval for a live metadata probe."] if blocked_sources else [],
        "blocked_sources": blocked_sources,
        "fixture_gaps": ["Fixtures are synthetic/public-safe and do not prove live storefront/app-store metadata behavior."],
        "live_probe_gaps": ["Blocked live probes provide gate evidence but no completed network metadata response."] if blocked_sources else [],
        "normalizer_gaps": ["Normalizers cover metadata fixture shapes, not product page fetches, screenshots, media, app/game/package/installer payloads, account data, purchases, entitlements, installs, launches, scraping, crawling, or restricted-source access."],
        "listing_identity_gaps": ["Listing identity candidates require review before any listing identity use."],
        "app_product_identity_gaps": ["App/product identity candidates are not product truth, entitlement proof, installability proof, or safety proof."],
        "version_release_channel_gaps": ["Version/release/channel candidates are not version truth, release correctness, availability proof, or installability proof."],
        "price_availability_region_gaps": ["Price/availability/region candidates are not current price, current availability, region availability, legal acquisition, or purchase eligibility truth."],
        "acquisition_path_gaps": ["Acquisition path candidates remain blocked and grant no download, purchase, checkout, account, entitlement, install, launch, or acquisition permission."],
        "review_rating_metadata_gaps": ["Review/rating candidates are not review correctness, rating correctness, quality truth, or write permission."],
        "account_entitlement_boundary_gaps": ["Account/entitlement candidates are not license entitlement truth and authorize no private data access."],
        "rights_safety_gaps": ["Rights/safety candidates are not rights clearance, legal acquisition truth, malware safety, content safety, privacy safety, or production readiness."],
        "restricted_source_policy_gaps": ["Rights-sensitive, grey-market, piracy-adjacent, account-locked, paid, authenticated, platform-restricted, DRM-gated, and restricted storefront sources remain policy-blocked by default."],
        "policy_gaps": ["source-specific live probe approvals remain absent"] if blocked_sources else [],
        "evidence_mapping_gaps": ["Evidence candidates remain previews only."],
        "review_mapping_gaps": ["Review seeds are not human review decisions and are not persisted."],
        "quality_delta_summary": summarize_h11_quality_delta(quality_delta, policy),
        "scorecard_summary": {
            "scorecard_update_count": quality_delta.get("scorecard_update_count", 0),
            "production_ready": False,
            "auto_approves_future_connectors": False,
        },
        "safety_boundary_assessment": {
            "network_calls_made": False,
            "api_catalog_query_enabled": False,
            "product_page_fetch_enabled": False,
            "downloads_enabled": False,
            "account_access_enabled": False,
            "purchase_automation_enabled": False,
            "entitlement_verification_enabled": False,
            "install_launch_enabled": False,
            "review_rating_write_enabled": False,
            "scraping_crawling_enabled": False,
            "restricted_source_access_enabled": False,
            "source_sync_enabled": False,
            "accepted_truth": False,
            "public_index_mutated": False,
            "master_index_mutated": False,
            "boundary_result": "preserved",
        },
        "next_phase_recommendation": "READY_FOR_H12_BUNDLE_01",
        "h12_or_j1_k_l_recommendation": "proceed_to_h12_policy_packs; keep_j1_k_l_deferred",
        "do_not_repeat_risks": [
            "Do not treat storefront metadata as listing, product, version, price, availability, acquisition, review/rating, account/entitlement, rights/safety, or public truth.",
            "Do not use fixture replay or blocked probes as live access approval.",
            "Do not let storefront metadata become query, fetch, download, account, purchase, entitlement, install, launch, review-write, scraping, crawling, bypass, restricted-source, source-sync, or action permission.",
        ],
        "source_os_reuse_assessment": "H11 reused H0-H10 Source OS review gates while preserving storefront/app-store-specific price, availability, account, acquisition, rights, payload, and safety boundaries.",
        "h12_handoff_recommendation": "H12-BUNDLE-01 may start policy-pack-only work for retro and community archive source families.",
        "j1_k_l_deferral_recommendation": "J1 risky actions, K semantic/AI, and L wider clients remain deferred unless explicit gates open.",
        "risks": ["Live H11 metadata probes remain blocked pending operator approval."] if blocked_sources else [],
        "no_goals_preserved": ["no_api_catalog_query", "no_product_page_fetch", "no_download_account_purchase_entitlement_install_launch", "no_review_rating_write", "no_scrape_crawl", "no_restricted_source_access", "no_truth_acceptance", "no_public_index_mutation"],
        "auto_approves_future_connectors": False,
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["Postmortem recommends H12 policy packs, not risky actions or production readiness."],
    }
    _raise_if_invalid(postmortem, policy)
    return postmortem


def build_h11_next_phase_recommendation(postmortem: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    recommendation = {
        "schema_version": "h11_storefront_next_phase_recommendation.v0",
        "recommendation_id": f"h11.next_phase.{_digest(postmortem)[:12]}.v0",
        "wave_id": "H11",
        "recommended_next_task": "H12-BUNDLE-01 - Retro and community archive source-family policy packs",
        "recommendation_status": "READY_FOR_H12_BUNDLE_01",
        "alternatives_considered": ["J1-POLICY-01", "K0-BUNDLE-01", "L0-BUNDLE-01", "H11-REMEDIATION-04"],
        "h12_readiness": "ready_with_fixture_equivalent_h11_outputs",
        "j1_deferral": "risky query/fetch/download/account/purchase/entitlement/install/launch/review-write actions remain deferred to J1",
        "k_deferral": "semantic/AI assist remains deferred to K0 typed no-truth policy",
        "l_deferral": "wider clients remain deferred to L0 planning",
        "deployment_deferral": "deployment remains operator-gated and out of scope",
        "remediation_required": False,
        "reason": "H11 storefront/app-store policy, fixture, blocked-live-probe, review, and quality artifacts are coherent enough to plan H12 without enabling live access, downloads, accounts, purchases, entitlement checks, installs, launches, review writes, scraping, crawling, restricted-source access, source sync, index mutation, or truth acceptance.",
        "limitations": ["No approved H11 live metadata probe completed; fixture-equivalent outputs carry the review integration."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
    }
    _raise_if_invalid(recommendation, policy)
    return recommendation


def build_h11_integration_audit(
    review_result: Mapping[str, Any],
    quality_delta: Mapping[str, Any],
    postmortem: Mapping[str, Any],
    recommendation: Mapping[str, Any] | None = None,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    recommendation = dict(recommendation or build_h11_next_phase_recommendation(postmortem, policy))
    review_summary = summarize_h11_review_integration(review_result)
    audit = {
        "schema_version": "h11_storefront_integration_audit.v0",
        "audit_id": f"h11.integration_audit.{_digest({'review': review_result, 'delta': quality_delta, 'postmortem': postmortem})[:12]}.v0",
        "wave_id": "H11",
        "audited_sources": list(review_result.get("sources", [])),
        "audited_tasks": ["H11-BUNDLE-01", "H11-BUNDLE-02", "H11-BUNDLE-03", "H11-BUNDLE-04"],
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
        "quality_delta_summary": summarize_h11_quality_delta(quality_delta),
        "postmortem_summary": summarize_h11_postmortem(postmortem),
        "restricted_source_policy_summary": {"restricted_or_rights_sensitive_storefront_sources": "blocked_by_default"},
        "account_purchase_action_boundary_summary": {"acquisition_account_entitlement_candidates": "blocked_candidates_only_no_action_permission"},
        "blockers": [],
        "warnings": ["H11 live probes remain blocked pending operator approval"] if review_result.get("blocked_sources") else [],
        "h11_exit_gate": "PASS_WITH_WARNINGS" if review_result.get("blocked_sources") else "PASS",
        "next_phase_recommendation": recommendation.get("recommendation_status", "READY_FOR_H12_BUNDLE_01"),
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["H11 passes for H12 policy-pack planning using fixture-equivalent outputs."],
    }
    apply_missing_source_gate(audit)
    _raise_if_invalid(audit, policy)
    return audit


def summarize_h11_postmortem(postmortem: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    errors = detect_h11_quality_overclaim(postmortem, policy)
    return {
        "schema_version": "h11_connector_wave_postmortem_summary.v0",
        "status": "pass" if not errors else "invalid",
        "postmortem_id": postmortem.get("postmortem_id"),
        "next_phase_recommendation": postmortem.get("next_phase_recommendation"),
        "h12_or_j1_k_l_recommendation": postmortem.get("h12_or_j1_k_l_recommendation"),
        "auto_approves_future_connectors": False,
        "errors": errors,
    }


def apply_missing_source_gate(integration_audit: dict[str, Any], required_sources: tuple[str, ...] = H11_SOURCE_IDS) -> dict[str, Any]:
    missing = [source for source in required_sources if source not in integration_audit.get("audited_sources", [])]
    if missing:
        integration_audit["h11_exit_gate"] = "PARTIAL"
        integration_audit["next_phase_recommendation"] = "NEEDS_REMEDIATION"
        integration_audit.setdefault("blockers", []).append(f"missing audited sources: {', '.join(missing)}")
    return integration_audit


def _truth_boundary() -> dict[str, bool]:
    return {
        "listing_identity_seed_accepts_listing_truth": False,
        "app_product_seed_accepts_product_truth": False,
        "version_release_seed_accepts_version_truth": False,
        "price_availability_seed_accepts_price_availability_truth": False,
        "acquisition_path_seed_accepts_action_permission": False,
        "review_rating_seed_accepts_review_rating_truth": False,
        "account_entitlement_seed_accepts_license_truth": False,
        "rights_safety_seed_accepts_rights_safety_truth": False,
        "source_cache_review_seed_accepts_source": False,
        "evidence_review_seed_accepts_evidence": False,
        "candidate_promotion_preview_promotes_candidate": False,
        "source_pack_preview_is_imported_or_submitted": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "storefront_availability_verified": False,
        "current_price_verified": False,
        "current_availability_verified": False,
        "license_entitlement_verified": False,
        "legal_acquisition_verified": False,
        "download_permission_verified": False,
        "installability_verified": False,
        "review_correctness_verified": False,
        "rating_correctness_verified": False,
        "rights_clearance_claimed": False,
        "malware_safety_claimed": False,
        "content_safety_claimed": False,
        "privacy_safety_claimed": False,
        "verified_authenticity_claimed": False,
        "production_readiness_claimed": False,
        "automatic_future_connector_approval": False,
        "accepted_listing_identity_truth": False,
        "accepted_app_product_truth": False,
        "accepted_version_release_truth": False,
        "accepted_price_availability_truth": False,
        "accepted_acquisition_permission": False,
        "accepted_review_rating_truth": False,
        "accepted_account_entitlement_truth": False,
        "accepted_rights_safety_truth": False,
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
        "enabled_accounts": False,
        "enabled_purchase_actions": False,
        "enabled_entitlement_checks": False,
        "enabled_install_launch": False,
        "enabled_crawling": False,
        "enabled_uploads": False,
        "enabled_telemetry": False,
        "mutated_public_index": False,
        "mutated_master_index": False,
    }


def _raise_if_invalid(payload: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> None:
    errors = detect_h11_quality_overclaim(payload, policy)
    errors.extend(detect_h11_review_truth_boundary_violations(payload, policy))
    errors.extend(detect_h11_review_product_boundary_violations(payload, policy))
    if errors:
        raise ValueError("; ".join(sorted(dict.fromkeys(errors))))


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, default=str).encode("utf-8")).hexdigest()
