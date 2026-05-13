"""H6 web archive/news/event wave postmortem and next-phase helpers."""

from __future__ import annotations

from collections.abc import Mapping
import hashlib
import json
from typing import Any

from control.prototypes.legacy_runtime.connectors.h6_web_archive_news_event.normalizer_common import H6_SOURCE_IDS
from control.prototypes.legacy_runtime.connectors.h6_web_archive_news_event.quality_delta import detect_h6_quality_overclaim, summarize_h6_quality_delta
from control.prototypes.legacy_runtime.connectors.h6_web_archive_news_event.review_integration import (
    detect_h6_review_product_boundary_violations,
    detect_h6_review_truth_boundary_violations,
    summarize_h6_review_integration,
)


def build_h6_connector_wave_postmortem(review_result: Mapping[str, Any], quality_delta: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    blocked_sources = list(review_result.get("blocked_sources") or [])
    postmortem = {
        "schema_version": "h6_web_archive_connector_wave_postmortem.v0",
        "postmortem_id": f"h6.connector_wave_postmortem.{_digest({'review': review_result, 'delta': quality_delta})[:12]}.v0",
        "wave_id": "H6",
        "what_worked": [
            "Thirteen H6 web archive/news/event/public-trace sources have policy packs, fixtures, normalizers, replay outputs, blocked live-probe envelopes, and review previews.",
            "Web capture identity, archived time-state, news/event mention, dead-link, public-document, and media/transcript candidates remain review-gated and candidate-only.",
            "Live-probe outputs failed closed when committed source approvals were missing.",
        ],
        "what_failed": ["No H6 source has committed operator approval for a live metadata probe."] if blocked_sources else [],
        "blocked_sources": blocked_sources,
        "fixture_gaps": ["Fixtures are synthetic/public-safe and do not prove live archive, news, event, or public-document behavior."],
        "live_probe_gaps": ["Blocked live probes provide gate evidence but no completed metadata response."] if blocked_sources else [],
        "normalizer_gaps": ["Normalizers cover metadata fixture shapes, not archived pages, WARC/WACZ payloads, media, transcripts, documents, scraping, or crawling."],
        "web_capture_identity_gaps": ["Web capture identity candidates require review before any capture identity or completeness use."],
        "archived_url_time_state_gaps": ["Archived URL time-state candidates are not exact historical state or absence proof."],
        "news_event_mention_gaps": ["News/event mention candidates are not event truth, article truth, or full context."],
        "dead_link_trace_gaps": ["Dead-link traces do not grant acquisition, fetch, crawl, download, authenticity, or rights permission."],
        "public_document_trace_gaps": ["Public-document traces are not public-document truth and restricted/sensitive sources remain policy-blocked."],
        "media_transcript_metadata_gaps": ["Media/transcript metadata does not prove full context or authorize downloads."],
        "sensitive_source_policy_gaps": ["Sensitive-source access remains blocked by default and requires future legal/privacy/safety review."],
        "policy_gaps": ["source-specific live probe approvals remain absent"] if blocked_sources else [],
        "evidence_mapping_gaps": ["Evidence candidates remain previews only."],
        "review_mapping_gaps": ["Review seeds are not human review decisions and are not persisted."],
        "quality_delta_summary": summarize_h6_quality_delta(quality_delta, policy),
        "scorecard_summary": {
            "scorecard_update_count": quality_delta.get("scorecard_update_count", 0),
            "production_ready": False,
            "auto_approves_future_connectors": False,
        },
        "safety_boundary_assessment": {
            "network_calls_made": False,
            "cdx_query_enabled": False,
            "memento_lookup_enabled": False,
            "warc_wacz_fetch_enabled": False,
            "archived_page_fetch_enabled": False,
            "media_download_enabled": False,
            "scraping_crawling_enabled": False,
            "sensitive_source_access_enabled": False,
            "source_sync_enabled": False,
            "accepted_truth": False,
            "public_index_mutated": False,
            "master_index_mutated": False,
            "boundary_result": "preserved",
        },
        "next_phase_recommendation": "READY_FOR_H7_BUNDLE_01",
        "h7_or_j1_k_l_recommendation": "proceed_to_h7_policy_packs; keep_j1_k_l_deferred",
        "do_not_repeat_risks": [
            "Do not treat archive/news/event metadata as capture completeness, event truth, article truth, public-document truth, authenticity, privacy, safety, rights, or public truth.",
            "Do not use fixture replay or blocked probes as live access approval.",
            "Do not let dead-link or media metadata become fetch, crawl, download, or acquisition permission.",
        ],
        "source_os_reuse_assessment": "H6 reused H0-H5 Source OS review gates while preserving web archive/news/event-specific boundaries.",
        "h7_handoff_recommendation": "H7-BUNDLE-01 may start policy-pack-only work for library, cultural, book, and research sources.",
        "j1_k_l_deferral_recommendation": "J1 risky actions, K semantic/AI, and L wider clients remain deferred unless explicit gates open.",
        "risks": ["Live H6 metadata probes remain blocked pending operator approval."],
        "no_goals_preserved": ["no_cdx_memento_query", "no_warc_wacz_fetch", "no_page_fetch", "no_media_document_download", "no_scrape_crawl", "no_sensitive_source_access", "no_truth_acceptance", "no_public_index_mutation"],
        "auto_approves_future_connectors": False,
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["Postmortem recommends H7 policy packs, not risky actions or production readiness."],
    }
    _raise_if_invalid(postmortem, policy)
    return postmortem


def build_h6_next_phase_recommendation(postmortem: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    recommendation = {
        "schema_version": "h6_web_archive_next_phase_recommendation.v0",
        "recommendation_id": f"h6.next_phase.{_digest(postmortem)[:12]}.v0",
        "wave_id": "H6",
        "recommended_next_task": "H7-BUNDLE-01 - Library, cultural, book, and research source-family policy packs",
        "recommendation_status": "READY_FOR_H7_BUNDLE_01",
        "alternatives_considered": ["J1-POLICY-01", "K0-BUNDLE-01", "L0-BUNDLE-01", "H6-REMEDIATION-04"],
        "h7_readiness": "ready_with_fixture_equivalent_h6_outputs",
        "j1_deferral": "risky fetch/download/acquisition actions remain deferred to J1",
        "k_deferral": "semantic/AI assist remains deferred to K0 typed no-truth policy",
        "l_deferral": "wider clients remain deferred to L0 planning",
        "deployment_deferral": "deployment remains operator-gated and out of scope",
        "remediation_required": False,
        "reason": "H6 web archive/news/event policy, fixture, blocked-live-probe, review, and quality artifacts are coherent enough to plan H7 without enabling fetches, crawling, downloads, sensitive-source access, or truth acceptance.",
        "limitations": ["No approved H6 live metadata probe completed; fixture-equivalent outputs carry the review integration."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
    }
    _raise_if_invalid(recommendation, policy)
    return recommendation


def build_h6_integration_audit(
    review_result: Mapping[str, Any],
    quality_delta: Mapping[str, Any],
    postmortem: Mapping[str, Any],
    recommendation: Mapping[str, Any] | None = None,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    recommendation = dict(recommendation or build_h6_next_phase_recommendation(postmortem, policy))
    review_summary = summarize_h6_review_integration(review_result)
    audit = {
        "schema_version": "h6_web_archive_integration_audit.v0",
        "audit_id": f"h6.integration_audit.{_digest({'review': review_result, 'delta': quality_delta, 'postmortem': postmortem})[:12]}.v0",
        "wave_id": "H6",
        "audited_sources": list(review_result.get("sources", [])),
        "audited_tasks": ["H6-BUNDLE-01", "H6-BUNDLE-02", "H6-BUNDLE-03", "H6-BUNDLE-04"],
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
        "quality_delta_summary": summarize_h6_quality_delta(quality_delta),
        "postmortem_summary": summarize_h6_postmortem(postmortem),
        "sensitive_source_policy_summary": {"restricted_public_document_manifest": "blocked_by_default"},
        "blockers": [],
        "warnings": ["H6 live probes remain blocked pending operator approval"] if review_result.get("blocked_sources") else [],
        "h6_exit_gate": "PASS_WITH_WARNINGS" if review_result.get("blocked_sources") else "PASS",
        "next_phase_recommendation": recommendation.get("recommendation_status", "READY_FOR_H7_BUNDLE_01"),
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["H6 passes with warnings for H7 policy-pack planning using fixture-equivalent outputs."],
    }
    apply_missing_source_gate(audit)
    _raise_if_invalid(audit, policy)
    return audit


def summarize_h6_postmortem(postmortem: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    errors = detect_h6_quality_overclaim(postmortem, policy)
    return {
        "schema_version": "h6_connector_wave_postmortem_summary.v0",
        "status": "pass" if not errors else "invalid",
        "postmortem_id": postmortem.get("postmortem_id"),
        "next_phase_recommendation": postmortem.get("next_phase_recommendation"),
        "h7_or_j1_k_l_recommendation": postmortem.get("h7_or_j1_k_l_recommendation"),
        "auto_approves_future_connectors": False,
        "errors": errors,
    }


def apply_missing_source_gate(integration_audit: dict[str, Any], required_sources: tuple[str, ...] = H6_SOURCE_IDS) -> dict[str, Any]:
    missing = [source for source in required_sources if source not in integration_audit.get("audited_sources", [])]
    if missing:
        integration_audit["h6_exit_gate"] = "PARTIAL"
        integration_audit["next_phase_recommendation"] = "NEEDS_REMEDIATION"
        integration_audit.setdefault("blockers", []).append(f"missing audited sources: {', '.join(missing)}")
    return integration_audit


def _truth_boundary() -> dict[str, bool]:
    return {
        "web_capture_seed_accepts_capture_truth": False,
        "archived_time_state_seed_accepts_historical_truth": False,
        "news_event_seed_accepts_event_truth": False,
        "dead_link_seed_grants_acquisition_permission": False,
        "public_document_seed_accepts_public_document_truth": False,
        "media_transcript_seed_accepts_full_context_truth": False,
        "source_cache_review_seed_accepts_source": False,
        "evidence_review_seed_accepts_evidence": False,
        "candidate_promotion_preview_promotes_candidate": False,
        "source_pack_preview_is_imported_or_submitted": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "rights_clearance_claimed": False,
        "privacy_safety_claimed": False,
        "malware_safety_claimed": False,
        "verified_authenticity_claimed": False,
        "production_readiness_claimed": False,
        "automatic_future_connector_approval": False,
        "accepted_web_capture_truth": False,
        "accepted_archived_time_state_truth": False,
        "accepted_event_truth": False,
        "accepted_article_truth": False,
        "accepted_public_document_truth": False,
        "accepted_privacy_safety_truth": False,
        "accepted_source_truth": False,
        "accepted_evidence_truth": False,
        "accepted_candidate_truth": False,
    }


def _product_boundary() -> dict[str, bool]:
    return {
        "changed_public_search_behavior": False,
        "enabled_hosting": False,
        "enabled_source_sync": False,
        "enabled_fetching": False,
        "enabled_crawling": False,
        "enabled_downloads": False,
        "enabled_uploads": False,
        "enabled_accounts": False,
        "enabled_telemetry": False,
        "enabled_cdx_query": False,
        "enabled_memento_lookup": False,
        "enabled_warc_wacz_fetch": False,
        "enabled_archived_page_fetch": False,
        "enabled_media_downloads": False,
        "enabled_scraping_crawling": False,
        "enabled_sensitive_source_access": False,
        "mutated_public_index": False,
        "mutated_master_index": False,
    }


def _raise_if_invalid(payload: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> None:
    errors = detect_h6_quality_overclaim(payload, policy)
    errors.extend(detect_h6_review_truth_boundary_violations(payload, policy))
    errors.extend(detect_h6_review_product_boundary_violations(payload, policy))
    if errors:
        raise ValueError("; ".join(sorted(dict.fromkeys(errors))))


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, default=str).encode("utf-8")).hexdigest()
