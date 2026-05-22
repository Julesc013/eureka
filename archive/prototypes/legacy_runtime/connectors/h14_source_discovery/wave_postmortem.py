"""H14 Source OS wave postmortem and next-phase helpers."""

from __future__ import annotations

from collections.abc import Mapping
import hashlib
import json
from typing import Any

from archive.prototypes.legacy_runtime.connectors.h14_source_discovery.normalizer_common import H14_SOURCE_IDS
from archive.prototypes.legacy_runtime.connectors.h14_source_discovery.quality_delta import detect_h14_quality_overclaim, summarize_h14_quality_delta
from archive.prototypes.legacy_runtime.connectors.h14_source_discovery.review_integration import (
    detect_h14_review_product_boundary_violations,
    detect_h14_review_registry_or_pack_mutation_violations,
    detect_h14_review_truth_boundary_violations,
    summarize_h14_review_integration,
)


def build_h14_connector_wave_postmortem(review_result: Mapping[str, Any], quality_delta: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    blocked_sources = list(review_result.get("blocked_sources") or [])
    postmortem = {
        "schema_version": "h14_source_discovery_connector_wave_postmortem.v0",
        "postmortem_id": f"h14.connector_wave_postmortem.{_digest({'review': review_result, 'delta': quality_delta})[:12]}.v0",
        "wave_id": "H14",
        "what_worked": [
            "H14 Source OS policy packs, fixture normalizers, rollup dry-run gates, review seeds, quality delta, and audit records align around candidate-only Source OS rollup evidence.",
            "SourceNeed, SourceCandidate, source discovery, pack, coverage, scorecard, reliability/freshness, dispute/revocation, lineage/provenance, cache, evidence, and pack-boundary outputs remain review-gated previews.",
            "Rollup dry-runs failed closed when source-specific approval was absent.",
        ],
        "what_failed": ["At least one H14 rollup dry-run concept remained blocked by policy and was represented by fixture-equivalent evidence only."] if blocked_sources else [],
        "blocked_sources": blocked_sources,
        "fixture_gaps": ["Fixtures are synthetic/public-safe and do not prove live source discovery, coverage completeness, reliability, freshness, rights clearance, or safety."],
        "rollup_dry_run_gaps": ["Blocked rollup dry-runs provide gate evidence but no approved rollup response."] if blocked_sources else [],
        "normalizer_gaps": ["Normalizers cover committed fixture and rollup shapes only, not live discovery, crawl, scrape, source sync, registry mutation, pack movement, or writes."],
        "source_need_gaps": ["SourceNeeds remain review inputs before any WorkUnit or source-plan approval."],
        "source_candidate_gaps": ["SourceCandidates remain candidate records and are not accepted source truth."],
        "source_discovery_gaps": ["Source discovery candidates do not run discovery or mutate registries."],
        "source_pack_manifest_gaps": ["Source pack manifests remain previews and are not exported, imported, signed, accepted, or published packs."],
        "connector_pack_manifest_gaps": ["Connector pack manifests do not approve connector runtime use."],
        "coverage_manifest_gaps": ["Coverage manifests are scoped claims and not exhaustive global coverage."],
        "connector_scorecard_gaps": ["Connector scorecards are review inputs and not connector approval or production readiness."],
        "reliability_freshness_gaps": ["Reliability/freshness signals remain candidates and not truth."],
        "dispute_revocation_gaps": ["Dispute/revocation records remain governance candidates and not automatic deletion."],
        "lineage_provenance_gaps": ["Lineage/provenance records remain candidates and do not auto-merge sources."],
        "pack_import_export_boundary_gaps": ["Pack import/export boundary previews grant no import, export, signing, publication, acceptance, or redistribution permission."],
        "registry_mutation_boundary_gaps": ["Source and connector registry mutation remains blocked pending future review."],
        "policy_gaps": ["source-specific rollup approvals are not universal"] if blocked_sources else [],
        "evidence_mapping_gaps": ["Evidence candidates remain previews only."],
        "review_mapping_gaps": ["Review seeds are not review decisions and are not persisted to a review queue."],
        "quality_delta_summary": summarize_h14_quality_delta(quality_delta, policy),
        "scorecard_summary": {"scorecard_update_count": quality_delta.get("scorecard_update_count", 0), "production_ready": False, "auto_approves_future_connectors": False},
        "source_os_rollup_assessment": "H14 is coherent for a policy-only F0 handoff using fixture/replay and approved-or-blocked rollup dry-run evidence.",
        "source_os_reuse_assessment": "H14 reused H0-H13 Source OS review gates while preserving no-live, no-pack, no-registry, no-write, and no-truth boundaries.",
        "next_phase_recommendation": "READY_FOR_F0_BUNDLE_01",
        "f_or_i_j_k_l_recommendation": "proceed_to_f0_extraction_boundary_policy_packs; keep_i_j_k_l_e_deferred",
        "f0_handoff_recommendation": "F0-BUNDLE-01 may start deep extraction source-family and extraction-boundary policy packs, not extraction runtime.",
        "i_j_k_l_deferral_recommendation": "Track I federation/private pack export, Track J risky actions/acquisition, Track K semantic/AI, Track L wider clients, and Track E deployment remain deferred unless explicit gates open.",
        "do_not_repeat_risks": [
            "Do not treat H14 candidates as source truth, connector approval, coverage truth, reliability truth, freshness truth, rights clearance, safe source status, or production readiness.",
            "Do not use H14 review outputs as source discovery runtime, registry mutation, pack import/export, source-cache write, evidence write, or public-index permission.",
        ],
        "risks": ["Some rollup dry-run evidence is blocked and carried by fixture-equivalent review outputs."] if blocked_sources else [],
        "no_goals_preserved": ["no_live_source_calls", "no_model_provider_calls", "no_source_discovery_runtime", "no_source_sync", "no_pack_import_export", "no_registry_mutation", "no_source_cache_writes", "no_evidence_writes", "no_public_index_mutation", "no_truth_acceptance"],
        "auto_approves_future_connectors": False,
        "auto_approves_source_discovery": False,
        "auto_approves_registry_mutation": False,
        "auto_approves_pack_import_export": False,
        "auto_approves_publication": False,
        "auto_approves_production_readiness": False,
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["Postmortem recommends F0 policy packs, not extraction runtime, live source discovery, pack federation, actions, AI, wider clients, or deployment."],
    }
    _raise_if_invalid(postmortem, policy)
    return postmortem


def build_h14_next_phase_recommendation(postmortem: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    recommendation = {
        "schema_version": "h14_source_discovery_next_phase_recommendation.v0",
        "recommendation_id": f"h14.next_phase.{_digest(postmortem)[:12]}.v0",
        "recommended_next_task": "F0-BUNDLE-01 - Deep extraction source-family and extraction-boundary policy packs",
        "recommendation_status": "READY_FOR_F0_BUNDLE_01",
        "alternatives_considered": ["H14-REMEDIATION-04", "I0-FUTURE", "J1-POLICY-FUTURE", "K0-FUTURE", "L0-FUTURE", "E-DEPLOYMENT-FUTURE"],
        "f0_readiness": "ready_for_extraction_boundary_policy_packs_only",
        "i_deferral": "pack federation and private pack export/import remain deferred unless Track I gates explicitly open",
        "j_deferral": "risky actions and acquisition remain deferred unless Track J gates explicitly open",
        "k_deferral": "semantic and AI/provider work remain deferred unless Track K gates explicitly open",
        "l_deferral": "wider clients remain deferred unless Track L gates explicitly open",
        "e_deployment_deferral": "hosting and deployment remain deferred unless Track E gates explicitly open",
        "remediation_required": False,
        "reason": "H14 Source OS rollup artifacts are coherent enough to hand off to F0 extraction-boundary policy packs while preserving no-live, no-pack, no-registry, no-write, and no-truth boundaries.",
        "limitations": ["F0 readiness is policy-pack readiness only; it does not enable extraction runtime, live access, downloads, publication, source sync, or public index writes."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
    }
    _raise_if_invalid(recommendation, policy)
    return recommendation


def build_h14_integration_audit(
    review_result: Mapping[str, Any],
    quality_delta: Mapping[str, Any],
    postmortem: Mapping[str, Any],
    recommendation: Mapping[str, Any] | None = None,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    recommendation = dict(recommendation or build_h14_next_phase_recommendation(postmortem, policy))
    audit = {
        "schema_version": "h14_source_discovery_integration_audit.v0",
        "audit_id": f"h14.integration_audit.{_digest({'review': review_result, 'delta': quality_delta, 'postmortem': postmortem})[:12]}.v0",
        "wave_id": "H14",
        "audited_sources": list(review_result.get("sources", [])),
        "audited_tasks": ["H14-BUNDLE-01", "H14-BUNDLE-02", "H14-BUNDLE-03", "H14-BUNDLE-04"],
        "artifact_inventory": {
            "review_integration_result": bool(review_result),
            "quality_delta_report": bool(quality_delta),
            "connector_wave_postmortem": bool(postmortem),
            "next_phase_recommendation": bool(recommendation),
            "fixture_outputs_integrated": len(review_result.get("used_fixture_outputs", [])),
            "rollup_dry_run_outputs_integrated": len(review_result.get("used_rollup_dry_run_outputs", [])),
        },
        "validation_summary": {"status": "pass", "offline_default": True},
        "source_policy_summary": {"policy_packs_present": True, "source_discovery_runtime_enabled": False},
        "fixture_runtime_summary": {"fixture_outputs_integrated": len(review_result.get("used_fixture_outputs", []))},
        "rollup_dry_run_summary": {
            "completed_sources": [item.get("source_id") for item in review_result.get("used_rollup_dry_run_outputs", []) if item.get("result_status") == "rollup_dry_run_completed"],
            "blocked_sources": list(review_result.get("blocked_sources", [])),
            "network_used": False,
            "model_provider_used": False,
        },
        "review_integration_summary": summarize_h14_review_integration(review_result),
        "quality_delta_summary": summarize_h14_quality_delta(quality_delta),
        "postmortem_summary": summarize_h14_postmortem(postmortem),
        "source_os_rollup_summary": {"source_count": len(review_result.get("sources", [])), "rollup_evidence": "fixture_and_dry_run_preview_only"},
        "pack_import_export_boundary_summary": {"pack_import_export": "blocked_current_preview_only"},
        "registry_mutation_boundary_summary": {"source_registry_mutation": False, "connector_registry_mutation": False},
        "blockers": [],
        "warnings": ["Some H14 rollup dry-run evidence remains blocked by policy; fixture-equivalent review evidence is used."] if review_result.get("blocked_sources") else [],
        "h14_exit_gate": "PASS_WITH_WARNINGS" if review_result.get("blocked_sources") else "PASS",
        "next_phase_recommendation": recommendation.get("recommendation_status", "READY_FOR_F0_BUNDLE_01"),
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["H14 closes for F0 policy-pack handoff without opening source discovery, pack import/export, registry mutation, writes, or truth acceptance."],
    }
    apply_missing_source_gate(audit)
    _raise_if_invalid(audit, policy)
    return audit


def summarize_h14_postmortem(postmortem: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    errors = detect_h14_quality_overclaim(postmortem, policy)
    return {
        "schema_version": "h14_connector_wave_postmortem_summary.v0",
        "status": "pass" if not errors else "invalid",
        "postmortem_id": postmortem.get("postmortem_id"),
        "next_phase_recommendation": postmortem.get("next_phase_recommendation"),
        "f_or_i_j_k_l_recommendation": postmortem.get("f_or_i_j_k_l_recommendation"),
        "auto_approves_future_connectors": False,
        "auto_approves_source_discovery": False,
        "auto_approves_registry_mutation": False,
        "auto_approves_pack_import_export": False,
        "errors": errors,
    }


def apply_missing_source_gate(integration_audit: dict[str, Any], required_sources: tuple[str, ...] = H14_SOURCE_IDS) -> dict[str, Any]:
    missing = [source for source in required_sources if source not in integration_audit.get("audited_sources", [])]
    if missing:
        integration_audit["h14_exit_gate"] = "PARTIAL"
        integration_audit["next_phase_recommendation"] = "NEEDS_REMEDIATION"
        integration_audit.setdefault("blockers", []).append(f"missing audited sources: {', '.join(missing)}")
    return integration_audit


def _truth_boundary() -> dict[str, bool]:
    return {key: False for key in [
        "source_need_seed_accepts_source_approval", "source_candidate_seed_accepts_source_truth",
        "source_discovery_seed_mutates_registry", "source_pack_manifest_seed_exports_pack",
        "connector_pack_manifest_seed_approves_connector",
        "coverage_manifest_seed_accepts_coverage_truth",
        "connector_scorecard_seed_approves_connector",
        "reliability_freshness_seed_accepts_truth",
        "dispute_revocation_seed_accepts_truth",
        "lineage_provenance_seed_accepts_lineage_truth",
        "pack_boundary_seed_grants_import_export_permission",
        "source_cache_review_seed_accepts_source",
        "evidence_review_seed_accepts_evidence",
        "candidate_promotion_preview_promotes_candidate",
        "source_pack_preview_is_imported_or_submitted",
        "source_registry_mutated", "connector_registry_mutated",
        "public_index_mutated", "master_index_mutated",
        "rights_clearance_claimed", "source_completeness_claimed",
        "production_readiness_claimed", "launch_readiness_claimed",
    ]}


def _product_boundary() -> dict[str, bool]:
    return {key: False for key in [
        "changed_public_search_behavior", "enabled_hosting", "enabled_source_discovery",
        "enabled_live_access", "enabled_network_access", "enabled_model_provider",
        "enabled_source_sync", "enabled_pack_export_import", "enabled_registry_mutation",
        "enabled_source_cache_writes", "enabled_evidence_writes", "mutated_public_index",
        "mutated_master_index",
    ]}


def _raise_if_invalid(payload: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> None:
    errors = detect_h14_quality_overclaim(payload, policy)
    errors.extend(detect_h14_review_truth_boundary_violations(payload, policy))
    errors.extend(detect_h14_review_product_boundary_violations(payload, policy))
    errors.extend(detect_h14_review_registry_or_pack_mutation_violations(payload, policy))
    for key in ("auto_approves_future_connectors", "auto_approves_source_discovery", "auto_approves_registry_mutation", "auto_approves_pack_import_export", "auto_approves_publication", "auto_approves_production_readiness"):
        if payload.get(key) is True:
            errors.append(f"postmortem must not set {key}")
    if errors:
        raise ValueError("; ".join(sorted(dict.fromkeys(errors))))


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, default=str).encode("utf-8")).hexdigest()
