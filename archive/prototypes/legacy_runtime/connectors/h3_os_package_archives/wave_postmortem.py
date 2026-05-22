"""H3 OS package archive wave postmortem and next-phase helpers."""

from __future__ import annotations

from collections.abc import Mapping
import hashlib
import json
from typing import Any

from archive.prototypes.legacy_runtime.connectors.h3_os_package_archives.normalizer_common import H3_SOURCE_IDS
from archive.prototypes.legacy_runtime.connectors.h3_os_package_archives.quality_delta import detect_h3_quality_overclaim, summarize_h3_quality_delta
from archive.prototypes.legacy_runtime.connectors.h3_os_package_archives.review_integration import (
    detect_h3_review_product_boundary_violations,
    detect_h3_review_truth_boundary_violations,
    summarize_h3_review_integration,
)


def build_h3_connector_wave_postmortem(
    review_result: Mapping[str, Any],
    quality_delta: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a non-promotional H3 connector-wave postmortem."""

    blocked_sources = list(review_result.get("blocked_sources") or [])
    postmortem = {
        "schema_version": "h3_os_package_connector_wave_postmortem.v0",
        "postmortem_id": f"h3.connector_wave_postmortem.{_digest({'review': review_result, 'delta': quality_delta})[:12]}.v0",
        "wave_id": "H3",
        "what_worked": [
            "Thirteen H3 OS package archive sources have policy packs, fixtures, normalizers, replay outputs, and review previews.",
            "OS package identity, compatibility, dependency/conflict/provides, and file/hash candidates remain review-gated and candidate-only.",
            "Live-probe outputs failed closed when committed source approvals were missing.",
        ],
        "what_failed": ["No H3 source has committed operator approval for a live metadata probe."] if blocked_sources else [],
        "blocked_sources": blocked_sources,
        "fixture_gaps": ["Fixtures are synthetic/public-safe and do not prove live archive behavior."],
        "live_probe_gaps": ["Blocked live probes provide gate evidence but no completed metadata response."] if blocked_sources else [],
        "normalizer_gaps": ["Normalizers cover metadata fixture shapes, not package payloads or repository mirrors."],
        "os_package_identity_gaps": ["PURL-style and OS identity candidates require review before any identity use."],
        "os_platform_compatibility_gaps": ["Compatibility candidates are not verified compatibility facts."],
        "dependency_mapping_gaps": ["Dependency candidates do not prove dependency correctness or environment solvability."],
        "conflict_provides_mapping_gaps": ["Conflict/provides candidates remain source observations only."],
        "file_hash_mapping_gaps": ["File/hash candidates do not grant download permission or malware safety."],
        "policy_gaps": ["source-specific live probe approvals remain absent"] if blocked_sources else [],
        "evidence_mapping_gaps": ["Evidence candidates remain previews only."],
        "review_mapping_gaps": ["Review seeds are not human review decisions and are not persisted."],
        "quality_delta_summary": summarize_h3_quality_delta(quality_delta, policy),
        "scorecard_summary": {
            "scorecard_update_count": quality_delta.get("scorecard_update_count", 0),
            "production_ready": False,
            "auto_approves_future_connectors": False,
        },
        "safety_boundary_assessment": {
            "network_calls_made": False,
            "repository_index_sync_enabled": False,
            "downloads_made": False,
            "package_manager_invoked": False,
            "install_execute_enabled": False,
            "source_sync_enabled": False,
            "accepted_truth": False,
            "public_index_mutated": False,
            "master_index_mutated": False,
            "boundary_result": "preserved",
        },
        "next_phase_recommendation": "READY_FOR_H4_BUNDLE_01",
        "h4_or_j1_k_l_recommendation": "proceed_to_h4_policy_packs; keep_j1_k_l_deferred",
        "do_not_repeat_risks": [
            "Do not treat OS package metadata as identity or compatibility truth.",
            "Do not use fixture replay as live access approval.",
            "Do not let package file metadata become repository index sync or download permission.",
        ],
        "auto_approves_future_connectors": False,
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["Postmortem recommends H4 policy packs, not risky actions or production readiness."],
    }
    _raise_if_invalid(postmortem, policy)
    return postmortem


def build_h3_next_phase_recommendation(postmortem: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Build the H3 next-phase recommendation."""

    recommendation = {
        "schema_version": "h3_os_package_next_phase_recommendation.v0",
        "recommendation_id": f"h3.next_phase.{_digest(postmortem)[:12]}.v0",
        "wave_id": "H3",
        "recommended_next_task": "H4-BUNDLE-01 - Code/source/release host source-family policy packs",
        "recommendation_status": "READY_FOR_H4_BUNDLE_01",
        "alternatives_considered": ["J1-POLICY-01", "K0-BUNDLE-01", "L0-BUNDLE-01", "H3-REMEDIATION-04"],
        "h4_readiness": "ready_with_fixture_equivalent_h3_outputs",
        "j1_deferral": "risky download/install/execute actions remain deferred to J1",
        "k_deferral": "semantic/AI assist remains deferred to K0 typed no-truth policy",
        "l_deferral": "wider clients remain deferred to L0 planning",
        "deployment_deferral": "deployment remains operator-gated and out of scope",
        "remediation_required": False,
        "reason": "H3 OS package archive policy, fixture, blocked-live-probe, review, and quality artifacts are coherent enough to plan H4 without enabling risky actions.",
        "limitations": ["No approved H3 live metadata probe completed; fixture-equivalent outputs carry the review integration."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
    }
    _raise_if_invalid(recommendation, policy)
    return recommendation


def build_h3_integration_audit(
    review_result: Mapping[str, Any],
    quality_delta: Mapping[str, Any],
    postmortem: Mapping[str, Any],
    recommendation: Mapping[str, Any] | None = None,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the H3 integration audit result."""

    recommendation = dict(recommendation or build_h3_next_phase_recommendation(postmortem, policy))
    review_summary = summarize_h3_review_integration(review_result)
    audit = {
        "schema_version": "h3_os_package_integration_audit.v0",
        "audit_id": f"h3.integration_audit.{_digest({'review': review_result, 'delta': quality_delta, 'postmortem': postmortem})[:12]}.v0",
        "wave_id": "H3",
        "audited_sources": list(review_result.get("sources", [])),
        "audited_tasks": ["H3-BUNDLE-01", "H3-BUNDLE-02", "H3-BUNDLE-03", "H3-BUNDLE-04"],
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
        "quality_delta_summary": summarize_h3_quality_delta(quality_delta),
        "postmortem_summary": summarize_h3_postmortem(postmortem),
        "blockers": [],
        "warnings": ["H3 live probes remain blocked pending operator approval"] if review_result.get("blocked_sources") else [],
        "h3_exit_gate": "PASS_WITH_WARNINGS" if review_result.get("blocked_sources") else "PASS",
        "next_phase_recommendation": recommendation.get("recommendation_status", "READY_FOR_H4_BUNDLE_01"),
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["H3 passes with warnings for H4 policy-pack planning using fixture-equivalent outputs."],
    }
    apply_missing_source_gate(audit)
    _raise_if_invalid(audit, policy)
    return audit


def summarize_h3_postmortem(postmortem: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    errors = detect_h3_quality_overclaim(postmortem, policy)
    return {
        "schema_version": "h3_connector_wave_postmortem_summary.v0",
        "status": "pass" if not errors else "invalid",
        "postmortem_id": postmortem.get("postmortem_id"),
        "next_phase_recommendation": postmortem.get("next_phase_recommendation"),
        "h4_or_j1_k_l_recommendation": postmortem.get("h4_or_j1_k_l_recommendation"),
        "auto_approves_future_connectors": False,
        "errors": errors,
    }


def apply_missing_source_gate(integration_audit: dict[str, Any], required_sources: tuple[str, ...] = H3_SOURCE_IDS) -> dict[str, Any]:
    missing = [source for source in required_sources if source not in integration_audit.get("audited_sources", [])]
    if missing:
        integration_audit["h3_exit_gate"] = "PARTIAL"
        integration_audit["next_phase_recommendation"] = "NEEDS_REMEDIATION"
        integration_audit.setdefault("blockers", []).append(f"missing audited sources: {', '.join(missing)}")
    return integration_audit


def _truth_boundary() -> dict[str, bool]:
    return {
        "os_package_identity_seed_accepts_identity": False,
        "os_platform_compatibility_seed_accepts_compatibility": False,
        "dependency_seed_accepts_correctness": False,
        "package_file_seed_grants_download_or_safety": False,
        "source_cache_review_seed_accepts_source": False,
        "evidence_review_seed_accepts_evidence": False,
        "candidate_promotion_preview_promotes_candidate": False,
        "source_pack_preview_is_imported_or_submitted": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "rights_clearance_claimed": False,
        "malware_safety_claimed": False,
        "verified_installability_claimed": False,
        "dependency_correctness_claimed": False,
        "compatibility_correctness_claimed": False,
        "production_readiness_claimed": False,
        "h3_postmortem_enables_future_connectors_automatically": False,
        "automatic_future_connector_approval": False,
    }


def _product_boundary() -> dict[str, bool]:
    return {
        "changed_public_search_behavior": False,
        "enabled_hosting": False,
        "enabled_source_sync": False,
        "enabled_repository_index_sync": False,
        "enabled_downloads": False,
        "enabled_uploads": False,
        "enabled_accounts": False,
        "enabled_telemetry": False,
        "enabled_installers": False,
        "enabled_execution": False,
        "mutated_public_index": False,
        "mutated_master_index": False,
        "repository_index_sync_enabled": False,
        "repository_mirror_enabled": False,
        "package_download_enabled": False,
        "package_manager_invocation_enabled": False,
        "install_execute_enabled": False,
    }


def _raise_if_invalid(payload: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> None:
    errors = detect_h3_quality_overclaim(payload, policy)
    errors.extend(detect_h3_review_truth_boundary_violations(payload, policy))
    errors.extend(detect_h3_review_product_boundary_violations(payload, policy))
    if errors:
        raise ValueError("; ".join(sorted(dict.fromkeys(errors))))


def _digest(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
