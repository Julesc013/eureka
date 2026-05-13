"""Fixture-only H5 vendor/update/driver normalization helpers."""

from __future__ import annotations

import hashlib
from collections.abc import Mapping
from typing import Any


H5_SOURCE_CONFIGS: dict[str, dict[str, Any]] = {'microsoft_download_center': {'label': 'Microsoft Download Center metadata', 'connector_family': 'vendor_update_catalog', 'vendor_name': 'Microsoft', 'catalog_kind': 'download_center', 'has_driver': False, 'has_firmware': False, 'has_runtime': True}, 'microsoft_update_catalog': {'label': 'Microsoft Update Catalog metadata', 'connector_family': 'vendor_update_catalog', 'vendor_name': 'Microsoft', 'catalog_kind': 'update_catalog', 'has_driver': True, 'has_firmware': True, 'has_runtime': False}, 'microsoft_runtime_redistributables': {'label': 'Microsoft runtime redistributable metadata', 'connector_family': 'runtime_redistributable_catalog', 'vendor_name': 'Microsoft', 'catalog_kind': 'runtime_catalog', 'has_driver': False, 'has_firmware': False, 'has_runtime': True}, 'apple_software_downloads': {'label': 'Apple software downloads metadata', 'connector_family': 'vendor_update_catalog', 'vendor_name': 'Apple', 'catalog_kind': 'software_downloads', 'has_driver': False, 'has_firmware': False, 'has_runtime': True}, 'apple_software_update_catalog': {'label': 'Apple software update catalog metadata', 'connector_family': 'vendor_update_catalog', 'vendor_name': 'Apple', 'catalog_kind': 'software_update_catalog', 'has_driver': False, 'has_firmware': True, 'has_runtime': False}, 'nvidia_driver_downloads': {'label': 'NVIDIA driver/download metadata', 'connector_family': 'driver_catalog', 'vendor_name': 'NVIDIA', 'catalog_kind': 'driver_downloads', 'has_driver': True, 'has_firmware': False, 'has_runtime': False}, 'amd_driver_downloads': {'label': 'AMD driver/download metadata', 'connector_family': 'driver_catalog', 'vendor_name': 'AMD', 'catalog_kind': 'driver_downloads', 'has_driver': True, 'has_firmware': False, 'has_runtime': False}, 'intel_driver_support': {'label': 'Intel driver/support metadata', 'connector_family': 'driver_catalog', 'vendor_name': 'Intel', 'catalog_kind': 'driver_support', 'has_driver': True, 'has_firmware': True, 'has_runtime': False}, 'dell_support_downloads': {'label': 'Dell support/download metadata', 'connector_family': 'vendor_support_catalog', 'vendor_name': 'Dell', 'catalog_kind': 'support_downloads', 'has_driver': True, 'has_firmware': True, 'has_runtime': False}, 'hp_support_downloads': {'label': 'HP support/download metadata', 'connector_family': 'vendor_support_catalog', 'vendor_name': 'HP', 'catalog_kind': 'support_downloads', 'has_driver': True, 'has_firmware': True, 'has_runtime': False}, 'lenovo_support_downloads': {'label': 'Lenovo support/download metadata', 'connector_family': 'vendor_support_catalog', 'vendor_name': 'Lenovo', 'catalog_kind': 'support_downloads', 'has_driver': True, 'has_firmware': True, 'has_runtime': False}, 'asus_support_downloads': {'label': 'ASUS support/download metadata', 'connector_family': 'vendor_support_catalog', 'vendor_name': 'ASUS', 'catalog_kind': 'support_downloads', 'has_driver': True, 'has_firmware': True, 'has_runtime': False}, 'acer_support_downloads': {'label': 'Acer support/download metadata', 'connector_family': 'vendor_support_catalog', 'vendor_name': 'Acer', 'catalog_kind': 'support_downloads', 'has_driver': True, 'has_firmware': True, 'has_runtime': False}, 'generic_vendor_driver_firmware': {'label': 'Generic vendor driver/firmware portal metadata', 'connector_family': 'vendor_support_catalog', 'vendor_name': 'Generic Vendor', 'catalog_kind': 'vendor_driver_firmware', 'has_driver': True, 'has_firmware': True, 'has_runtime': False}, 'generic_runtime_redistributable': {'label': 'Generic runtime redistributable catalog metadata', 'connector_family': 'runtime_redistributable_catalog', 'vendor_name': 'Generic Runtime Vendor', 'catalog_kind': 'runtime_catalog', 'has_driver': False, 'has_firmware': False, 'has_runtime': True}}
H5_SOURCE_IDS = tuple(H5_SOURCE_CONFIGS)
H5_FIXTURE_KINDS = ('minimal', 'typical', 'driver', 'firmware', 'runtime', 'compatibility', 'policy_blocked')

FORBIDDEN_TRUTH_TRUE_KEYS = {'runtime_candidate_is_installability_truth', 'firmware_identity_candidate_is_truth', 'accepted_evidence_truth', 'vendor_source_proves_official_status', 'verified_installability_claimed', 'accepted_safety_truth', 'accepted_source_truth', 'malware_safety_claimed', 'vendor_identity_candidate_is_truth', 'dependency_metadata_is_dependency_correctness', 'firmware_update_candidate_is_approved_to_flash', 'accepted_runtime_identity_truth', 'sbom_metadata_is_verified_provenance', 'accepted_driver_identity_truth', 'verified_authenticity_claimed', 'license_metadata_is_rights_clearance', 'accepted_public_record', 'firmware_signature_metadata_is_verified_authenticity', 'installer_metadata_is_execution_permission', 'vendor_identity_candidate_is_accepted_vendor_truth', 'master_index_mutated', 'verified_compatibility_claimed', 'accepted_authenticity_truth', 'signature_metadata_proves_authenticity', 'compatibility_candidate_is_truth', 'firmware_hash_proves_malware_safety', 'runtime_identity_candidate_is_truth', 'vendor_presence_proves_endorsement', 'security_update_metadata_is_safety_proof', 'rights_clearance_claimed', 'accepted_compatibility_truth', 'payload_hash_proves_malware_safety', 'accepted_candidate_truth', 'public_index_mutated', 'driver_identity_candidate_is_truth', 'source_cache_preview_is_accepted_source', 'firmware_metadata_proves_device_compatibility', 'evidence_preview_is_accepted_evidence', 'production_readiness_claimed', 'compatibility_candidate_is_verified_compatibility', 'os_version_match_proves_runtime_correctness', 'device_id_match_proves_safe_installability', 'flashing_tool_metadata_is_execution_permission', 'accepted_firmware_identity_truth', 'architecture_match_proves_device_compatibility', 'accepted_vendor_truth', 'normalized_record_is_public_truth'}
FORBIDDEN_PRODUCT_TRUE_KEYS = {'vendor_catalog_fetch_used', 'enabled_accounts', 'vendor_tool_invoked', 'package_manager_invoked', 'enabled_telemetry', 'enabled_execution', 'network_calls_made', 'installer_or_artifact_executed', 'enabled_installers', 'mutated_master_index', 'enabled_firmware_flashing', 'api_calls_made', 'changed_public_search_behavior', 'enabled_hosting', 'mutated_public_index', 'enabled_downloads', 'download_used', 'enabled_source_sync', 'enabled_uploads', 'firmware_flash_invoked', 'enabled_catalog_fetch', 'enabled_live_probes', 'enabled_source_connectors'}
FIXTURE_FORBIDDEN_TRUE_KEYS = {
    "live_call_used",
    "network_used",
    "external_api_used",
    "driver_payload_included",
    "firmware_payload_included",
    "runtime_payload_included",
    "installer_payload_included",
    "vendor_tool_output_included",
    "package_manager_invoked",
    "firmware_flash_invoked",
    "installer_or_artifact_executed",
}


def normalize_h5_vendor_update_fixture(raw_fixture: Mapping[str, Any], source_id: str, policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    if source_id not in H5_SOURCE_CONFIGS:
        raise ValueError(f"unknown H5 source_id: {source_id}")
    if raw_fixture.get("source_id") != source_id:
        raise ValueError(f"fixture source_id does not match requested source_id: {source_id}")
    _require_fixture_boundaries(raw_fixture)
    payload = _mapping(raw_fixture.get("fixture_payload"), "fixture_payload")
    config = H5_SOURCE_CONFIGS[source_id]
    native_id = _text(payload.get("vendor_native_id")) or f"fixture-{source_id}"
    limitations = list(raw_fixture.get("limitations") or [])
    limitations.extend(_missing_optional_limitations(payload))
    if raw_fixture.get("fixture_status") == "policy_blocked":
        limitations.append("fixture is policy-blocked and remains candidate-only")
    record: dict[str, Any] = {
        "schema_version": "h5_vendor_update_normalized_record.v0",
        "normalized_record_id": f"h5.normalized.{source_id}.{_slug(native_id)}.v0",
        "source_id": source_id,
        "connector_family": str(raw_fixture.get("connector_family") or config["connector_family"]),
        "vendor_name": _text(payload.get("vendor_name")) or str(config["vendor_name"]),
        "product_name": _text(payload.get("product_name")) or "unknown",
        "product_family": _text(payload.get("product_family")) or "unknown",
        "product_line": _text(payload.get("product_line")) or "unknown",
        "support_page_ref": _text(payload.get("support_page_ref")) or "unknown",
        "catalog_record_id": _text(payload.get("catalog_record_id")) or "unknown",
        "update_record_id": _text(payload.get("update_record_id")) or "unknown",
        "download_record_id": _text(payload.get("download_record_id")) or "unknown",
        "vendor_native_id": native_id,
        "vendor_release_id": _text(payload.get("vendor_release_id")) or "unknown",
        "vendor_version": _text(payload.get("vendor_version")) or "unknown",
        "release_date_candidate": _text(payload.get("release_date_candidate")) or "unknown",
        "package_or_payload_name": _text(payload.get("package_or_payload_name")) or "unknown",
        "payload_kind": _text(payload.get("payload_kind")) or "metadata_only",
        "device_vendor_id": _text(payload.get("device_vendor_id")) or "unknown",
        "device_product_id": _text(payload.get("device_product_id")) or "unknown",
        "hardware_model": _text(payload.get("hardware_model")) or "unknown",
        "hardware_revision": _text(payload.get("hardware_revision")) or "unknown",
        "operating_system_family": _text(payload.get("operating_system_family")) or "unknown",
        "operating_system_version": _text(payload.get("operating_system_version")) or "unknown",
        "architecture": _text(payload.get("architecture")) or "unknown",
        "driver_name": _text(payload.get("driver_name")) or "unknown",
        "driver_version": _text(payload.get("driver_version")) or "unknown",
        "driver_class": _text(payload.get("driver_class")) or "unknown",
        "chipset_or_component": _text(payload.get("chipset_or_component")) or "unknown",
        "firmware_name": _text(payload.get("firmware_name")) or "unknown",
        "firmware_version": _text(payload.get("firmware_version")) or "unknown",
        "bios_or_uefi_version": _text(payload.get("bios_or_uefi_version")) or "unknown",
        "device_model": _text(payload.get("device_model")) or "unknown",
        "board_model": _text(payload.get("board_model")) or "unknown",
        "update_package_id": _text(payload.get("update_package_id")) or "unknown",
        "update_type": _text(payload.get("update_type")) or "unknown",
        "runtime_family": _text(payload.get("runtime_family")) or "unknown",
        "runtime_name": _text(payload.get("runtime_name")) or "unknown",
        "runtime_version": _text(payload.get("runtime_version")) or "unknown",
        "installer_name": _text(payload.get("installer_name")) or "unknown",
        "redistributable_package_id": _text(payload.get("redistributable_package_id")) or "unknown",
        "prerequisite_summary": _text(payload.get("prerequisite_summary")) or "unknown",
        "compatibility_summary": _text(payload.get("compatibility_summary")) or "unknown",
        "risk_warning_summary": _text(payload.get("risk_warning_summary")) or "unknown",
        "release_note_or_changelog_refs": _strings(payload.get("release_note_or_changelog_refs")),
        "advisory_refs": _strings(payload.get("advisory_refs")),
        "hash_metadata": _mapping(payload.get("hash_metadata"), "hash_metadata", default={"candidate_only": True, "hash_metadata_proves_malware_safety": False}),
        "signature_metadata": _mapping(payload.get("signature_metadata"), "signature_metadata", default={"candidate_only": True, "signature_metadata_proves_authenticity": False}),
        "payload_locator_candidate": _text(payload.get("payload_locator_candidate")) or "unknown",
        "source_metadata": _mapping(payload.get("source_metadata"), "source_metadata", default={}),
        "source_limitations": _dedupe(limitations),
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["Fixture-only H5 normalized record; review is required before any downstream use."],
    }
    record["vendor_identity_candidate"] = build_h5_vendor_identity_candidate(record, policy)
    driver_candidates = build_h5_driver_device_compatibility_candidates(record, policy)
    firmware_candidates = build_h5_firmware_update_candidates(record, policy)
    runtime_candidates = build_h5_runtime_redistributable_candidates(record, policy)
    payload_candidates = build_h5_payload_metadata_candidates(record, policy)
    record["driver_device_compatibility_candidate"] = driver_candidates[0] if driver_candidates else {}
    record["firmware_update_candidate"] = firmware_candidates[0] if firmware_candidates else {}
    record["runtime_redistributable_candidate"] = runtime_candidates[0] if runtime_candidates else {}
    record["payload_metadata_candidate"] = payload_candidates[0] if payload_candidates else {}
    record["driver_device_compatibility_candidate_preview"] = driver_candidates
    record["firmware_update_candidate_preview"] = firmware_candidates
    record["runtime_redistributable_candidate_preview"] = runtime_candidates
    record["payload_metadata_candidate_preview"] = payload_candidates
    record["source_cache_candidate_preview"] = build_h5_source_cache_candidate_preview(record, policy)
    record["evidence_candidate_preview"] = build_h5_evidence_candidate_preview(record, policy)
    _raise_on_boundary_errors(record)
    return record


def build_h5_vendor_identity_candidate(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source_id = str(normalized_record.get("source_id"))
    native_id = str(normalized_record.get("vendor_native_id") or "unknown")
    fields = ("vendor_name", "product_name", "product_family", "catalog_record_id", "update_record_id", "download_record_id", "vendor_native_id", "vendor_version", "support_page_ref")
    candidate = {
        "schema_version": "h5_vendor_identity_candidate.v0",
        "vendor_identity_candidate_id": f"h5.vendor_identity.{source_id}.{_slug(native_id)}.v0",
        "source_id": source_id,
        "vendor_name": normalized_record.get("vendor_name", "unknown"),
        "vendor_domain_or_source_ref": normalized_record.get("support_page_ref", "unknown"),
        "product_name": normalized_record.get("product_name", "unknown"),
        "product_family": normalized_record.get("product_family", "unknown"),
        "catalog_record_id": normalized_record.get("catalog_record_id", "unknown"),
        "update_record_id": normalized_record.get("update_record_id", "unknown"),
        "download_record_id": normalized_record.get("download_record_id", "unknown"),
        "vendor_native_id": native_id,
        "vendor_version": normalized_record.get("vendor_version", "unknown"),
        "official_status_candidate": "candidate_only_requires_review",
        "support_page_ref": normalized_record.get("support_page_ref", "unknown"),
        "confidence_or_uncertainty": "candidate_from_fixture_no_vendor_truth",
        "supporting_fields": [field for field in fields if normalized_record.get(field) not in (None, "", "unknown", [], {})],
        "missing_fields": [field for field in fields if normalized_record.get(field) in (None, "", "unknown", [], {})],
        "limitations": ["Vendor identity candidate is not accepted vendor truth and does not prove official status."],
        "truth_boundary": {
            "vendor_identity_candidate_is_accepted_vendor_truth": False,
            "vendor_identity_candidate_is_truth": False,
            "vendor_source_proves_official_status": False,
            "vendor_presence_proves_endorsement": False,
            "license_metadata_is_rights_clearance": False,
        },
        "product_boundary": _product_boundary(),
    }
    _raise_on_boundary_errors(candidate)
    return candidate


def build_h5_driver_device_compatibility_candidates(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    if not _has_any(normalized_record, ("driver_name", "driver_version", "device_vendor_id", "device_product_id", "hardware_model", "operating_system_family", "architecture")):
        return []
    source_id = str(normalized_record.get("source_id"))
    ref = normalized_record.get("vendor_identity_candidate", {}).get("vendor_identity_candidate_id")
    native_id = str(normalized_record.get("vendor_native_id") or "unknown")
    candidate = {
        "schema_version": "h5_driver_device_compatibility_candidate.v0",
        "compatibility_candidate_id": f"h5.compatibility.{source_id}.{_slug(native_id)}.v0",
        "source_id": source_id,
        "vendor_identity_candidate_ref": ref,
        "driver_name": normalized_record.get("driver_name", "unknown"),
        "driver_version": normalized_record.get("driver_version", "unknown"),
        "device_vendor_id": normalized_record.get("device_vendor_id", "unknown"),
        "device_product_id": normalized_record.get("device_product_id", "unknown"),
        "hardware_model": normalized_record.get("hardware_model", "unknown"),
        "hardware_revision": normalized_record.get("hardware_revision", "unknown"),
        "operating_system_family": normalized_record.get("operating_system_family", "unknown"),
        "operating_system_version": normalized_record.get("operating_system_version", "unknown"),
        "architecture": normalized_record.get("architecture", "unknown"),
        "driver_class": normalized_record.get("driver_class", "unknown"),
        "chipset_or_component": normalized_record.get("chipset_or_component", "unknown"),
        "minimum_system_requirement_candidate": normalized_record.get("prerequisite_summary", "unknown"),
        "compatibility_status_candidate": normalized_record.get("compatibility_summary", "unknown"),
        "unsupported_candidate": "unknown",
        "known_issue_candidate": "unknown",
        "install_requirement_candidate": "unknown",
        "reboot_requirement_candidate": "unknown",
        "limitations": ["Compatibility candidate is not verified compatibility or safe installability."],
        "truth_boundary": {
            "compatibility_candidate_is_verified_compatibility": False,
            "compatibility_candidate_is_truth": False,
            "device_id_match_proves_safe_installability": False,
            "os_version_match_proves_runtime_correctness": False,
            "architecture_match_proves_device_compatibility": False,
            "malware_safety_claimed": False,
        },
        "product_boundary": _product_boundary(),
    }
    _raise_on_boundary_errors(candidate)
    return [candidate]


def build_h5_firmware_update_candidates(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    if not _has_any(normalized_record, ("firmware_name", "firmware_version", "bios_or_uefi_version", "update_package_id", "risk_warning_summary")):
        return []
    source_id = str(normalized_record.get("source_id"))
    ref = normalized_record.get("vendor_identity_candidate", {}).get("vendor_identity_candidate_id")
    native_id = str(normalized_record.get("vendor_native_id") or "unknown")
    candidate = {
        "schema_version": "h5_firmware_update_candidate.v0",
        "firmware_update_candidate_id": f"h5.firmware_update.{source_id}.{_slug(native_id)}.v0",
        "source_id": source_id,
        "vendor_identity_candidate_ref": ref,
        "firmware_name": normalized_record.get("firmware_name", "unknown"),
        "firmware_version": normalized_record.get("firmware_version", "unknown"),
        "bios_or_uefi_version": normalized_record.get("bios_or_uefi_version", "unknown"),
        "device_model": normalized_record.get("device_model", "unknown"),
        "board_model": normalized_record.get("board_model", "unknown"),
        "hardware_revision": normalized_record.get("hardware_revision", "unknown"),
        "update_package_id": normalized_record.get("update_package_id", "unknown"),
        "update_type": normalized_record.get("update_type", "unknown"),
        "release_date_candidate": normalized_record.get("release_date_candidate", "unknown"),
        "prerequisite_candidate": normalized_record.get("prerequisite_summary", "unknown"),
        "downgrade_or_rollback_candidate": "unknown",
        "risk_warning_candidate": normalized_record.get("risk_warning_summary", "unknown"),
        "checksum_metadata_candidate": normalized_record.get("hash_metadata", {}),
        "signature_metadata_candidate": normalized_record.get("signature_metadata", {}),
        "flashing_tool_candidate": "blocked_action_candidate_only",
        "blocked_action_candidate": "firmware_flash_blocked_current",
        "limitations": ["Firmware update candidate is not approval to download, install, execute, or flash."],
        "truth_boundary": {
            "firmware_update_candidate_is_approved_to_flash": False,
            "firmware_identity_candidate_is_truth": False,
            "firmware_metadata_proves_device_compatibility": False,
            "firmware_hash_proves_malware_safety": False,
            "firmware_signature_metadata_is_verified_authenticity": False,
            "flashing_tool_metadata_is_execution_permission": False,
        },
        "product_boundary": _product_boundary(),
    }
    _raise_on_boundary_errors(candidate)
    return [candidate]


def build_h5_runtime_redistributable_candidates(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    if not _has_any(normalized_record, ("runtime_family", "runtime_name", "runtime_version", "redistributable_package_id", "installer_name")):
        return []
    source_id = str(normalized_record.get("source_id"))
    ref = normalized_record.get("vendor_identity_candidate", {}).get("vendor_identity_candidate_id")
    native_id = str(normalized_record.get("vendor_native_id") or "unknown")
    candidate = {
        "schema_version": "h5_runtime_redistributable_candidate.v0",
        "runtime_candidate_id": f"h5.runtime.{source_id}.{_slug(native_id)}.v0",
        "source_id": source_id,
        "vendor_identity_candidate_ref": ref,
        "runtime_family": normalized_record.get("runtime_family", "unknown"),
        "runtime_name": normalized_record.get("runtime_name", "unknown"),
        "runtime_version": normalized_record.get("runtime_version", "unknown"),
        "installer_name": normalized_record.get("installer_name", "unknown"),
        "architecture": normalized_record.get("architecture", "unknown"),
        "operating_system_family": normalized_record.get("operating_system_family", "unknown"),
        "operating_system_version": normalized_record.get("operating_system_version", "unknown"),
        "redistributable_package_id": normalized_record.get("redistributable_package_id", "unknown"),
        "dependency_or_requirement_candidate": normalized_record.get("prerequisite_summary", "unknown"),
        "security_update_candidate": "unknown",
        "end_of_life_candidate": "unknown",
        "hash_metadata_candidate": normalized_record.get("hash_metadata", {}),
        "signature_metadata_candidate": normalized_record.get("signature_metadata", {}),
        "download_locator_candidate": normalized_record.get("payload_locator_candidate", "unknown"),
        "limitations": ["Runtime candidate is not installability truth or execution permission."],
        "truth_boundary": {
            "runtime_candidate_is_installability_truth": False,
            "runtime_identity_candidate_is_truth": False,
            "installer_metadata_is_execution_permission": False,
            "dependency_metadata_is_dependency_correctness": False,
            "security_update_metadata_is_safety_proof": False,
        },
        "product_boundary": _product_boundary(),
    }
    _raise_on_boundary_errors(candidate)
    return [candidate]


def build_h5_payload_metadata_candidates(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    if not _has_any(normalized_record, ("package_or_payload_name", "payload_locator_candidate", "payload_kind")):
        return []
    source_id = str(normalized_record.get("source_id"))
    native_id = str(normalized_record.get("vendor_native_id") or "unknown")
    driver_ref = normalized_record.get("driver_device_compatibility_candidate", {}).get("compatibility_candidate_id")
    firmware_ref = normalized_record.get("firmware_update_candidate", {}).get("firmware_update_candidate_id")
    runtime_ref = normalized_record.get("runtime_redistributable_candidate", {}).get("runtime_candidate_id")
    candidate = {
        "schema_version": "h5_vendor_payload_metadata_candidate.v0",
        "payload_candidate_id": f"h5.payload.{source_id}.{_slug(native_id)}.v0",
        "source_id": source_id,
        "vendor_identity_candidate_ref": normalized_record.get("vendor_identity_candidate", {}).get("vendor_identity_candidate_id"),
        "related_driver_candidate_ref": driver_ref,
        "related_firmware_candidate_ref": firmware_ref,
        "related_runtime_candidate_ref": runtime_ref,
        "payload_name": normalized_record.get("package_or_payload_name", "unknown"),
        "payload_kind": normalized_record.get("payload_kind", "metadata_only"),
        "payload_size": "unknown",
        "payload_hashes": normalized_record.get("hash_metadata", {}),
        "signature_metadata": normalized_record.get("signature_metadata", {}),
        "sbom_metadata": {"candidate_only": True, "sbom_metadata_is_verified_provenance": False},
        "source_locator": normalized_record.get("payload_locator_candidate", "unknown"),
        "download_allowed_current": False,
        "payload_available_current": False,
        "installer_execution_allowed_current": False,
        "firmware_flash_allowed_current": False,
        "limitations": ["Payload metadata candidate grants no download, availability, install, execution, flash, safety, or authenticity permission."],
        "truth_boundary": {
            "payload_hash_proves_malware_safety": False,
            "signature_metadata_proves_authenticity": False,
            "sbom_metadata_is_verified_provenance": False,
            "malware_safety_claimed": False,
            "verified_authenticity_claimed": False,
        },
        "product_boundary": _product_boundary(),
    }
    _raise_on_boundary_errors(candidate)
    return [candidate]


def build_h5_source_cache_candidate_preview(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source_id = str(normalized_record.get("source_id"))
    preview = {
        "schema_version": "h5_vendor_update_source_cache_candidate.v0",
        "source_cache_candidate_id": f"h5.source_cache.{source_id}.{_slug(str(normalized_record.get('vendor_native_id') or 'unknown'))}.v0",
        "source_id": source_id,
        "record_ref": normalized_record.get("normalized_record_id"),
        "candidate_status": "preview_only",
        "accepted_as_source": False,
        "review_required": True,
        "truth_boundary": {"source_cache_preview_is_accepted_source": False, "accepted_source_truth": False, "public_index_mutated": False, "master_index_mutated": False},
        "product_boundary": _product_boundary(),
    }
    _raise_on_boundary_errors(preview)
    return preview


def build_h5_evidence_candidate_preview(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source_id = str(normalized_record.get("source_id"))
    preview = {
        "schema_version": "h5_vendor_update_evidence_candidate_preview.v0",
        "evidence_candidate_preview_id": f"h5.evidence_preview.{source_id}.{_slug(str(normalized_record.get('vendor_native_id') or 'unknown'))}.v0",
        "source_id": source_id,
        "record_ref": normalized_record.get("normalized_record_id"),
        "candidate_status": "preview_only",
        "accepted_as_evidence": False,
        "review_required": True,
        "truth_boundary": {"evidence_preview_is_accepted_evidence": False, "accepted_evidence_truth": False, "public_index_mutated": False, "master_index_mutated": False},
        "product_boundary": _product_boundary(),
    }
    _raise_on_boundary_errors(preview)
    return preview


def build_h5_fixture_replay_result(fixture: Mapping[str, Any], normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source_id = str(fixture.get("source_id"))
    result = {
        "schema_version": "h5_vendor_update_fixture_replay_result.v0",
        "replay_result_id": f"h5.replay.{source_id}.{_slug(str(fixture.get('fixture_id') or 'fixture'))}.v0",
        "fixture_id": fixture.get("fixture_id"),
        "source_id": source_id,
        "connector_family": fixture.get("connector_family"),
        "replay_status": "pass_fixture_only" if fixture.get("fixture_status") != "policy_blocked" else "blocked_by_policy_fixture",
        "normalized_record_ref": normalized_record.get("normalized_record_id"),
        "vendor_identity_candidate_ref": normalized_record.get("vendor_identity_candidate", {}).get("vendor_identity_candidate_id"),
        "driver_device_compatibility_candidate_refs": [item.get("compatibility_candidate_id") for item in normalized_record.get("driver_device_compatibility_candidate_preview", [])],
        "firmware_update_candidate_refs": [item.get("firmware_update_candidate_id") for item in normalized_record.get("firmware_update_candidate_preview", [])],
        "runtime_redistributable_candidate_refs": [item.get("runtime_candidate_id") for item in normalized_record.get("runtime_redistributable_candidate_preview", [])],
        "payload_metadata_candidate_refs": [item.get("payload_candidate_id") for item in normalized_record.get("payload_metadata_candidate_preview", [])],
        "source_cache_candidate_ref": normalized_record.get("source_cache_candidate_preview", {}).get("source_cache_candidate_id"),
        "evidence_candidate_preview_ref": normalized_record.get("evidence_candidate_preview", {}).get("evidence_candidate_preview_id"),
        "validation_summary": {
            "normalized": True,
            "fixture_only": True,
            "truth_boundary_violations": detect_h5_truth_boundary_violations(normalized_record),
            "product_boundary_violations": detect_h5_product_boundary_violations(normalized_record),
        },
        "warnings": [],
        "limitations": list(normalized_record.get("source_limitations") or []),
        "no_network_used": True,
        "no_live_source_used": True,
        "no_vendor_catalog_fetch_used": True,
        "no_download_used": True,
        "no_vendor_tool_invoked": True,
        "no_package_manager_invoked": True,
        "no_firmware_flash_invoked": True,
        "no_installer_or_artifact_executed": True,
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["Fixture replay result is not evidence acceptance or public truth."],
    }
    _raise_on_boundary_errors(result)
    return result


def summarize_h5_normalized_record(record: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "source_id": record.get("source_id"),
        "vendor_name": record.get("vendor_name"),
        "product_name": record.get("product_name"),
        "has_driver_candidate": bool(record.get("driver_device_compatibility_candidate_preview")),
        "has_firmware_candidate": bool(record.get("firmware_update_candidate_preview")),
        "has_runtime_candidate": bool(record.get("runtime_redistributable_candidate_preview")),
        "has_payload_candidate": bool(record.get("payload_metadata_candidate_preview")),
        "truth_boundary_violations": detect_h5_truth_boundary_violations(record),
        "product_boundary_violations": detect_h5_product_boundary_violations(record),
    }


def detect_h5_truth_boundary_violations(record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    return _detect_true_keys(record, FORBIDDEN_TRUTH_TRUE_KEYS, "truth")


def detect_h5_product_boundary_violations(record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    return _detect_true_keys(record, FORBIDDEN_PRODUCT_TRUE_KEYS, "product")


def _require_fixture_boundaries(fixture: Mapping[str, Any]) -> None:
    for key in FIXTURE_FORBIDDEN_TRUE_KEYS:
        if fixture.get(key) is True:
            raise ValueError(f"fixture forbidden behavior flag is true: {key}")
    if fixture.get("fixture_public_safe") is not True:
        raise ValueError("fixture_public_safe must be true")
    for item in detect_h5_truth_boundary_violations(fixture) + detect_h5_product_boundary_violations(fixture):
        raise ValueError(item)


def _truth_boundary() -> dict[str, bool]:
    return {'normalized_record_is_public_truth': False, 'vendor_identity_candidate_is_truth': False, 'vendor_identity_candidate_is_accepted_vendor_truth': False, 'vendor_source_proves_official_status': False, 'vendor_presence_proves_endorsement': False, 'driver_identity_candidate_is_truth': False, 'firmware_identity_candidate_is_truth': False, 'runtime_identity_candidate_is_truth': False, 'compatibility_candidate_is_truth': False, 'compatibility_candidate_is_verified_compatibility': False, 'device_id_match_proves_safe_installability': False, 'os_version_match_proves_runtime_correctness': False, 'architecture_match_proves_device_compatibility': False, 'firmware_update_candidate_is_approved_to_flash': False, 'firmware_metadata_proves_device_compatibility': False, 'firmware_hash_proves_malware_safety': False, 'firmware_signature_metadata_is_verified_authenticity': False, 'flashing_tool_metadata_is_execution_permission': False, 'runtime_candidate_is_installability_truth': False, 'installer_metadata_is_execution_permission': False, 'dependency_metadata_is_dependency_correctness': False, 'security_update_metadata_is_safety_proof': False, 'payload_hash_proves_malware_safety': False, 'signature_metadata_proves_authenticity': False, 'sbom_metadata_is_verified_provenance': False, 'license_metadata_is_rights_clearance': False, 'source_cache_preview_is_accepted_source': False, 'evidence_preview_is_accepted_evidence': False, 'accepted_source_truth': False, 'accepted_evidence_truth': False, 'accepted_candidate_truth': False, 'accepted_vendor_truth': False, 'accepted_driver_identity_truth': False, 'accepted_firmware_identity_truth': False, 'accepted_runtime_identity_truth': False, 'accepted_compatibility_truth': False, 'accepted_authenticity_truth': False, 'accepted_safety_truth': False, 'accepted_public_record': False, 'public_index_mutated': False, 'master_index_mutated': False, 'rights_clearance_claimed': False, 'malware_safety_claimed': False, 'verified_installability_claimed': False, 'verified_compatibility_claimed': False, 'verified_authenticity_claimed': False, 'production_readiness_claimed': False}


def _product_boundary() -> dict[str, bool]:
    return {'changed_public_search_behavior': False, 'enabled_hosting': False, 'enabled_live_probes': False, 'enabled_source_sync': False, 'enabled_source_connectors': False, 'enabled_catalog_fetch': False, 'enabled_downloads': False, 'enabled_installers': False, 'enabled_execution': False, 'enabled_firmware_flashing': False, 'enabled_uploads': False, 'enabled_accounts': False, 'enabled_telemetry': False, 'mutated_public_index': False, 'mutated_master_index': False, 'network_calls_made': False, 'api_calls_made': False, 'vendor_catalog_fetch_used': False, 'download_used': False, 'vendor_tool_invoked': False, 'package_manager_invoked': False, 'firmware_flash_invoked': False, 'installer_or_artifact_executed': False}


def _mapping(value: Any, name: str, default: dict[str, Any] | None = None) -> dict[str, Any]:
    if value is None:
        return dict(default or {})
    if not isinstance(value, Mapping):
        raise ValueError(f"{name} must be an object")
    return dict(value)


def _strings(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [str(item) for item in value if item not in (None, "")]
    return []


def _text(value: Any) -> str:
    if value in (None, ""):
        return ""
    return str(value)


def _slug(value: str) -> str:
    safe = "".join(ch.lower() if ch.isalnum() else "-" for ch in value).strip("-")
    safe = "-".join(part for part in safe.split("-") if part)
    if safe:
        return safe[:64]
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:12]


def _missing_optional_limitations(payload: Mapping[str, Any]) -> list[str]:
    expected = ("vendor_version", "release_date_candidate", "driver_version", "firmware_version", "runtime_version", "payload_locator_candidate", "hash_metadata", "signature_metadata")
    return [f"optional field absent or unknown: {key}" for key in expected if payload.get(key) in (None, "", "unknown", [], {})]


def _has_any(record: Mapping[str, Any], fields: tuple[str, ...]) -> bool:
    return any(record.get(field) not in (None, "", "unknown", [], {}) for field in fields)


def _dedupe(items: list[Any]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        text = str(item)
        if text not in seen:
            out.append(text)
            seen.add(text)
    return out


def _detect_true_keys(value: Any, forbidden: set[str], category: str, path: str = "") -> list[str]:
    errors: list[str] = []
    if isinstance(value, Mapping):
        for key, item in value.items():
            current = f"{path}.{key}" if path else str(key)
            if key in forbidden and item is True:
                errors.append(f"{category} boundary forbidden true value: {current}")
            errors.extend(_detect_true_keys(item, forbidden, category, current))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            errors.extend(_detect_true_keys(item, forbidden, category, f"{path}[{index}]"))
    return errors


def _raise_on_boundary_errors(record: Mapping[str, Any]) -> None:
    errors = detect_h5_truth_boundary_violations(record) + detect_h5_product_boundary_violations(record)
    if errors:
        raise ValueError("; ".join(errors))
