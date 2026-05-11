"""Fixture-only H8 manuals/docs/standards normalization helpers."""

from __future__ import annotations

import hashlib
from collections.abc import Mapping
from typing import Any

H8_SOURCE_CONFIGS: dict[str, dict[str, Any]] = {'bitsavers_docs': {'label': 'Bitsavers computing documentation metadata', 'connector_family': 'manual_library_metadata'}, 'ia_manuals_library': {'label': 'Internet Archive Manuals Library metadata', 'connector_family': 'manual_library_metadata'}, 'manualslib_metadata': {'label': 'ManualsLib-style manual metadata', 'connector_family': 'manual_library_metadata'}, 'vendor_documentation_portal': {'label': 'Vendor documentation portal metadata', 'connector_family': 'vendor_documentation_catalog'}, 'microsoft_technical_docs': {'label': 'Microsoft technical documentation metadata', 'connector_family': 'vendor_documentation_catalog'}, 'apple_support_developer_docs': {'label': 'Apple support/developer documentation metadata', 'connector_family': 'vendor_documentation_catalog'}, 'ibm_documentation': {'label': 'IBM documentation metadata', 'connector_family': 'vendor_documentation_catalog'}, 'sun_oracle_documentation': {'label': 'Sun / Oracle documentation metadata', 'connector_family': 'vendor_documentation_catalog'}, 'hp_hpe_documentation': {'label': 'HP / HPE technical documentation metadata', 'connector_family': 'vendor_documentation_catalog'}, 'dec_vax_pdp_documentation': {'label': 'DEC / VAX / PDP documentation metadata', 'connector_family': 'technical_document_catalog'}, 'sgi_documentation': {'label': 'SGI technical documentation metadata', 'connector_family': 'technical_document_catalog'}, 'rfc_editor_ietf': {'label': 'RFC Editor / IETF RFC metadata', 'connector_family': 'standards_metadata'}, 'w3c_technical_reports': {'label': 'W3C technical report metadata', 'connector_family': 'standards_metadata'}, 'iso_iec_public_standards': {'label': 'ISO / IEC public standards metadata', 'connector_family': 'standards_metadata'}, 'ieee_acm_standards_metadata': {'label': 'IEEE / ACM / standards-body public metadata, policy-limited', 'connector_family': 'restricted_manifest_only'}, 'semiconductor_datasheets': {'label': 'Semiconductor datasheet metadata', 'connector_family': 'datasheet_catalog'}, 'service_manual_schematic_archive': {'label': 'Service manual / schematic archive metadata', 'connector_family': 'service_manual_catalog'}, 'generic_technical_document_collection': {'label': 'Generic technical-document collection metadata', 'connector_family': 'technical_document_catalog'}}
H8_SOURCE_IDS = tuple(H8_SOURCE_CONFIGS)
H8_FIXTURE_KINDS = ('minimal', 'document_identity', 'manual_artifact_relation', 'datasheet_device', 'standards_specification', 'install_requirement', 'repair_service_safety', 'access_rights', 'policy_blocked')

FIXTURE_FORBIDDEN_TRUE_KEYS = {
    "live_call_used",
    "network_used",
    "external_api_used",
    "catalog_payload_included",
    "document_payload_included",
    "pdf_payload_included",
    "scan_payload_included",
    "datasheet_payload_included",
    "standards_document_payload_included",
    "schematic_payload_included",
    "service_manual_payload_included",
    "full_text_payload_included",
    "ocr_payload_included",
    "iiif_payload_included",
    "media_payload_included",
    "scraping_output_included",
    "crawling_output_included",
    "restricted_source_accessed",
    "bypass_or_automation_used",
}
FORBIDDEN_TRUTH_TRUE_KEYS = {'repair_service_safety_candidate_is_safety_truth', 'accepted_access_rights_truth', 'accepted_manual_artifact_relation_truth', 'standards_specification_candidate_is_truth', 'datasheet_device_identity_candidate_is_truth', 'accepted_datasheet_device_truth', 'technical_document_identity_candidate_is_truth', 'accepted_standards_truth', 'source_cache_preview_is_accepted_source', 'access_metadata_is_rights_truth', 'privacy_safety_claimed', 'installability_claimed', 'accepted_source_truth', 'manual_artifact_relation_candidate_is_truth', 'accepted_evidence_truth', 'evidence_preview_is_accepted_evidence', 'open_access_metadata_is_rights_clearance', 'electrical_safety_claimed', 'accepted_public_record', 'open_access_truth_claimed', 'malware_safety_claimed', 'documentation_completeness_claimed', 'public_index_mutated', 'document_metadata_grants_download_permission', 'master_index_mutated', 'compatibility_correctness_claimed', 'accepted_candidate_truth', 'verified_authenticity_claimed', 'accepted_repair_service_safety_truth', 'repair_service_candidate_authorizes_action', 'install_requirement_candidate_is_installability_truth', 'accepted_install_requirement_truth', 'rights_clearance_claimed', 'production_readiness_claimed', 'normalized_record_is_public_truth', 'accepted_document_truth', 'repair_safety_claimed', 'standards_conformance_verified'}
FORBIDDEN_PRODUCT_TRUE_KEYS = {'ocr_extraction_used', 'network_calls_made', 'enabled_source_sync', 'bypass_or_automation_used', 'crawling_used', 'enabled_downloads', 'enabled_telemetry', 'mutated_master_index', 'service_manual_download_used', 'api_calls_made', 'media_download_used', 'restricted_source_access_used', 'full_text_fetch_used', 'schematic_download_used', 'datasheet_download_used', 'catalog_fetch_used', 'enabled_accounts', 'changed_public_search_behavior', 'document_fetch_used', 'enabled_extraction', 'document_download_used', 'pdf_download_used', 'browser_automation_used', 'mutated_public_index', 'standards_document_download_used', 'enabled_crawling', 'iiif_fetch_used', 'scan_download_used', 'enabled_hosting', 'enabled_live_probes', 'scraping_used', 'enabled_uploads'}


def normalize_h8_manuals_docs_fixture(raw_fixture: Mapping[str, Any], source_id: str, policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    if source_id not in H8_SOURCE_CONFIGS:
        raise ValueError(f"unknown H8 source_id: {source_id}")
    if raw_fixture.get("source_id") != source_id:
        raise ValueError(f"fixture source_id does not match requested source_id: {source_id}")
    _require_fixture_boundaries(raw_fixture)
    payload = _mapping(raw_fixture.get("fixture_payload"), "fixture_payload")
    config = H8_SOURCE_CONFIGS[source_id]
    native_id = _text(payload.get("source_native_id")) or _text(payload.get("catalog_record_id")) or f"fixture-{source_id}"
    limitations = list(raw_fixture.get("limitations") or [])
    limitations.extend(_missing_optional_limitations(payload))
    if raw_fixture.get("fixture_status") == "policy_blocked":
        limitations.append("fixture is policy-blocked and remains candidate-only")
    record: dict[str, Any] = {
        "schema_version": "h8_manuals_docs_normalized_record.v0",
        "normalized_record_id": f"h8.normalized.{source_id}.{_slug(native_id)}.v0",
        "source_id": source_id,
        "connector_family": str(raw_fixture.get("connector_family") or config["connector_family"]),
        "source_record_kind": _text(payload.get("source_record_kind")) or _text(raw_fixture.get("fixture_kind")) or "unknown",
        "document_title": _text(payload.get("document_title")) or "unknown",
        "document_subtitle": _text(payload.get("document_subtitle")) or "unknown",
        "document_type": _text(payload.get("document_type")) or "unknown",
        "document_number": _text(payload.get("document_number")) or "unknown",
        "document_revision": _text(payload.get("document_revision")) or "unknown",
        "edition": _text(payload.get("edition")) or "unknown",
        "publication_date": _text(payload.get("publication_date")) or "unknown",
        "vendor_or_publisher": _text(payload.get("vendor_or_publisher")) or "unknown",
        "author_or_editor": _list(payload.get("author_or_editor")),
        "product_or_subject": _text(payload.get("product_or_subject")) or "unknown",
        "language": _text(payload.get("language")) or "unknown",
        "format_or_medium": _text(payload.get("format_or_medium")) or "unknown",
        "page_count_candidate": payload.get("page_count_candidate", "unknown"),
        "catalog_record_id": _text(payload.get("catalog_record_id")) or "unknown",
        "collection_id": _text(payload.get("collection_id")) or "unknown",
        "source_native_id": native_id,
        "manufacturer": _text(payload.get("manufacturer")) or "unknown",
        "part_number": _text(payload.get("part_number")) or "unknown",
        "device_family": _text(payload.get("device_family")) or "unknown",
        "package_type": _text(payload.get("package_type")) or "unknown",
        "standards_body": _text(payload.get("standards_body")) or "unknown",
        "standard_number": _text(payload.get("standard_number")) or "unknown",
        "specification_title": _text(payload.get("specification_title")) or "unknown",
        "version_or_revision": _text(payload.get("version_or_revision")) or "unknown",
        "operating_system": _text(payload.get("operating_system")) or "unknown",
        "architecture": _text(payload.get("architecture")) or "unknown",
        "hardware_requirement": _text(payload.get("hardware_requirement")) or "unknown",
        "dependency_requirement": _text(payload.get("dependency_requirement")) or "unknown",
        "install_step_candidate": _text(payload.get("install_step_candidate")) or "unknown",
        "hazard_note_candidate": _text(payload.get("hazard_note_candidate")) or "unknown",
        "safety_warning_candidate": _text(payload.get("safety_warning_candidate")) or "unknown",
        "rights_or_license_metadata": _text(payload.get("rights_or_license_metadata")) or "unknown",
        "source_locator_candidate": _text(payload.get("source_locator_candidate")) or "unknown",
        "checksum_metadata_candidate": _text(payload.get("checksum_metadata_candidate")) or "unknown",
        "ocr_or_full_text_availability_candidate": _text(payload.get("ocr_or_full_text_availability_candidate")) or "unknown",
        "relations": _list(payload.get("relations")),
        "access": _mapping(payload.get("access"), "access", default={}),
        "source_metadata": _mapping(payload.get("source_metadata"), "source_metadata", default={}),
        "metadata_summary": _text(payload.get("metadata_summary")) or "fixture-only technical-document metadata summary",
        "source_limitations": _dedupe(limitations),
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["Fixture-only H8 normalized record; review is required before any downstream use."],
    }
    record["technical_document_identity_candidate"] = build_h8_technical_document_identity_candidate(record, policy)
    record["manual_artifact_relation_candidate"] = build_h8_manual_artifact_relation_candidates(record, policy)
    record["datasheet_device_identity_candidate"] = build_h8_datasheet_device_identity_candidate(record, policy)
    record["standards_specification_identity_candidate"] = build_h8_standards_specification_identity_candidate(record, policy)
    record["install_requirement_claim_candidate"] = build_h8_install_requirement_claim_candidates(record, policy)
    record["repair_service_safety_candidate"] = build_h8_repair_service_safety_candidates(record, policy)
    record["access_rights_candidate"] = build_h8_access_rights_candidate(record, policy)
    record["source_cache_candidate_preview"] = build_h8_source_cache_candidate_preview(record, policy)
    record["evidence_candidate_preview"] = build_h8_evidence_candidate_preview(record, policy)
    _raise_on_boundary_errors(record)
    return record


def build_h8_technical_document_identity_candidate(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    fields = ("document_title", "document_type", "document_number", "document_revision", "edition", "publication_date", "vendor_or_publisher", "author_or_editor", "product_or_subject", "language", "format_or_medium", "page_count_candidate", "catalog_record_id", "collection_id", "checksum_metadata_candidate", "source_locator_candidate", "ocr_or_full_text_availability_candidate")
    return _candidate(normalized_record, "h8_technical_document_identity_candidate.v0", "technical_document_identity", fields, "Technical document identity candidate is not accepted document truth, completeness proof, authenticity proof, extraction permission, or download permission.")


def build_h8_manual_artifact_relation_candidates(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    fields = ("document_title", "product_or_subject", "part_number", "operating_system", "architecture", "version_or_revision", "relations")
    return [_candidate(normalized_record, "h8_manual_artifact_relation_candidate.v0", "manual_artifact_relation", fields, "Manual-artifact relation candidate is not relation truth, compatibility correctness, installability, repair safety, or rights clearance.")]


def build_h8_datasheet_device_identity_candidate(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    fields = ("manufacturer", "part_number", "device_family", "package_type", "document_number", "document_revision", "source_locator_candidate")
    return _candidate(normalized_record, "h8_datasheet_device_identity_candidate.v0", "datasheet_device_identity", fields, "Datasheet/device identity candidate is not accepted device truth, electrical safety proof, lifecycle truth, or engineering guidance.")


def build_h8_standards_specification_identity_candidate(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    fields = ("standards_body", "standard_number", "specification_title", "version_or_revision", "publication_date", "product_or_subject", "source_locator_candidate", "rights_or_license_metadata")
    return _candidate(normalized_record, "h8_standards_specification_identity_candidate.v0", "standards_specification_identity", fields, "Standards/specification candidate is not standards truth, conformance proof, document access permission, or rights clearance.")


def build_h8_install_requirement_claim_candidates(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    fields = ("product_or_subject", "operating_system", "architecture", "hardware_requirement", "dependency_requirement", "install_step_candidate", "source_locator_candidate")
    return [_candidate(normalized_record, "h8_install_requirement_claim_candidate.v0", "install_requirement_claim", fields, "Install requirement candidate is not installability truth, safe execution guidance, compatibility correctness, or action permission.")]


def build_h8_repair_service_safety_candidates(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    fields = ("document_title", "product_or_subject", "hazard_note_candidate", "safety_warning_candidate", "part_number", "source_locator_candidate")
    return [_candidate(normalized_record, "h8_repair_service_safety_candidate.v0", "repair_service_safety", fields, "Repair/service/safety candidate is not safety truth, electrical safety proof, repair authorization, calibration permission, or action permission.")]


def build_h8_access_rights_candidate(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    fields = ("rights_or_license_metadata", "source_locator_candidate", "access", "ocr_or_full_text_availability_candidate")
    return _candidate(normalized_record, "h8_access_rights_candidate.v0", "access_rights", fields, "Access/rights candidate is not rights clearance, open-access truth, redistribution permission, or download permission.")


def build_h8_source_cache_candidate_preview(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    preview = {
        "schema_version": "h8_manuals_docs_source_cache_candidate_preview.v0",
        "source_cache_candidate_preview_id": f"h8.source_cache_preview.{normalized_record.get('source_id')}.{_slug(normalized_record.get('source_native_id'))}.v0",
        "source_id": normalized_record.get("source_id"),
        "source_record_ref": normalized_record.get("normalized_record_id"),
        "preview_only": True,
        "accepted_source": False,
        "persistence_allowed_current": False,
        "supporting_fields": [field for field in ("document_title", "source_native_id", "connector_family", "source_record_kind") if _is_present(normalized_record.get(field))],
        "limitations": ["Source-cache candidate preview only; no source cache mutation or accepted source truth."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
    }
    _raise_on_boundary_errors(preview)
    return preview


def build_h8_evidence_candidate_preview(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    preview = {
        "schema_version": "h8_manuals_docs_evidence_candidate_preview.v0",
        "evidence_candidate_preview_id": f"h8.evidence_preview.{normalized_record.get('source_id')}.{_slug(normalized_record.get('source_native_id'))}.v0",
        "source_id": normalized_record.get("source_id"),
        "source_record_ref": normalized_record.get("normalized_record_id"),
        "preview_only": True,
        "accepted_evidence": False,
        "evidence_ledger_write_allowed_current": False,
        "supporting_fields": [field for field in ("document_title", "document_number", "metadata_summary") if _is_present(normalized_record.get(field))],
        "limitations": ["Evidence candidate preview only; no evidence ledger mutation or accepted evidence truth."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
    }
    _raise_on_boundary_errors(preview)
    return preview


def build_h8_fixture_replay_result(fixture: Mapping[str, Any], normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    status = "blocked_by_policy_fixture" if fixture.get("fixture_status") == "policy_blocked" else "fixture_replayed"
    result = {
        "schema_version": "h8_manuals_docs_fixture_replay_result.v0",
        "fixture_replay_result_id": f"h8.replay.{fixture.get('source_id')}.{_slug(fixture.get('fixture_id'))}.v0",
        "fixture_ref": fixture.get("fixture_id"),
        "source_id": fixture.get("source_id"),
        "connector_family": fixture.get("connector_family"),
        "fixture_kind": fixture.get("fixture_kind"),
        "replay_status": status,
        "normalized_record": dict(normalized_record),
        "technical_document_identity_candidate": normalized_record.get("technical_document_identity_candidate", {}),
        "manual_artifact_relation_candidate": normalized_record.get("manual_artifact_relation_candidate", []),
        "datasheet_device_identity_candidate": normalized_record.get("datasheet_device_identity_candidate", {}),
        "standards_specification_identity_candidate": normalized_record.get("standards_specification_identity_candidate", {}),
        "install_requirement_claim_candidate": normalized_record.get("install_requirement_claim_candidate", []),
        "repair_service_safety_candidate": normalized_record.get("repair_service_safety_candidate", []),
        "access_rights_candidate": normalized_record.get("access_rights_candidate", {}),
        "source_cache_candidate_preview": normalized_record.get("source_cache_candidate_preview", {}),
        "evidence_candidate_preview": normalized_record.get("evidence_candidate_preview", {}),
        "no_network_used": True,
        "no_live_source_used": True,
        "no_api_catalog_query_used": True,
        "no_query_fetch_download_extract_used": True,
        "no_document_pdf_datasheet_standard_fetch_used": True,
        "no_full_text_or_ocr_used": True,
        "no_iiif_or_media_fetch_used": True,
        "no_scraping_crawling_used": True,
        "no_restricted_source_access_used": True,
        "no_repair_install_action_authorized": True,
        "warnings": [],
        "limitations": ["Fixture replay result is a candidate-only offline parser proof, not accepted truth or action permission."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
    }
    _raise_on_boundary_errors(result)
    return result


def summarize_h8_normalized_record(record: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "h8_manuals_docs_normalized_record_summary.v0",
        "source_id": record.get("source_id"),
        "normalized_record_id": record.get("normalized_record_id"),
        "document_title": record.get("document_title"),
        "technical_document_candidates": 1 if record.get("technical_document_identity_candidate") else 0,
        "manual_artifact_relation_candidates": len(record.get("manual_artifact_relation_candidate", []) or []),
        "datasheet_device_candidates": 1 if record.get("datasheet_device_identity_candidate") else 0,
        "standards_specification_candidates": 1 if record.get("standards_specification_identity_candidate") else 0,
        "install_requirement_candidates": len(record.get("install_requirement_claim_candidate", []) or []),
        "repair_service_safety_candidates": len(record.get("repair_service_safety_candidate", []) or []),
        "access_rights_candidates": 1 if record.get("access_rights_candidate") else 0,
        "network_calls_made": False,
        "query_fetch_download_extract_used": False,
    }


def detect_h8_truth_boundary_violations(record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    return _detect_true_keys(record, "truth_boundary", FORBIDDEN_TRUTH_TRUE_KEYS)


def detect_h8_product_boundary_violations(record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    return _detect_true_keys(record, "product_boundary", FORBIDDEN_PRODUCT_TRUE_KEYS)


def _candidate(normalized_record: Mapping[str, Any], schema_version: str, candidate_type: str, fields: tuple[str, ...], limitation: str) -> dict[str, Any]:
    source_id = str(normalized_record.get("source_id"))
    native_id = str(normalized_record.get("source_native_id") or normalized_record.get("normalized_record_id") or "unknown")
    supporting = [field for field in fields if _is_present(normalized_record.get(field))]
    candidate = {
        "schema_version": schema_version,
        "candidate_id": f"h8.{candidate_type}.{source_id}.{_slug(native_id)}.v0",
        "source_id": source_id,
        "source_record_ref": str(normalized_record.get("normalized_record_id") or "unknown"),
        "candidate_type": candidate_type,
        "candidate_fields": {field: normalized_record.get(field, "unknown") for field in fields},
        "supporting_fields": supporting,
        "missing_fields": [field for field in fields if field not in supporting],
        "confidence_or_uncertainty": "candidate_from_committed_fixture_no_truth_acceptance",
        "limitations": [limitation],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
    }
    _raise_on_boundary_errors(candidate)
    return candidate


def _require_fixture_boundaries(raw_fixture: Mapping[str, Any]) -> None:
    if raw_fixture.get("schema_version") != "h8_manuals_docs_fixture.v0":
        raise ValueError("fixture schema_version must be h8_manuals_docs_fixture.v0")
    for key in FIXTURE_FORBIDDEN_TRUE_KEYS:
        if raw_fixture.get(key) is True:
            raise ValueError(f"H8 fixture cannot enable or include forbidden behavior: {key}")
    truth_boundary = raw_fixture.get("truth_boundary")
    if isinstance(truth_boundary, Mapping):
        errors = _detect_true_keys({"truth_boundary": truth_boundary}, "truth_boundary", FORBIDDEN_TRUTH_TRUE_KEYS)
        if errors:
            raise ValueError("; ".join(errors))
    product_boundary = raw_fixture.get("product_boundary")
    if isinstance(product_boundary, Mapping):
        errors = _detect_true_keys({"product_boundary": product_boundary}, "product_boundary", FORBIDDEN_PRODUCT_TRUE_KEYS)
        if errors:
            raise ValueError("; ".join(errors))


def _raise_on_boundary_errors(record: Mapping[str, Any]) -> None:
    errors = detect_h8_truth_boundary_violations(record) + detect_h8_product_boundary_violations(record)
    if errors:
        raise ValueError("; ".join(errors))


def _detect_true_keys(record: Mapping[str, Any], section: str, keys: set[str]) -> list[str]:
    errors: list[str] = []
    boundary = record.get(section)
    if isinstance(boundary, Mapping):
        for key in keys:
            if boundary.get(key) is True:
                errors.append(f"{section}.{key} must remain false")
    return errors


def _truth_boundary() -> dict[str, bool]:
    return {'normalized_record_is_public_truth': False, 'accepted_source_truth': False, 'accepted_evidence_truth': False, 'accepted_candidate_truth': False, 'accepted_document_truth': False, 'accepted_manual_artifact_relation_truth': False, 'accepted_datasheet_device_truth': False, 'accepted_standards_truth': False, 'accepted_install_requirement_truth': False, 'accepted_repair_service_safety_truth': False, 'accepted_access_rights_truth': False, 'accepted_public_record': False, 'technical_document_identity_candidate_is_truth': False, 'manual_artifact_relation_candidate_is_truth': False, 'datasheet_device_identity_candidate_is_truth': False, 'standards_specification_candidate_is_truth': False, 'install_requirement_candidate_is_installability_truth': False, 'repair_service_safety_candidate_is_safety_truth': False, 'access_metadata_is_rights_truth': False, 'open_access_metadata_is_rights_clearance': False, 'document_metadata_grants_download_permission': False, 'repair_service_candidate_authorizes_action': False, 'source_cache_preview_is_accepted_source': False, 'evidence_preview_is_accepted_evidence': False, 'documentation_completeness_claimed': False, 'standards_conformance_verified': False, 'compatibility_correctness_claimed': False, 'installability_claimed': False, 'repair_safety_claimed': False, 'electrical_safety_claimed': False, 'public_index_mutated': False, 'master_index_mutated': False, 'rights_clearance_claimed': False, 'open_access_truth_claimed': False, 'privacy_safety_claimed': False, 'malware_safety_claimed': False, 'verified_authenticity_claimed': False, 'production_readiness_claimed': False}.copy()


def _product_boundary() -> dict[str, bool]:
    return {'network_calls_made': False, 'api_calls_made': False, 'catalog_fetch_used': False, 'document_fetch_used': False, 'document_download_used': False, 'pdf_download_used': False, 'scan_download_used': False, 'datasheet_download_used': False, 'standards_document_download_used': False, 'schematic_download_used': False, 'service_manual_download_used': False, 'full_text_fetch_used': False, 'ocr_extraction_used': False, 'iiif_fetch_used': False, 'media_download_used': False, 'scraping_used': False, 'crawling_used': False, 'browser_automation_used': False, 'bypass_or_automation_used': False, 'restricted_source_access_used': False, 'changed_public_search_behavior': False, 'enabled_hosting': False, 'enabled_live_probes': False, 'enabled_source_sync': False, 'enabled_downloads': False, 'enabled_extraction': False, 'enabled_crawling': False, 'enabled_uploads': False, 'enabled_accounts': False, 'enabled_telemetry': False, 'mutated_public_index': False, 'mutated_master_index': False}.copy()


def _missing_optional_limitations(payload: Mapping[str, Any]) -> list[str]:
    optional = ("document_title", "document_type", "document_number", "document_revision", "publication_date", "vendor_or_publisher", "product_or_subject", "catalog_record_id", "source_native_id", "manufacturer", "part_number", "standards_body", "standard_number", "install_step_candidate", "hazard_note_candidate", "safety_warning_candidate", "rights_or_license_metadata")
    return [f"optional field absent or unknown: {field}" for field in optional if not _is_present(payload.get(field))]


def _mapping(value: Any, name: str, default: dict[str, Any] | None = None) -> dict[str, Any]:
    if value is None:
        return {} if default is None else dict(default)
    if not isinstance(value, Mapping):
        raise ValueError(f"{name} must be a mapping")
    return dict(value)


def _list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return str(value)


def _is_present(value: Any) -> bool:
    return value not in (None, "", "unknown", [], {})


def _dedupe(items: list[Any]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        text = str(item)
        if text not in seen:
            seen.add(text)
            result.append(text)
    return result


def _slug(value: Any) -> str:
    text = str(value or "unknown").encode("utf-8", "ignore")
    return hashlib.sha256(text).hexdigest()[:16]
