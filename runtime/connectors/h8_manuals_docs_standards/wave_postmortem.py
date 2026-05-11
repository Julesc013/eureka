"""H8 manuals/docs/standards wave postmortem and next-phase helpers."""

from __future__ import annotations

from collections.abc import Mapping
import hashlib
import json
from typing import Any

from runtime.connectors.h8_manuals_docs_standards.normalizer_common import H8_SOURCE_IDS
from runtime.connectors.h8_manuals_docs_standards.quality_delta import detect_h8_quality_overclaim, summarize_h8_quality_delta
from runtime.connectors.h8_manuals_docs_standards.review_integration import (
    detect_h8_review_product_boundary_violations,
    detect_h8_review_truth_boundary_violations,
    summarize_h8_review_integration,
)


def build_h8_connector_wave_postmortem(review_result: Mapping[str, Any], quality_delta: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    blocked_sources = list(review_result.get("blocked_sources") or [])
    postmortem = {
        "schema_version": "h8_manuals_docs_connector_wave_postmortem.v0",
        "postmortem_id": f"h8.connector_wave_postmortem.{_digest({'review': review_result, 'delta': quality_delta})[:12]}.v0",
        "wave_id": "H8",
        "what_worked": [
            "Eighteen H8 manuals/docs/standards sources have policy packs, fixtures, normalizers, replay outputs, fail-closed live-probe envelopes, and review previews.",
            "Technical document, manual-artifact, datasheet/device, standards/specification, install requirement, repair/service/safety, and access-rights candidates remain review-gated and candidate-only.",
            "Live-probe outputs failed closed when committed source approvals were missing.",
        ],
        "what_failed": ["No H8 source has committed operator approval for a live metadata probe."] if blocked_sources else [],
        "blocked_sources": blocked_sources,
        "fixture_gaps": ["Fixtures are synthetic/public-safe and do not prove live manuals/docs/standards behavior."],
        "live_probe_gaps": ["Blocked live probes provide gate evidence but no completed metadata response."] if blocked_sources else [],
        "normalizer_gaps": ["Normalizers cover metadata fixture shapes, not PDFs, manuals, datasheets, standards documents, schematics, service manuals, OCR/full text, media, scraping, or crawling."],
        "technical_document_identity_gaps": ["Technical document identity candidates require review before any document identity use."],
        "manual_artifact_relation_gaps": ["Manual-artifact relation candidates are not applicability, compatibility, installability, repair safety, or rights truth."],
        "datasheet_device_identity_gaps": ["Datasheet/device candidates are not device truth, lifecycle availability, electrical safety, or engineering guidance."],
        "standards_specification_identity_gaps": ["Standards/specification candidates are not standards truth, conformance proof, or standards-document access permission."],
        "install_requirement_claim_gaps": ["Install requirement candidates are not installability, compatibility correctness, safe execution guidance, or action permission."],
        "repair_service_safety_gaps": ["Repair/service/safety candidates are not repair safety, electrical safety, calibration permission, or action authorization."],
        "access_rights_gaps": ["Access/rights candidates are not rights clearance, open-access truth, redistribution permission, or download permission."],
        "restricted_source_policy_gaps": ["Paywalled, restricted, licensed, standards-body controlled, and rights-sensitive sources remain policy-blocked by default."],
        "policy_gaps": ["source-specific live probe approvals remain absent"] if blocked_sources else [],
        "evidence_mapping_gaps": ["Evidence candidates remain previews only."],
        "review_mapping_gaps": ["Review seeds are not human review decisions and are not persisted."],
        "quality_delta_summary": summarize_h8_quality_delta(quality_delta, policy),
        "scorecard_summary": {
            "scorecard_update_count": quality_delta.get("scorecard_update_count", 0),
            "production_ready": False,
            "auto_approves_future_connectors": False,
        },
        "safety_boundary_assessment": {
            "network_calls_made": False,
            "api_catalog_query_enabled": False,
            "document_fetch_enabled": False,
            "download_enabled": False,
            "full_text_ocr_enabled": False,
            "scraping_crawling_enabled": False,
            "restricted_source_access_enabled": False,
            "repair_or_install_action_permission": False,
            "source_sync_enabled": False,
            "accepted_truth": False,
            "public_index_mutated": False,
            "master_index_mutated": False,
            "boundary_result": "preserved",
        },
        "next_phase_recommendation": "READY_FOR_H9_BUNDLE_01",
        "h9_or_j1_k_l_recommendation": "proceed_to_h9_policy_packs; keep_j1_k_l_deferred",
        "do_not_repeat_risks": [
            "Do not treat manuals/docs/standards metadata as documentation completeness, standards compliance, compatibility correctness, installability, repair safety, electrical safety, access rights, rights clearance, open-access truth, malware safety, verified authenticity, or public truth.",
            "Do not use fixture replay or blocked probes as live access approval.",
            "Do not let access metadata become query, fetch, download, extraction, repair, install, or acquisition permission.",
        ],
        "source_os_reuse_assessment": "H8 reused H0-H7 Source OS review gates while preserving technical-document-specific boundaries.",
        "h9_handoff_recommendation": "H9-BUNDLE-01 may start policy-pack-only work for media, music, image, video, and map sources.",
        "j1_k_l_deferral_recommendation": "J1 risky actions, K semantic/AI, and L wider clients remain deferred unless explicit gates open.",
        "risks": ["Live H8 metadata probes remain blocked pending operator approval."] if blocked_sources else [],
        "no_goals_preserved": ["no_api_catalog_query", "no_document_fetch", "no_downloads", "no_full_text_ocr", "no_iiif_media_fetch", "no_scrape_crawl", "no_restricted_source_access", "no_repair_install_action", "no_truth_acceptance", "no_public_index_mutation"],
        "auto_approves_future_connectors": False,
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["Postmortem recommends H9 policy packs, not risky actions or production readiness."],
    }
    _raise_if_invalid(postmortem, policy)
    return postmortem


def build_h8_next_phase_recommendation(postmortem: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    recommendation = {
        "schema_version": "h8_manuals_docs_next_phase_recommendation.v0",
        "recommendation_id": f"h8.next_phase.{_digest(postmortem)[:12]}.v0",
        "wave_id": "H8",
        "recommended_next_task": "H9-BUNDLE-01 - Media, music, image, video, and map source-family policy packs",
        "recommendation_status": "READY_FOR_H9_BUNDLE_01",
        "alternatives_considered": ["J1-POLICY-01", "K0-BUNDLE-01", "L0-BUNDLE-01", "H8-REMEDIATION-04"],
        "h9_readiness": "ready_with_fixture_equivalent_h8_outputs",
        "j1_deferral": "risky query/fetch/download/extract/repair/install/acquisition actions remain deferred to J1",
        "k_deferral": "semantic/AI assist remains deferred to K0 typed no-truth policy",
        "l_deferral": "wider clients remain deferred to L0 planning",
        "deployment_deferral": "deployment remains operator-gated and out of scope",
        "remediation_required": False,
        "reason": "H8 manuals/docs/standards policy, fixture, blocked-live-probe, review, and quality artifacts are coherent enough to plan H9 without enabling queries, fetches, crawling, downloads, extraction, restricted-source access, repair/install actions, or truth acceptance.",
        "limitations": ["No approved H8 live metadata probe completed; fixture-equivalent outputs carry the review integration."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
    }
    _raise_if_invalid(recommendation, policy)
    return recommendation


def build_h8_integration_audit(
    review_result: Mapping[str, Any],
    quality_delta: Mapping[str, Any],
    postmortem: Mapping[str, Any],
    recommendation: Mapping[str, Any] | None = None,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    recommendation = dict(recommendation or build_h8_next_phase_recommendation(postmortem, policy))
    review_summary = summarize_h8_review_integration(review_result)
    audit = {
        "schema_version": "h8_manuals_docs_integration_audit.v0",
        "audit_id": f"h8.integration_audit.{_digest({'review': review_result, 'delta': quality_delta, 'postmortem': postmortem})[:12]}.v0",
        "wave_id": "H8",
        "audited_sources": list(review_result.get("sources", [])),
        "audited_tasks": ["H8-BUNDLE-01", "H8-BUNDLE-02", "H8-BUNDLE-03", "H8-BUNDLE-04"],
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
        "quality_delta_summary": summarize_h8_quality_delta(quality_delta),
        "postmortem_summary": summarize_h8_postmortem(postmortem),
        "restricted_source_policy_summary": {"restricted_or_licensed_sources": "blocked_by_default"},
        "safety_boundary_summary": {"repair_install_electrical_actions": "blocked"},
        "blockers": [],
        "warnings": ["H8 live probes remain blocked pending operator approval"] if review_result.get("blocked_sources") else [],
        "h8_exit_gate": "PASS_WITH_WARNINGS" if review_result.get("blocked_sources") else "PASS",
        "next_phase_recommendation": recommendation.get("recommendation_status", "READY_FOR_H9_BUNDLE_01"),
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["H8 passes for H9 policy-pack planning using fixture-equivalent outputs."],
    }
    apply_missing_source_gate(audit)
    _raise_if_invalid(audit, policy)
    return audit


def summarize_h8_postmortem(postmortem: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    errors = detect_h8_quality_overclaim(postmortem, policy)
    return {
        "schema_version": "h8_connector_wave_postmortem_summary.v0",
        "status": "pass" if not errors else "invalid",
        "postmortem_id": postmortem.get("postmortem_id"),
        "next_phase_recommendation": postmortem.get("next_phase_recommendation"),
        "h9_or_j1_k_l_recommendation": postmortem.get("h9_or_j1_k_l_recommendation"),
        "auto_approves_future_connectors": False,
        "errors": errors,
    }


def apply_missing_source_gate(integration_audit: dict[str, Any], required_sources: tuple[str, ...] = H8_SOURCE_IDS) -> dict[str, Any]:
    missing = [source for source in required_sources if source not in integration_audit.get("audited_sources", [])]
    if missing:
        integration_audit["h8_exit_gate"] = "PARTIAL"
        integration_audit["next_phase_recommendation"] = "NEEDS_REMEDIATION"
        integration_audit.setdefault("blockers", []).append(f"missing audited sources: {', '.join(missing)}")
    return integration_audit


def _truth_boundary() -> dict[str, bool]:
    return {
        "technical_document_seed_accepts_document_truth": False,
        "manual_artifact_seed_accepts_relation_truth": False,
        "datasheet_device_seed_accepts_device_truth": False,
        "standards_specification_seed_accepts_standards_truth": False,
        "install_requirement_seed_accepts_installability_truth": False,
        "repair_service_safety_seed_accepts_safety_truth": False,
        "access_rights_seed_accepts_rights_truth": False,
        "source_cache_review_seed_accepts_source": False,
        "evidence_review_seed_accepts_evidence": False,
        "candidate_promotion_preview_promotes_candidate": False,
        "source_pack_preview_is_imported_or_submitted": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "rights_clearance_claimed": False,
        "open_access_truth_claimed": False,
        "compatibility_correctness_claimed": False,
        "installability_claimed": False,
        "repair_safety_claimed": False,
        "electrical_safety_claimed": False,
        "malware_safety_claimed": False,
        "verified_authenticity_claimed": False,
        "production_readiness_claimed": False,
        "automatic_future_connector_approval": False,
        "accepted_document_truth": False,
        "accepted_manual_artifact_relation_truth": False,
        "accepted_datasheet_device_truth": False,
        "accepted_standards_truth": False,
        "accepted_install_requirement_truth": False,
        "accepted_repair_service_safety_truth": False,
        "accepted_access_rights_truth": False,
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
        "enabled_extraction": False,
        "enabled_crawling": False,
        "enabled_uploads": False,
        "enabled_accounts": False,
        "enabled_telemetry": False,
        "mutated_public_index": False,
        "mutated_master_index": False,
    }


def _raise_if_invalid(payload: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> None:
    errors = detect_h8_quality_overclaim(payload, policy)
    errors.extend(detect_h8_review_truth_boundary_violations(payload, policy))
    errors.extend(detect_h8_review_product_boundary_violations(payload, policy))
    if errors:
        raise ValueError("; ".join(sorted(dict.fromkeys(errors))))


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, default=str).encode("utf-8")).hexdigest()
