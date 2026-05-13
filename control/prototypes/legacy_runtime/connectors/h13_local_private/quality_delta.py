"""Offline H13 local/private quality delta helpers."""

from __future__ import annotations

from collections.abc import Mapping
import hashlib
import json
from typing import Any

from control.prototypes.legacy_runtime.connectors.h13_local_private.normalizer_common import H13_SOURCE_IDS
from control.prototypes.legacy_runtime.connectors.h13_local_private.review_integration import (
    REVIEW_SEED_KEYS,
    detect_h13_review_product_boundary_violations,
    detect_h13_review_truth_boundary_violations,
)

FORBIDDEN_TRUE_KEYS = set(['accepted_CAS_import_truth', 'accepted_authenticated_source_truth', 'accepted_candidate_truth', 'accepted_cas_import_truth', 'accepted_evidence_truth', 'accepted_local_source_identity_truth', 'accepted_pack_export_import_truth', 'accepted_privacy_redaction_truth', 'accepted_private_source_truth', 'accepted_public_record', 'accepted_restricted_source_truth', 'accepted_rights_safety_truth', 'accepted_source_truth', 'accepted_user_supplied_url_truth', 'account_entitlement_claimed', 'authenticated_source_seed_grants_account_permission', 'automatic_future_connector_approval', 'candidate_promotion_preview_promotes_candidate', 'cas_import_seed_grants_import_permission', 'evidence_review_seed_accepts_evidence', 'legal_access_claimed', 'local_source_identity_seed_accepts_source_truth', 'malware_safety_claimed', 'master_index_mutated', 'mutated_master_index', 'mutated_public_index', 'ownership_truth_claimed', 'pack_export_import_seed_grants_export_import_permission', 'privacy_redaction_seed_proves_public_safety', 'privacy_safety_claimed', 'private_source_boundary_seed_grants_access_permission', 'production_readiness_claimed', 'public_index_mutated', 'publication_permission_claimed', 'restricted_source_manifest_seed_grants_access_permission', 'review_seed_is_review_decision', 'rights_clearance_claimed', 'rights_safety_seed_accepts_rights_safety_truth', 'source_cache_review_seed_accepts_source', 'source_pack_preview_is_imported_or_submitted', 'source_safety_claimed', 'user_authority_claimed', 'user_supplied_url_seed_grants_fetch_permission', 'verified_authenticity_claimed'] + ['production_search_quality', 'production_local_private_coverage', 'private_source_completeness_verified', 'file_identity_verified', 'ownership_verified', 'user_authority_verified', 'legal_access_verified', 'rights_clearance', 'account_entitlement_verified', 'publication_permission_verified', 'privacy_safety', 'malware_safety', 'source_safety_verified', 'verified_authenticity', 'public_safety_verified', 'automatic_future_connector_approval'])


def build_h13_quality_delta(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    review = dict(inputs.get("review_integration_result") or inputs)
    sources = list(review.get("sources") or [])
    blocked_sources = list(review.get("blocked_sources") or [])
    fixture_outputs = list(review.get("used_fixture_outputs") or [])
    boundary_outputs = list(review.get("used_boundary_dry_run_outputs") or [])
    known_gaps = _known_gaps(review)
    metrics = {
        "source_count": len(sources) or len(H13_SOURCE_IDS),
        "fixture_sources_count": len({item.get("source_id") for item in fixture_outputs if item.get("source_id")}) or len(sources),
        "boundary_dry_run_sources_count": len({item.get("source_id") for item in boundary_outputs if item.get("result_status") == "boundary_dry_run_completed"}),
        "blocked_sources_count": len(blocked_sources),
        "normalized_record_count": len(review.get("source_cache_review_seeds", [])),
        "local_source_identity_candidate_count": len(review.get("local_source_identity_review_seeds", [])),
        "private_source_boundary_candidate_count": len(review.get("private_source_boundary_review_seeds", [])),
        "user_supplied_url_boundary_candidate_count": len(review.get("user_supplied_url_boundary_review_seeds", [])),
        "authenticated_source_boundary_candidate_count": len(review.get("authenticated_source_boundary_review_seeds", [])),
        "restricted_source_manifest_candidate_count": len(review.get("restricted_source_manifest_review_seeds", [])),
        "local_cas_import_boundary_candidate_count": len(review.get("local_cas_import_boundary_review_seeds", [])),
        "pack_export_import_boundary_candidate_count": len(review.get("pack_export_import_boundary_review_seeds", [])),
        "privacy_redaction_candidate_count": len(review.get("privacy_redaction_review_seeds", [])),
        "local_private_rights_safety_candidate_count": len(review.get("local_private_rights_safety_review_seeds", [])),
        "source_cache_candidate_count": len(review.get("source_cache_review_seeds", [])),
        "evidence_candidate_preview_count": len(review.get("evidence_candidate_review_seeds", [])),
        "review_seed_count": sum(len(review.get(key, [])) for key in REVIEW_SEED_KEYS),
        "coverage_preview_count": len(review.get("coverage_update_previews", [])),
        "scorecard_update_count": len(review.get("scorecard_updates", [])),
        "known_gap_count": len(known_gaps),
        "blocker_count": 0,
        "warning_count": len(review.get("warnings", [])) + (1 if blocked_sources else 0),
    }
    delta = {
        "schema_version": "h13_local_private_quality_delta_report.v0",
        "quality_delta_id": f"h13.quality_delta.{_digest(review)[:12]}.v0",
        "wave_id": "H13",
        "comparison_scope": "fixture_replay_and_blocked_boundary_dry_run_evidence",
        **metrics,
        "per_source_deltas": [_per_source_delta(source_id, review, fixture_outputs, boundary_outputs, blocked_sources) for source_id in sorted(set(sources) or set(H13_SOURCE_IDS))],
        "limitations": [
            "Quality delta measures H13 review readiness only.",
            "Blocked boundary dry-runs do not prove local, private, URL, account, restricted-source, CAS, pack, privacy, or rights/safety behavior.",
            "H13 quality delta is not production search quality, production local/private coverage, private-source completeness, file identity, ownership, user authority, legal access, rights clearance, account entitlement, publication permission, privacy safety, malware safety, source safety, verified authenticity, public safety, or future connector approval.",
        ],
        "forbidden_claims": ['production_search_quality', 'production_local_private_coverage', 'private_source_completeness_verified', 'file_identity_verified', 'ownership_verified', 'user_authority_verified', 'legal_access_verified', 'rights_clearance', 'account_entitlement_verified', 'publication_permission_verified', 'privacy_safety', 'malware_safety', 'source_safety_verified', 'verified_authenticity', 'public_safety_verified', 'automatic_future_connector_approval'],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["H13 quality delta is operational review evidence only."],
    }
    errors = detect_h13_quality_overclaim(delta, policy)
    if errors:
        raise ValueError("; ".join(errors))
    return delta


def summarize_h13_quality_delta(delta: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    errors = detect_h13_quality_overclaim(delta, policy)
    return {
        "schema_version": "h13_quality_delta_summary.v0",
        "status": "pass" if not errors else "invalid",
        "quality_delta_id": delta.get("quality_delta_id"),
        "source_count": delta.get("source_count", 0),
        "fixture_sources_count": delta.get("fixture_sources_count", 0),
        "boundary_dry_run_sources_count": delta.get("boundary_dry_run_sources_count", 0),
        "blocked_sources_count": delta.get("blocked_sources_count", 0),
        "local_source_identity_candidate_count": delta.get("local_source_identity_candidate_count", 0),
        "private_source_boundary_candidate_count": delta.get("private_source_boundary_candidate_count", 0),
        "user_supplied_url_boundary_candidate_count": delta.get("user_supplied_url_boundary_candidate_count", 0),
        "authenticated_source_boundary_candidate_count": delta.get("authenticated_source_boundary_candidate_count", 0),
        "restricted_source_manifest_candidate_count": delta.get("restricted_source_manifest_candidate_count", 0),
        "local_cas_import_boundary_candidate_count": delta.get("local_cas_import_boundary_candidate_count", 0),
        "pack_export_import_boundary_candidate_count": delta.get("pack_export_import_boundary_candidate_count", 0),
        "privacy_redaction_candidate_count": delta.get("privacy_redaction_candidate_count", 0),
        "local_private_rights_safety_candidate_count": delta.get("local_private_rights_safety_candidate_count", 0),
        "review_seed_count": delta.get("review_seed_count", 0),
        "known_gap_count": delta.get("known_gap_count", 0),
        "blocker_count": delta.get("blocker_count", 0),
        "claims_private_source_completeness_verified": False,
        "claims_file_identity_verified": False,
        "claims_ownership_verified": False,
        "claims_user_authority_verified": False,
        "claims_legal_access": False,
        "claims_rights_clearance": False,
        "claims_account_entitlement": False,
        "claims_publication_permission": False,
        "claims_privacy_safety": False,
        "claims_malware_safety": False,
        "claims_source_safety": False,
        "claims_verified_authenticity": False,
        "claims_production_readiness": False,
        "overclaim_errors": errors,
    }


def detect_h13_quality_overclaim(delta: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    errors = [f"quality overclaim: {path}=true" for path, key, value in _iter_key_values(delta) if key in FORBIDDEN_TRUE_KEYS and value is True]
    errors.extend(detect_h13_review_truth_boundary_violations(delta, policy))
    errors.extend(detect_h13_review_product_boundary_violations(delta, policy))
    return sorted(dict.fromkeys(errors))


def _per_source_delta(source_id: str, review: Mapping[str, Any], fixture_outputs: list[Mapping[str, Any]], boundary_outputs: list[Mapping[str, Any]], blocked_sources: list[str]) -> dict[str, Any]:
    represented = source_id in review.get("sources", [])
    return {
        "source_id": source_id,
        "fixture_output_integrated": any(item.get("source_id") == source_id for item in fixture_outputs) or represented,
        "boundary_dry_run_completed": any(item.get("source_id") == source_id and item.get("result_status") == "boundary_dry_run_completed" for item in boundary_outputs),
        "boundary_dry_run_blocked": source_id in blocked_sources,
        "local_source_identity_review_seed_created": represented,
        "private_source_boundary_review_seed_created": represented,
        "user_supplied_url_boundary_review_seed_created": represented,
        "authenticated_source_boundary_review_seed_created": represented,
        "restricted_source_manifest_review_seed_created": represented,
        "local_cas_import_boundary_review_seed_created": represented,
        "pack_export_import_boundary_review_seed_created": represented,
        "privacy_redaction_review_seed_created": represented,
        "local_private_rights_safety_review_seed_created": represented,
        "source_cache_review_seed_created": represented,
        "evidence_review_seed_created": represented,
        "limitations": ["Fixture/local review only; not accepted source, evidence, candidate, local/private/user-supplied/authenticated/restricted/CAS/pack/redaction/rights-safety/public, or production proof."],
    }


def _known_gaps(review: Mapping[str, Any]) -> list[str]:
    gaps: list[str] = []
    if review.get("blocked_sources"):
        gaps.append("operator_approval_missing_for_boundary_dry_runs")
    if len(review.get("source_cache_review_seeds", [])) < len(H13_SOURCE_IDS):
        gaps.append("not_all_sources_have_review_seeds")
    if not any(item.get("result_status") == "boundary_dry_run_completed" for item in review.get("used_boundary_dry_run_outputs", [])):
        gaps.append("approved_boundary_dry_run_outputs_not_available")
    return sorted(dict.fromkeys(gaps))


def _truth_boundary() -> dict[str, bool]:
    return {key: False for key in FORBIDDEN_TRUE_KEYS}


def _product_boundary() -> dict[str, bool]:
    return {key: False for key in ['account_access_used', 'acquisition_action_used', 'api_calls_made', 'archive_listing_used', 'authenticated_access_used', 'cas_import_used', 'changed_public_search_behavior', 'credential_handling_used', 'directory_listing_used', 'enabled_account_access', 'enabled_acquisition_actions', 'enabled_cas_import', 'enabled_evidence_writes', 'enabled_execution', 'enabled_extraction', 'enabled_hosting', 'enabled_local_access', 'enabled_pack_export_import', 'enabled_private_access', 'enabled_publication', 'enabled_restricted_access', 'enabled_source_cache_writes', 'enabled_source_sync', 'enabled_telemetry', 'enabled_uploads', 'enabled_url_fetch', 'evidence_write_used', 'execution_used', 'extraction_used', 'file_hashing_used', 'filesystem_scan_used', 'fingerprinting_used', 'local_access_used', 'malware_scanning_used', 'model_provider_calls_made', 'mutated_master_index', 'mutated_public_index', 'network_calls_made', 'pack_export_import_used', 'private_source_access_used', 'publication_used', 'restricted_source_access_used', 'source_cache_write_used', 'upload_used', 'user_supplied_url_fetch_used']}


def _iter_key_values(value: Any, prefix: str = ""):
    if isinstance(value, Mapping):
        for key, inner in value.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            yield path, str(key), inner
            yield from _iter_key_values(inner, path)
    elif isinstance(value, list):
        for index, inner in enumerate(value):
            yield from _iter_key_values(inner, f"{prefix}[{index}]")


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, default=str).encode("utf-8")).hexdigest()
