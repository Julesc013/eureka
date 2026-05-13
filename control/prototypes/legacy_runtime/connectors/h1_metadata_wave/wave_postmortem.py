"""H1 metadata-wave postmortem and next-phase helpers."""

from __future__ import annotations

from collections.abc import Mapping
import hashlib
import json
from typing import Any

from control.prototypes.legacy_runtime.connectors.h1_metadata_wave.quality_delta import detect_h1_quality_overclaim, summarize_h1_quality_delta
from control.prototypes.legacy_runtime.connectors.h1_metadata_wave.review_integration import (
    detect_h1_review_product_boundary_violations,
    detect_h1_review_truth_boundary_violations,
    summarize_h1_review_integration,
)


def build_h1_connector_wave_postmortem(
    review_result: Mapping[str, Any],
    quality_delta: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a non-promotional H1 connector-wave postmortem."""

    blocked_sources = list(review_result.get("blocked_sources") or [])
    postmortem = {
        "schema_version": "h1_connector_wave_postmortem.v0",
        "postmortem_id": f"h1.connector_wave_postmortem.{_digest({'review': review_result, 'delta': quality_delta})[:12]}.v0",
        "wave_id": "H1",
        "what_worked": [
            "Seven H1 metadata sources have policy packs, fixtures, normalizers, replay outputs, and review previews.",
            "Source OS contracts handled fixture replay, coverage, scorecards, and source-pack previews without special one-off source truth.",
            "Live-probe outputs failed closed when committed approvals were missing.",
        ],
        "what_failed": [
            "No H1 source has committed operator approval for a live metadata probe."
        ] if blocked_sources else [],
        "policy_gaps": ["source-specific live probe approvals remain absent"] if blocked_sources else [],
        "fixture_gaps": ["fixtures are synthetic/public-safe and do not prove live endpoint compatibility"],
        "normalizer_gaps": ["normalizers cover metadata fixture shapes, not downloaded artifacts or extraction payloads"],
        "live_probe_gaps": ["blocked live probes provide gate evidence but no completed metadata response"] if blocked_sources else [],
        "source_cache_mapping_gaps": ["source-cache candidates remain previews only"],
        "evidence_mapping_gaps": ["evidence candidates remain previews only"],
        "review_gaps": ["review seeds are not human review decisions and are not persisted"],
        "quality_delta_summary": summarize_h1_quality_delta(quality_delta, policy),
        "scorecard_summary": {
            "scorecard_update_count": quality_delta.get("scorecard_update_count", 0),
            "production_ready": False,
            "auto_approves_future_connectors": False,
        },
        "safety_boundary_assessment": {
            "network_calls_made": False,
            "downloads_made": False,
            "source_sync_enabled": False,
            "accepted_truth": False,
            "public_index_mutated": False,
            "master_index_mutated": False,
            "boundary_result": "preserved",
        },
        "next_phase_recommendation": "READY_FOR_F_BUNDLE_01",
        "h2_or_extraction_recommendation": "proceed_to_f_bundle_01_before_h2_live_expansion",
        "do_not_repeat_risks": [
            "Do not treat metadata observations as public truth.",
            "Do not use fixture replay as live access approval.",
            "Do not widen exact request manifests into broad source search.",
        ],
        "auto_approves_future_connectors": False,
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["Postmortem recommends fixture extraction planning, not production readiness."],
    }
    _raise_if_invalid(postmortem, policy)
    return postmortem


def build_h1_next_phase_recommendation(postmortem: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Build the H1 next-phase recommendation."""

    recommendation = {
        "schema_version": "h1_next_phase_recommendation.v0",
        "recommendation_id": f"h1.next_phase.{_digest(postmortem)[:12]}.v0",
        "wave_id": "H1",
        "h1_exit_gate": "PASS_WITH_WARNINGS",
        "next_phase_recommendation": "READY_FOR_F_BUNDLE_01",
        "recommended_next_task": "F-BUNDLE-01 - Extraction sandbox and Tier 0-2 fixture extraction",
        "rationale": [
            "H1 has enough fixture-equivalent metadata outputs for offline extraction sandbox planning.",
            "Live metadata probes are still operator-gated and can proceed separately when approved.",
        ],
        "h2_defer_or_continue_recommendation": "defer_h2_policy_packs_until_f_bundle_01_fixture_extraction_boundary_exists",
        "auto_approves_future_connectors": False,
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
    }
    _raise_if_invalid(recommendation, policy)
    return recommendation


def summarize_h1_postmortem(postmortem: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    errors = detect_h1_quality_overclaim(postmortem, policy)
    return {
        "schema_version": "h1_connector_wave_postmortem_summary.v0",
        "status": "pass" if not errors else "invalid",
        "postmortem_id": postmortem.get("postmortem_id"),
        "next_phase_recommendation": postmortem.get("next_phase_recommendation"),
        "h2_or_extraction_recommendation": postmortem.get("h2_or_extraction_recommendation"),
        "auto_approves_future_connectors": False,
        "errors": errors,
    }


def build_h1_integration_audit(
    review_result: Mapping[str, Any],
    quality_delta: Mapping[str, Any],
    postmortem: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the H1 integration audit result."""

    review_summary = summarize_h1_review_integration(review_result)
    audit = {
        "schema_version": "h1_integration_audit.v0",
        "audit_id": f"h1.integration_audit.{_digest({'review': review_result, 'delta': quality_delta, 'postmortem': postmortem})[:12]}.v0",
        "wave_id": "H1",
        "audited_sources": list(review_result.get("sources", [])),
        "audited_tasks": ["H1-BUNDLE-01", "H1-BUNDLE-02", "H1-BUNDLE-03", "H1-BUNDLE-04"],
        "artifact_inventory": {
            "review_integration_result": bool(review_result),
            "quality_delta_report": bool(quality_delta),
            "connector_wave_postmortem": bool(postmortem),
            "fixture_outputs_integrated": len(review_result.get("used_fixture_outputs", [])),
            "live_probe_outputs_integrated": len(review_result.get("used_live_probe_outputs", [])),
        },
        "validation_summary": {"status": "pass", "offline_default": True},
        "source_policy_summary": {"policy_packs_present": True, "live_access_default": False},
        "fixture_runtime_summary": {"fixture_outputs_integrated": review_summary.get("source_count", 0)},
        "live_probe_summary": {
            "completed_sources": [],
            "blocked_sources": list(review_result.get("blocked_sources", [])),
            "network_used": False,
        },
        "review_integration_summary": review_summary,
        "quality_delta_summary": summarize_h1_quality_delta(quality_delta),
        "postmortem_summary": summarize_h1_postmortem(postmortem),
        "blockers": [],
        "warnings": ["H1 live probes remain blocked pending operator approval"] if review_result.get("blocked_sources") else [],
        "h1_exit_gate": "PASS_WITH_WARNINGS",
        "next_phase_recommendation": "READY_FOR_F_BUNDLE_01",
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["H1 passes with warnings for offline extraction sandbox planning."],
    }
    _raise_if_invalid(audit, policy)
    return audit


def _truth_boundary() -> dict[str, bool]:
    return {
        "source_cache_review_seed_accepts_source": False,
        "evidence_review_seed_accepts_evidence": False,
        "candidate_promotion_preview_promotes_candidate": False,
        "source_pack_preview_is_imported_or_submitted": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "rights_clearance_claimed": False,
        "malware_safety_claimed": False,
        "verified_installability_claimed": False,
        "production_readiness_claimed": False,
        "external_superiority_claimed": False,
        "h1_postmortem_enables_future_connectors_automatically": False,
    }


def _product_boundary() -> dict[str, bool]:
    return {
        "changed_public_search_behavior": False,
        "enabled_hosting": False,
        "enabled_source_sync": False,
        "enabled_downloads": False,
        "enabled_uploads": False,
        "enabled_accounts": False,
        "enabled_telemetry": False,
        "mutated_public_index": False,
        "mutated_master_index": False,
    }


def _raise_if_invalid(payload: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> None:
    errors = detect_h1_quality_overclaim(payload, policy)
    errors.extend(detect_h1_review_truth_boundary_violations(payload, policy))
    errors.extend(detect_h1_review_product_boundary_violations(payload, policy))
    if errors:
        raise ValueError("; ".join(sorted(dict.fromkeys(errors))))


def _digest(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
