"""Offline H13 local/private fixture normalization helpers."""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
H13_SOURCE_CONFIGS = {'local_folder_metadata': {'source_id': 'local_folder_metadata', 'source_label': 'Local folder metadata', 'connector_family': 'local_folder_boundary', 'trust_lane': 'local_private', 'source_boundary_class': 'local_source'}, 'local_archive_file_metadata': {'source_id': 'local_archive_file_metadata', 'source_label': 'Local archive file metadata', 'connector_family': 'local_archive_boundary', 'trust_lane': 'local_private', 'source_boundary_class': 'local_source'}, 'local_removable_media_metadata': {'source_id': 'local_removable_media_metadata', 'source_label': 'Local removable media metadata', 'connector_family': 'local_media_boundary', 'trust_lane': 'local_private', 'source_boundary_class': 'local_source'}, 'local_disk_image_metadata': {'source_id': 'local_disk_image_metadata', 'source_label': 'Local disk image metadata', 'connector_family': 'local_disk_image_boundary', 'trust_lane': 'local_private', 'source_boundary_class': 'local_source'}, 'local_package_cache_metadata': {'source_id': 'local_package_cache_metadata', 'source_label': 'Local package cache metadata', 'connector_family': 'local_package_cache_boundary', 'trust_lane': 'local_private', 'source_boundary_class': 'local_source'}, 'private_nas_metadata_boundary': {'source_id': 'private_nas_metadata_boundary', 'source_label': 'Private NAS metadata boundary', 'connector_family': 'private_network_storage_boundary', 'trust_lane': 'local_private', 'source_boundary_class': 'private_source'}, 'private_object_store_metadata_boundary': {'source_id': 'private_object_store_metadata_boundary', 'source_label': 'Private object-store metadata boundary', 'connector_family': 'private_object_store_boundary', 'trust_lane': 'local_private', 'source_boundary_class': 'private_source'}, 'institutional_private_collection_boundary': {'source_id': 'institutional_private_collection_boundary', 'source_label': 'Institutional private collection boundary', 'connector_family': 'institutional_private_boundary', 'trust_lane': 'local_private', 'source_boundary_class': 'institutional_private_source'}, 'user_supplied_url_metadata_boundary': {'source_id': 'user_supplied_url_metadata_boundary', 'source_label': 'User-supplied URL metadata boundary', 'connector_family': 'user_supplied_url_boundary', 'trust_lane': 'user_supplied', 'source_boundary_class': 'user_supplied_source'}, 'user_owned_authenticated_source_boundary': {'source_id': 'user_owned_authenticated_source_boundary', 'source_label': 'User-owned authenticated source boundary', 'connector_family': 'authenticated_user_source_boundary', 'trust_lane': 'user_supplied', 'source_boundary_class': 'authenticated_user_source'}, 'restricted_source_manifest_only': {'source_id': 'restricted_source_manifest_only', 'source_label': 'Restricted-source manifest-only boundary', 'connector_family': 'restricted_manifest_only', 'trust_lane': 'restricted_manifest_only', 'source_boundary_class': 'restricted_manifest_only'}, 'rights_sensitive_source_policy_blocked': {'source_id': 'rights_sensitive_source_policy_blocked', 'source_label': 'Rights-sensitive source policy-blocked boundary', 'connector_family': 'policy_blocked_boundary', 'trust_lane': 'policy_blocked', 'source_boundary_class': 'policy_blocked_source'}}
H13_SOURCE_IDS = tuple(H13_SOURCE_CONFIGS)
H13_FIXTURE_KINDS = ('minimal', 'local_source_identity', 'private_source_boundary', 'user_supplied_url_boundary', 'authenticated_source_boundary', 'restricted_source_manifest', 'local_cas_import_boundary', 'pack_export_import_boundary', 'privacy_redaction', 'rights_safety', 'policy_blocked')
NORMALIZED_SCALAR_FIELDS = ('local_source_label', 'local_source_kind', 'declared_owner_or_controller_candidate', 'source_scope_candidate', 'path_or_locator_redacted', 'path_hash_candidate', 'source_manifest_ref', 'file_count_candidate', 'byte_count_candidate', 'observed_format_candidate', 'local_identifier_candidate', 'source_visibility', 'source_sensitivity', 'private_source_ref', 'private_source_kind', 'access_method_candidate', 'declared_controller_candidate', 'privacy_label', 'confidentiality_label', 'exportability_label', 'public_safe_label', 'redaction_requirement', 'consent_or_authority_requirement', 'review_required', 'blocked_action_candidate', 'user_supplied_locator_candidate', 'locator_hash_candidate', 'declared_purpose_candidate', 'public_or_private_locator_candidate', 'access_control_risk_candidate', 'robots_or_policy_risk_candidate', 'rights_sensitivity_candidate', 'fetch_allowed_current', 'authenticated_source_ref', 'account_required_candidate', 'user_owned_account_candidate', 'credential_or_token_candidate', 'session_cookie_candidate', 'entitlement_or_license_candidate', 'personal_data_risk_candidate', 'privacy_review_required', 'restricted_source_ref', 'restricted_source_category', 'manifest_only_allowed_candidate', 'forbidden_access_reason', 'legal_or_policy_risk_candidate', 'safety_risk_candidate', 'public_metadata_only_candidate', 'user_import_boundary', 'local_import_candidate_id', 'source_ref', 'import_scope_candidate', 'hash_algorithm_candidate', 'cas_write_allowed_current', 'dedup_allowed_current', 'file_hashing_allowed_current', 'private_blob_status', 'pack_candidate_id', 'pack_kind', 'public_safe_status', 'private_data_risk_candidate', 'rights_sensitive_data_risk_candidate', 'export_allowed_current', 'import_allowed_current', 'private_path_policy', 'locator_redaction_policy', 'account_identifier_policy', 'user_identifier_policy', 'file_name_sensitivity_policy', 'source_label_policy', 'metadata_minimization_policy', 'public_safe_field_policy', 'blocked_field_policy', 'rights_statement_candidate', 'declared_ownership_candidate', 'user_authority_candidate', 'license_metadata_candidate', 'restricted_access_candidate', 'sensitive_content_candidate', 'malware_or_security_risk_candidate', 'privacy_risk_candidate', 'personal_data_risk_candidate', 'publication_permission_current', 'source_native_id', 'metadata_summary')
CANDIDATE_FIELD_MAP = {'local_source_identity': ['local_source_label', 'local_source_kind', 'declared_owner_or_controller_candidate', 'source_scope_candidate', 'path_or_locator_redacted', 'path_hash_candidate', 'source_manifest_ref', 'file_count_candidate', 'byte_count_candidate', 'observed_format_candidate', 'local_identifier_candidate', 'source_visibility', 'source_sensitivity', 'allowed_current_mode', 'blocked_action_candidate'], 'private_source_boundary': ['private_source_ref', 'private_source_kind', 'access_method_candidate', 'declared_controller_candidate', 'privacy_label', 'confidentiality_label', 'exportability_label', 'public_safe_label', 'redaction_requirement', 'consent_or_authority_requirement', 'review_required', 'blocked_action_candidate'], 'user_supplied_url_boundary': ['user_supplied_locator_candidate', 'locator_hash_candidate', 'declared_purpose_candidate', 'public_or_private_locator_candidate', 'access_control_risk_candidate', 'robots_or_policy_risk_candidate', 'rights_sensitivity_candidate', 'fetch_allowed_current', 'review_required', 'blocked_action_candidate'], 'authenticated_source_boundary': ['authenticated_source_ref', 'account_required_candidate', 'user_owned_account_candidate', 'credential_or_token_candidate', 'session_cookie_candidate', 'entitlement_or_license_candidate', 'personal_data_risk_candidate', 'allowed_current_mode', 'privacy_review_required', 'blocked_action_candidate'], 'restricted_source_manifest': ['restricted_source_ref', 'restricted_source_category', 'manifest_only_allowed_candidate', 'forbidden_access_reason', 'rights_sensitivity_candidate', 'legal_or_policy_risk_candidate', 'safety_risk_candidate', 'public_metadata_only_candidate', 'user_import_boundary', 'review_required', 'blocked_action_candidate'], 'local_cas_import_boundary': ['local_import_candidate_id', 'source_ref', 'import_scope_candidate', 'hash_algorithm_candidate', 'cas_write_allowed_current', 'dedup_allowed_current', 'file_hashing_allowed_current', 'private_blob_status', 'exportability_label', 'review_required', 'blocked_action_candidate'], 'pack_export_import_boundary': ['pack_candidate_id', 'pack_kind', 'source_ref', 'public_safe_status', 'private_data_risk_candidate', 'rights_sensitive_data_risk_candidate', 'redaction_requirement', 'export_allowed_current', 'import_allowed_current', 'review_required', 'blocked_action_candidate'], 'privacy_redaction': ['private_path_policy', 'locator_redaction_policy', 'account_identifier_policy', 'user_identifier_policy', 'file_name_sensitivity_policy', 'source_label_policy', 'metadata_minimization_policy', 'public_safe_field_policy', 'blocked_field_policy', 'review_required'], 'local_private_rights_safety': ['rights_statement_candidate', 'declared_ownership_candidate', 'user_authority_candidate', 'license_metadata_candidate', 'restricted_access_candidate', 'sensitive_content_candidate', 'malware_or_security_risk_candidate', 'privacy_risk_candidate', 'personal_data_risk_candidate', 'blocked_action_candidate', 'publication_permission_current']}
FIXTURE_FORBIDDEN_TRUE_KEYS = {'private_source_access_used', 'credential_or_token_payload_included', 'filesystem_scan_performed', 'account_payload_included', 'authenticated_access_used', 'archive_listing_performed', 'unrestricted_local_path_included', 'master_index_write_included', 'external_api_used', 'receipt_payload_included', 'exported_pack_included', 'extraction_output_included', 'execution_output_included', 'user_supplied_url_fetch_used', 'model_provider_used', 'private_nas_accessed', 'removable_media_accessed', 'evidence_write_included', 'package_cache_accessed', 'directory_listing_performed', 'restricted_source_access_used', 'cookie_or_session_payload_included', 'cas_blob_included', 'disk_image_accessed', 'object_store_accessed', 'private_file_payload_included', 'upload_performed', 'acquisition_action_performed', 'license_key_payload_included', 'publication_performed', 'source_cache_write_included', 'public_index_write_included', 'local_file_content_included', 'network_used', 'local_access_used', 'entitlement_payload_included', 'imported_pack_included'}
TRUTH_FORBIDDEN_TRUE_KEYS = {'malware_safety_claimed', 'accepted_pack_export_import_truth', 'accepted_user_supplied_url_truth', 'accepted_CAS_import_truth', 'rights_clearance_claimed', 'accepted_candidate_truth', 'accepted_local_source_identity_truth', 'user_supplied_url_boundary_candidate_is_fetch_permission', 'restricted_source_manifest_candidate_grants_access_permission', 'privacy_redaction_candidate_proves_public_safety', 'production_readiness_claimed', 'local_cas_import_boundary_candidate_is_import_permission', 'pack_export_import_candidate_is_export_import_permission', 'restricted_source_manifest_grants_access_permission', 'accepted_restricted_source_truth', 'accepted_rights_safety_truth', 'user_authority_claimed', 'authenticated_source_boundary_candidate_is_account_permission', 'pack_export_import_boundary_candidate_is_export_import_permission', 'source_cache_preview_is_accepted_source', 'accepted_cas_import_truth', 'private_source_boundary_candidate_is_access_permission', 'master_index_mutation_allowed', 'accepted_private_source_truth', 'accepted_source_truth', 'cas_import_candidate_is_import_permission', 'public_index_mutated', 'legal_access_claimed', 'verified_authenticity_claimed', 'accepted_public_record', 'ownership_truth_claimed', 'mutated_master_index', 'publication_permission_claimed', 'mutated_public_index', 'source_safety_claimed', 'public_index_mutation_allowed', 'accepted_authenticated_source_truth', 'privacy_safety_claimed', 'accepted_privacy_redaction_truth', 'accepted_evidence_truth', 'declared_ownership_is_rights_clearance', 'user_supplied_url_candidate_is_fetch_permission', 'master_index_mutated', 'authenticated_source_candidate_is_account_permission', 'local_source_identity_candidate_is_truth', 'local_private_rights_safety_candidate_is_rights_or_safety_truth', 'normalized_record_is_public_truth', 'rights_safety_candidate_is_rights_or_safety_truth', 'evidence_preview_is_accepted_evidence'}
PRODUCT_FORBIDDEN_TRUE_KEYS = {'fingerprinting_used', 'private_source_access_used', 'enabled_url_fetch', 'enabled_execution', 'authenticated_access_used', 'cas_import_used', 'account_access_used', 'enabled_telemetry', 'malware_scanning_used', 'enabled_uploads', 'enabled_local_access', 'acquisition_action_used', 'filesystem_scan_used', 'credential_handling_used', 'enabled_extraction', 'enabled_pack_export_import', 'user_supplied_url_fetch_used', 'publication_used', 'enabled_acquisition_actions', 'directory_listing_used', 'mutated_master_index', 'file_hashing_used', 'mutated_public_index', 'enabled_private_access', 'enabled_restricted_access', 'enabled_cas_import', 'restricted_source_access_used', 'enabled_hosting', 'upload_used', 'api_calls_made', 'pack_export_import_used', 'enabled_account_access', 'model_provider_calls_made', 'network_calls_made', 'local_access_used', 'extraction_used', 'archive_listing_used', 'execution_used', 'enabled_source_sync', 'changed_public_search_behavior'}
SECRET_KEY_RE = re.compile(r"(^|_)(api_key|api_token|access_token|auth_token|client_secret|password|private_key|cookie|session_cookie|credential|token|receipt|license_key|entitlement)($|_)", re.IGNORECASE)
PRIVATE_PAYLOAD_KEY_RE = re.compile(r"(private_file_payload|local_file_content|account_payload|cas_blob|exported_pack|imported_pack|source_cache_write|evidence_write|public_index_write|master_index_write)", re.IGNORECASE)
UNREDACTED_LOCATOR_RE = re.compile(r"(https?://|file://|[A-Za-z]:\\|\\\\|/Users/|/home/|/Volumes/)")
SAFE_FIXTURE_ROOT = (REPO_ROOT / "examples/connectors/h13_local_private/fixtures").resolve()


def load_h13_local_private_fixture(path: str | Path) -> dict[str, Any]:
    fixture_path = validate_h13_fixture_input_path(path)
    payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    _require_fixture_boundaries(payload)
    return payload


def validate_h13_fixture_input_path(path: str | Path) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = REPO_ROOT / candidate
    resolved = candidate.resolve()
    try:
        resolved.relative_to(SAFE_FIXTURE_ROOT)
    except ValueError as exc:
        raise ValueError("fixture input must be under committed H13 fixture root") from exc
    return resolved


def normalize_h13_local_private_fixture(raw_fixture: Mapping[str, Any], source_id: str, policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    _require_fixture_boundaries(raw_fixture)
    if source_id not in H13_SOURCE_CONFIGS:
        raise ValueError(f"unknown H13 source_id: {source_id}")
    if raw_fixture.get("source_id") != source_id:
        raise ValueError("fixture source_id does not match requested source")
    config = H13_SOURCE_CONFIGS[source_id]
    payload = _mapping(raw_fixture.get("fixture_payload"), "fixture_payload")
    fixture_kind = _text(raw_fixture.get("fixture_kind")) or "unknown"
    native_id = _text(payload.get("source_native_id")) or _text(raw_fixture.get("fixture_id")) or fixture_kind
    record: dict[str, Any] = {
        "schema_version": "h13_local_private_normalized_record.v0",
        "normalized_record_id": f"h13.normalized.{source_id}.{_slug(native_id)}.v0",
        "source_id": source_id,
        "connector_family": config["connector_family"],
        "source_record_kind": _text(payload.get("source_record_kind")) or fixture_kind,
        "source_metadata": {
            "fixture_id": raw_fixture.get("fixture_id", "unknown"),
            "fixture_kind": fixture_kind,
            "fixture_status": raw_fixture.get("fixture_status", "unknown"),
            "source_label": config["source_label"],
            "trust_lane": config["trust_lane"],
            "metadata_summary": payload.get("metadata_summary", "synthetic boundary fixture metadata only"),
        },
        "source_limitations": _dedupe(_list(raw_fixture.get("limitations")) + _missing_optional_limitations(payload)),
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": [
            "Offline H13 fixture normalization only.",
            "Candidate and preview outputs require review and do not grant local access, private-source access, URL fetch, account access, restricted-source access, CAS import, pack export/import, source cache write, evidence write, publication, or public truth.",
        ],
    }
    for field in NORMALIZED_SCALAR_FIELDS:
        record[field] = _value(payload.get(field))
    record["privacy_redaction_metadata"] = _mapping(payload.get("privacy_redaction_metadata"), "privacy_redaction_metadata") if isinstance(payload.get("privacy_redaction_metadata"), Mapping) else {}
    record["local_private_rights_safety_metadata"] = _mapping(payload.get("local_private_rights_safety_metadata"), "local_private_rights_safety_metadata") if isinstance(payload.get("local_private_rights_safety_metadata"), Mapping) else {}
    record["local_source_identity_candidate"] = build_h13_local_source_identity_candidate(record, policy)
    record["private_source_boundary_candidate"] = build_h13_private_source_boundary_candidate(record, policy)
    record["user_supplied_url_boundary_candidate"] = build_h13_user_supplied_url_boundary_candidate(record, policy)
    record["authenticated_source_boundary_candidate"] = build_h13_authenticated_source_boundary_candidate(record, policy)
    record["restricted_source_manifest_candidate"] = build_h13_restricted_source_manifest_candidate(record, policy)
    record["local_cas_import_boundary_candidate"] = build_h13_local_cas_import_boundary_candidate(record, policy)
    record["pack_export_import_boundary_candidate"] = build_h13_pack_export_import_boundary_candidate(record, policy)
    record["privacy_redaction_candidate"] = build_h13_privacy_redaction_candidate(record, policy)
    record["local_private_rights_safety_candidate"] = build_h13_local_private_rights_safety_candidate(record, policy)
    record["source_cache_candidate_preview"] = build_h13_source_cache_candidate_preview(record, policy)
    record["evidence_candidate_preview"] = build_h13_evidence_candidate_preview(record, policy)
    _raise_on_boundary_errors(record)
    return record


def redact_h13_locator(value: Any, policy: Mapping[str, Any] | None = None) -> str:
    text = _text(value)
    if not text:
        return "[redacted-h13-locator]"
    return f"[redacted-h13-locator:{_slug(text)}]"


def hash_h13_locator(value: Any, policy: Mapping[str, Any] | None = None) -> str:
    text = _text(value) or "unknown"
    return "sha256:" + hashlib.sha256(("h13-synthetic-locator:" + text).encode("utf-8")).hexdigest()


def validate_h13_public_safe_path(value: Any, policy: Mapping[str, Any] | None = None) -> bool:
    text = _text(value)
    return not bool(UNREDACTED_LOCATOR_RE.search(text))


def validate_h13_no_secret_fields(record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> bool:
    return not detect_h13_secret_or_private_data_violations(record, policy)


def build_h13_local_source_identity_candidate(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return _candidate(normalized_record, "local_source_identity", "h13_local_source_identity_candidate.v0", CANDIDATE_FIELD_MAP["local_source_identity"], "Local source identity candidate only; declared ownership, labels, counts, paths, hashes, and identifiers are not accepted source truth.")


def build_h13_private_source_boundary_candidate(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    candidate = _candidate(normalized_record, "private_source_boundary", "h13_private_source_boundary_candidate.v0", CANDIDATE_FIELD_MAP["private_source_boundary"], "Private source boundary candidate only; source presence is not access, inspection, export, sharing, or indexing permission.")
    candidate["access_permission_current"] = "blocked_current"
    _raise_on_boundary_errors(candidate)
    return candidate


def build_h13_user_supplied_url_boundary_candidate(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    candidate = _candidate(normalized_record, "user_supplied_url_boundary", "h13_user_supplied_url_boundary_candidate.v0", CANDIDATE_FIELD_MAP["user_supplied_url_boundary"], "User-supplied URL boundary candidate only; arbitrary locator input is not fetch, scrape, crawl, mirror, download, index, or publication permission.")
    candidate["fetch_permission_current"] = "blocked_current"
    _raise_on_boundary_errors(candidate)
    return candidate


def build_h13_authenticated_source_boundary_candidate(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    candidate = _candidate(normalized_record, "authenticated_source_boundary", "h13_authenticated_source_boundary_candidate.v0", CANDIDATE_FIELD_MAP["authenticated_source_boundary"], "Authenticated source boundary candidate only; no accounts, cookies, tokens, sessions, receipts, entitlements, subscriptions, or user libraries are accessed.")
    candidate["account_permission_current"] = "blocked_current"
    _raise_on_boundary_errors(candidate)
    return candidate


def build_h13_restricted_source_manifest_candidate(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    candidate = _candidate(normalized_record, "restricted_source_manifest", "h13_restricted_source_manifest_candidate.v0", CANDIDATE_FIELD_MAP["restricted_source_manifest"], "Restricted-source manifest candidate only; manifest-only status does not grant direct access, scraping, crawling, download, bypass, or acquisition permission.")
    candidate["restricted_source_access_permission_current"] = "blocked_current_manifest_only"
    _raise_on_boundary_errors(candidate)
    return candidate


def build_h13_local_cas_import_boundary_candidate(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    candidate = _candidate(normalized_record, "local_cas_import_boundary", "h13_local_cas_import_boundary_candidate.v0", CANDIDATE_FIELD_MAP["local_cas_import_boundary"], "Local CAS import boundary candidate only; no files are hashed, copied, deduplicated, imported, stored, exported, or published.")
    candidate["import_permission_current"] = "blocked_current"
    _raise_on_boundary_errors(candidate)
    return candidate


def build_h13_pack_export_import_boundary_candidate(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    candidate = _candidate(normalized_record, "pack_export_import_boundary", "h13_pack_export_import_boundary_candidate.v0", CANDIDATE_FIELD_MAP["pack_export_import_boundary"], "Pack export/import boundary candidate only; pack movement requires future review, redaction, authority, and policy checks.")
    candidate["export_import_permission_current"] = "blocked_current"
    _raise_on_boundary_errors(candidate)
    return candidate


def build_h13_privacy_redaction_candidate(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return _candidate(normalized_record, "privacy_redaction", "h13_privacy_redaction_candidate.v0", CANDIDATE_FIELD_MAP["privacy_redaction"], "Privacy/redaction candidate only; redaction and hashing do not prove public safety or publication permission.")


def build_h13_local_private_rights_safety_candidate(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    candidate = _candidate(normalized_record, "local_private_rights_safety", "h13_local_private_rights_safety_candidate.v0", CANDIDATE_FIELD_MAP["local_private_rights_safety"], "Local/private rights-safety candidate only; declared ownership, rights labels, license metadata, and safety notes are not rights clearance, legal access, privacy safety, malware safety, or source safety.")
    candidate["publication_permission_current"] = False
    _raise_on_boundary_errors(candidate)
    return candidate


def build_h13_source_cache_candidate_preview(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    preview = {
        "schema_version": "h13_local_private_source_cache_candidate_preview.v0",
        "preview_id": f"h13.source_cache.preview.{normalized_record.get('source_id')}.{_slug(normalized_record.get('source_native_id'))}.v0",
        "source_id": normalized_record.get("source_id"),
        "source_record_ref": normalized_record.get("normalized_record_id"),
        "preview_only": True,
        "accepted_source": False,
        "mutates_source_cache": False,
        "supporting_fields": {
            "source_record_kind": normalized_record.get("source_record_kind"),
            "source_native_id": normalized_record.get("source_native_id"),
            "source_visibility": normalized_record.get("source_visibility"),
        },
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "limitations": ["Source-cache preview only; no source cache write or source truth acceptance occurs."],
    }
    _raise_on_boundary_errors(preview)
    return preview


def build_h13_evidence_candidate_preview(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    preview = {
        "schema_version": "h13_local_private_evidence_candidate_preview.v0",
        "preview_id": f"h13.evidence.preview.{normalized_record.get('source_id')}.{_slug(normalized_record.get('source_native_id'))}.v0",
        "source_id": normalized_record.get("source_id"),
        "source_record_ref": normalized_record.get("normalized_record_id"),
        "preview_only": True,
        "accepted_evidence": False,
        "mutates_evidence_ledger": False,
        "claim_summary": "H13 local/private fixture boundary metadata candidate only.",
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "limitations": ["Evidence preview only; no evidence acceptance occurs."],
    }
    _raise_on_boundary_errors(preview)
    return preview


def build_h13_fixture_replay_result(fixture: Mapping[str, Any], normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    result = {
        "schema_version": "h13_local_private_fixture_replay_result.v0",
        "fixture_replay_result_id": f"h13.replay.{fixture.get('source_id')}.{fixture.get('fixture_kind')}.v0",
        "source_id": fixture.get("source_id"),
        "connector_family": normalized_record.get("connector_family"),
        "fixture_ref": fixture.get("fixture_id"),
        "normalized_record_ref": normalized_record.get("normalized_record_id"),
        "result_status": "normalized_fixture",
        "network_used": False,
        "local_private_access_used": False,
        "candidate_counts": {
            "local_source_identity_candidate": 1,
            "private_source_boundary_candidate": 1,
            "user_supplied_url_boundary_candidate": 1,
            "authenticated_source_boundary_candidate": 1,
            "restricted_source_manifest_candidate": 1,
            "local_cas_import_boundary_candidate": 1,
            "pack_export_import_boundary_candidate": 1,
            "privacy_redaction_candidate": 1,
            "local_private_rights_safety_candidate": 1,
        },
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "limitations": ["Fixture replay output is not source, evidence, candidate, public, or master truth."],
    }
    _raise_on_boundary_errors(result)
    return result


def summarize_h13_normalized_record(record: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "source_id": record.get("source_id"),
        "source_record_kind": record.get("source_record_kind"),
        "candidate_count": 9,
        "truth_boundary_violations": detect_h13_truth_boundary_violations(record),
        "product_boundary_violations": detect_h13_product_boundary_violations(record),
        "secret_or_private_data_violations": detect_h13_secret_or_private_data_violations(record),
    }


def detect_h13_truth_boundary_violations(record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    violations: list[str] = []
    _collect_true_keys(record, TRUTH_FORBIDDEN_TRUE_KEYS, "truth", violations)
    return violations


def detect_h13_product_boundary_violations(record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    violations: list[str] = []
    _collect_true_keys(record, PRODUCT_FORBIDDEN_TRUE_KEYS, "product", violations)
    return violations


def detect_h13_secret_or_private_data_violations(record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    violations: list[str] = []
    _collect_secret_or_private_data(record, "record", violations)
    return violations


def _candidate(normalized_record: Mapping[str, Any], kind: str, schema_version: str, fields: list[str], limitation: str) -> dict[str, Any]:
    supporting = {field: normalized_record.get(field) for field in fields if normalized_record.get(field) not in (None, "", [], {}, "unknown")}
    missing = [field for field in fields if field not in supporting]
    candidate = {
        "schema_version": schema_version,
        "candidate_id": f"h13.{kind}.{normalized_record.get('source_id')}.{_slug(normalized_record.get('source_native_id'))}.v0",
        "source_id": normalized_record.get("source_id"),
        "source_record_ref": normalized_record.get("normalized_record_id"),
        "candidate_kind": kind,
        "supporting_fields": supporting,
        "missing_fields": missing,
        "confidence_or_uncertainty": "low_confidence_fixture_candidate",
        "limitations": [limitation, "Review required before downstream use."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
    }
    _raise_on_boundary_errors(candidate)
    return candidate


def _require_fixture_boundaries(raw_fixture: Mapping[str, Any]) -> None:
    if not isinstance(raw_fixture, Mapping):
        raise ValueError("fixture must be a mapping")
    errors: list[str] = []
    _collect_true_keys(raw_fixture, FIXTURE_FORBIDDEN_TRUE_KEYS, "fixture", errors)
    _collect_true_keys(raw_fixture, TRUTH_FORBIDDEN_TRUE_KEYS, "truth", errors)
    _collect_true_keys(raw_fixture, PRODUCT_FORBIDDEN_TRUE_KEYS, "product", errors)
    _collect_secret_or_private_data(raw_fixture, "fixture", errors)
    if errors:
        raise ValueError("; ".join(errors))


def _raise_on_boundary_errors(record: Mapping[str, Any]) -> None:
    errors = detect_h13_truth_boundary_violations(record) + detect_h13_product_boundary_violations(record) + detect_h13_secret_or_private_data_violations(record)
    if errors:
        raise ValueError("; ".join(errors))


def _collect_true_keys(value: Any, forbidden: set[str], prefix: str, errors: list[str]) -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            if str(key) in forbidden and item is True:
                errors.append(f"{prefix} boundary true claim: {key}")
            _collect_true_keys(item, forbidden, prefix, errors)
    elif isinstance(value, list):
        for item in value:
            _collect_true_keys(item, forbidden, prefix, errors)


def _collect_secret_or_private_data(value: Any, label: str, errors: list[str]) -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            key_text = str(key)
            if SECRET_KEY_RE.search(key_text) and item not in (False, None, "", "unknown", "blocked_current_no_credentials", "blocked_current_no_sessions", "not_evaluated_no_account_access"):
                errors.append(f"{label} forbidden secret/account field: {key_text}")
            if PRIVATE_PAYLOAD_KEY_RE.search(key_text) and item not in (False, None, "", [], {}, "no_blob_present"):
                errors.append(f"{label} forbidden private payload field: {key_text}")
            _collect_secret_or_private_data(item, label, errors)
    elif isinstance(value, list):
        for item in value:
            _collect_secret_or_private_data(item, label, errors)
    elif isinstance(value, str):
        if UNREDACTED_LOCATOR_RE.search(value):
            errors.append(f"{label} contains unrestricted local path or URL-like locator")


def _truth_boundary() -> dict[str, bool]:
    return {key: False for key in TRUTH_FORBIDDEN_TRUE_KEYS}


def _product_boundary() -> dict[str, bool]:
    return {key: False for key in PRODUCT_FORBIDDEN_TRUE_KEYS}


def _mapping(value: Any, label: str) -> Mapping[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise ValueError(f"{label} must be a mapping")
    return value


def _value(value: Any) -> Any:
    if value is None:
        return "unknown"
    if isinstance(value, str):
        return value.strip() or "unknown"
    return value


def _text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()


def _list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    return [str(value)]


def _missing_optional_limitations(payload: Mapping[str, Any]) -> list[str]:
    missing = [field for field in NORMALIZED_SCALAR_FIELDS if field not in payload]
    if not missing:
        return []
    return ["Missing optional H13 fixture fields are unknown, not fabricated: " + ", ".join(missing[:10])]


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        text = _text(value)
        if text and text not in seen:
            result.append(text)
            seen.add(text)
    return result


def _slug(value: Any) -> str:
    text = _text(value) or "unknown"
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]
