"""Fail-closed H13 local/private boundary dry-run helpers."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from control.prototypes.legacy_runtime.connectors.h13_local_private.normalizer_common import (
    H13_SOURCE_CONFIGS,
    H13_SOURCE_IDS,
    build_h13_evidence_candidate_preview as _fixture_evidence_preview,
    build_h13_local_cas_import_boundary_candidate as _fixture_cas_candidate,
    build_h13_local_private_rights_safety_candidate as _fixture_rights_candidate,
    build_h13_local_source_identity_candidate as _fixture_local_source_candidate,
    build_h13_pack_export_import_boundary_candidate as _fixture_pack_candidate,
    build_h13_privacy_redaction_candidate as _fixture_privacy_candidate,
    build_h13_private_source_boundary_candidate as _fixture_private_candidate,
    build_h13_restricted_source_manifest_candidate as _fixture_restricted_candidate,
    build_h13_source_cache_candidate_preview as _fixture_source_cache_preview,
    build_h13_user_supplied_url_boundary_candidate as _fixture_url_candidate,
    build_h13_authenticated_source_boundary_candidate as _fixture_auth_candidate,
    detect_h13_product_boundary_violations as _fixture_product_violations,
    detect_h13_secret_or_private_data_violations as _fixture_private_data_violations,
    detect_h13_truth_boundary_violations as _fixture_truth_violations,
    hash_h13_locator,
    normalize_h13_local_private_fixture,
    redact_h13_locator,
)

POLICY_PATHS = {
    "boundary_dry_run_policy": "control/inventory/connectors/h13_local_private_boundary_dry_run_policy.json",
    "allowed_requests": "control/inventory/connectors/h13_local_private_boundary_dry_run_allowed_requests.json",
    "operation_policy": "control/inventory/connectors/h13_local_private_boundary_operation_policy.json",
    "kill_switch_policy": "control/inventory/connectors/h13_local_private_boundary_kill_switch_policy.json",
    "output_policy": "control/inventory/connectors/h13_local_private_boundary_output_policy.json",
    "path_policy": "control/inventory/connectors/h13_local_private_boundary_path_policy.json",
    "review_policy": "control/inventory/connectors/h13_local_private_boundary_review_policy.json",
    "truth_policy": "control/inventory/connectors/h13_local_private_boundary_truth_policy.json",
    "no_access_policy": "control/inventory/connectors/h13_local_private_boundary_no_access_policy.json",
    "no_import_export_policy": "control/inventory/connectors/h13_local_private_boundary_no_import_export_policy.json",
    "private_data_policy": "control/inventory/connectors/h13_local_private_boundary_private_data_policy.json",
}

BOUNDARY_REQUEST_KEYS = {'local_folder_metadata': 'example_local_source_boundary', 'local_archive_file_metadata': 'example_archive_file_boundary', 'local_removable_media_metadata': 'example_removable_media_boundary', 'local_disk_image_metadata': 'example_disk_image_boundary', 'local_package_cache_metadata': 'example_package_cache_boundary', 'private_nas_metadata_boundary': 'example_private_nas_boundary', 'private_object_store_metadata_boundary': 'example_object_store_boundary', 'institutional_private_collection_boundary': 'example_institutional_private_boundary', 'user_supplied_url_metadata_boundary': 'example_user_supplied_url_boundary', 'user_owned_authenticated_source_boundary': 'example_authenticated_source_boundary', 'restricted_source_manifest_only': 'example_restricted_manifest_boundary', 'rights_sensitive_source_policy_blocked': 'example_rights_sensitive_policy_blocked_boundary'}
OPERATION_CLASSES = {'local_folder_metadata': ['local_source_boundary_check_future', 'filesystem_scan_forbidden_current'], 'local_archive_file_metadata': ['archive_boundary_check_future', 'archive_listing_forbidden_current', 'extraction_forbidden_current'], 'local_removable_media_metadata': ['removable_media_boundary_check_future', 'media_access_forbidden_current'], 'local_disk_image_metadata': ['disk_image_boundary_check_future', 'disk_image_listing_forbidden_current'], 'local_package_cache_metadata': ['package_cache_boundary_check_future', 'package_cache_scan_forbidden_current'], 'private_nas_metadata_boundary': ['private_network_storage_boundary_check_future', 'private_nas_access_forbidden_current'], 'private_object_store_metadata_boundary': ['object_store_boundary_check_future', 'object_store_access_forbidden_current'], 'institutional_private_collection_boundary': ['institutional_private_boundary_check_future', 'institutional_access_forbidden_current'], 'user_supplied_url_metadata_boundary': ['user_supplied_url_boundary_check_future', 'url_fetch_forbidden_current'], 'user_owned_authenticated_source_boundary': ['authenticated_source_boundary_check_future', 'account_access_forbidden_current'], 'restricted_source_manifest_only': ['restricted_manifest_boundary_check_future', 'restricted_source_access_forbidden_current'], 'rights_sensitive_source_policy_blocked': ['policy_blocked_boundary_check_current', 'direct_access_forbidden_current']}
REQUEST_FORBIDDEN_TRUE_KEYS = set(['account_access_requested', 'acquisition_action_requested', 'archive_listing_requested', 'authenticated_source_access_requested', 'credential_handling_requested', 'directory_listing_requested', 'disk_image_access_requested', 'evidence_write_requested', 'execution_requested', 'external_api_requested', 'extraction_requested', 'file_hashing_requested', 'filesystem_scan_requested', 'fingerprinting_requested', 'local_access_requested', 'local_cas_import_requested', 'malware_scanning_requested', 'model_provider_requested', 'network_access_requested', 'object_store_access_requested', 'pack_export_requested', 'pack_import_requested', 'package_cache_access_requested', 'private_nas_access_requested', 'private_source_access_requested', 'public_index_write_requested', 'public_share_requested', 'removable_media_access_requested', 'restricted_source_access_requested', 'review_queue_write_requested', 'source_cache_write_requested', 'upload_requested', 'user_supplied_url_fetch_requested'])
APPROVAL_FALSE_KEYS = tuple(['local_access_approved', 'private_source_access_approved', 'user_supplied_url_fetch_approved', 'authenticated_source_access_approved', 'restricted_source_access_approved', 'network_access_approved', 'external_api_approved', 'model_provider_approved', 'filesystem_scan_approved', 'directory_listing_approved', 'archive_listing_approved', 'removable_media_access_approved', 'disk_image_access_approved', 'package_cache_access_approved', 'private_nas_access_approved', 'object_store_access_approved', 'account_access_approved', 'credential_handling_approved', 'local_cas_import_approved', 'pack_export_approved', 'pack_import_approved', 'file_hashing_approved', 'fingerprinting_approved', 'malware_scanning_approved', 'extraction_approved', 'execution_approved', 'acquisition_action_approved', 'upload_approved', 'public_share_approved', 'source_cache_write_approved', 'evidence_write_approved', 'review_queue_write_approved', 'public_index_write_approved', 'master_index_write_approved', 'unrestricted_local_path_output_approved', 'credential_or_token_output_approved', 'private_payload_output_approved'])
TRUTH_BOUNDARY = {'boundary_dry_run_result_is_public_truth': False, 'normalized_record_is_public_truth': False, 'local_source_identity_candidate_is_truth': False, 'private_source_boundary_candidate_is_access_permission': False, 'user_supplied_url_candidate_is_fetch_permission': False, 'user_supplied_url_boundary_candidate_is_fetch_permission': False, 'authenticated_source_candidate_is_account_permission': False, 'authenticated_source_boundary_candidate_is_account_permission': False, 'restricted_source_manifest_grants_access_permission': False, 'restricted_source_manifest_candidate_grants_access_permission': False, 'cas_import_candidate_is_import_permission': False, 'local_cas_import_boundary_candidate_is_import_permission': False, 'pack_export_import_candidate_is_export_import_permission': False, 'pack_export_import_boundary_candidate_is_export_import_permission': False, 'privacy_redaction_candidate_proves_public_safety': False, 'rights_safety_candidate_is_rights_or_safety_truth': False, 'local_private_rights_safety_candidate_is_rights_or_safety_truth': False, 'source_cache_candidate_is_accepted_source': False, 'source_cache_preview_is_accepted_source': False, 'evidence_candidate_preview_is_accepted_evidence': False, 'evidence_preview_is_accepted_evidence': False, 'review_seed_is_review_decision': False, 'accepted_local_source_identity_truth': False, 'accepted_private_source_truth': False, 'accepted_user_supplied_url_truth': False, 'accepted_authenticated_source_truth': False, 'accepted_restricted_source_truth': False, 'accepted_cas_import_truth': False, 'accepted_CAS_import_truth': False, 'accepted_pack_export_import_truth': False, 'accepted_privacy_redaction_truth': False, 'accepted_rights_safety_truth': False, 'accepted_source_truth': False, 'accepted_evidence_truth': False, 'accepted_candidate_truth': False, 'accepted_public_record': False, 'public_index_mutated': False, 'master_index_mutated': False, 'mutated_public_index': False, 'mutated_master_index': False, 'rights_clearance_claimed': False, 'ownership_truth_claimed': False, 'user_authority_claimed': False, 'legal_access_claimed': False, 'publication_permission_claimed': False, 'privacy_safety_claimed': False, 'malware_safety_claimed': False, 'source_safety_claimed': False, 'verified_authenticity_claimed': False, 'production_readiness_claimed': False}
PRODUCT_BOUNDARY = {'changed_public_search_behavior': False, 'enabled_hosting': False, 'enabled_local_access': False, 'enabled_private_access': False, 'enabled_url_fetch': False, 'enabled_account_access': False, 'enabled_restricted_access': False, 'enabled_source_sync': False, 'enabled_cas_import': False, 'enabled_pack_export_import': False, 'enabled_extraction': False, 'enabled_execution': False, 'enabled_acquisition_actions': False, 'enabled_uploads': False, 'enabled_telemetry': False, 'local_access_used': False, 'private_source_access_used': False, 'user_supplied_url_fetch_used': False, 'authenticated_access_used': False, 'restricted_source_access_used': False, 'network_calls_made': False, 'api_calls_made': False, 'model_provider_calls_made': False, 'filesystem_scan_used': False, 'directory_listing_used': False, 'archive_listing_used': False, 'account_access_used': False, 'credential_handling_used': False, 'cas_import_used': False, 'pack_export_import_used': False, 'file_hashing_used': False, 'fingerprinting_used': False, 'malware_scanning_used': False, 'extraction_used': False, 'execution_used': False, 'acquisition_action_used': False, 'upload_used': False, 'publication_used': False, 'mutated_public_index': False, 'mutated_master_index': False}


def load_h13_local_private_boundary_policy_bundle(root: str | Path | None = None) -> dict[str, Any]:
    base = Path(root) if root is not None else Path(__file__).resolve().parents[5]
    return {key: json.loads((base / rel).read_text(encoding="utf-8")) for key, rel in POLICY_PATHS.items()}


def build_h13_local_private_boundary_dry_run_request(source_id: str, request_key: str, policy_bundle: Mapping[str, Any] | None = None, dry_run_requested: bool = True) -> dict[str, Any]:
    if source_id not in H13_SOURCE_CONFIGS:
        raise ValueError(f"unknown H13 source_id: {source_id}")
    cfg = H13_SOURCE_CONFIGS[source_id]
    operation_class = OPERATION_CLASSES[source_id][0]
    request = {
        "schema_version": "h13_local_private_boundary_dry_run_request.v0",
        "boundary_dry_run_request_id": f"h13.boundary_request.{source_id}.{_slug(request_key)}.v0",
        "source_id": source_id,
        "connector_family": cfg["connector_family"],
        "source_record_kind": cfg["source_boundary_class"],
        "operation_scope": "boundary_dry_run_only",
        "boundary_operation_class": operation_class,
        "approved_request_key": request_key,
        "local_source_context": "fixture_or_policy_boundary_only",
        "private_source_context": "blocked_current_no_private_access",
        "user_supplied_url_context": "blocked_current_no_fetch",
        "authenticated_source_context": "blocked_current_no_account_access",
        "restricted_source_context": "manifest_policy_only_no_direct_access",
        "cas_import_context": "blocked_current_no_cas_import",
        "pack_export_import_context": "blocked_current_no_pack_export_import",
        "privacy_redaction_context": "redacted_synthetic_public_safe_fields_only",
        "rights_safety_context": "candidate_only_no_rights_or_safety_truth",
        "approval_refs": [POLICY_PATHS["allowed_requests"]],
        "policy_refs": list(POLICY_PATHS.values()),
        "dry_run_requested": bool(dry_run_requested),
        "output_policy_ref": POLICY_PATHS["output_policy"],
        "review_policy_ref": POLICY_PATHS["review_policy"],
        "truth_policy_ref": POLICY_PATHS["truth_policy"],
        "product_boundary": _product_boundary(),
        "truth_boundary": _truth_boundary(),
        "limitations": ["Boundary dry-run request is fail-closed unless committed source policy approves the exact request key."],
        "notes": ["H13-BUNDLE-03 request envelopes are offline preflight material and do not access local/private/restricted sources."],
    }
    for key in REQUEST_FORBIDDEN_TRUE_KEYS:
        request[key] = False
    _raise_on_boundary_errors(request)
    return request


def validate_h13_boundary_dry_run_request(request: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []
    source_id = str(request.get("source_id") or "")
    request_key = str(request.get("approved_request_key") or "")
    if source_id not in H13_SOURCE_CONFIGS:
        reasons.append(f"{source_id or 'missing_source'} is not a known H13 local/private source")
    else:
        if request.get("operation_scope") != "boundary_dry_run_only":
            reasons.append("operation_scope must be boundary_dry_run_only")
        operation_class = str(request.get("boundary_operation_class") or "")
        if operation_class not in OPERATION_CLASSES[source_id]:
            reasons.append("boundary_operation_class is not allowlisted for this source")
    for key in sorted(REQUEST_FORBIDDEN_TRUE_KEYS):
        if request.get(key) is True:
            reasons.append(f"{key} is forbidden for H13-BUNDLE-03 boundary dry-runs")
    if source_id in H13_SOURCE_CONFIGS:
        reasons.extend(validate_h13_boundary_source_approval(source_id, request_key, policy_bundle)["blocked_reasons"])
    reasons = _dedupe(reasons)
    return {"approved": not reasons, "result_status": _status_for_reasons(reasons), "blocked_reasons": reasons}


def validate_h13_boundary_source_approval(source_id: str, request_key: str, policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []
    if source_id not in H13_SOURCE_CONFIGS:
        return {"approved": False, "result_status": "blocked_by_policy", "blocked_reasons": [f"{source_id} is not a known H13 source"]}
    allowed = _source_policy(source_id, policy_bundle, "allowed_requests")
    if not allowed:
        reasons.append("source is not listed in H13 boundary allowed request policy")
    else:
        if allowed.get("approval_status") != "approved_for_boundary_dry_run":
            reasons.append("source approval_status is not approved_for_boundary_dry_run")
        if allowed.get("boundary_dry_run_approved") is not True:
            reasons.append("boundary_dry_run_approved is missing or false")
        if allowed.get("approved_source_id") != source_id:
            reasons.append("approved_source_id does not match requested source")
        if allowed.get("operation_scope") != "boundary_dry_run_only":
            reasons.append("operation_scope is not boundary_dry_run_only")
        if allowed.get("approved_operation_class") != "boundary_only":
            reasons.append("approved operation class is not boundary_only")
        if request_key not in (allowed.get("allowed_request_keys") or []):
            reasons.append("request key is not approved for this source")
        if int(allowed.get("max_operations_current") or 0) <= 0:
            reasons.append("request budget is not approved")
        for key in APPROVAL_FALSE_KEYS:
            if allowed.get(key) is not False:
                reasons.append(f"{key} must remain false")
    global_policy = policy_bundle.get("boundary_dry_run_policy", {})
    if global_policy.get("allowed_operation_scope") != "boundary_dry_run_only":
        reasons.append("global allowed operation scope is not boundary_dry_run_only")
    for key, value in global_policy.items():
        if key.endswith("_enabled") and value is True:
            reasons.append(f"global policy {key} must remain false")
    kill = policy_bundle.get("kill_switch_policy", {})
    if kill.get("kill_switch_defaults_fail_closed") is not True:
        reasons.append("kill switch does not default fail-closed")
    if kill.get("boundary_dry_run_kill_switch_enabled") is True:
        reasons.append("boundary dry-run kill switch is enabled")
    return {"approved": not reasons, "result_status": _status_for_reasons(reasons), "blocked_reasons": _dedupe(reasons)}


def build_h13_boundary_dry_run_blocked_result(request: Mapping[str, Any], reason: str | list[str], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    source_id = str(request.get("source_id") or "unknown")
    cfg = H13_SOURCE_CONFIGS.get(source_id, {"connector_family": request.get("connector_family", "unknown"), "source_boundary_class": request.get("source_record_kind", "unknown")})
    reasons = reason if isinstance(reason, list) else [reason]
    normalized = _normal_record_from_request(request)
    result = {
        "schema_version": "h13_local_private_boundary_dry_run_result.v0",
        "boundary_dry_run_result_id": f"h13.boundary_result.{source_id}.{_short_fingerprint(request)}.v0",
        "boundary_dry_run_request_ref": request.get("boundary_dry_run_request_id"),
        "source_id": source_id,
        "connector_family": cfg["connector_family"],
        "source_record_kind": cfg["source_boundary_class"],
        "result_status": _status_for_reasons(reasons),
        "operation_count": 0,
        "local_access_used": False,
        "private_source_access_used": False,
        "user_supplied_url_fetch_used": False,
        "authenticated_access_used": False,
        "restricted_source_access_used": False,
        "network_used": False,
        "external_api_used": False,
        "model_provider_used": False,
        "filesystem_scan_performed": False,
        "directory_listing_performed": False,
        "archive_listing_performed": False,
        "cas_import_performed": False,
        "pack_export_performed": False,
        "pack_import_performed": False,
        "source_cache_write_performed": False,
        "evidence_write_performed": False,
        "public_index_write_performed": False,
        "master_index_write_performed": False,
        "normalized_record": normalized,
        "local_source_identity_candidate": normalized["local_source_identity_candidate"],
        "private_source_boundary_candidate": normalized["private_source_boundary_candidate"],
        "user_supplied_url_boundary_candidate": normalized["user_supplied_url_boundary_candidate"],
        "authenticated_source_boundary_candidate": normalized["authenticated_source_boundary_candidate"],
        "restricted_source_manifest_candidate": normalized["restricted_source_manifest_candidate"],
        "local_cas_import_boundary_candidate": normalized["local_cas_import_boundary_candidate"],
        "pack_export_import_boundary_candidate": normalized["pack_export_import_boundary_candidate"],
        "privacy_redaction_candidate": normalized["privacy_redaction_candidate"],
        "local_private_rights_safety_candidate": normalized["local_private_rights_safety_candidate"],
        "source_cache_candidate_preview": normalized["source_cache_candidate_preview"],
        "evidence_candidate_preview": normalized["evidence_candidate_preview"],
        "review_queue_seed_preview": None,
        "boundary_health_summary": None,
        "blocked_reason": "; ".join(reasons) if reasons else None,
        "blocked_reasons": reasons,
        "warnings": [],
        "limitations": ["No boundary action was approved or performed; output is fixture-equivalent candidate/preview material only."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["No local/private/restricted access, source cache write, evidence write, review queue write, public index mutation, or master index mutation occurs."],
    }
    result["review_queue_seed_preview"] = build_h13_review_queue_seed_preview_from_boundary(result, result["source_cache_candidate_preview"], result["evidence_candidate_preview"], policy_bundle)
    result["boundary_health_summary"] = build_h13_boundary_health_summary(result, policy_bundle)
    _raise_on_boundary_errors(result)
    return result


def build_h13_boundary_dry_run_result(source_id: str, fixture_or_boundary_payload: Mapping[str, Any], response_metadata: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    if source_id not in H13_SOURCE_CONFIGS:
        raise ValueError(f"unknown H13 source_id: {source_id}")
    cfg = H13_SOURCE_CONFIGS[source_id]
    if fixture_or_boundary_payload.get("schema_version") == "h13_local_private_fixture.v0":
        fixture = dict(fixture_or_boundary_payload)
    else:
        fixture = _synthetic_fixture(source_id, str(response_metadata.get("request_key") or BOUNDARY_REQUEST_KEYS[source_id]), fixture_or_boundary_payload)
    normalized = normalize_h13_local_private_fixture(fixture, source_id, policy_bundle)
    result = {
        "schema_version": "h13_local_private_boundary_dry_run_result.v0",
        "boundary_dry_run_result_id": f"h13.boundary_result.{source_id}.{_short_fingerprint(fixture)}.v0",
        "boundary_dry_run_request_ref": response_metadata.get("boundary_dry_run_request_ref", "mocked_or_fixture_equivalent_boundary_request"),
        "source_id": source_id,
        "connector_family": cfg["connector_family"],
        "source_record_kind": cfg["source_boundary_class"],
        "result_status": response_metadata.get("result_status", "boundary_dry_run_completed"),
        "operation_count": int(response_metadata.get("operation_count") or 1),
        "local_access_used": False,
        "private_source_access_used": False,
        "user_supplied_url_fetch_used": False,
        "authenticated_access_used": False,
        "restricted_source_access_used": False,
        "network_used": False,
        "external_api_used": False,
        "model_provider_used": False,
        "filesystem_scan_performed": False,
        "directory_listing_performed": False,
        "archive_listing_performed": False,
        "cas_import_performed": False,
        "pack_export_performed": False,
        "pack_import_performed": False,
        "source_cache_write_performed": False,
        "evidence_write_performed": False,
        "public_index_write_performed": False,
        "master_index_write_performed": False,
        "normalized_record": normalized,
        "local_source_identity_candidate": normalized["local_source_identity_candidate"],
        "private_source_boundary_candidate": normalized["private_source_boundary_candidate"],
        "user_supplied_url_boundary_candidate": normalized["user_supplied_url_boundary_candidate"],
        "authenticated_source_boundary_candidate": normalized["authenticated_source_boundary_candidate"],
        "restricted_source_manifest_candidate": normalized["restricted_source_manifest_candidate"],
        "local_cas_import_boundary_candidate": normalized["local_cas_import_boundary_candidate"],
        "pack_export_import_boundary_candidate": normalized["pack_export_import_boundary_candidate"],
        "privacy_redaction_candidate": normalized["privacy_redaction_candidate"],
        "local_private_rights_safety_candidate": normalized["local_private_rights_safety_candidate"],
        "source_cache_candidate_preview": normalized["source_cache_candidate_preview"],
        "evidence_candidate_preview": normalized["evidence_candidate_preview"],
        "review_queue_seed_preview": None,
        "boundary_health_summary": None,
        "blocked_reason": None,
        "blocked_reasons": [],
        "warnings": list(response_metadata.get("warnings") or []),
        "limitations": ["Boundary dry-run output remains candidate/preview material only."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["No local/private/restricted access, import/export/publication, source cache write, evidence write, or index mutation occurs."],
    }
    result["review_queue_seed_preview"] = build_h13_review_queue_seed_preview_from_boundary(result, result["source_cache_candidate_preview"], result["evidence_candidate_preview"], policy_bundle)
    result["boundary_health_summary"] = build_h13_boundary_health_summary(result, policy_bundle)
    _raise_on_boundary_errors(result)
    return result


def normalize_h13_boundary_dry_run_result(result: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    normalized = result.get("normalized_record")
    if not isinstance(normalized, Mapping):
        raise ValueError("boundary dry-run result is missing normalized_record")
    return dict(normalized)


def build_h13_local_source_identity_candidate_from_boundary(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return _fixture_local_source_candidate(normalized_record, policy_bundle)


def build_h13_private_source_boundary_candidate_from_boundary(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return _fixture_private_candidate(normalized_record, policy_bundle)


def build_h13_user_supplied_url_boundary_candidate_from_boundary(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return _fixture_url_candidate(normalized_record, policy_bundle)


def build_h13_authenticated_source_boundary_candidate_from_boundary(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return _fixture_auth_candidate(normalized_record, policy_bundle)


def build_h13_restricted_source_manifest_candidate_from_boundary(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return _fixture_restricted_candidate(normalized_record, policy_bundle)


def build_h13_local_cas_import_boundary_candidate_from_boundary(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return _fixture_cas_candidate(normalized_record, policy_bundle)


def build_h13_pack_export_import_boundary_candidate_from_boundary(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return _fixture_pack_candidate(normalized_record, policy_bundle)


def build_h13_privacy_redaction_candidate_from_boundary(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return _fixture_privacy_candidate(normalized_record, policy_bundle)


def build_h13_local_private_rights_safety_candidate_from_boundary(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return _fixture_rights_candidate(normalized_record, policy_bundle)


def build_h13_source_cache_candidate_preview_from_boundary(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return _fixture_source_cache_preview(normalized_record, policy_bundle)


def build_h13_evidence_candidate_preview_from_boundary(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return _fixture_evidence_preview(normalized_record, policy_bundle)


def build_h13_review_queue_seed_preview_from_boundary(result: Mapping[str, Any], source_cache_preview: Mapping[str, Any], evidence_preview: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    seed = {
        "schema_version": "h13_local_private_boundary_review_seed.v0",
        "review_seed_id": f"h13.boundary.review_seed.{result.get('source_id')}.{_short_fingerprint(result)}.v0",
        "source_id": result.get("source_id"),
        "boundary_dry_run_result_ref": result.get("boundary_dry_run_result_id"),
        "source_cache_candidate_preview_ref": source_cache_preview.get("preview_id"),
        "evidence_candidate_preview_ref": evidence_preview.get("preview_id"),
        "review_seed_only": True,
        "review_decision": False,
        "review_queue_write_performed": False,
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "limitations": ["Review seed preview only; no review queue write or review decision occurs."],
    }
    _raise_on_boundary_errors(seed)
    return seed


def build_h13_boundary_health_summary(result: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    health = {
        "schema_version": "h13_local_private_boundary_health_summary.v0",
        "health_summary_id": f"h13.boundary.health.{result.get('source_id')}.{_short_fingerprint(result)}.v0",
        "source_id": result.get("source_id"),
        "connector_family": result.get("connector_family"),
        "boundary_dry_run_status": result.get("result_status"),
        "operation_count": int(result.get("operation_count") or 0),
        "policy_blockers": list(result.get("blocked_reasons") or []),
        "warnings": list(result.get("warnings") or []),
        "source_limitations": list(result.get("limitations") or []),
        "private_data_status": "blocked_no_private_payloads",
        "redaction_status": "synthetic_public_safe_redaction_required",
        "restricted_source_status": "manifest_policy_only_no_direct_access",
        "next_recommended_action": "review_fixture_equivalent_outputs_before_any_future_approval",
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "limitations": ["Boundary health summary is not production readiness."],
    }
    _raise_on_boundary_errors(health)
    return health


def build_h13_boundary_dry_run_output_bundle(result: Mapping[str, Any]) -> dict[str, Any]:
    bundle = {
        "schema_version": "h13_local_private_boundary_dry_run_output_bundle.v0",
        "boundary_dry_run_result": result,
        "normalized_record": result.get("normalized_record"),
        "local_source_identity_candidate": result.get("local_source_identity_candidate"),
        "private_source_boundary_candidate": result.get("private_source_boundary_candidate"),
        "user_supplied_url_boundary_candidate": result.get("user_supplied_url_boundary_candidate"),
        "authenticated_source_boundary_candidate": result.get("authenticated_source_boundary_candidate"),
        "restricted_source_manifest_candidate": result.get("restricted_source_manifest_candidate"),
        "local_cas_import_boundary_candidate": result.get("local_cas_import_boundary_candidate"),
        "pack_export_import_boundary_candidate": result.get("pack_export_import_boundary_candidate"),
        "privacy_redaction_candidate": result.get("privacy_redaction_candidate"),
        "local_private_rights_safety_candidate": result.get("local_private_rights_safety_candidate"),
        "source_cache_candidate_preview": result.get("source_cache_candidate_preview"),
        "evidence_candidate_preview": result.get("evidence_candidate_preview"),
        "review_queue_seed_preview": result.get("review_queue_seed_preview"),
        "boundary_health_summary": result.get("boundary_health_summary"),
        "validation_summary": {
            "truth_boundary_violations": detect_h13_boundary_truth_boundary_violations(result, {}),
            "product_boundary_violations": detect_h13_boundary_product_boundary_violations(result, {}),
            "private_data_violations": detect_h13_boundary_private_data_violations(result, {}),
        },
    }
    _raise_on_boundary_errors(bundle)
    return bundle


def summarize_h13_boundary_dry_run_result(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "source_id": result.get("source_id"),
        "result_status": result.get("result_status"),
        "operation_count": int(result.get("operation_count") or 0),
        "local_access_used": bool(result.get("local_access_used")),
        "network_used": bool(result.get("network_used")),
        "blocked_reasons": list(result.get("blocked_reasons") or []),
        "candidate_count": 9,
        "truth_boundary_violations": detect_h13_boundary_truth_boundary_violations(result, {}),
        "product_boundary_violations": detect_h13_boundary_product_boundary_violations(result, {}),
        "private_data_violations": detect_h13_boundary_private_data_violations(result, {}),
    }


def detect_h13_boundary_truth_boundary_violations(result: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> list[str]:
    return _fixture_truth_violations(result)


def detect_h13_boundary_product_boundary_violations(result: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> list[str]:
    return _fixture_product_violations(result)


def detect_h13_boundary_private_data_violations(result: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> list[str]:
    return _fixture_private_data_violations(result)


def _normal_record_from_request(request: Mapping[str, Any]) -> dict[str, Any]:
    source_id = str(request.get("source_id") or "local_folder_metadata")
    if source_id not in H13_SOURCE_CONFIGS:
        source_id = "local_folder_metadata"
    fixture = _synthetic_fixture(source_id, str(request.get("approved_request_key") or BOUNDARY_REQUEST_KEYS[source_id]), {
        "metadata_summary": "Blocked boundary dry-run fixture-equivalent metadata only.",
        "source_native_id": f"blocked-boundary-{source_id}",
    })
    return normalize_h13_local_private_fixture(fixture, source_id)


def _synthetic_fixture(source_id: str, request_key: str, payload: Mapping[str, Any]) -> dict[str, Any]:
    cfg = H13_SOURCE_CONFIGS[source_id]
    safe_payload = {
        "source_record_kind": cfg["source_boundary_class"],
        "source_native_id": str(payload.get("source_native_id") or f"boundary-{source_id}-{request_key}"),
        "metadata_summary": str(payload.get("metadata_summary") or "Synthetic H13 boundary dry-run metadata only."),
        "local_source_label": str(payload.get("local_source_label") or cfg["source_label"]),
        "local_source_kind": cfg["source_boundary_class"],
        "declared_owner_or_controller_candidate": "declared_controller_candidate_not_verified",
        "source_scope_candidate": "synthetic_fixture_boundary_scope",
        "path_or_locator_redacted": redact_h13_locator(f"h13:{source_id}:{request_key}"),
        "path_hash_candidate": hash_h13_locator(f"h13:{source_id}:{request_key}"),
        "source_manifest_ref": f"h13-boundary-manifest:{source_id}:{request_key}",
        "file_count_candidate": "not_evaluated_no_scan",
        "byte_count_candidate": "not_evaluated_no_scan",
        "observed_format_candidate": "not_evaluated_no_access",
        "local_identifier_candidate": f"h13-local-boundary:{source_id}",
        "source_visibility": "local_private_or_restricted_boundary",
        "source_sensitivity": "review_required",
        "private_source_ref": f"private-boundary:{source_id}",
        "private_source_kind": cfg["source_boundary_class"],
        "access_method_candidate": "blocked_current_no_access",
        "privacy_label": "private_or_sensitive_review_required",
        "confidentiality_label": "not_public",
        "exportability_label": "blocked_current",
        "public_safe_label": "synthetic_public_safe_candidate",
        "redaction_requirement": "required",
        "consent_or_authority_requirement": "required_before_any_access",
        "review_required": True,
        "blocked_action_candidate": "direct_access_import_export_publication_blocked_current",
        "user_supplied_locator_candidate": "[redacted-h13-locator:boundary-request]",
        "locator_hash_candidate": hash_h13_locator(f"locator:{source_id}:{request_key}"),
        "declared_purpose_candidate": "boundary_dry_run_only",
        "public_or_private_locator_candidate": "not_evaluated_no_fetch",
        "access_control_risk_candidate": "review_required",
        "robots_or_policy_risk_candidate": "not_evaluated_no_fetch",
        "rights_sensitivity_candidate": "review_required",
        "fetch_allowed_current": False,
        "authenticated_source_ref": f"authenticated-boundary:{source_id}",
        "account_required_candidate": "not_evaluated_no_account_access",
        "user_owned_account_candidate": "not_verified",
        "credential_or_token_candidate": "blocked_current_no_credentials",
        "session_cookie_candidate": "blocked_current_no_sessions",
        "entitlement_or_license_candidate": "not_evaluated_no_account_access",
        "personal_data_risk_candidate": "review_required",
        "privacy_review_required": True,
        "restricted_source_ref": f"restricted-manifest:{source_id}",
        "restricted_source_category": "not_evaluable",
        "manifest_only_allowed_candidate": True,
        "forbidden_access_reason": "direct_access_forbidden_current",
        "legal_or_policy_risk_candidate": "review_required",
        "safety_risk_candidate": "not_evaluated_no_access",
        "public_metadata_only_candidate": "manifest_only_candidate",
        "user_import_boundary": "blocked_current_no_import",
        "local_import_candidate_id": f"cas-boundary:{source_id}",
        "source_ref": f"h13-source:{source_id}",
        "import_scope_candidate": "blocked_current_no_import",
        "hash_algorithm_candidate": "not_evaluated_no_file_hashing",
        "cas_write_allowed_current": False,
        "dedup_allowed_current": False,
        "file_hashing_allowed_current": False,
        "private_blob_status": "no_blob_present",
        "pack_candidate_id": f"pack-boundary:{source_id}",
        "pack_kind": "boundary_preview_only",
        "public_safe_status": "not_proven_review_required",
        "private_data_risk_candidate": "review_required",
        "rights_sensitive_data_risk_candidate": "review_required",
        "export_allowed_current": False,
        "import_allowed_current": False,
        "private_path_policy": "redact_or_hash",
        "locator_redaction_policy": "redact_or_hash",
        "account_identifier_policy": "blocked",
        "user_identifier_policy": "blocked",
        "file_name_sensitivity_policy": "minimize_or_redact",
        "source_label_policy": "synthetic_public_safe_only",
        "metadata_minimization_policy": "required",
        "public_safe_field_policy": "candidate_only",
        "blocked_field_policy": "credentials_private_payloads_unrestricted_paths",
        "rights_statement_candidate": "not_evaluated",
        "declared_ownership_candidate": "not_rights_clearance",
        "user_authority_candidate": "not_verified",
        "license_metadata_candidate": "not_evaluated",
        "restricted_access_candidate": "review_required",
        "sensitive_content_candidate": "not_evaluated_no_access",
        "malware_or_security_risk_candidate": "not_evaluated_no_scan",
        "privacy_risk_candidate": "review_required",
        "publication_permission_current": False,
    }
    safe_payload.update({key: value for key, value in payload.items() if isinstance(value, (str, int, bool, list, dict)) and key in safe_payload})
    return {
        "schema_version": "h13_local_private_fixture.v0",
        "fixture_id": f"h13.boundary.fixture.{source_id}.{_slug(request_key)}.v0",
        "source_id": source_id,
        "connector_family": cfg["connector_family"],
        "fixture_kind": "policy_blocked",
        "fixture_status": "synthetic_boundary_dry_run",
        "fixture_public_safe": True,
        "local_access_used": False,
        "private_source_access_used": False,
        "user_supplied_url_fetch_used": False,
        "authenticated_access_used": False,
        "restricted_source_access_used": False,
        "network_used": False,
        "external_api_used": False,
        "model_provider_used": False,
        "filesystem_scan_performed": False,
        "directory_listing_performed": False,
        "archive_listing_performed": False,
        "removable_media_accessed": False,
        "disk_image_accessed": False,
        "package_cache_accessed": False,
        "private_nas_accessed": False,
        "object_store_accessed": False,
        "account_payload_included": False,
        "credential_or_token_payload_included": False,
        "cookie_or_session_payload_included": False,
        "receipt_payload_included": False,
        "license_key_payload_included": False,
        "entitlement_payload_included": False,
        "private_file_payload_included": False,
        "local_file_content_included": False,
        "unrestricted_local_path_included": False,
        "redacted_path_included": True,
        "path_hash_included": True,
        "cas_blob_included": False,
        "exported_pack_included": False,
        "imported_pack_included": False,
        "source_cache_write_included": False,
        "evidence_write_included": False,
        "public_index_write_included": False,
        "master_index_write_included": False,
        "extraction_output_included": False,
        "execution_output_included": False,
        "acquisition_action_performed": False,
        "upload_performed": False,
        "publication_performed": False,
        "fixture_payload": safe_payload,
        "expected_normalized_ref": None,
        "limitations": ["Synthetic boundary dry-run fixture-equivalent payload only."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["No local/private/restricted source is accessed."],
    }


def _source_policy(source_id: str, policy_bundle: Mapping[str, Any], section: str) -> dict[str, Any]:
    for item in policy_bundle.get(section, {}).get("sources", []):
        if isinstance(item, Mapping) and item.get("source_id") == source_id:
            return dict(item)
    return {}


def _status_for_reasons(reasons: list[str]) -> str:
    text = " ".join(reasons).casefold()
    if not reasons:
        return "boundary_dry_run_completed"
    if "approval_status" in text or "boundary_dry_run_approved" in text or "request key" in text or "budget" in text:
        return "blocked_by_missing_approval"
    if "kill switch" in text:
        return "blocked_by_kill_switch"
    if "local_access" in text or "local access" in text:
        return "blocked_by_local_access_policy"
    if "private_source" in text:
        return "blocked_by_private_source_policy"
    if "user_supplied_url" in text or "url" in text and "fetch" in text:
        return "blocked_by_user_supplied_url_policy"
    if "authenticated" in text or "account_access" in text:
        return "blocked_by_authenticated_source_policy"
    if "restricted" in text:
        return "blocked_by_restricted_source_policy"
    if "network" in text or "external_api" in text or "model_provider" in text:
        return "blocked_by_network_policy"
    if "filesystem" in text or "directory_listing" in text or "archive_listing" in text:
        return "blocked_by_filesystem_policy"
    if "credential" in text or "token" in text or "session" in text or "cookie" in text:
        return "blocked_by_credential_policy"
    if "cas" in text or "pack_" in text or "hashing" in text or "fingerprinting" in text or "malware" in text:
        return "blocked_by_import_export_policy"
    if "publication" in text or "upload" in text or "public_share" in text or "execution" in text or "extraction" in text or "acquisition" in text:
        return "blocked_by_publication_policy"
    if "approval" in text or "approved" in text:
        return "blocked_by_missing_approval"
    return "blocked_by_policy"


def _truth_boundary() -> dict[str, bool]:
    return dict(TRUTH_BOUNDARY)


def _product_boundary() -> dict[str, bool]:
    return dict(PRODUCT_BOUNDARY)


def _slug(value: Any) -> str:
    digest = hashlib.sha256(str(value).encode("utf-8")).hexdigest()
    return digest[:12]


def _short_fingerprint(value: Any) -> str:
    return _slug(json.dumps(value, sort_keys=True, default=str))


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        if item and item not in seen:
            seen.add(item)
            out.append(item)
    return out


def _raise_on_boundary_errors(value: Mapping[str, Any]) -> None:
    violations = detect_h13_boundary_truth_boundary_violations(value, {}) + detect_h13_boundary_product_boundary_violations(value, {}) + detect_h13_boundary_private_data_violations(value, {})
    if violations:
        raise ValueError("; ".join(violations))
