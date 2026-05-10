"""H5 vendor/update/driver wave postmortem and next-phase helpers."""

from __future__ import annotations

from collections.abc import Mapping
import hashlib
import json
from typing import Any

from runtime.connectors.h5_vendor_update_driver.normalizer_common import H5_SOURCE_IDS
from runtime.connectors.h5_vendor_update_driver.quality_delta import detect_h5_quality_overclaim, summarize_h5_quality_delta
from runtime.connectors.h5_vendor_update_driver.review_integration import (
    detect_h5_review_product_boundary_violations,
    detect_h5_review_truth_boundary_violations,
    summarize_h5_review_integration,
)


def build_h5_connector_wave_postmortem(review_result: Mapping[str, Any], quality_delta: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    blocked_sources = list(review_result.get("blocked_sources") or [])
    postmortem = {
        "schema_version": "h5_vendor_update_connector_wave_postmortem.v0",
        "postmortem_id": f"h5.connector_wave_postmortem.{_digest({'review': review_result, 'delta': quality_delta})[:12]}.v0",
        "wave_id": "H5",
        "what_worked": [
            "Fifteen H5 vendor/update/driver/firmware/runtime sources have policy packs, fixtures, normalizers, replay outputs, and review previews.",
            "Vendor identity, driver/device compatibility, firmware/update, runtime redistributable, and payload metadata candidates remain review-gated and candidate-only.",
            "Live-probe outputs failed closed when committed source approvals were missing.",
        ],
        "what_failed": ["No H5 source has committed operator approval for a live metadata probe."] if blocked_sources else [],
        "blocked_sources": blocked_sources,
        "fixture_gaps": ["Fixtures are synthetic/public-safe and do not prove live vendor behavior."],
        "live_probe_gaps": ["Blocked live probes provide gate evidence but no completed metadata response."] if blocked_sources else [],
        "normalizer_gaps": ["Normalizers cover metadata fixture shapes, not catalogs, payloads, installers, firmware images, or vendor tools."],
        "vendor_identity_gaps": ["Vendor identity candidates require review before any identity or official-status use."],
        "driver_device_compatibility_gaps": ["Driver/device compatibility candidates are not verified compatibility or safe installability facts."],
        "firmware_update_gaps": ["Firmware/update candidates are not install, execute, download, or flash permission."],
        "runtime_redistributable_gaps": ["Runtime redistributable candidates are not installability or dependency correctness proof."],
        "payload_metadata_gaps": ["Payload metadata does not grant download permission, safety, authenticity, or rights clearance."],
        "policy_gaps": ["source-specific live probe approvals remain absent"] if blocked_sources else [],
        "evidence_mapping_gaps": ["Evidence candidates remain previews only."],
        "review_mapping_gaps": ["Review seeds are not human review decisions and are not persisted."],
        "quality_delta_summary": summarize_h5_quality_delta(quality_delta, policy),
        "scorecard_summary": {
            "scorecard_update_count": quality_delta.get("scorecard_update_count", 0),
            "production_ready": False,
            "auto_approves_future_connectors": False,
        },
        "safety_boundary_assessment": {
            "network_calls_made": False,
            "catalog_sync_enabled": False,
            "downloads_enabled": False,
            "vendor_tool_invocation_enabled": False,
            "firmware_flash_enabled": False,
            "install_execute_enabled": False,
            "source_sync_enabled": False,
            "accepted_truth": False,
            "public_index_mutated": False,
            "master_index_mutated": False,
            "boundary_result": "preserved",
        },
        "next_phase_recommendation": "READY_FOR_H6_BUNDLE_01",
        "h6_or_j1_k_l_recommendation": "proceed_to_h6_policy_packs; keep_j1_k_l_deferred",
        "do_not_repeat_risks": [
            "Do not treat vendor metadata as official status, compatibility, authenticity, safety, installability, rights, malware, or public truth.",
            "Do not use fixture replay as live access approval.",
            "Do not let payload metadata become download, install, execute, or firmware flashing permission.",
        ],
        "source_os_reuse_assessment": "H5 reused H0-H4 Source OS review gates while preserving vendor/update/driver-specific boundaries.",
        "h6_handoff_recommendation": "H6-BUNDLE-01 may start policy-pack-only work for web archive, news, and event sources.",
        "j1_k_l_deferral_recommendation": "J1 risky actions, K semantic/AI, and L wider clients remain deferred unless explicit gates open.",
        "risks": ["Live H5 metadata probes remain blocked pending operator approval."],
        "no_goals_preserved": ["no_catalog_sync", "no_download", "no_vendor_tool", "no_flash", "no_install_execute", "no_truth_acceptance", "no_public_index_mutation"],
        "auto_approves_future_connectors": False,
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["Postmortem recommends H6 policy packs, not risky actions or production readiness."],
    }
    _raise_if_invalid(postmortem, policy)
    return postmortem


def build_h5_next_phase_recommendation(postmortem: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    recommendation = {
        "schema_version": "h5_vendor_update_next_phase_recommendation.v0",
        "recommendation_id": f"h5.next_phase.{_digest(postmortem)[:12]}.v0",
        "wave_id": "H5",
        "recommended_next_task": "H6-BUNDLE-01 - Web archive, news, and event source-family policy packs",
        "recommendation_status": "READY_FOR_H6_BUNDLE_01",
        "alternatives_considered": ["J1-POLICY-01", "K0-BUNDLE-01", "L0-BUNDLE-01", "H5-REMEDIATION-04"],
        "h6_readiness": "ready_with_fixture_equivalent_h5_outputs",
        "j1_deferral": "risky download/install/execute/flash actions remain deferred to J1",
        "k_deferral": "semantic/AI assist remains deferred to K0 typed no-truth policy",
        "l_deferral": "wider clients remain deferred to L0 planning",
        "deployment_deferral": "deployment remains operator-gated and out of scope",
        "remediation_required": False,
        "reason": "H5 vendor/update/driver policy, fixture, blocked-live-probe, review, and quality artifacts are coherent enough to plan H6 without enabling catalog sync, downloads, tools, firmware flash, execution, or truth acceptance.",
        "limitations": ["No approved H5 live metadata probe completed; fixture-equivalent outputs carry the review integration."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
    }
    _raise_if_invalid(recommendation, policy)
    return recommendation


def build_h5_integration_audit(
    review_result: Mapping[str, Any],
    quality_delta: Mapping[str, Any],
    postmortem: Mapping[str, Any],
    recommendation: Mapping[str, Any] | None = None,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    recommendation = dict(recommendation or build_h5_next_phase_recommendation(postmortem, policy))
    review_summary = summarize_h5_review_integration(review_result)
    audit = {
        "schema_version": "h5_vendor_update_integration_audit.v0",
        "audit_id": f"h5.integration_audit.{_digest({'review': review_result, 'delta': quality_delta, 'postmortem': postmortem})[:12]}.v0",
        "wave_id": "H5",
        "audited_sources": list(review_result.get("sources", [])),
        "audited_tasks": ["H5-BUNDLE-01", "H5-BUNDLE-02", "H5-BUNDLE-03", "H5-BUNDLE-04"],
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
        "quality_delta_summary": summarize_h5_quality_delta(quality_delta),
        "postmortem_summary": summarize_h5_postmortem(postmortem),
        "blockers": [],
        "warnings": ["H5 live probes remain blocked pending operator approval"] if review_result.get("blocked_sources") else [],
        "h5_exit_gate": "PASS_WITH_WARNINGS" if review_result.get("blocked_sources") else "PASS",
        "next_phase_recommendation": recommendation.get("recommendation_status", "READY_FOR_H6_BUNDLE_01"),
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["H5 passes with warnings for H6 policy-pack planning using fixture-equivalent outputs."],
    }
    apply_missing_source_gate(audit)
    _raise_if_invalid(audit, policy)
    return audit


def summarize_h5_postmortem(postmortem: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    errors = detect_h5_quality_overclaim(postmortem, policy)
    return {
        "schema_version": "h5_connector_wave_postmortem_summary.v0",
        "status": "pass" if not errors else "invalid",
        "postmortem_id": postmortem.get("postmortem_id"),
        "next_phase_recommendation": postmortem.get("next_phase_recommendation"),
        "h6_or_j1_k_l_recommendation": postmortem.get("h6_or_j1_k_l_recommendation"),
        "auto_approves_future_connectors": False,
        "errors": errors,
    }


def apply_missing_source_gate(integration_audit: dict[str, Any], required_sources: tuple[str, ...] = H5_SOURCE_IDS) -> dict[str, Any]:
    missing = [source for source in required_sources if source not in integration_audit.get("audited_sources", [])]
    if missing:
        integration_audit["h5_exit_gate"] = "PARTIAL"
        integration_audit["next_phase_recommendation"] = "NEEDS_REMEDIATION"
        integration_audit.setdefault("blockers", []).append(f"missing audited sources: {', '.join(missing)}")
    return integration_audit


def _truth_boundary() -> dict[str, bool]:
    return {
        "vendor_identity_seed_accepts_vendor_truth": False,
        "driver_identity_seed_accepts_driver_truth": False,
        "firmware_identity_seed_accepts_firmware_truth": False,
        "runtime_identity_seed_accepts_runtime_truth": False,
        "compatibility_seed_accepts_compatibility_truth": False,
        "authenticity_seed_accepts_authenticity_truth": False,
        "safety_seed_accepts_safety_truth": False,
        "payload_seed_grants_download_or_safety": False,
        "source_cache_review_seed_accepts_source": False,
        "evidence_review_seed_accepts_evidence": False,
        "candidate_promotion_preview_promotes_candidate": False,
        "source_pack_preview_is_imported_or_submitted": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "rights_clearance_claimed": False,
        "malware_safety_claimed": False,
        "verified_installability_claimed": False,
        "verified_compatibility_claimed": False,
        "verified_authenticity_claimed": False,
        "production_readiness_claimed": False,
        "h5_postmortem_enables_future_connectors_automatically": False,
        "automatic_future_connector_approval": False,
    }


def _product_boundary() -> dict[str, bool]:
    return {
        "changed_public_search_behavior": False,
        "enabled_hosting": False,
        "enabled_source_sync": False,
        "enabled_catalog_sync": False,
        "enabled_downloads": False,
        "enabled_uploads": False,
        "enabled_accounts": False,
        "enabled_telemetry": False,
        "enabled_installers": False,
        "enabled_execution": False,
        "enabled_firmware_flashing": False,
        "enabled_vendor_tool_invocation": False,
        "mutated_public_index": False,
        "mutated_master_index": False,
        "catalog_fetch_enabled": False,
        "driver_download_enabled": False,
        "firmware_download_enabled": False,
        "runtime_download_enabled": False,
        "installer_download_enabled": False,
        "vendor_tool_invocation_enabled": False,
        "firmware_flash_enabled": False,
        "install_execute_enabled": False,
    }


def _raise_if_invalid(value: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> None:
    errors = detect_h5_quality_overclaim(value, policy) + detect_h5_review_truth_boundary_violations(value, policy) + detect_h5_review_product_boundary_violations(value, policy)
    if errors:
        raise ValueError("; ".join(sorted(dict.fromkeys(errors))))


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, default=str).encode("utf-8")).hexdigest()
