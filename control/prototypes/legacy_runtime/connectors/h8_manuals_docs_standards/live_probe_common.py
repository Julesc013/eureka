"""Fail-closed H8 manuals/docs/standards metadata live-probe helpers."""

from __future__ import annotations

from collections.abc import Mapping
import hashlib
import json
from pathlib import Path
from typing import Any

from control.prototypes.legacy_runtime.connectors.h8_manuals_docs_standards.normalizer_common import (
    build_h8_access_rights_candidate as _fixture_access_candidate,
    build_h8_datasheet_device_identity_candidate as _fixture_datasheet_candidate,
    build_h8_evidence_candidate_preview as _fixture_evidence_preview,
    build_h8_install_requirement_claim_candidates as _fixture_install_candidates,
    build_h8_manual_artifact_relation_candidates as _fixture_relation_candidates,
    build_h8_repair_service_safety_candidates as _fixture_repair_candidates,
    build_h8_source_cache_candidate_preview as _fixture_source_cache_preview,
    build_h8_standards_specification_identity_candidate as _fixture_standard_candidate,
    build_h8_technical_document_identity_candidate as _fixture_document_candidate,
    detect_h8_product_boundary_violations as _fixture_product_violations,
    detect_h8_truth_boundary_violations as _fixture_truth_violations,
    normalize_h8_manuals_docs_fixture,
)

POLICY_PATHS = {
    "live_probe_policy": "control/inventory/connectors/h8_manuals_docs_live_probe_policy.json",
    "allowed_requests": "control/inventory/connectors/h8_manuals_docs_live_probe_allowed_requests" + ".json",
    "endpoint_policy": "control/inventory/connectors/h8_manuals_docs_live_probe_endpoint_policy.json",
    "rate_limit_policy": "control/inventory/connectors/h8_manuals_docs_live_probe_rate_limit_policy.json",
    "cache_policy": "control/inventory/connectors/h8_manuals_docs_live_probe_cache_policy.json",
    "kill_switch_policy": "control/inventory/connectors/h8_manuals_docs_live_probe_kill_switch_policy.json",
    "output_policy": "control/inventory/connectors/h8_manuals_docs_live_probe_output_policy.json",
    "path_policy": "control/inventory/connectors/h8_manuals_docs_live_probe_path_policy.json",
    "review_policy": "control/inventory/connectors/h8_manuals_docs_live_probe_review_policy.json",
    "truth_policy": "control/inventory/connectors/h8_manuals_docs_live_probe_truth_policy.json",
    "no_download_extract_policy": "control/inventory/connectors/h8_manuals_docs_live_probe_no_download_extract_policy.json",
    "restricted_source_policy": "control/inventory/connectors/h8_manuals_docs_live_probe_restricted_source_policy.json",
}
SOURCE_CONFIGS = {'bitsavers_docs': {'label': 'Bitsavers computing documentation metadata', 'connector_family': 'manual_library_metadata', 'source_record_kind': 'technical_document_metadata', 'endpoint_or_metadata_class': 'document_metadata_lookup_future', 'request_key': 'example_document_metadata'}, 'ia_manuals_library': {'label': 'Internet Archive Manuals Library metadata', 'connector_family': 'manual_library_metadata', 'source_record_kind': 'manual_metadata', 'endpoint_or_metadata_class': 'item_metadata_lookup_future', 'request_key': 'example_manual_metadata'}, 'manualslib_metadata': {'label': 'ManualsLib-style manual metadata', 'connector_family': 'manual_library_metadata', 'source_record_kind': 'manual_metadata', 'endpoint_or_metadata_class': 'manual_metadata_lookup_future', 'request_key': 'example_manual_metadata'}, 'vendor_documentation_portal': {'label': 'Vendor documentation portal metadata', 'connector_family': 'vendor_documentation_catalog', 'source_record_kind': 'technical_document_metadata', 'endpoint_or_metadata_class': 'technical_document_metadata_lookup_future', 'request_key': 'example_document_metadata'}, 'microsoft_technical_docs': {'label': 'Microsoft technical documentation metadata', 'connector_family': 'vendor_documentation_catalog', 'source_record_kind': 'technical_document_metadata', 'endpoint_or_metadata_class': 'technical_document_metadata_lookup_future', 'request_key': 'example_document_metadata'}, 'apple_support_developer_docs': {'label': 'Apple support/developer documentation metadata', 'connector_family': 'vendor_documentation_catalog', 'source_record_kind': 'technical_document_metadata', 'endpoint_or_metadata_class': 'technical_document_metadata_lookup_future', 'request_key': 'example_document_metadata'}, 'ibm_documentation': {'label': 'IBM documentation metadata', 'connector_family': 'vendor_documentation_catalog', 'source_record_kind': 'technical_document_metadata', 'endpoint_or_metadata_class': 'technical_document_metadata_lookup_future', 'request_key': 'example_document_metadata'}, 'sun_oracle_documentation': {'label': 'Sun / Oracle documentation metadata', 'connector_family': 'vendor_documentation_catalog', 'source_record_kind': 'technical_document_metadata', 'endpoint_or_metadata_class': 'technical_document_metadata_lookup_future', 'request_key': 'example_document_metadata'}, 'hp_hpe_documentation': {'label': 'HP / HPE technical documentation metadata', 'connector_family': 'vendor_documentation_catalog', 'source_record_kind': 'technical_document_metadata', 'endpoint_or_metadata_class': 'technical_document_metadata_lookup_future', 'request_key': 'example_document_metadata'}, 'dec_vax_pdp_documentation': {'label': 'DEC / VAX / PDP documentation metadata', 'connector_family': 'technical_document_catalog', 'source_record_kind': 'technical_document_metadata', 'endpoint_or_metadata_class': 'technical_document_metadata_lookup_future', 'request_key': 'example_document_metadata'}, 'sgi_documentation': {'label': 'SGI technical documentation metadata', 'connector_family': 'technical_document_catalog', 'source_record_kind': 'technical_document_metadata', 'endpoint_or_metadata_class': 'technical_document_metadata_lookup_future', 'request_key': 'example_document_metadata'}, 'rfc_editor_ietf': {'label': 'RFC Editor / IETF RFC metadata', 'connector_family': 'standards_metadata', 'source_record_kind': 'standards_specification_metadata', 'endpoint_or_metadata_class': 'rfc_metadata_lookup_future', 'request_key': 'example_rfc_metadata'}, 'w3c_technical_reports': {'label': 'W3C technical report metadata', 'connector_family': 'standards_metadata', 'source_record_kind': 'standards_specification_metadata', 'endpoint_or_metadata_class': 'technical_report_metadata_lookup_future', 'request_key': 'example_technical_report_metadata'}, 'iso_iec_public_standards': {'label': 'ISO / IEC public standards metadata', 'connector_family': 'standards_metadata', 'source_record_kind': 'standards_specification_metadata', 'endpoint_or_metadata_class': 'public_metadata_lookup_future', 'request_key': 'example_standard_metadata'}, 'ieee_acm_standards_metadata': {'label': 'IEEE / ACM / standards-body public metadata, policy-limited', 'connector_family': 'restricted_manifest_only', 'source_record_kind': 'standards_specification_metadata', 'endpoint_or_metadata_class': 'public_metadata_policy_limited_future', 'request_key': 'example_standard_metadata'}, 'semiconductor_datasheets': {'label': 'Semiconductor datasheet metadata', 'connector_family': 'datasheet_catalog', 'source_record_kind': 'datasheet_metadata', 'endpoint_or_metadata_class': 'datasheet_metadata_lookup_future', 'request_key': 'example_datasheet_metadata'}, 'service_manual_schematic_archive': {'label': 'Service manual / schematic archive metadata', 'connector_family': 'service_manual_catalog', 'source_record_kind': 'service_manual_metadata', 'endpoint_or_metadata_class': 'service_manual_metadata_lookup_future', 'request_key': 'example_service_manual_metadata'}, 'generic_technical_document_collection': {'label': 'Generic technical-document collection metadata', 'connector_family': 'technical_document_catalog', 'source_record_kind': 'technical_document_metadata', 'endpoint_or_metadata_class': 'technical_document_metadata_fixture_future', 'request_key': 'example_document_metadata'}}
H8_SOURCE_IDS = tuple(SOURCE_CONFIGS)

REQUEST_FORBIDDEN_TRUE_KEYS = {
    "document_download_requested",
    "pdf_download_requested",
    "scan_download_requested",
    "full_text_fetch_requested",
    "ocr_extraction_requested",
    "iiif_manifest_fetch_requested",
    "standards_document_fetch_requested",
    "datasheet_download_requested",
    "schematic_download_requested",
    "service_manual_download_requested",
    "media_download_requested",
    "scraping_or_crawling_requested",
    "restricted_source_requested",
    "bypass_or_automation_requested",
}
FORBIDDEN_TRUTH_TRUE_KEYS = set(['accepted_access_rights_truth', 'accepted_candidate_truth', 'accepted_datasheet_device_truth', 'accepted_document_truth', 'accepted_evidence_truth', 'accepted_install_requirement_truth', 'accepted_manual_artifact_relation_truth', 'accepted_public_record', 'accepted_repair_service_safety_truth', 'accepted_source_truth', 'accepted_standards_truth', 'access_metadata_is_rights_truth', 'compatibility_correctness_claimed', 'datasheet_device_candidate_is_truth', 'datasheet_device_identity_candidate_is_truth', 'documentation_completeness_claimed', 'electrical_safety_claimed', 'evidence_candidate_preview_is_accepted_evidence', 'evidence_preview_is_accepted_evidence', 'install_requirement_candidate_is_installability_truth', 'install_requirement_candidate_is_truth', 'installability_claimed', 'live_probe_result_is_public_truth', 'malware_safety_claimed', 'manual_artifact_relation_candidate_is_truth', 'master_index_mutated', 'normalized_record_is_public_truth', 'open_access_metadata_is_rights_clearance', 'open_access_truth_claimed', 'production_readiness_claimed', 'public_index_mutated', 'repair_safety_claimed', 'repair_service_safety_candidate_is_safety_truth', 'repair_service_safety_candidate_is_truth', 'review_seed_is_review_decision', 'rights_clearance_claimed', 'source_cache_candidate_is_accepted_source', 'source_cache_preview_is_accepted_source', 'standards_conformance_verified', 'standards_specification_candidate_is_truth', 'technical_document_identity_candidate_is_truth', 'verified_authenticity_claimed', 'verified_availability_claimed'])
FORBIDDEN_PRODUCT_TRUE_KEYS = set(['api_calls_made', 'browser_automation_used', 'bypass_or_automation_used', 'catalog_fetch_used', 'changed_public_search_behavior', 'crawling_used', 'datasheet_download_used', 'document_download_used', 'document_fetch_used', 'enabled_accounts', 'enabled_crawling', 'enabled_downloads', 'enabled_extraction', 'enabled_hosting', 'enabled_live_probes', 'enabled_source_sync', 'enabled_telemetry', 'enabled_uploads', 'full_text_fetch_used', 'iiif_fetch_used', 'manual_download_used', 'media_download_used', 'mutated_master_index', 'mutated_public_index', 'network_calls_made', 'ocr_extraction_used', 'pdf_download_used', 'restricted_source_access_used', 'scan_download_used', 'schematic_download_used', 'scraping_used', 'service_manual_download_used', 'standards_document_download_used'])


def load_h8_manuals_docs_live_probe_policy_bundle(root: str | Path | None = None) -> dict[str, Any]:
    base = Path(root) if root is not None else Path(__file__).resolve().parents[5]
    return {key: json.loads((base / rel).read_text(encoding="utf-8")) for key, rel in POLICY_PATHS.items()}


def build_h8_manuals_docs_live_probe_request(source_id: str, request_key: str, policy_bundle: Mapping[str, Any], live_requested: bool = False) -> dict[str, Any]:
    if source_id not in SOURCE_CONFIGS:
        raise ValueError(f"unknown H8 source_id: {source_id}")
    cfg = SOURCE_CONFIGS[source_id]
    request = {
        "schema_version": "h8_manuals_docs_live_probe_request.v0",
        "live_probe_request_id": f"h8.live_probe_request.{source_id}.{_slug(request_key)}.v0",
        "source_id": source_id,
        "connector_family": cfg["connector_family"],
        "source_record_kind": cfg["source_record_kind"],
        "operation_scope": "metadata_only",
        "endpoint_or_metadata_class": cfg["endpoint_or_metadata_class"],
        "request_shape": {"request_key": request_key, "identifier_shape": "single_committed_metadata_identifier_future", "arbitrary_url_allowed": False},
        "approved_request_key": request_key,
        "document_or_catalog_identifier": f"metadata-only-candidate:{source_id}:{request_key}",
        "product_or_device_context": "candidate_metadata_context_only",
        "standards_or_spec_context": "candidate_metadata_context_only",
        "manufacturer_or_vendor_context": cfg["label"],
        "approval_refs": [POLICY_PATHS["allowed_requests"]],
        "policy_refs": list(POLICY_PATHS.values()),
        "live_requested": bool(live_requested),
        "dry_run_only": not bool(live_requested),
        "api_query_requested": False,
        "catalog_fetch_requested": False,
        "document_download_requested": False,
        "pdf_download_requested": False,
        "scan_download_requested": False,
        "full_text_fetch_requested": False,
        "ocr_extraction_requested": False,
        "iiif_manifest_fetch_requested": False,
        "standards_document_fetch_requested": False,
        "datasheet_download_requested": False,
        "schematic_download_requested": False,
        "service_manual_download_requested": False,
        "media_download_requested": False,
        "scraping_or_crawling_requested": False,
        "restricted_source_requested": False,
        "bypass_or_automation_requested": False,
        "output_policy_ref": POLICY_PATHS["output_policy"],
        "review_policy_ref": POLICY_PATHS["review_policy"],
        "truth_policy_ref": POLICY_PATHS["truth_policy"],
        "limitations": ["Request envelope is fail-closed unless committed source policy approves the exact metadata-only request."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["H8-BUNDLE-03 examples are dry preflight by default and do not call networks."],
    }
    _raise_on_boundary_errors(request, policy_bundle)
    return request


def validate_h8_manuals_docs_live_probe_request(request: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []
    source_id = str(request.get("source_id") or "")
    request_key = str(request.get("approved_request_key") or "")
    if source_id not in SOURCE_CONFIGS:
        reasons.append(f"{source_id or 'missing_source'} is not a known H8 manuals/docs/standards source")
    else:
        cfg = SOURCE_CONFIGS[source_id]
        if request.get("operation_scope") != "metadata_only":
            reasons.append("approved_operation_scope must be metadata_only")
        endpoint = str(request.get("endpoint_or_metadata_class") or "")
        if endpoint != cfg["endpoint_or_metadata_class"]:
            reasons.append("endpoint_or_metadata_class download/fetch class is forbidden or does not match source policy plan")
    if request.get("api_query_requested") is True:
        reasons.append("api_query_requested is not approved without exact committed bounded metadata policy")
    if request.get("catalog_fetch_requested") is True:
        reasons.append("catalog_fetch_requested is not approved without exact committed bounded metadata policy")
    for key in sorted(REQUEST_FORBIDDEN_TRUE_KEYS):
        if request.get(key) is True:
            reasons.append(f"{key} is forbidden for H8-BUNDLE-03 live probes")
    if source_id in SOURCE_CONFIGS:
        reasons.extend(validate_h8_source_approval(source_id, request_key, policy_bundle)["blocked_reasons"])
    reasons = _dedupe(reasons)
    return {"approved": not reasons, "result_status": _status_for_reasons(reasons), "blocked_reasons": reasons}


def validate_h8_source_approval(source_id: str, request_key: str, policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []
    if source_id not in SOURCE_CONFIGS:
        return {"approved": False, "result_status": "blocked_by_policy", "blocked_reasons": [f"{source_id} is not a known H8 source"]}
    cfg = SOURCE_CONFIGS[source_id]
    allowed = _source_policy(source_id, policy_bundle, "allowed_requests")
    if not allowed:
        reasons.append("source is not listed in H8 allowed request policy")
    else:
        if allowed.get("approval_status") != "approved_for_bounded_metadata_probe":
            reasons.append("source approval_status is not approved_for_bounded_metadata_probe")
        if allowed.get("live_access_approved") is not True:
            reasons.append("live_access_approved is missing or false")
        if allowed.get("metadata_probe_approved") is not True:
            reasons.append("metadata_probe_approved is missing or false")
        if allowed.get("approved_operation_scope") != "metadata_only":
            reasons.append("approved_operation_scope is not metadata_only")
        if allowed.get("approved_source_id") != source_id:
            reasons.append("approved_source_id does not match requested source")
        if request_key not in (allowed.get("allowed_request_keys") or []):
            reasons.append("request key is not approved for this source")
        for key in ("source_sync_approved", "document_download_approved", "pdf_download_approved", "scan_download_approved", "full_text_fetch_approved", "ocr_extraction_approved", "standards_document_fetch_approved", "datasheet_download_approved", "schematic_download_approved", "service_manual_download_approved", "media_download_approved", "scraping_approved", "crawling_approved", "browser_automation_approved", "restricted_rights_sensitive_source_approved", "bypass_or_access_control_automation_approved", "public_query_fanout_approved"):
            if allowed.get(key) is not False:
                reasons.append(f"{key} must remain false")
    endpoint = _source_policy(source_id, policy_bundle, "endpoint_policy")
    if cfg["endpoint_or_metadata_class"] not in (endpoint.get("allowlisted_endpoint_or_metadata_classes_current") or []):
        reasons.append("endpoint/metadata class is not allowlisted for current live access")
    rate = _source_policy(source_id, policy_bundle, "rate_limit_policy")
    if rate.get("decision_status") != "approved_for_bounded_metadata_probe":
        reasons.append("rate limit policy is not approved")
    if int(rate.get("max_requests_per_run") or 0) < 1:
        reasons.append("request budget is zero or missing")
    if int(rate.get("timeout_seconds") or 0) <= 0:
        reasons.append("timeout_seconds is missing")
    if not isinstance(rate.get("retry_policy"), Mapping):
        reasons.append("retry policy is missing")
    if not str(rate.get("user_agent_contact_posture") or "").startswith("approved"):
        reasons.append("User-Agent/contact posture is not approved")
    if not str(rate.get("auth_posture") or "").startswith("approved"):
        reasons.append("auth/no-auth posture is not approved")
    cache = _source_policy(source_id, policy_bundle, "cache_policy")
    if cache.get("decision_status") != "approved_for_bounded_metadata_probe" and cache.get("no_cache_decision") != "approved":
        reasons.append("cache TTL/no-cache decision is not approved")
    kill = _source_policy(source_id, policy_bundle, "kill_switch_policy")
    if kill.get("default_enabled") is not True or kill.get("live_probe_kill_switch_engaged") is not False:
        reasons.append("kill switch defaults fail-closed or is engaged")
    reasons = _dedupe(reasons)
    return {"approved": not reasons, "result_status": _status_for_reasons(reasons), "blocked_reasons": reasons}


def build_h8_manuals_docs_live_probe_blocked_result(request: Mapping[str, Any], reason: str | list[str], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    source_id = str(request.get("source_id") or "unknown")
    cfg = SOURCE_CONFIGS.get(source_id, {"connector_family": request.get("connector_family", "unknown"), "source_record_kind": request.get("source_record_kind", "unknown"), "endpoint_or_metadata_class": request.get("endpoint_or_metadata_class", "unknown")})
    reasons = reason if isinstance(reason, list) else [str(reason)]
    status = _status_for_reasons(reasons)
    result: dict[str, Any] = {
        "schema_version": "h8_manuals_docs_live_probe_result.v0",
        "live_probe_result_id": f"h8.live_probe_result.{source_id}.blocked.{_short_fingerprint(request)}.v0",
        "live_probe_request_ref": request.get("live_probe_request_id"),
        "source_id": source_id,
        "connector_family": cfg.get("connector_family"),
        "source_record_kind": cfg.get("source_record_kind"),
        "result_status": status,
        "request_count": 0,
        "network_used": False,
        "endpoint_or_metadata_used": request.get("endpoint_or_metadata_class") or cfg.get("endpoint_or_metadata_class"),
        "response_status_code": None,
        "response_fingerprint": None,
        "response_summary": "blocked before network; no source call performed",
        "normalized_record": _blocked_candidate(),
        "technical_document_identity_candidate": _blocked_candidate(),
        "manual_artifact_relation_candidate": _blocked_candidate(),
        "datasheet_device_identity_candidate": _blocked_candidate(),
        "standards_specification_identity_candidate": _blocked_candidate(),
        "install_requirement_claim_candidate": _blocked_candidate(),
        "repair_service_safety_candidate": _blocked_candidate(),
        "access_rights_candidate": _blocked_candidate(),
        "source_cache_candidate_preview": _blocked_candidate(),
        "evidence_candidate_preview": _blocked_candidate(),
        "review_queue_seed_preview": _blocked_review_seed(source_id, status, reasons),
        "blocked_reason": reasons[0] if reasons else None,
        "blocked_reasons": reasons,
        "warnings": [],
        "limitations": ["Blocked result: no network call, no download, no extraction, no scrape/crawl, no restricted-source access, and no truth acceptance."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["H8 live probe failed closed."],
    }
    result["connector_health_summary"] = build_h8_connector_health_summary(result, policy_bundle)
    _raise_on_boundary_errors(result, policy_bundle)
    return result


def build_h8_manuals_docs_live_probe_result(source_id: str, response_payload: Mapping[str, Any], response_metadata: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    if source_id not in SOURCE_CONFIGS:
        raise ValueError(f"unknown H8 source_id: {source_id}")
    cfg = SOURCE_CONFIGS[source_id]
    payload = _metadata_payload_defaults(source_id, response_payload)
    fixture = _fixture_from_payload(source_id, payload)
    normalized = normalize_h8_manuals_docs_fixture(fixture, source_id)
    network_used = bool(response_metadata.get("network_used"))
    result: dict[str, Any] = {
        "schema_version": "h8_manuals_docs_live_probe_result.v0",
        "live_probe_result_id": f"h8.live_probe_result.{source_id}.{_short_fingerprint(payload)}.v0",
        "live_probe_request_ref": response_metadata.get("live_probe_request_ref"),
        "source_id": source_id,
        "connector_family": cfg["connector_family"],
        "source_record_kind": cfg["source_record_kind"],
        "result_status": "live_probe_completed" if network_used else "dry_run_preflight_pass",
        "request_count": int(response_metadata.get("request_count") or (1 if network_used else 0)),
        "network_used": network_used,
        "endpoint_or_metadata_used": cfg["endpoint_or_metadata_class"],
        "response_status_code": response_metadata.get("response_status_code") if network_used else "not_called_dry_run",
        "response_fingerprint": _fingerprint(payload),
        "response_summary": "bounded metadata response normalized as candidate-only preview" if network_used else "fixture-equivalent metadata preview normalized without network",
        "normalized_record": normalized,
        "technical_document_identity_candidate": _fixture_document_candidate(normalized),
        "manual_artifact_relation_candidate": _fixture_relation_candidates(normalized),
        "datasheet_device_identity_candidate": _fixture_datasheet_candidate(normalized),
        "standards_specification_identity_candidate": _fixture_standard_candidate(normalized),
        "install_requirement_claim_candidate": _fixture_install_candidates(normalized),
        "repair_service_safety_candidate": _fixture_repair_candidates(normalized),
        "access_rights_candidate": _fixture_access_candidate(normalized),
        "source_cache_candidate_preview": _fixture_source_cache_preview(normalized),
        "evidence_candidate_preview": _fixture_evidence_preview(normalized),
        "blocked_reason": None,
        "blocked_reasons": [],
        "warnings": list(response_metadata.get("warnings") or []),
        "limitations": ["Live-probe result is candidate-only metadata; it does not accept truth or authorize downloads/extraction/actions."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["Output bundle remains preview-only until separate review accepts it."],
    }
    result["review_queue_seed_preview"] = build_h8_review_queue_seed_preview_from_probe(result, result["source_cache_candidate_preview"], result["evidence_candidate_preview"], policy_bundle)
    result["connector_health_summary"] = build_h8_connector_health_summary(result, policy_bundle)
    _raise_on_boundary_errors(result, policy_bundle)
    return result


def normalize_h8_manuals_docs_live_probe_result(result: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    normalized = result.get("normalized_record")
    if not isinstance(normalized, Mapping):
        raise ValueError("live probe result does not contain a normalized record")
    return dict(normalized)


def build_h8_technical_document_identity_candidate_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return _fixture_document_candidate(normalized_record)


def build_h8_manual_artifact_relation_candidate_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> list[dict[str, Any]]:
    return _fixture_relation_candidates(normalized_record)


def build_h8_datasheet_device_identity_candidate_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return _fixture_datasheet_candidate(normalized_record)


def build_h8_standards_specification_identity_candidate_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return _fixture_standard_candidate(normalized_record)


def build_h8_install_requirement_claim_candidate_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> list[dict[str, Any]]:
    return _fixture_install_candidates(normalized_record)


def build_h8_repair_service_safety_candidate_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> list[dict[str, Any]]:
    return _fixture_repair_candidates(normalized_record)


def build_h8_access_rights_candidate_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return _fixture_access_candidate(normalized_record)


def build_h8_source_cache_candidate_preview_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return _fixture_source_cache_preview(normalized_record)


def build_h8_evidence_candidate_preview_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return _fixture_evidence_preview(normalized_record)


def build_h8_review_queue_seed_preview_from_probe(result: Mapping[str, Any], source_cache_preview: Mapping[str, Any], evidence_preview: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    source_id = str(result.get("source_id") or "unknown")
    seed = {
        "schema_version": "h8_manuals_docs_live_probe_review_seed.v0",
        "review_queue_seed_preview_id": f"h8.review_seed_preview.{source_id}.{_short_fingerprint(result)}.v0",
        "source_id": source_id,
        "live_probe_result_ref": result.get("live_probe_result_id"),
        "source_cache_candidate_preview_ref": source_cache_preview.get("source_cache_candidate_preview_id") if isinstance(source_cache_preview, Mapping) else None,
        "evidence_candidate_preview_ref": evidence_preview.get("evidence_candidate_preview_id") if isinstance(evidence_preview, Mapping) else None,
        "preview_only": True,
        "review_seed_is_review_decision": False,
        "review_queue_write_allowed_current": False,
        "required_review": "human_or_future_policy_review_required_before_any_acceptance",
        "limitations": ["Review queue seed preview only; no review queue mutation or review decision."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
    }
    _raise_on_boundary_errors(seed, policy_bundle)
    return seed


def build_h8_connector_health_summary(result: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    source_id = str(result.get("source_id") or "unknown")
    cfg = SOURCE_CONFIGS.get(source_id, {})
    health = {
        "schema_version": "h8_manuals_docs_connector_health_summary.v0",
        "health_summary_id": f"h8.connector_health.{source_id}.{_short_fingerprint(result)}.v0",
        "source_id": source_id,
        "connector_family": str(cfg.get("connector_family") or result.get("connector_family") or "unknown"),
        "live_probe_status": str(result.get("result_status") or "not_evaluable"),
        "request_count": int(result.get("request_count") or 0),
        "response_status_summary": "blocked_before_network" if result.get("network_used") is not True else str(result.get("response_status_code") or "metadata_response_observed"),
        "policy_blockers": list(result.get("blocked_reasons") or []),
        "warnings": list(result.get("warnings") or []),
        "source_limitations": list(result.get("limitations") or []),
        "restricted_source_status": "blocked_current",
        "next_recommended_action": "review_fixture_equivalent_outputs_or_commit_operator_approval_before_live_probe",
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
    }
    _raise_on_boundary_errors(health, policy_bundle)
    return health


def build_h8_manuals_docs_live_probe_output_bundle(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "h8_manuals_docs_live_probe_output_bundle.v0",
        "live_probe_result": dict(result),
        "normalized_record": result.get("normalized_record", {}),
        "technical_document_identity_candidate": result.get("technical_document_identity_candidate", {}),
        "manual_artifact_relation_candidate": result.get("manual_artifact_relation_candidate", []),
        "datasheet_device_identity_candidate": result.get("datasheet_device_identity_candidate", {}),
        "standards_specification_identity_candidate": result.get("standards_specification_identity_candidate", {}),
        "install_requirement_claim_candidate": result.get("install_requirement_claim_candidate", []),
        "repair_service_safety_candidate": result.get("repair_service_safety_candidate", []),
        "access_rights_candidate": result.get("access_rights_candidate", {}),
        "source_cache_candidate_preview": result.get("source_cache_candidate_preview", {}),
        "evidence_candidate_preview": result.get("evidence_candidate_preview", {}),
        "review_queue_seed_preview": result.get("review_queue_seed_preview", {}),
        "connector_health_summary": result.get("connector_health_summary", {}),
        "validation_summary": {
            "truth_boundary_violations": detect_h8_manuals_docs_live_probe_truth_boundary_violations(result, {}),
            "product_boundary_violations": detect_h8_manuals_docs_live_probe_product_boundary_violations(result, {}),
        },
    }


def summarize_h8_manuals_docs_live_probe_result(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "h8_manuals_docs_live_probe_summary.v0",
        "source_id": result.get("source_id"),
        "result_status": result.get("result_status"),
        "request_count": int(result.get("request_count") or 0),
        "network_used": bool(result.get("network_used")),
        "blocked_reasons": list(result.get("blocked_reasons") or []),
        "technical_document_candidate_present": _present(result.get("technical_document_identity_candidate")),
        "manual_artifact_relation_candidate_present": bool(result.get("manual_artifact_relation_candidate")) and not _blocked(result.get("manual_artifact_relation_candidate")),
        "datasheet_device_candidate_present": _present(result.get("datasheet_device_identity_candidate")),
        "standards_specification_candidate_present": _present(result.get("standards_specification_identity_candidate")),
        "install_requirement_candidate_present": bool(result.get("install_requirement_claim_candidate")) and not _blocked(result.get("install_requirement_claim_candidate")),
        "repair_service_safety_candidate_present": bool(result.get("repair_service_safety_candidate")) and not _blocked(result.get("repair_service_safety_candidate")),
        "access_rights_candidate_present": _present(result.get("access_rights_candidate")),
        "source_cache_preview_present": _present(result.get("source_cache_candidate_preview")),
        "evidence_preview_present": _present(result.get("evidence_candidate_preview")),
        "review_seed_present": _present(result.get("review_queue_seed_preview")),
        "connector_health_present": _present(result.get("connector_health_summary")),
    }


def detect_h8_manuals_docs_live_probe_truth_boundary_violations(result: Mapping[str, Any], policy_bundle: Mapping[str, Any] | None = None) -> list[str]:
    return _fixture_truth_violations(result) + _detect_true_keys(result, FORBIDDEN_TRUTH_TRUE_KEYS, "truth")


def detect_h8_manuals_docs_live_probe_product_boundary_violations(result: Mapping[str, Any], policy_bundle: Mapping[str, Any] | None = None) -> list[str]:
    return _fixture_product_violations(result) + _detect_true_keys(result, FORBIDDEN_PRODUCT_TRUE_KEYS, "product")


def _metadata_payload_defaults(source_id: str, response_payload: Mapping[str, Any]) -> dict[str, Any]:
    payload = dict(response_payload)
    cfg = SOURCE_CONFIGS[source_id]
    payload.setdefault("source_record_kind", cfg["source_record_kind"])
    payload.setdefault("source_native_id", f"{source_id}-metadata-candidate")
    payload.setdefault("document_title", f"Synthetic {cfg['label']} record")
    payload.setdefault("document_subtitle", "Metadata-only live-probe preview")
    payload.setdefault("document_type", "technical_document_metadata")
    payload.setdefault("document_number", f"H8-{source_id.upper().replace('_', '-')}-META")
    payload.setdefault("document_revision", "candidate")
    payload.setdefault("edition", "candidate")
    payload.setdefault("publication_date", "2026-05-11")
    payload.setdefault("vendor_or_publisher", cfg["label"])
    payload.setdefault("author_or_editor", ["Eureka Synthetic Metadata Contributor"])
    payload.setdefault("product_or_subject", f"{cfg['label']} subject candidate")
    payload.setdefault("language", "en")
    payload.setdefault("format_or_medium", "metadata_record")
    payload.setdefault("page_count_candidate", "unknown")
    payload.setdefault("catalog_record_id", f"catalog:{source_id}:probe")
    payload.setdefault("collection_id", f"collection:{source_id}")
    payload.setdefault("manufacturer", cfg["label"])
    payload.setdefault("part_number", f"{source_id.upper()}-PART-CANDIDATE")
    payload.setdefault("device_family", f"{source_id} candidate family")
    payload.setdefault("package_type", "unknown")
    payload.setdefault("standards_body", cfg["label"] if cfg["connector_family"] in {"standards_metadata", "restricted_manifest_only"} else "unknown")
    payload.setdefault("standard_number", f"STD-{source_id.upper()}-CANDIDATE" if cfg["connector_family"] in {"standards_metadata", "restricted_manifest_only"} else "unknown")
    payload.setdefault("specification_title", f"{cfg['label']} specification metadata candidate" if cfg["connector_family"] in {"standards_metadata", "restricted_manifest_only"} else "unknown")
    payload.setdefault("version_or_revision", "candidate")
    payload.setdefault("operating_system", "unknown")
    payload.setdefault("architecture", "unknown")
    payload.setdefault("hardware_requirement", "candidate hardware requirement metadata only")
    payload.setdefault("dependency_requirement", "candidate dependency metadata only")
    payload.setdefault("install_step_candidate", "candidate install metadata only; no action authorized")
    payload.setdefault("hazard_note_candidate", "candidate hazard metadata only; not safety guidance")
    payload.setdefault("safety_warning_candidate", "candidate safety warning metadata only; review required")
    payload.setdefault("rights_or_license_metadata", "candidate access metadata only; no rights clearance")
    payload.setdefault("source_locator_candidate", f"metadata-only-candidate:{source_id}")
    payload.setdefault("checksum_metadata_candidate", "unknown")
    payload.setdefault("ocr_or_full_text_availability_candidate", "availability metadata only; no extraction permission")
    payload.setdefault("relations", [{"relation_kind": "manual_for_product", "target_ref": f"artifact:{source_id}:candidate", "confidence_or_uncertainty": "probe_preview_no_relation_truth"}])
    payload.setdefault("access", {"download_permission_current": False, "rights_clearance_claimed": False, "open_access_truth_claimed": False})
    payload.setdefault("source_metadata", {"source_label": cfg["label"], "metadata_only_probe_preview": True})
    payload.setdefault("metadata_summary", f"Metadata-only observation candidate for {cfg['label']}.")
    return payload


def _fixture_from_payload(source_id: str, payload: Mapping[str, Any]) -> dict[str, Any]:
    cfg = SOURCE_CONFIGS[source_id]
    return {
        "schema_version": "h8_manuals_docs_fixture.v0",
        "fixture_id": f"h8.live_probe_fixture_equivalent.{source_id}.{_slug(str(payload.get('source_native_id') or 'metadata'))}.v0",
        "source_id": source_id,
        "connector_family": cfg["connector_family"],
        "fixture_kind": "live_probe_metadata_response_preview",
        "fixture_status": "ready",
        "fixture_public_safe": True,
        "live_call_used": False,
        "network_used": False,
        "external_api_used": False,
        "catalog_payload_included": False,
        "document_payload_included": False,
        "pdf_payload_included": False,
        "scan_payload_included": False,
        "datasheet_payload_included": False,
        "standards_document_payload_included": False,
        "schematic_payload_included": False,
        "service_manual_payload_included": False,
        "full_text_payload_included": False,
        "ocr_payload_included": False,
        "iiif_payload_included": False,
        "media_payload_included": False,
        "scraping_output_included": False,
        "crawling_output_included": False,
        "restricted_source_accessed": False,
        "bypass_or_automation_used": False,
        "fixture_payload": dict(payload),
        "expected_normalized_ref": "live_probe_result.normalized_record",
        "limitations": ["Probe response payload is normalized as candidate-only metadata; no payload download or truth acceptance."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["Internal fixture-equivalent envelope for H8 live-probe normalization."],
    }


def _blocked_review_seed(source_id: str, status: str, reasons: list[str]) -> dict[str, Any]:
    return {
        "schema_version": "h8_manuals_docs_live_probe_review_seed.v0",
        "review_queue_seed_preview_id": f"h8.review_seed_preview.{source_id}.blocked.{_short_fingerprint({'source_id': source_id, 'reasons': reasons})}.v0",
        "source_id": source_id,
        "preview_only": True,
        "review_seed_is_review_decision": False,
        "review_queue_write_allowed_current": False,
        "blocked_status": status,
        "blocked_reasons": reasons,
        "limitations": ["Blocked review seed preview only; no review queue mutation or review decision."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
    }


def _blocked_candidate() -> dict[str, Any]:
    return {"status": "not_created_blocked_by_policy", "truth_boundary": _truth_boundary(), "product_boundary": _product_boundary()}


def _present(value: Any) -> bool:
    return isinstance(value, Mapping) and value.get("status") != "not_created_blocked_by_policy" and bool(value)


def _blocked(value: Any) -> bool:
    return isinstance(value, Mapping) and value.get("status") == "not_created_blocked_by_policy"


def _source_policy(source_id: str, policy_bundle: Mapping[str, Any], bundle_key: str = "allowed_requests") -> dict[str, Any]:
    for item in _mapping(policy_bundle.get(bundle_key)).get("sources", []):
        if isinstance(item, Mapping) and item.get("source_id") == source_id:
            return dict(item)
    return {}


def _status_for_reasons(reasons: list[str]) -> str:
    joined = " ".join(reasons).casefold()
    if not reasons:
        return "dry_run_preflight_pass"
    if "approved" in joined or "approval" in joined or "not approved" in joined:
        return "blocked_by_missing_approval"
    if "kill switch" in joined:
        return "blocked_by_kill_switch"
    if any(word in joined for word in ("download", "pdf", "manual", "datasheet", "standards", "schematic", "service_manual", "payload")):
        return "blocked_by_download_policy"
    if "ocr" in joined or "full_text" in joined or "extract" in joined:
        return "blocked_by_extraction_policy"
    if "endpoint" in joined:
        return "blocked_by_endpoint_policy"
    if "restricted" in joined or "sensitive" in joined or "paywall" in joined:
        return "blocked_by_restricted_source_policy"
    if "bypass" in joined or "automation" in joined or "access control" in joined:
        return "blocked_by_bypass_policy"
    return "blocked_by_policy"


def _raise_on_boundary_errors(value: Mapping[str, Any], policy_bundle: Mapping[str, Any] | None = None) -> None:
    errors = detect_h8_manuals_docs_live_probe_truth_boundary_violations(value, policy_bundle or {})
    errors.extend(detect_h8_manuals_docs_live_probe_product_boundary_violations(value, policy_bundle or {}))
    if errors:
        raise ValueError("; ".join(_dedupe(errors)))


def _truth_boundary() -> dict[str, bool]:
    return {'live_probe_result_is_public_truth': False, 'normalized_record_is_public_truth': False, 'technical_document_identity_candidate_is_truth': False, 'manual_artifact_relation_candidate_is_truth': False, 'datasheet_device_candidate_is_truth': False, 'datasheet_device_identity_candidate_is_truth': False, 'standards_specification_candidate_is_truth': False, 'install_requirement_candidate_is_truth': False, 'install_requirement_candidate_is_installability_truth': False, 'repair_service_safety_candidate_is_truth': False, 'repair_service_safety_candidate_is_safety_truth': False, 'access_metadata_is_rights_truth': False, 'open_access_metadata_is_rights_clearance': False, 'source_cache_candidate_is_accepted_source': False, 'source_cache_preview_is_accepted_source': False, 'evidence_candidate_preview_is_accepted_evidence': False, 'evidence_preview_is_accepted_evidence': False, 'review_seed_is_review_decision': False, 'accepted_source_truth': False, 'accepted_evidence_truth': False, 'accepted_candidate_truth': False, 'accepted_document_truth': False, 'accepted_manual_artifact_relation_truth': False, 'accepted_datasheet_device_truth': False, 'accepted_standards_truth': False, 'accepted_install_requirement_truth': False, 'accepted_repair_service_safety_truth': False, 'accepted_access_rights_truth': False, 'accepted_public_record': False, 'public_index_mutated': False, 'master_index_mutated': False, 'rights_clearance_claimed': False, 'open_access_truth_claimed': False, 'compatibility_correctness_claimed': False, 'installability_claimed': False, 'repair_safety_claimed': False, 'electrical_safety_claimed': False, 'malware_safety_claimed': False, 'verified_authenticity_claimed': False, 'verified_availability_claimed': False, 'production_readiness_claimed': False, 'standards_conformance_verified': False, 'documentation_completeness_claimed': False}.copy()


def _product_boundary() -> dict[str, bool]:
    return {'network_calls_made': False, 'api_calls_made': False, 'catalog_fetch_used': False, 'document_fetch_used': False, 'document_download_used': False, 'pdf_download_used': False, 'scan_download_used': False, 'manual_download_used': False, 'datasheet_download_used': False, 'standards_document_download_used': False, 'schematic_download_used': False, 'service_manual_download_used': False, 'full_text_fetch_used': False, 'ocr_extraction_used': False, 'iiif_fetch_used': False, 'media_download_used': False, 'scraping_used': False, 'crawling_used': False, 'browser_automation_used': False, 'bypass_or_automation_used': False, 'restricted_source_access_used': False, 'changed_public_search_behavior': False, 'enabled_hosting': False, 'enabled_live_probes': False, 'enabled_source_sync': False, 'enabled_downloads': False, 'enabled_extraction': False, 'enabled_crawling': False, 'enabled_uploads': False, 'enabled_accounts': False, 'enabled_telemetry': False, 'mutated_public_index': False, 'mutated_master_index': False}.copy()


def _mapping(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _fingerprint(payload: Mapping[str, Any]) -> str:
    body = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(body).hexdigest()


def _short_fingerprint(payload: Mapping[str, Any]) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode("utf-8")).hexdigest()[:12]


def _slug(value: str) -> str:
    safe = "".join(ch.lower() if ch.isalnum() else "-" for ch in value).strip("-")
    safe = "-".join(part for part in safe.split("-") if part)
    return safe[:64] if safe else hashlib.sha256(value.encode("utf-8")).hexdigest()[:12]


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


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        if item not in seen:
            out.append(item)
            seen.add(item)
    return out
