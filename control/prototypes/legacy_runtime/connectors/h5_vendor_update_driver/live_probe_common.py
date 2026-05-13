"""Fail-closed H5 vendor/update/driver metadata live-probe helpers."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time
from typing import Any, Mapping
import urllib.error
import urllib.request

from control.prototypes.legacy_runtime.connectors.h5_vendor_update_driver.normalizer_common import (
    H5_SOURCE_IDS,
    build_h5_driver_device_compatibility_candidates as _fixture_driver_candidates,
    build_h5_evidence_candidate_preview as _fixture_evidence_preview,
    build_h5_firmware_update_candidates as _fixture_firmware_candidates,
    build_h5_payload_metadata_candidates as _fixture_payload_candidates,
    build_h5_runtime_redistributable_candidates as _fixture_runtime_candidates,
    build_h5_source_cache_candidate_preview as _fixture_source_cache_preview,
    build_h5_vendor_identity_candidate as _fixture_vendor_identity_candidate,
    detect_h5_product_boundary_violations as _fixture_product_violations,
    detect_h5_truth_boundary_violations as _fixture_truth_violations,
    normalize_h5_vendor_update_fixture,
)

POLICY_PATHS = {
    "live_probe_policy": "control/inventory/connectors/h5_vendor_update_live_probe_policy.json",
    "allowed_requests": "control/inventory/connectors/h5_vendor_update_live_probe_allowed_requests.json",
    "endpoint_policy": "control/inventory/connectors/h5_vendor_update_live_probe_endpoint_policy.json",
    "rate_limit_policy": "control/inventory/connectors/h5_vendor_update_live_probe_rate_limit_policy.json",
    "cache_policy": "control/inventory/connectors/h5_vendor_update_live_probe_cache_policy.json",
    "kill_switch_policy": "control/inventory/connectors/h5_vendor_update_live_probe_kill_switch_policy.json",
    "output_policy": "control/inventory/connectors/h5_vendor_update_live_probe_output_policy.json",
    "path_policy": "control/inventory/connectors/h5_vendor_update_live_probe_path_policy.json",
    "review_policy": "control/inventory/connectors/h5_vendor_update_live_probe_review_policy.json",
    "truth_policy": "control/inventory/connectors/h5_vendor_update_live_probe_truth_policy.json",
    "no_download_execute_policy": "control/inventory/connectors/h5_vendor_update_live_probe_no_download_execute_policy.json",
    "no_catalog_sync_policy": "control/inventory/connectors/h5_vendor_update_live_probe_no_catalog_sync_policy.json",
}

SOURCE_CONFIGS = {'acer_support_downloads': {'catalog_kind': 'support_downloads',
                            'connector_family': 'vendor_support_catalog',
                            'endpoint_or_metadata_class': 'support_page_metadata_lookup_future',
                            'has_driver': True,
                            'has_firmware': True,
                            'has_runtime': False,
                            'label': 'Acer support/download metadata',
                            'request_key': 'example_support_metadata',
                            'vendor_name': 'Acer'},
 'amd_driver_downloads': {'catalog_kind': 'driver_downloads',
                          'connector_family': 'driver_catalog',
                          'endpoint_or_metadata_class': 'driver_metadata_lookup_future',
                          'has_driver': True,
                          'has_firmware': False,
                          'has_runtime': False,
                          'label': 'AMD driver/download metadata',
                          'request_key': 'example_driver_metadata',
                          'vendor_name': 'AMD'},
 'apple_software_downloads': {'catalog_kind': 'software_downloads',
                              'connector_family': 'vendor_update_catalog',
                              'endpoint_or_metadata_class': 'software_download_metadata_lookup_future',
                              'has_driver': False,
                              'has_firmware': False,
                              'has_runtime': True,
                              'label': 'Apple software downloads metadata',
                              'request_key': 'example_runtime_metadata',
                              'vendor_name': 'Apple'},
 'apple_software_update_catalog': {'catalog_kind': 'software_update_catalog',
                                   'connector_family': 'vendor_update_catalog',
                                   'endpoint_or_metadata_class': 'update_catalog_metadata_lookup_future',
                                   'has_driver': False,
                                   'has_firmware': True,
                                   'has_runtime': False,
                                   'label': 'Apple software update catalog metadata',
                                   'request_key': 'example_firmware_metadata',
                                   'vendor_name': 'Apple'},
 'asus_support_downloads': {'catalog_kind': 'support_downloads',
                            'connector_family': 'vendor_support_catalog',
                            'endpoint_or_metadata_class': 'support_page_metadata_lookup_future',
                            'has_driver': True,
                            'has_firmware': True,
                            'has_runtime': False,
                            'label': 'ASUS support/download metadata',
                            'request_key': 'example_support_metadata',
                            'vendor_name': 'ASUS'},
 'dell_support_downloads': {'catalog_kind': 'support_downloads',
                            'connector_family': 'vendor_support_catalog',
                            'endpoint_or_metadata_class': 'support_page_metadata_lookup_future',
                            'has_driver': True,
                            'has_firmware': True,
                            'has_runtime': False,
                            'label': 'Dell support/download metadata',
                            'request_key': 'example_support_metadata',
                            'vendor_name': 'Dell'},
 'generic_runtime_redistributable': {'catalog_kind': 'runtime_catalog',
                                     'connector_family': 'runtime_redistributable_catalog',
                                     'endpoint_or_metadata_class': 'runtime_metadata_fixture_future',
                                     'has_driver': False,
                                     'has_firmware': False,
                                     'has_runtime': True,
                                     'label': 'Generic runtime redistributable catalog metadata',
                                     'request_key': 'example_runtime_metadata',
                                     'vendor_name': 'Generic Runtime Vendor'},
 'generic_vendor_driver_firmware': {'catalog_kind': 'vendor_driver_firmware',
                                    'connector_family': 'vendor_support_catalog',
                                    'endpoint_or_metadata_class': 'vendor_metadata_fixture_future',
                                    'has_driver': True,
                                    'has_firmware': True,
                                    'has_runtime': False,
                                    'label': 'Generic vendor driver/firmware portal metadata',
                                    'request_key': 'example_firmware_metadata',
                                    'vendor_name': 'Generic Vendor'},
 'hp_support_downloads': {'catalog_kind': 'support_downloads',
                          'connector_family': 'vendor_support_catalog',
                          'endpoint_or_metadata_class': 'support_page_metadata_lookup_future',
                          'has_driver': True,
                          'has_firmware': True,
                          'has_runtime': False,
                          'label': 'HP support/download metadata',
                          'request_key': 'example_support_metadata',
                          'vendor_name': 'HP'},
 'intel_driver_support': {'catalog_kind': 'driver_support',
                          'connector_family': 'driver_catalog',
                          'endpoint_or_metadata_class': 'support_metadata_lookup_future',
                          'has_driver': True,
                          'has_firmware': True,
                          'has_runtime': False,
                          'label': 'Intel driver/support metadata',
                          'request_key': 'example_driver_metadata',
                          'vendor_name': 'Intel'},
 'lenovo_support_downloads': {'catalog_kind': 'support_downloads',
                              'connector_family': 'vendor_support_catalog',
                              'endpoint_or_metadata_class': 'support_page_metadata_lookup_future',
                              'has_driver': True,
                              'has_firmware': True,
                              'has_runtime': False,
                              'label': 'Lenovo support/download metadata',
                              'request_key': 'example_support_metadata',
                              'vendor_name': 'Lenovo'},
 'microsoft_download_center': {'catalog_kind': 'download_center',
                               'connector_family': 'vendor_update_catalog',
                               'endpoint_or_metadata_class': 'download_page_metadata_lookup_future',
                               'has_driver': False,
                               'has_firmware': False,
                               'has_runtime': True,
                               'label': 'Microsoft Download Center metadata',
                               'request_key': 'example_runtime_metadata',
                               'vendor_name': 'Microsoft'},
 'microsoft_runtime_redistributables': {'catalog_kind': 'runtime_catalog',
                                        'connector_family': 'runtime_redistributable_catalog',
                                        'endpoint_or_metadata_class': 'runtime_metadata_lookup_future',
                                        'has_driver': False,
                                        'has_firmware': False,
                                        'has_runtime': True,
                                        'label': 'Microsoft runtime redistributable metadata',
                                        'request_key': 'example_runtime_metadata',
                                        'vendor_name': 'Microsoft'},
 'microsoft_update_catalog': {'catalog_kind': 'update_catalog',
                              'connector_family': 'vendor_update_catalog',
                              'endpoint_or_metadata_class': 'update_catalog_metadata_lookup_future',
                              'has_driver': True,
                              'has_firmware': True,
                              'has_runtime': False,
                              'label': 'Microsoft Update Catalog metadata',
                              'request_key': 'example_firmware_metadata',
                              'vendor_name': 'Microsoft'},
 'nvidia_driver_downloads': {'catalog_kind': 'driver_downloads',
                             'connector_family': 'driver_catalog',
                             'endpoint_or_metadata_class': 'driver_metadata_lookup_future',
                             'has_driver': True,
                             'has_firmware': False,
                             'has_runtime': False,
                             'label': 'NVIDIA driver/download metadata',
                             'request_key': 'example_driver_metadata',
                             'vendor_name': 'NVIDIA'}}
ENDPOINT_URL_TEMPLATES = {
    source_id: "https://example.invalid/eureka/h5/{source_id}/{request_key}?metadata_class={metadata_class}"
    for source_id in H5_SOURCE_IDS
}

FORBIDDEN_TRUTH_TRUE_KEYS = {'accepted_authenticity_truth',
 'accepted_candidate_truth',
 'accepted_compatibility_truth',
 'accepted_driver_identity_truth',
 'accepted_evidence_truth',
 'accepted_firmware_identity_truth',
 'accepted_public_record',
 'accepted_runtime_identity_truth',
 'accepted_safety_truth',
 'accepted_source_truth',
 'accepted_vendor_truth',
 'compatibility_candidate_is_truth',
 'driver_identity_candidate_is_truth',
 'evidence_candidate_preview_is_accepted_evidence',
 'firmware_identity_candidate_is_truth',
 'live_probe_result_is_public_truth',
 'malware_safety_claimed',
 'master_index_mutated',
 'normalized_record_is_public_truth',
 'payload_hash_candidate_is_malware_safety',
 'production_readiness_claimed',
 'public_index_mutated',
 'review_seed_is_review_decision',
 'rights_clearance_claimed',
 'runtime_identity_candidate_is_truth',
 'signature_metadata_is_authenticity',
 'source_cache_candidate_is_accepted_source',
 'vendor_identity_candidate_is_truth',
 'verified_authenticity_claimed',
 'verified_compatibility_claimed',
 'verified_installability_claimed'}
FORBIDDEN_PRODUCT_TRUE_KEYS = {'changed_public_search_behavior',
 'enabled_accounts',
 'enabled_catalog_sync',
 'enabled_downloads',
 'enabled_execution',
 'enabled_firmware_flashing',
 'enabled_hosting',
 'enabled_installers',
 'enabled_source_sync',
 'enabled_telemetry',
 'enabled_uploads',
 'mutated_master_index',
 'mutated_public_index'}


class H5VendorUpdateLiveProbeBlocked(RuntimeError):
    """Raised when H5 live-probe policy blocks before network use."""

    def __init__(self, result: Mapping[str, Any]):
        super().__init__("H5 vendor/update/driver metadata live probe blocked by committed policy")
        self.result = dict(result)


def load_h5_vendor_update_live_probe_policy_bundle(repo_root: str | Path | None = None) -> dict[str, Any]:
    root = Path(repo_root) if repo_root is not None else Path(__file__).resolve().parents[5]
    bundle: dict[str, Any] = {}
    for key, rel_path in POLICY_PATHS.items():
        with (root / rel_path).open("r", encoding="utf-8") as handle:
            bundle[key] = json.load(handle)
    return bundle


def build_h5_vendor_update_live_probe_request(source_id: str, request_key: str, policy_bundle: Mapping[str, Any], live_requested: bool = False) -> dict[str, Any]:
    source_policy = _source_policy(source_id, policy_bundle)
    request_detail = _request_detail(source_policy, request_key)
    cfg = SOURCE_CONFIGS.get(source_id, {})
    endpoint_class = str(request_detail.get("endpoint_or_metadata_class") or cfg.get("endpoint_or_metadata_class") or "metadata_lookup_future")
    identifier = _mapping(_mapping(request_detail.get("request_shape")).get("identifier") or request_detail.get("identifier_or_query"))
    request = {
        "schema_version": "h5_vendor_update_live_probe_request.v0",
        "live_probe_request_id": f"h5.vendor_update_live_probe_request.{source_id}.{_slug(request_key)}.v0",
        "source_id": source_id,
        "connector_family": str(cfg.get("connector_family") or "vendor_update_driver_firmware"),
        "vendor_name": str(identifier.get("vendor_name") or cfg.get("vendor_name") or "unknown"),
        "operation_scope": "metadata_only",
        "endpoint_or_metadata_class": endpoint_class,
        "request_shape": request_detail.get("request_shape") or {"kind": "bounded_metadata_lookup", "identifier": dict(identifier)},
        "approved_request_key": request_key,
        "product_or_package_identifier": str(identifier.get("product_or_package_identifier") or f"{source_id}-metadata-fixture"),
        "driver_or_update_identifier": str(identifier.get("driver_or_update_identifier") or "metadata-only-driver-or-update-candidate"),
        "device_or_hardware_identifier": str(identifier.get("device_or_hardware_identifier") or "metadata-only-device-candidate"),
        "runtime_or_firmware_identifier": str(identifier.get("runtime_or_firmware_identifier") or "metadata-only-runtime-or-firmware-candidate"),
        "os_or_architecture_context": str(identifier.get("os_or_architecture_context") or "metadata-only-os-architecture-candidate"),
        "approval_refs": ["control/inventory/connectors/h5_vendor_update_live_probe_allowed_requests.json"],
        "policy_refs": list(POLICY_PATHS.values()),
        "live_requested": bool(live_requested),
        "dry_run_only": not bool(live_requested),
        "vendor_catalog_fetch_requested": False,
        "driver_download_requested": False,
        "firmware_download_requested": False,
        "runtime_download_requested": False,
        "installer_download_requested": False,
        "checksum_signature_fetch_requested": False,
        "vendor_tool_invocation_requested": False,
        "firmware_flash_requested": False,
        "install_execute_requested": False,
        "output_policy_ref": POLICY_PATHS["output_policy"],
        "review_policy_ref": POLICY_PATHS["review_policy"],
        "truth_policy_ref": POLICY_PATHS["truth_policy"],
        "product_boundary": _product_boundary(),
        "truth_boundary": _truth_boundary(),
        "limitations": ["Request envelope does not grant live access."],
        "notes": ["H5 vendor/update live probes fail closed unless committed source policy approves this exact metadata request."],
    }
    _raise_on_boundary_errors(request)
    return request


def validate_h5_vendor_update_live_probe_request(request: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []
    source_id = str(request.get("source_id") or "")
    request_key = str(request.get("approved_request_key") or "")
    endpoint_class = str(request.get("endpoint_or_metadata_class") or "")
    if source_id not in H5_SOURCE_IDS:
        reasons.append(f"source is not in H5 allowlist: {source_id}")
        return {"approved": False, "blocked_reasons": reasons, "result_status": "blocked_by_policy"}
    if request.get("operation_scope") != "metadata_only":
        reasons.append("approved_operation_scope must be metadata_only")
    for key in (
        "driver_download_requested",
        "firmware_download_requested",
        "runtime_download_requested",
        "installer_download_requested",
        "vendor_tool_invocation_requested",
        "firmware_flash_requested",
        "install_execute_requested",
    ):
        if request.get(key) is True:
            reasons.append(f"{key} must be false")
    if request.get("vendor_catalog_fetch_requested") is True:
        reasons.append("vendor_catalog_fetch_requested must be false unless exact bounded metadata policy approves it")
    if request.get("checksum_signature_fetch_requested") is True:
        reasons.append("checksum_signature_fetch_requested must be false unless exact fixture-equivalent metadata policy approves it")

    source = _source_policy(source_id, policy_bundle)
    endpoint = _source_policy(source_id, policy_bundle, "endpoint_policy")
    rate = _source_policy(source_id, policy_bundle, "rate_limit_policy")
    cache = _source_policy(source_id, policy_bundle, "cache_policy")
    kill = _source_policy(source_id, policy_bundle, "kill_switch_policy")

    for key in ("live_access_approved", "metadata_probe_approved"):
        if source.get(key) is not True:
            reasons.append(f"allowed_requests.{source_id}.{key} must be true")
    for key in (
        "source_sync_approved",
        "vendor_catalog_fetch_approved",
        "driver_download_approved",
        "firmware_download_approved",
        "runtime_download_approved",
        "installer_download_approved",
        "update_package_download_approved",
        "checksum_fetch_approved",
        "signature_fetch_approved",
        "vendor_tool_invocation_approved",
        "package_manager_invocation_approved",
        "firmware_flash_approved",
        "install_execute_approved",
        "scraping_approved",
        "crawling_approved",
        "public_query_fanout_approved",
    ):
        if source.get(key) is not False:
            reasons.append(f"allowed_requests.{source_id}.{key} must be false")
    if source.get("approved_operation_scope") != "metadata_only":
        reasons.append("approved_operation_scope must be metadata_only")
    if source.get("approved_source_id") != source_id:
        reasons.append("approved_source_id must match requested source")
    if request_key not in list(source.get("allowed_request_keys") or []):
        reasons.append(f"request key is not approved for live use: {request_key}")
    if request_key not in _mapping(source.get("requests")):
        reasons.append(f"request key is not present in request manifest: {request_key}")

    allowlisted = list(endpoint.get("allowlisted_endpoint_or_metadata_classes_current") or [])
    if endpoint_class not in allowlisted:
        reasons.append(f"endpoint/metadata class is not currently allowlisted: {endpoint_class}")
    forbidden_classes = list(endpoint.get("forbidden_endpoint_or_metadata_classes_current") or [])
    forbidden_terms = ("download", "payload", "installer", "firmware_flash", "flash", "sync", "scraping", "crawling")
    if endpoint_class in forbidden_classes or any(term in endpoint_class.casefold() and "metadata" not in endpoint_class.casefold() for term in forbidden_terms):
        reasons.append(f"endpoint/metadata class is forbidden: {endpoint_class}")
    if endpoint.get("catalog_sync_allowed") is not False:
        reasons.append("catalog sync must be disabled in endpoint policy")
    if endpoint.get("download_allowed") is not False:
        reasons.append("downloads must be disabled in endpoint policy")
    if rate.get("decision_status") != "approved_for_bounded_metadata_probe":
        reasons.append("rate limit policy is not approved for bounded metadata probe")
    if int(rate.get("max_requests_per_run") or 0) < 1:
        reasons.append("request budget must allow at least one request")
    if not rate.get("timeout_seconds"):
        reasons.append("timeout_seconds must be set")
    if not isinstance(rate.get("retry_policy"), Mapping):
        reasons.append("retry_policy must be set")
    if "approved" not in str(rate.get("user_agent_contact_posture") or "not_approved"):
        reasons.append("User-Agent/contact posture must be approved or documented")
    if "approved" not in str(rate.get("auth_posture") or "not_approved"):
        reasons.append("auth/no-auth posture must be approved")
    if cache.get("decision_status") != "approved_for_bounded_metadata_probe":
        reasons.append("cache/no-cache decision is not approved")
    if kill.get("decision_status") != "approved_for_bounded_metadata_probe":
        reasons.append("kill switch policy is not approved")
    if kill.get("default_enabled") is not True or kill.get("live_probe_kill_switch_engaged") is True:
        reasons.append("kill switch blocks live probe")
    status = _status_for_reasons(reasons)
    return {"approved": not reasons, "blocked_reasons": reasons, "result_status": status}


def validate_h5_source_approval(source_id: str, request_key: str, policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    request = build_h5_vendor_update_live_probe_request(source_id, request_key, policy_bundle, live_requested=True)
    return validate_h5_vendor_update_live_probe_request(request, policy_bundle)


def build_h5_vendor_update_live_probe_blocked_result(request: Mapping[str, Any], reason: str | list[str], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    reasons = [reason] if isinstance(reason, str) else list(reason)
    source_id = str(request.get("source_id") or "unknown")
    cfg = SOURCE_CONFIGS.get(source_id, {})
    status = _status_for_reasons(reasons)
    health = build_h5_connector_health_summary({
        "schema_version": "h5_vendor_update_live_probe_result.v0",
        "source_id": source_id,
        "connector_family": str(cfg.get("connector_family") or request.get("connector_family") or "unknown"),
        "result_status": status,
        "request_count": 0,
        "network_used": False,
        "blocked_reasons": reasons,
        "warnings": [],
        "source_limitations": ["Live probe blocked before network use."],
    }, policy_bundle)
    result = {
        "schema_version": "h5_vendor_update_live_probe_result.v0",
        "live_probe_result_id": f"h5.vendor_update_live_probe_result.{source_id}.blocked.v0",
        "live_probe_request_ref": request.get("live_probe_request_id"),
        "source_id": source_id,
        "connector_family": str(cfg.get("connector_family") or request.get("connector_family") or "unknown"),
        "vendor_name": str(cfg.get("vendor_name") or request.get("vendor_name") or "unknown"),
        "result_status": status,
        "request_count": 0,
        "network_used": False,
        "endpoint_or_metadata_used": request.get("endpoint_or_metadata_class"),
        "response_status_code": None,
        "response_fingerprint": None,
        "response_summary": "No external request was made.",
        "normalized_record": {},
        "vendor_identity_candidate": _blocked_candidate(),
        "driver_device_compatibility_candidate": _blocked_candidate(),
        "firmware_update_candidate": _blocked_candidate(),
        "runtime_redistributable_candidate": _blocked_candidate(),
        "payload_metadata_candidate": _blocked_candidate(),
        "source_cache_candidate_preview": _blocked_candidate(),
        "evidence_candidate_preview": _blocked_candidate(),
        "review_queue_seed_preview": {"status": "not_created_blocked_by_policy", "review_seed_is_review_decision": False, "truth_boundary": _truth_boundary(), "product_boundary": _product_boundary()},
        "connector_health_summary": health,
        "blocked_reason": reasons[0] if reasons else "blocked by policy",
        "blocked_reasons": reasons,
        "warnings": [],
        "limitations": ["Blocked preflight output only; no catalog sync, download, tool invocation, flash, install, or execution occurred."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["Blocked result is candidate/preflight output only."],
    }
    _raise_on_boundary_errors(result)
    return result


def build_h5_vendor_update_live_probe_result(source_id: str, response_payload: Mapping[str, Any], response_metadata: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    cfg = SOURCE_CONFIGS[source_id]
    normalized = normalize_h5_vendor_update_live_probe_result({"source_id": source_id, "response_payload": dict(response_payload), "response_metadata": dict(response_metadata)}, policy_bundle)
    vendor_identity = build_h5_vendor_identity_candidate_from_probe(normalized, policy_bundle)
    driver_candidate = _first(build_h5_driver_device_compatibility_candidate_from_probe(normalized, policy_bundle))
    firmware_candidate = _first(build_h5_firmware_update_candidate_from_probe(normalized, policy_bundle))
    runtime_candidate = _first(build_h5_runtime_redistributable_candidate_from_probe(normalized, policy_bundle))
    payload_candidate = _first(build_h5_payload_metadata_candidate_from_probe(normalized, policy_bundle))
    source_cache = build_h5_source_cache_candidate_preview_from_probe(normalized, policy_bundle)
    evidence = build_h5_evidence_candidate_preview_from_probe(normalized, policy_bundle)
    result_stub = {
        "source_id": source_id,
        "connector_family": cfg["connector_family"],
        "result_status": "live_probe_completed",
        "request_count": int(response_metadata.get("request_count") or 1),
        "network_used": bool(response_metadata.get("network_used", True)),
        "blocked_reasons": [],
        "warnings": [],
    }
    review_seed = build_h5_review_queue_seed_preview_from_probe(result_stub, source_cache, evidence, policy_bundle)
    result = {
        "schema_version": "h5_vendor_update_live_probe_result.v0",
        "live_probe_result_id": f"h5.vendor_update_live_probe_result.{source_id}.{_slug(str(response_metadata.get('request_key') or cfg['request_key']))}.v0",
        "live_probe_request_ref": response_metadata.get("live_probe_request_ref"),
        "source_id": source_id,
        "connector_family": cfg["connector_family"],
        "vendor_name": cfg["vendor_name"],
        "result_status": "live_probe_completed",
        "request_count": int(response_metadata.get("request_count") or 1),
        "network_used": bool(response_metadata.get("network_used", True)),
        "endpoint_or_metadata_used": response_metadata.get("endpoint_or_metadata_used") or cfg["endpoint_or_metadata_class"],
        "response_status_code": response_metadata.get("response_status_code"),
        "response_fingerprint": _fingerprint(response_payload),
        "response_summary": "Bounded metadata response normalized from approved live-probe payload.",
        "normalized_record": normalized,
        "vendor_identity_candidate": vendor_identity,
        "driver_device_compatibility_candidate": driver_candidate,
        "firmware_update_candidate": firmware_candidate,
        "runtime_redistributable_candidate": runtime_candidate,
        "payload_metadata_candidate": payload_candidate,
        "source_cache_candidate_preview": source_cache,
        "evidence_candidate_preview": evidence,
        "review_queue_seed_preview": review_seed,
        "connector_health_summary": build_h5_connector_health_summary(result_stub, policy_bundle),
        "blocked_reason": None,
        "blocked_reasons": [],
        "warnings": [],
        "limitations": ["Live metadata result is not truth, compatibility verification, authenticity verification, safety proof, installability proof, or download permission."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["Network metadata observation remains candidate-only pending review."],
    }
    _raise_on_boundary_errors(result)
    return result


def normalize_h5_vendor_update_live_probe_result(result: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    source_id = str(result.get("source_id") or "")
    payload = _mapping(result.get("response_payload"))
    cfg = SOURCE_CONFIGS[source_id]
    fixture_payload = {
        "vendor_name": payload.get("vendor_name") or cfg["vendor_name"],
        "product_name": payload.get("product_name") or f"{cfg['label']} metadata observation",
        "product_family": payload.get("product_family") or cfg["catalog_kind"],
        "product_line": payload.get("product_line") or "metadata_only",
        "support_page_ref": payload.get("support_page_ref") or "metadata-only-locator-redacted",
        "catalog_record_id": payload.get("catalog_record_id") or f"{source_id}-catalog-candidate",
        "update_record_id": payload.get("update_record_id") or f"{source_id}-update-candidate",
        "download_record_id": payload.get("download_record_id") or "download-blocked-current",
        "vendor_native_id": payload.get("vendor_native_id") or f"{source_id}-live-metadata-candidate",
        "vendor_release_id": payload.get("vendor_release_id") or "release-candidate",
        "vendor_version": payload.get("vendor_version") or "unknown",
        "release_date_candidate": payload.get("release_date_candidate") or "unknown",
        "package_or_payload_name": payload.get("package_or_payload_name") or "metadata-only-payload-candidate",
        "payload_kind": payload.get("payload_kind") or "metadata_only",
        "device_vendor_id": payload.get("device_vendor_id") or "unknown",
        "device_product_id": payload.get("device_product_id") or "unknown",
        "hardware_model": payload.get("hardware_model") or "unknown",
        "hardware_revision": payload.get("hardware_revision") or "unknown",
        "operating_system_family": payload.get("operating_system_family") or "unknown",
        "operating_system_version": payload.get("operating_system_version") or "unknown",
        "architecture": payload.get("architecture") or "unknown",
        "driver_name": payload.get("driver_name") or ("metadata-only-driver-candidate" if cfg.get("has_driver") else "unknown"),
        "driver_version": payload.get("driver_version") or "unknown",
        "driver_class": payload.get("driver_class") or "unknown",
        "chipset_or_component": payload.get("chipset_or_component") or "unknown",
        "firmware_name": payload.get("firmware_name") or ("metadata-only-firmware-candidate" if cfg.get("has_firmware") else "unknown"),
        "firmware_version": payload.get("firmware_version") or "unknown",
        "bios_or_uefi_version": payload.get("bios_or_uefi_version") or "unknown",
        "device_model": payload.get("device_model") or "unknown",
        "board_model": payload.get("board_model") or "unknown",
        "update_package_id": payload.get("update_package_id") or "unknown",
        "update_type": payload.get("update_type") or "metadata_only",
        "runtime_family": payload.get("runtime_family") or ("metadata-only-runtime-candidate" if cfg.get("has_runtime") else "unknown"),
        "runtime_name": payload.get("runtime_name") or ("metadata-only-runtime" if cfg.get("has_runtime") else "unknown"),
        "runtime_version": payload.get("runtime_version") or "unknown",
        "installer_name": payload.get("installer_name") or "installer-download-blocked-current",
        "redistributable_package_id": payload.get("redistributable_package_id") or "unknown",
        "prerequisite_summary": payload.get("prerequisite_summary") or "unknown",
        "compatibility_summary": payload.get("compatibility_summary") or "candidate_only_requires_review",
        "risk_warning_summary": payload.get("risk_warning_summary") or "candidate_only_no_install_or_flash_permission",
        "release_note_or_changelog_refs": payload.get("release_note_or_changelog_refs") or [],
        "advisory_refs": payload.get("advisory_refs") or [],
        "hash_metadata": payload.get("hash_metadata") or {"candidate_only": True, "hash_metadata_proves_malware_safety": False},
        "signature_metadata": payload.get("signature_metadata") or {"candidate_only": True, "signature_metadata_proves_authenticity": False},
        "payload_locator_candidate": payload.get("payload_locator_candidate") or "download-blocked-current",
        "source_metadata": {"live_probe_metadata_only": True, "response_fingerprint": _fingerprint(payload)},
    }
    fixture = {
        "schema_version": "h5_vendor_update_fixture.v0",
        "fixture_id": f"h5.live_probe_synthetic_fixture.{source_id}.v0",
        "source_id": source_id,
        "connector_family": cfg["connector_family"],
        "fixture_kind": "live_probe_metadata_response",
        "fixture_status": "synthetic_probe_response",
        "fixture_public_safe": True,
        "live_call_used": False,
        "network_used": False,
        "external_api_used": False,
        "vendor_catalog_payload_included": False,
        "driver_payload_included": False,
        "firmware_payload_included": False,
        "runtime_payload_included": False,
        "installer_payload_included": False,
        "vendor_tool_output_included": False,
        "package_manager_invoked": False,
        "firmware_flash_invoked": False,
        "installer_or_artifact_executed": False,
        "fixture_payload": fixture_payload,
        "expected_normalized_ref": None,
        "limitations": ["Constructed from bounded live-probe metadata response; not accepted truth."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["Synthetic fixture envelope exists only to reuse fixture normalizer boundaries."],
    }
    return normalize_h5_vendor_update_fixture(fixture, source_id, policy_bundle)


def build_h5_vendor_identity_candidate_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return _fixture_vendor_identity_candidate(normalized_record, policy_bundle)


def build_h5_driver_device_compatibility_candidate_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> list[dict[str, Any]]:
    return _fixture_driver_candidates(normalized_record, policy_bundle)


def build_h5_firmware_update_candidate_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> list[dict[str, Any]]:
    return _fixture_firmware_candidates(normalized_record, policy_bundle)


def build_h5_runtime_redistributable_candidate_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> list[dict[str, Any]]:
    return _fixture_runtime_candidates(normalized_record, policy_bundle)


def build_h5_payload_metadata_candidate_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> list[dict[str, Any]]:
    return _fixture_payload_candidates(normalized_record, policy_bundle)


def build_h5_source_cache_candidate_preview_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return _fixture_source_cache_preview(normalized_record, policy_bundle)


def build_h5_evidence_candidate_preview_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return _fixture_evidence_preview(normalized_record, policy_bundle)


def build_h5_review_queue_seed_preview_from_probe(result: Mapping[str, Any], source_cache_preview: Mapping[str, Any], evidence_preview: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    seed = {
        "schema_version": "h5_vendor_update_live_probe_review_seed.v0",
        "review_seed_id": f"h5.review_seed.{result.get('source_id')}.{_slug(str(result.get('result_status') or 'probe'))}.v0",
        "source_id": result.get("source_id"),
        "seed_status": "preview_only",
        "source_cache_candidate_ref": source_cache_preview.get("source_cache_candidate_id"),
        "evidence_candidate_preview_ref": evidence_preview.get("evidence_candidate_preview_id"),
        "review_required": True,
        "review_seed_is_review_decision": False,
        "accepted_candidate_truth": False,
        "accepted_evidence_truth": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
    }
    _raise_on_boundary_errors(seed)
    return seed


def build_h5_connector_health_summary(result: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    source_id = str(result.get("source_id") or "unknown")
    cfg = SOURCE_CONFIGS.get(source_id, {})
    health = {
        "schema_version": "h5_vendor_update_connector_health_summary.v0",
        "health_summary_id": f"h5.vendor_update_connector_health.{source_id}.{_slug(str(result.get('result_status') or 'unknown'))}.v0",
        "source_id": source_id,
        "connector_family": str(result.get("connector_family") or cfg.get("connector_family") or "unknown"),
        "live_probe_status": str(result.get("result_status") or "not_evaluable"),
        "request_count": int(result.get("request_count") or 0),
        "response_status_summary": "metadata_observed" if result.get("network_used") is True else "no_network_call",
        "policy_blockers": list(result.get("blocked_reasons") or ([] if not result.get("blocked_reason") else [result.get("blocked_reason")])),
        "warnings": list(result.get("warnings") or []),
        "source_limitations": list(result.get("source_limitations") or result.get("limitations") or []),
        "next_recommended_action": "review_fixture_or_probe_output_before_any_promotion",
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
    }
    _raise_on_boundary_errors(health)
    return health


def build_h5_vendor_update_live_probe_output_bundle(result: Mapping[str, Any]) -> dict[str, Any]:
    bundle = {
        "schema_version": "h5_vendor_update_live_probe_output_bundle.v0",
        "bundle_id": f"h5.live_probe_output_bundle.{result.get('source_id')}.{_slug(str(result.get('result_status') or 'unknown'))}.v0",
        "live_probe_result": dict(result),
        "normalized_record": result.get("normalized_record", {}),
        "vendor_identity_candidate": result.get("vendor_identity_candidate", {}),
        "driver_device_compatibility_candidate": result.get("driver_device_compatibility_candidate", {}),
        "firmware_update_candidate": result.get("firmware_update_candidate", {}),
        "runtime_redistributable_candidate": result.get("runtime_redistributable_candidate", {}),
        "payload_metadata_candidate": result.get("payload_metadata_candidate", {}),
        "source_cache_candidate_preview": result.get("source_cache_candidate_preview", {}),
        "evidence_candidate_preview": result.get("evidence_candidate_preview", {}),
        "review_queue_seed_preview": result.get("review_queue_seed_preview", {}),
        "connector_health_summary": result.get("connector_health_summary", {}),
        "validation_summary": {
            "truth_boundary_violations": detect_h5_vendor_update_live_probe_truth_boundary_violations(result, {}),
            "product_boundary_violations": detect_h5_vendor_update_live_probe_product_boundary_violations(result, {}),
        },
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
    }
    _raise_on_boundary_errors(bundle)
    return bundle


def fetch_h5_vendor_update_metadata_once(request: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    validation = validate_h5_vendor_update_live_probe_request(request, policy_bundle)
    if not validation["approved"]:
        raise H5VendorUpdateLiveProbeBlocked(build_h5_vendor_update_live_probe_blocked_result(request, validation["blocked_reasons"], policy_bundle))
    source_id = str(request["source_id"])
    cfg = SOURCE_CONFIGS[source_id]
    url = ENDPOINT_URL_TEMPLATES[source_id].format(source_id=source_id, request_key=request["approved_request_key"], metadata_class=request["endpoint_or_metadata_class"])
    timeout = int(_source_policy(source_id, policy_bundle, "rate_limit_policy").get("timeout_seconds") or 10)
    started = time.time()
    req = urllib.request.Request(url, headers={"User-Agent": "Eureka-H5-Metadata-Probe/0 blocked-by-default"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            body = response.read(16384)
            status = getattr(response, "status", None)
    except urllib.error.URLError as exc:
        payload = {"vendor_name": cfg["vendor_name"], "product_name": cfg["label"], "source_metadata": {"url_error": str(exc)}}
        metadata = {"network_used": True, "request_count": 1, "response_status_code": None, "elapsed_seconds": round(time.time() - started, 3), "request_key": request["approved_request_key"]}
        return payload, metadata
    try:
        payload = json.loads(body.decode("utf-8"))
        if not isinstance(payload, Mapping):
            payload = {"response_summary": str(payload)}
    except Exception:
        payload = {"response_summary": body[:512].decode("utf-8", errors="replace")}
    metadata = {"network_used": True, "request_count": 1, "response_status_code": status, "elapsed_seconds": round(time.time() - started, 3), "request_key": request["approved_request_key"], "endpoint_or_metadata_used": request["endpoint_or_metadata_class"]}
    return dict(payload), metadata


def summarize_h5_vendor_update_live_probe_result(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "source_id": result.get("source_id"),
        "result_status": result.get("result_status"),
        "request_count": int(result.get("request_count") or 0),
        "network_used": bool(result.get("network_used")),
        "blocked_reasons": list(result.get("blocked_reasons") or ([] if not result.get("blocked_reason") else [result.get("blocked_reason")])),
        "vendor_identity_candidate_present": isinstance(result.get("vendor_identity_candidate"), Mapping) and result.get("vendor_identity_candidate", {}).get("status") != "not_created_blocked_by_policy",
        "driver_device_compatibility_candidate_present": isinstance(result.get("driver_device_compatibility_candidate"), Mapping) and result.get("driver_device_compatibility_candidate", {}).get("status") != "not_created_blocked_by_policy",
        "firmware_update_candidate_present": isinstance(result.get("firmware_update_candidate"), Mapping) and result.get("firmware_update_candidate", {}).get("status") != "not_created_blocked_by_policy",
        "runtime_redistributable_candidate_present": isinstance(result.get("runtime_redistributable_candidate"), Mapping) and result.get("runtime_redistributable_candidate", {}).get("status") != "not_created_blocked_by_policy",
        "payload_metadata_candidate_present": isinstance(result.get("payload_metadata_candidate"), Mapping) and result.get("payload_metadata_candidate", {}).get("status") != "not_created_blocked_by_policy",
        "public_index_mutated": False,
        "master_index_mutated": False,
    }


def detect_h5_vendor_update_live_probe_truth_boundary_violations(result: Mapping[str, Any], policy_bundle: Mapping[str, Any] | None = None) -> list[str]:
    return _dedupe(_detect_true_keys(result, FORBIDDEN_TRUTH_TRUE_KEYS, "truth") + _fixture_truth_violations(result))


def detect_h5_vendor_update_live_probe_product_boundary_violations(result: Mapping[str, Any], policy_bundle: Mapping[str, Any] | None = None) -> list[str]:
    return _dedupe(_detect_true_keys(result, FORBIDDEN_PRODUCT_TRUE_KEYS, "product") + _fixture_product_violations(result))


def build_metadata_request(source_id: str, request: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    cfg = SOURCE_CONFIGS[source_id]
    return {
        "source_id": source_id,
        "request_key": request.get("approved_request_key"),
        "endpoint_or_metadata_class": request.get("endpoint_or_metadata_class") or cfg["endpoint_or_metadata_class"],
        "request_shape": request.get("request_shape", {}),
        "url_template": ENDPOINT_URL_TEMPLATES[source_id],
        "download_allowed": False,
        "catalog_sync_allowed": False,
        "metadata_only": True,
    }


def parse_metadata_response(source_id: str, response_payload: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    payload = dict(response_payload)
    payload.setdefault("vendor_name", SOURCE_CONFIGS[source_id]["vendor_name"])
    payload.setdefault("product_name", SOURCE_CONFIGS[source_id]["label"])
    payload.setdefault("vendor_native_id", f"{source_id}-probe-response")
    return payload


def _source_policy(source_id: str, policy_bundle: Mapping[str, Any], bundle_key: str = "allowed_requests") -> dict[str, Any]:
    sources = _mapping(policy_bundle.get(bundle_key)).get("sources", [])
    for item in sources:
        if isinstance(item, Mapping) and item.get("source_id") == source_id:
            return dict(item)
    return {}


def _request_detail(source_policy: Mapping[str, Any], request_key: str) -> dict[str, Any]:
    requests = _mapping(source_policy.get("requests"))
    detail = requests.get(request_key)
    return dict(detail) if isinstance(detail, Mapping) else {}


def _status_for_reasons(reasons: list[str]) -> str:
    joined = " ".join(reasons).casefold()
    if not reasons:
        return "dry_run_preflight_pass"
    if "approved" in joined or "approval" in joined:
        return "blocked_by_missing_approval"
    if "kill switch" in joined:
        return "blocked_by_kill_switch"
    if "endpoint" in joined:
        return "blocked_by_download_policy" if "download" in joined else "blocked_by_endpoint_policy"
    if "catalog" in joined or "sync" in joined:
        return "blocked_by_catalog_sync_policy"
    if "download" in joined or "checksum" in joined or "signature" in joined:
        return "blocked_by_download_policy"
    if "vendor_tool" in joined or "package_manager" in joined:
        return "blocked_by_vendor_tool_policy"
    if "firmware_flash" in joined or "flash" in joined:
        return "blocked_by_firmware_flash_policy"
    if "install" in joined or "execute" in joined:
        return "blocked_by_install_execute_policy"
    return "blocked_by_policy"


def _blocked_candidate() -> dict[str, Any]:
    return {"status": "not_created_blocked_by_policy", "truth_boundary": _truth_boundary(), "product_boundary": _product_boundary()}


def _first(items: list[dict[str, Any]]) -> dict[str, Any]:
    return dict(items[0]) if items else {}


def _fingerprint(payload: Mapping[str, Any]) -> str:
    body = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(body).hexdigest()


def _truth_boundary() -> dict[str, bool]:
    return {'accepted_authenticity_truth': False,
 'accepted_candidate_truth': False,
 'accepted_compatibility_truth': False,
 'accepted_driver_identity_truth': False,
 'accepted_evidence_truth': False,
 'accepted_firmware_identity_truth': False,
 'accepted_public_record': False,
 'accepted_runtime_identity_truth': False,
 'accepted_safety_truth': False,
 'accepted_source_truth': False,
 'accepted_vendor_truth': False,
 'compatibility_candidate_is_truth': False,
 'driver_identity_candidate_is_truth': False,
 'evidence_candidate_preview_is_accepted_evidence': False,
 'firmware_identity_candidate_is_truth': False,
 'live_probe_result_is_public_truth': False,
 'malware_safety_claimed': False,
 'master_index_mutated': False,
 'normalized_record_is_public_truth': False,
 'payload_hash_candidate_is_malware_safety': False,
 'production_readiness_claimed': False,
 'public_index_mutated': False,
 'review_seed_is_review_decision': False,
 'rights_clearance_claimed': False,
 'runtime_identity_candidate_is_truth': False,
 'signature_metadata_is_authenticity': False,
 'source_cache_candidate_is_accepted_source': False,
 'vendor_identity_candidate_is_truth': False,
 'verified_authenticity_claimed': False,
 'verified_compatibility_claimed': False,
 'verified_installability_claimed': False}


def _product_boundary() -> dict[str, bool]:
    return {'changed_public_search_behavior': False,
 'enabled_accounts': False,
 'enabled_catalog_sync': False,
 'enabled_downloads': False,
 'enabled_execution': False,
 'enabled_firmware_flashing': False,
 'enabled_hosting': False,
 'enabled_installers': False,
 'enabled_source_sync': False,
 'enabled_telemetry': False,
 'enabled_uploads': False,
 'mutated_master_index': False,
 'mutated_public_index': False}


def _mapping(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        return {}
    return dict(value)


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


def _raise_on_boundary_errors(record: Mapping[str, Any]) -> None:
    errors = detect_h5_vendor_update_live_probe_truth_boundary_violations(record) + detect_h5_vendor_update_live_probe_product_boundary_violations(record)
    if errors:
        raise ValueError("; ".join(errors))
