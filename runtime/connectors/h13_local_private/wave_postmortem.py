"""H13 local/private wave postmortem and next-phase helpers."""

from __future__ import annotations

from collections.abc import Mapping
import hashlib
import json
from typing import Any

from runtime.connectors.h13_local_private.normalizer_common import H13_SOURCE_IDS
from runtime.connectors.h13_local_private.quality_delta import detect_h13_quality_overclaim, summarize_h13_quality_delta
from runtime.connectors.h13_local_private.review_integration import (
    detect_h13_review_product_boundary_violations,
    detect_h13_review_truth_boundary_violations,
    summarize_h13_review_integration,
)


def build_h13_connector_wave_postmortem(review_result: Mapping[str, Any], quality_delta: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    blocked_sources = list(review_result.get("blocked_sources") or [])
    postmortem = {
        "schema_version": "h13_local_private_connector_wave_postmortem.v0",
        "postmortem_id": f"h13.connector_wave_postmortem.{_digest({'review': review_result, 'delta': quality_delta})[:12]}.v0",
        "wave_id": "H13",
        "what_worked": [
            "Twelve H13 local/private/user-supplied/authenticated/restricted source classes have policy packs, fixture outputs, boundary dry-run blocked evidence, and review previews.",
            "Local source identity, private boundary, user-supplied URL, authenticated boundary, restricted manifest, CAS, pack, privacy/redaction, and rights/safety candidates remain review-gated and candidate-only.",
            "Boundary dry-runs failed closed where committed approvals were missing.",
        ],
        "what_failed": ["No H13 source/input class has committed approval for an approved boundary dry-run."] if blocked_sources else [],
        "blocked_sources": blocked_sources,
        "fixture_gaps": ["Fixtures are synthetic/public-safe and do not prove local/private/restricted source behavior."],
        "boundary_dry_run_gaps": ["Blocked boundary dry-runs provide gate evidence but no approved boundary operation response."] if blocked_sources else [],
        "normalizer_gaps": ["Normalizers cover fixture boundary shapes, not local scans, private-source access, URL fetches, accounts, CAS import, pack export/import, extraction, execution, or publication."],
        "local_source_identity_gaps": ["Local source identity candidates require review before any identity or source use."],
        "private_source_boundary_gaps": ["Private source boundary candidates grant no access, inspection, export, sharing, indexing, or publication permission."],
        "user_supplied_url_boundary_gaps": ["User-supplied URL candidates grant no fetch, scrape, crawl, mirror, download, index, or publication permission."],
        "authenticated_source_boundary_gaps": ["Authenticated source candidates grant no account, credential, session, receipt, entitlement, subscription, or user-library access."],
        "restricted_source_manifest_gaps": ["Restricted-source manifest candidates remain manifest-only and policy-blocked for direct access."],
        "local_cas_import_boundary_gaps": ["CAS import candidates grant no file hashing, copy, deduplication, CAS write, import, export, or publication permission."],
        "pack_export_import_boundary_gaps": ["Pack export/import candidates grant no export, import, redistribution, submission, acceptance, or publication permission."],
        "privacy_redaction_gaps": ["Privacy/redaction candidates do not prove public safety or publication permission."],
        "rights_safety_gaps": ["Rights/safety candidates are not rights clearance, legal access, ownership proof, account entitlement proof, privacy safety, malware safety, source safety, or publication permission."],
        "private_data_policy_gaps": ["Private paths, credentials, account data, local file contents, private payloads, CAS blobs, and packs remain prohibited from public-safe outputs."],
        "restricted_source_policy_gaps": ["Restricted, rights-sensitive, account-locked, private, leaked/proprietary, and unsafe source classes remain blocked by default."],
        "policy_gaps": ["source-specific boundary dry-run approvals remain absent"] if blocked_sources else [],
        "evidence_mapping_gaps": ["Evidence candidates remain previews only."],
        "review_mapping_gaps": ["Review seeds are not review decisions and are not persisted."],
        "quality_delta_summary": summarize_h13_quality_delta(quality_delta, policy),
        "scorecard_summary": {"scorecard_update_count": quality_delta.get("scorecard_update_count", 0), "production_ready": False, "auto_approves_future_connectors": False},
        "safety_boundary_assessment": {
            "local_access_enabled": False,
            "private_source_access_enabled": False,
            "url_fetch_enabled": False,
            "account_access_enabled": False,
            "restricted_source_access_enabled": False,
            "cas_import_enabled": False,
            "pack_export_import_enabled": False,
            "source_cache_writes_enabled": False,
            "evidence_writes_enabled": False,
            "publication_enabled": False,
            "accepted_truth": False,
            "public_index_mutated": False,
            "master_index_mutated": False,
            "boundary_result": "preserved",
        },
        "next_phase_recommendation": "READY_FOR_H14_BUNDLE_01",
        "h14_or_f_i_j_k_l_recommendation": "proceed_to_h14_source_discovery_scorecards; keep_f_i_j_k_l_deferred",
        "source_os_reuse_assessment": "H13 reused H0-H12 Source OS review gates while preserving local/private/restricted data boundaries.",
        "h14_handoff_recommendation": "H14-BUNDLE-01 may start source discovery/source pack/scorecard aggregation without opening local/private/restricted access.",
        "f_i_j_k_l_deferral_recommendation": "F deep extraction, I federation/private pack export, J risky actions/acquisition, K semantic/AI, and L wider clients remain deferred unless explicit gates open.",
        "risks": ["H13 boundary dry-runs remain blocked pending operator/user approval."] if blocked_sources else [],
        "do_not_repeat_risks": [
            "Do not treat H13 candidates as source truth, access permission, rights clearance, legal access, safety proof, publication permission, or production readiness.",
            "Do not use fixture replay or blocked dry-runs as local/private/restricted access approval.",
            "Do not enable source cache writes, evidence writes, index mutation, CAS import, pack export/import, extraction, execution, acquisition, uploads, or publication from H13 review outputs.",
        ],
        "no_goals_preserved": ["no_local_private_restricted_access", "no_url_fetch", "no_account_access", "no_cas_import", "no_pack_export_import", "no_publication", "no_truth_acceptance", "no_public_index_mutation"],
        "auto_approves_future_connectors": False,
        "auto_approves_access_import_export_publication": False,
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["Postmortem recommends H14 aggregation, not local/private access or production readiness."],
    }
    _raise_if_invalid(postmortem, policy)
    return postmortem


def build_h13_next_phase_recommendation(postmortem: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    recommendation = {
        "schema_version": "h13_local_private_next_phase_recommendation.v0",
        "recommendation_id": f"h13.next_phase.{_digest(postmortem)[:12]}.v0",
        "recommended_next_task": "H14-BUNDLE-01 - Source discovery, source packs, and connector scorecards",
        "recommendation_status": "READY_FOR_H14_BUNDLE_01",
        "alternatives_considered": ["H13-REMEDIATION-04", "F0-FUTURE", "I0-FUTURE", "J1-POLICY-FUTURE", "K0-FUTURE", "L0-FUTURE"],
        "h14_readiness": "ready_with_fixture_equivalent_h13_outputs_and_blocked_boundary_evidence",
        "f_deferral": "deep extraction remains deferred unless Track F gates explicitly open",
        "i_deferral": "federation/private pack export remains deferred unless Track I gates explicitly open",
        "j_deferral": "risky actions/acquisition remain deferred unless Track J gates explicitly open",
        "k_deferral": "semantic/AI remains deferred unless Track K gates explicitly open",
        "l_deferral": "wider clients remain deferred unless Track L gates explicitly open",
        "deployment_deferral": "deployment remains operator-gated",
        "remediation_required": False,
        "reason": "H13 local/private/restricted source boundaries are coherent enough to aggregate source discovery, scorecards, coverage, and source packs in H14 without enabling access, import/export, publication, source/evidence writes, index mutation, or truth acceptance.",
        "limitations": ["No approved H13 boundary dry-run completed; fixture-equivalent and blocked outputs carry the review integration."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
    }
    _raise_if_invalid(recommendation, policy)
    return recommendation


def build_h13_integration_audit(
    review_result: Mapping[str, Any],
    quality_delta: Mapping[str, Any],
    postmortem: Mapping[str, Any],
    recommendation: Mapping[str, Any] | None = None,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    recommendation = dict(recommendation or build_h13_next_phase_recommendation(postmortem, policy))
    audit = {
        "schema_version": "h13_local_private_integration_audit.v0",
        "audit_id": f"h13.integration_audit.{_digest({'review': review_result, 'delta': quality_delta, 'postmortem': postmortem})[:12]}.v0",
        "wave_id": "H13",
        "audited_sources": list(review_result.get("sources", [])),
        "audited_tasks": ["H13-BUNDLE-01", "H13-BUNDLE-02", "H13-BUNDLE-03", "H13-BUNDLE-04"],
        "artifact_inventory": {
            "review_integration_result": bool(review_result),
            "quality_delta_report": bool(quality_delta),
            "connector_wave_postmortem": bool(postmortem),
            "next_phase_recommendation": bool(recommendation),
            "fixture_outputs_integrated": len(review_result.get("used_fixture_outputs", [])),
            "boundary_dry_run_outputs_integrated": len(review_result.get("used_boundary_dry_run_outputs", [])),
        },
        "validation_summary": {"status": "pass", "offline_default": True},
        "source_policy_summary": {"policy_packs_present": True, "local_private_access_default": False},
        "fixture_runtime_summary": {"fixture_outputs_integrated": len(review_result.get("used_fixture_outputs", []))},
        "boundary_dry_run_summary": {
            "completed_sources": [item.get("source_id") for item in review_result.get("used_boundary_dry_run_outputs", []) if item.get("result_status") == "boundary_dry_run_completed"],
            "blocked_sources": list(review_result.get("blocked_sources", [])),
            "network_used": False,
            "local_access_used": False,
        },
        "review_integration_summary": summarize_h13_review_integration(review_result),
        "quality_delta_summary": summarize_h13_quality_delta(quality_delta),
        "postmortem_summary": summarize_h13_postmortem(postmortem),
        "local_private_boundary_summary": {"local_private_boundary": "candidate_preview_only_no_access"},
        "private_data_policy_summary": {"private_data_outputs": "blocked_current"},
        "restricted_source_policy_summary": {"restricted_source_access": "blocked_current_manifest_only"},
        "blockers": [],
        "warnings": ["H13 boundary dry-runs remain blocked pending operator/user approval"] if review_result.get("blocked_sources") else [],
        "h13_exit_gate": "PASS_WITH_WARNINGS" if review_result.get("blocked_sources") else "PASS",
        "next_phase_recommendation": recommendation.get("recommendation_status", "READY_FOR_H14_BUNDLE_01"),
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["H13 passes for H14 aggregation using fixture-equivalent outputs and blocked boundary evidence."],
    }
    apply_missing_source_gate(audit)
    _raise_if_invalid(audit, policy)
    return audit


def summarize_h13_postmortem(postmortem: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    errors = detect_h13_quality_overclaim(postmortem, policy)
    return {
        "schema_version": "h13_connector_wave_postmortem_summary.v0",
        "status": "pass" if not errors else "invalid",
        "postmortem_id": postmortem.get("postmortem_id"),
        "next_phase_recommendation": postmortem.get("next_phase_recommendation"),
        "h14_or_f_i_j_k_l_recommendation": postmortem.get("h14_or_f_i_j_k_l_recommendation"),
        "auto_approves_future_connectors": False,
        "auto_approves_access_import_export_publication": False,
        "errors": errors,
    }


def apply_missing_source_gate(integration_audit: dict[str, Any], required_sources: tuple[str, ...] = H13_SOURCE_IDS) -> dict[str, Any]:
    missing = [source for source in required_sources if source not in integration_audit.get("audited_sources", [])]
    if missing:
        integration_audit["h13_exit_gate"] = "PARTIAL"
        integration_audit["next_phase_recommendation"] = "NEEDS_REMEDIATION"
        integration_audit.setdefault("blockers", []).append(f"missing audited sources: {', '.join(missing)}")
    return integration_audit


def _truth_boundary() -> dict[str, bool]:
    return {key: False for key in ['accepted_CAS_import_truth', 'accepted_authenticated_source_truth', 'accepted_candidate_truth', 'accepted_cas_import_truth', 'accepted_evidence_truth', 'accepted_local_source_identity_truth', 'accepted_pack_export_import_truth', 'accepted_privacy_redaction_truth', 'accepted_private_source_truth', 'accepted_public_record', 'accepted_restricted_source_truth', 'accepted_rights_safety_truth', 'accepted_source_truth', 'accepted_user_supplied_url_truth', 'account_entitlement_claimed', 'authenticated_source_seed_grants_account_permission', 'automatic_future_connector_approval', 'candidate_promotion_preview_promotes_candidate', 'cas_import_seed_grants_import_permission', 'evidence_review_seed_accepts_evidence', 'legal_access_claimed', 'local_source_identity_seed_accepts_source_truth', 'malware_safety_claimed', 'master_index_mutated', 'mutated_master_index', 'mutated_public_index', 'ownership_truth_claimed', 'pack_export_import_seed_grants_export_import_permission', 'privacy_redaction_seed_proves_public_safety', 'privacy_safety_claimed', 'private_source_boundary_seed_grants_access_permission', 'production_readiness_claimed', 'public_index_mutated', 'publication_permission_claimed', 'restricted_source_manifest_seed_grants_access_permission', 'review_seed_is_review_decision', 'rights_clearance_claimed', 'rights_safety_seed_accepts_rights_safety_truth', 'source_cache_review_seed_accepts_source', 'source_pack_preview_is_imported_or_submitted', 'source_safety_claimed', 'user_authority_claimed', 'user_supplied_url_seed_grants_fetch_permission', 'verified_authenticity_claimed']}


def _product_boundary() -> dict[str, bool]:
    return {key: False for key in ['account_access_used', 'acquisition_action_used', 'api_calls_made', 'archive_listing_used', 'authenticated_access_used', 'cas_import_used', 'changed_public_search_behavior', 'credential_handling_used', 'directory_listing_used', 'enabled_account_access', 'enabled_acquisition_actions', 'enabled_cas_import', 'enabled_evidence_writes', 'enabled_execution', 'enabled_extraction', 'enabled_hosting', 'enabled_local_access', 'enabled_pack_export_import', 'enabled_private_access', 'enabled_publication', 'enabled_restricted_access', 'enabled_source_cache_writes', 'enabled_source_sync', 'enabled_telemetry', 'enabled_uploads', 'enabled_url_fetch', 'evidence_write_used', 'execution_used', 'extraction_used', 'file_hashing_used', 'filesystem_scan_used', 'fingerprinting_used', 'local_access_used', 'malware_scanning_used', 'model_provider_calls_made', 'mutated_master_index', 'mutated_public_index', 'network_calls_made', 'pack_export_import_used', 'private_source_access_used', 'publication_used', 'restricted_source_access_used', 'source_cache_write_used', 'upload_used', 'user_supplied_url_fetch_used']}


def _raise_if_invalid(payload: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> None:
    errors = detect_h13_quality_overclaim(payload, policy)
    errors.extend(detect_h13_review_truth_boundary_violations(payload, policy))
    errors.extend(detect_h13_review_product_boundary_violations(payload, policy))
    if payload.get("auto_approves_future_connectors") is True or payload.get("auto_approves_access_import_export_publication") is True:
        errors.append("postmortem must not auto-approve future connectors/access/import/export/publication")
    if errors:
        raise ValueError("; ".join(sorted(dict.fromkeys(errors))))


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, default=str).encode("utf-8")).hexdigest()
