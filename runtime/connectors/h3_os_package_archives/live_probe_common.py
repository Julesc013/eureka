"""Fail-closed H3 OS package archive metadata live-probe helpers."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time
from typing import Any, Mapping
import urllib.error
import urllib.request

from runtime.connectors.h3_os_package_archives.normalizer_common import (
    H3_SOURCE_CONFIGS,
    H3_SOURCE_IDS,
    build_h3_dependency_candidates as _fixture_dependency_candidates,
    build_h3_evidence_candidate_preview as _fixture_evidence_preview,
    build_h3_os_package_identity_candidate as _fixture_identity_candidate,
    build_h3_os_platform_compatibility_candidate as _fixture_compatibility_candidate,
    build_h3_package_file_candidates as _fixture_file_candidates,
    build_h3_source_cache_candidate_preview as _fixture_source_cache_preview,
    normalize_h3_os_package_fixture,
)


POLICY_PATHS = {
    "live_probe_policy": "control/inventory/connectors/h3_os_package_live_probe_policy.json",
    "allowed_requests": "control/inventory/connectors/h3_os_package_live_probe_allowed_requests.json",
    "endpoint_policy": "control/inventory/connectors/h3_os_package_live_probe_endpoint_policy.json",
    "rate_limit_policy": "control/inventory/connectors/h3_os_package_live_probe_rate_limit_policy.json",
    "cache_policy": "control/inventory/connectors/h3_os_package_live_probe_cache_policy.json",
    "kill_switch_policy": "control/inventory/connectors/h3_os_package_live_probe_kill_switch_policy.json",
    "output_policy": "control/inventory/connectors/h3_os_package_live_probe_output_policy.json",
    "path_policy": "control/inventory/connectors/h3_os_package_live_probe_path_policy.json",
    "review_policy": "control/inventory/connectors/h3_os_package_live_probe_review_policy.json",
    "truth_policy": "control/inventory/connectors/h3_os_package_live_probe_truth_policy.json",
    "no_download_policy": "control/inventory/connectors/h3_os_package_live_probe_no_download_policy.json",
    "no_index_sync_policy": "control/inventory/connectors/h3_os_package_live_probe_no_index_sync_policy.json",
}

SOURCE_CONFIGS = {
    source_id: {
        "label": source_id.replace("_", " "),
        "connector_family": cfg["connector_family"],
        "ecosystem": cfg["ecosystem"],
        "distribution": cfg["distribution"],
        "distribution_release": cfg["distribution_release"],
        "repository_component": cfg["repository_component"],
        "repository_channel": cfg["repository_channel"],
        "architecture": cfg["architecture"],
        "package_manager_context": cfg["package_manager_context"],
        "endpoint_or_index_class": {
            "debian_snapshot": "package_metadata_lookup_future",
            "ubuntu_old_releases": "package_metadata_lookup_future",
            "arch_linux_archive": "package_metadata_lookup_future",
            "fedora_rpm_metadata": "rpm_metadata_lookup_future",
            "freebsd_packages_ports": "package_metadata_lookup_future",
            "pkgsrc": "port_metadata_lookup_future",
            "homebrew": "formula_metadata_lookup_future",
            "macports": "port_metadata_lookup_future",
            "nixpkgs": "package_metadata_lookup_future",
            "winget": "package_manifest_metadata_lookup_future",
            "chocolatey": "package_metadata_lookup_future",
            "flathub": "app_metadata_lookup_future",
            "snapcraft": "snap_metadata_lookup_future",
        }[source_id],
        "request_key": "example_package_metadata",
        "package_name": f"fixture-{source_id.replace('_', '-')}",
        "version": "1.2.3",
        "identifier": {
            "package": f"fixture-{source_id.replace('_', '-')}",
            "distribution_release": cfg["distribution_release"],
            "architecture": cfg["architecture"],
        },
    }
    for source_id, cfg in H3_SOURCE_CONFIGS.items()
}

ENDPOINT_URL_TEMPLATES = {
    source_id: "https://example.invalid/eureka/h3/{source_id}/{package}?release={distribution_release}&arch={architecture}"
    for source_id in H3_SOURCE_IDS
}

FORBIDDEN_TRUTH_TRUE_KEYS = {
    "accepted_candidate_truth",
    "accepted_compatibility_truth",
    "accepted_evidence",
    "accepted_evidence_truth",
    "accepted_os_compatibility_fact",
    "accepted_os_package_identity",
    "accepted_package_identity_truth",
    "accepted_public_record",
    "accepted_public_truth",
    "accepted_source_truth",
    "architecture_match_proves_runtime_compatibility",
    "compatibility_candidate_is_verified_compatibility",
    "compatibility_correctness_claimed",
    "dependency_candidate_is_correctness_proof",
    "dependency_candidate_proves_correctness",
    "dependency_correctness_claimed",
    "download_allowed_current",
    "evidence_candidate_preview_is_accepted_evidence",
    "evidence_preview_is_accepted_evidence",
    "file_hash_candidate_is_malware_safety",
    "license_metadata_is_rights_clearance",
    "live_probe_can_claim_malware_safety",
    "live_probe_can_claim_rights_clearance",
    "live_probe_can_claim_verified_installability",
    "live_probe_can_mutate_master_index",
    "live_probe_can_mutate_public_index",
    "live_probe_result_is_public_truth",
    "malware_safety_claimed",
    "master_index_mutated",
    "mutated_master_index",
    "mutated_public_index",
    "normalized_record_is_public_truth",
    "os_package_identity_candidate_is_truth",
    "os_platform_compatibility_candidate_is_truth",
    "payload_available_current",
    "public_index_mutated",
    "purl_candidate_is_truth",
    "repository_metadata_is_installability_verification",
    "repository_presence_proves_installability",
    "review_queue_seed_is_review_decision",
    "review_seed_is_review_decision",
    "rights_clearance_claimed",
    "source_cache_candidate_is_accepted_source",
    "source_cache_preview_is_accepted_source",
    "verified_installability_claimed",
}

FORBIDDEN_PRODUCT_TRUE_KEYS = {
    "artifact_download_enabled",
    "changed_public_search_behavior",
    "container_layer_download_enabled",
    "enabled_accounts",
    "enabled_downloads",
    "enabled_execution",
    "enabled_hosting",
    "enabled_installers",
    "enabled_public_query_fanout",
    "enabled_repository_index_sync",
    "enabled_scraping",
    "enabled_source_sync",
    "enabled_telemetry",
    "enabled_uploads",
    "install_execute_enabled",
    "mutated_master_index",
    "mutated_public_index",
    "package_download_enabled",
    "package_manager_invocation_enabled",
    "repository_index_sync_enabled",
    "repository_mirror_enabled",
    "source_archive_download_enabled",
}


class H3OSPackageLiveProbeBlocked(RuntimeError):
    """Raised when H3 live-probe policy blocks before network use."""

    def __init__(self, result: Mapping[str, Any]):
        super().__init__("H3 OS package metadata live probe blocked by committed policy")
        self.result = dict(result)


def load_h3_os_package_live_probe_policy_bundle(repo_root: str | Path | None = None) -> dict[str, Any]:
    root = Path(repo_root) if repo_root is not None else Path(__file__).resolve().parents[3]
    bundle: dict[str, Any] = {}
    for key, rel_path in POLICY_PATHS.items():
        with (root / rel_path).open("r", encoding="utf-8") as handle:
            bundle[key] = json.load(handle)
    return bundle


def build_h3_os_package_live_probe_request(source_id: str, request_key: str, policy_bundle: Mapping[str, Any], live_requested: bool = False) -> dict[str, Any]:
    source_policy = _source_policy(source_id, policy_bundle)
    request_detail = _request_detail(source_policy, request_key)
    cfg = SOURCE_CONFIGS.get(source_id, {})
    endpoint_class = str(request_detail.get("endpoint_or_index_class") or request_detail.get("endpoint_class") or cfg.get("endpoint_or_index_class") or "package_metadata_lookup_future")
    identifier = _mapping(_mapping(request_detail.get("request_shape")).get("identifier") or request_detail.get("identifier_or_query") or cfg.get("identifier"))
    request = {
        "schema_version": "h3_os_package_live_probe_request.v0",
        "live_probe_request_id": f"h3.os_package_live_probe_request.{source_id}.{_slug(request_key)}.v0",
        "source_id": source_id,
        "connector_family": str(cfg.get("connector_family") or H3_SOURCE_CONFIGS.get(source_id, {}).get("connector_family") or "os_package_archive"),
        "ecosystem": str(cfg.get("ecosystem") or "unknown"),
        "distribution": str(cfg.get("distribution") or "unknown"),
        "operation_scope": "metadata_only",
        "endpoint_or_index_class": endpoint_class,
        "request_shape": request_detail.get("request_shape") or {"kind": "bounded_metadata_lookup", "identifier": dict(identifier)},
        "approved_request_key": request_key,
        "package_name_or_identifier": cfg.get("package_name") or identifier.get("package"),
        "version_or_release_identifier": cfg.get("version"),
        "distribution_release_or_channel": cfg.get("distribution_release"),
        "architecture": cfg.get("architecture"),
        "approval_refs": ["control/inventory/connectors/h3_os_package_live_probe_allowed_requests.json"],
        "policy_refs": list(POLICY_PATHS.values()),
        "live_requested": bool(live_requested),
        "dry_run_only": not bool(live_requested),
        "repository_index_fetch_requested": False,
        "package_download_requested": False,
        "package_manager_invocation_requested": False,
        "artifact_download_requested": False,
        "source_archive_download_requested": False,
        "container_layer_download_requested": False,
        "repository_mirror_requested": False,
        "install_execute_requested": False,
        "output_policy_ref": POLICY_PATHS["output_policy"],
        "review_policy_ref": POLICY_PATHS["review_policy"],
        "truth_policy_ref": POLICY_PATHS["truth_policy"],
        "product_boundary": _product_boundary(),
        "truth_boundary": _truth_boundary(),
        "limitations": ["Request envelope does not grant live access."],
        "notes": ["H3 OS package live probes fail closed unless committed source policy approves this exact metadata request."],
    }
    _raise_on_boundary_errors(request)
    return request


def validate_h3_os_package_live_probe_request(request: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []
    source_id = str(request.get("source_id") or "")
    request_key = str(request.get("approved_request_key") or "")
    endpoint_class = str(request.get("endpoint_or_index_class") or "")
    if source_id not in H3_SOURCE_IDS:
        reasons.append(f"source is not in H3 allowlist: {source_id}")
        return {"approved": False, "blocked_reasons": reasons, "result_status": "blocked_by_policy"}
    if request.get("operation_scope") != "metadata_only":
        reasons.append("approved_operation_scope must be metadata_only")
    for key in (
        "package_download_requested",
        "artifact_download_requested",
        "source_archive_download_requested",
        "container_layer_download_requested",
    ):
        if request.get(key) is True:
            reasons.append(f"{key} must be false")
    for key in ("package_manager_invocation_requested", "install_execute_requested"):
        if request.get(key) is True:
            reasons.append(f"{key} must be false")
    for key in ("repository_mirror_requested",):
        if request.get(key) is True:
            reasons.append(f"{key} must be false")

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
        "repository_mirror_approved",
        "package_download_approved",
        "artifact_download_approved",
        "source_archive_download_approved",
        "container_layer_download_approved",
        "package_manager_invocation_approved",
        "install_execute_approved",
        "scraping_approved",
        "crawling_approved",
        "public_query_fanout_approved",
    ):
        if source.get(key) is not False:
            reasons.append(f"allowed_requests.{source_id}.{key} must be false")
    if request.get("repository_index_fetch_requested") is True and source.get("repository_index_fetch_approved") is not True:
        reasons.append("repository index fetch requested but not approved")
    if source.get("approved_operation_scope") != "metadata_only":
        reasons.append("approved_operation_scope must be metadata_only")
    if source.get("approved_source_id") != source_id:
        reasons.append("approved_source_id must match requested source")
    if request_key not in list(source.get("allowed_request_keys") or []):
        reasons.append(f"request key is not approved for live use: {request_key}")
    if request_key not in _mapping(source.get("requests")):
        reasons.append(f"request key is not present in request manifest: {request_key}")

    allowlisted = list(endpoint.get("allowlisted_endpoint_or_index_classes_current") or endpoint.get("allowlisted_endpoint_classes_current") or [])
    if endpoint_class not in allowlisted:
        reasons.append(f"endpoint/index class is not currently allowlisted: {endpoint_class}")
    forbidden_endpoint_classes = list(endpoint.get("forbidden_endpoint_or_index_classes_current") or endpoint.get("forbidden_endpoint_classes_current") or [])
    forbidden_terms = ("download", "payload", "layer_pull", "install", "mirror", "sync", "full_repository_index_fetch")
    if endpoint_class in forbidden_endpoint_classes or any(term in endpoint_class for term in forbidden_terms):
        if "repository_index" in endpoint_class or "mirror" in endpoint_class or "sync" in endpoint_class:
            reasons.append(f"endpoint/index class is forbidden by no-index-sync policy: {endpoint_class}")
        elif "download" in endpoint_class or "payload" in endpoint_class or "layer_pull" in endpoint_class:
            reasons.append(f"endpoint/index class is forbidden by no-download policy: {endpoint_class}")
        else:
            reasons.append(f"endpoint/index class is forbidden: {endpoint_class}")
    for key in ("arbitrary_url_fetch_allowed", "broad_search_allowed", "scraping_allowed", "crawling_allowed", "repository_index_sync_allowed", "repository_mirror_allowed"):
        if endpoint.get(key) is not False:
            reasons.append(f"endpoint_policy.{source_id}.{key} must be false")

    if rate.get("decision_status") not in {"approved_for_bounded_metadata_probe", "approved"}:
        reasons.append("rate_limit_policy decision is not approved")
    if not isinstance(rate.get("timeout_seconds"), (int, float)) or rate.get("timeout_seconds") <= 0:
        reasons.append("timeout_seconds must be set")
    if not isinstance(rate.get("max_requests_per_run"), int) or rate.get("max_requests_per_run") < 1:
        reasons.append("request budget must be set")
    if not isinstance(rate.get("retry_policy"), Mapping):
        reasons.append("retry policy must be set")
    if rate.get("user_agent_contact_posture") not in {"approved", "not_required_documented"}:
        reasons.append("User-Agent/contact posture is not approved or documented as not required")

    if cache.get("decision_status") not in {"approved_for_bounded_metadata_probe", "approved"}:
        reasons.append("cache policy decision is not approved")
    if cache.get("cache_ttl") in {None, "", "not_approved"} and cache.get("no_cache_decision") not in {"approved", "not_required_documented"}:
        reasons.append("cache TTL or no-cache decision must be approved")

    if kill.get("failure_mode") != "fail_closed":
        reasons.append("kill switch failure_mode must be fail_closed")
    if kill.get("default_enabled") is not True:
        reasons.append("kill switch blocks live call")

    if detect_h3_os_package_live_probe_truth_boundary_violations(request, policy_bundle) or detect_h3_os_package_live_probe_product_boundary_violations(request, policy_bundle):
        reasons.append("request has truth/product boundary violations")

    return {"approved": not reasons, "blocked_reasons": reasons, "result_status": _blocked_status(reasons)}


def validate_h3_source_approval(source_id: str, request_key: str, policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    request = build_h3_os_package_live_probe_request(source_id, request_key, policy_bundle, live_requested=True)
    return validate_h3_os_package_live_probe_request(request, policy_bundle)


def build_h3_os_package_live_probe_blocked_result(request: Mapping[str, Any], reason: str | list[str], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    reasons = [reason] if isinstance(reason, str) else list(reason)
    source_id = str(request.get("source_id") or "unknown")
    request_key = str(request.get("approved_request_key") or "not_selected")
    cfg = SOURCE_CONFIGS.get(source_id, {})
    status = _blocked_status(reasons)
    result = {
        "schema_version": "h3_os_package_live_probe_result.v0",
        "live_probe_result_id": f"h3.os_package_live_probe_result.{source_id}.{_slug(request_key)}.blocked.v0",
        "live_probe_request_ref": request.get("live_probe_request_id"),
        "source_id": source_id,
        "connector_family": request.get("connector_family") or cfg.get("connector_family"),
        "ecosystem": request.get("ecosystem") or cfg.get("ecosystem"),
        "distribution": request.get("distribution") or cfg.get("distribution"),
        "result_status": status,
        "request_count": 0,
        "network_used": False,
        "endpoint_or_index_used": None,
        "response_status_code": None,
        "response_fingerprint": None,
        "response_summary": None,
        "normalized_record": None,
        "os_package_identity_candidate": build_not_created_preview("os_package_identity_candidate", source_id, request_key, reasons),
        "os_platform_compatibility_candidate": build_not_created_preview("os_platform_compatibility_candidate", source_id, request_key, reasons),
        "dependency_candidate_preview": [],
        "package_file_candidate_preview": [],
        "source_cache_candidate_preview": build_not_created_preview("source_cache_candidate_preview", source_id, request_key, reasons),
        "evidence_candidate_preview": build_not_created_preview("evidence_candidate_preview", source_id, request_key, reasons),
        "review_queue_seed_preview": build_not_created_preview("review_queue_seed_preview", source_id, request_key, reasons),
        "connector_health_summary": build_h3_connector_health_summary(source_id, status, 0, False, reasons),
        "blocked_reason": "; ".join(reasons),
        "blocked_reasons": reasons,
        "warnings": [],
        "limitations": ["No network call was made.", "Committed policy did not approve this H3 OS package metadata live probe."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["Blocked result is deterministic offline evidence."],
    }
    _raise_on_boundary_errors(result)
    return result


def build_h3_os_package_live_probe_result(source_id: str, response_payload: Mapping[str, Any], response_metadata: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    cfg = SOURCE_CONFIGS[source_id]
    request_key = str(response_metadata.get("request_key") or cfg["request_key"])
    request_ref = str(response_metadata.get("live_probe_request_ref") or f"h3.os_package_live_probe_request.{source_id}.{_slug(request_key)}.v0")
    normalized = _source_normalize_response_payload(source_id, response_payload, policy_bundle)
    identity = build_h3_os_package_identity_candidate_from_probe(normalized, policy_bundle)
    compatibility = build_h3_os_platform_compatibility_candidate_from_probe(normalized, policy_bundle)
    dependencies = build_h3_dependency_candidate_preview_from_probe(normalized, policy_bundle)
    files = build_h3_package_file_candidate_preview_from_probe(normalized, policy_bundle)
    source_cache = build_h3_source_cache_candidate_preview_from_probe(normalized, policy_bundle)
    evidence = build_h3_evidence_candidate_preview_from_probe(normalized, policy_bundle)
    result = {
        "schema_version": "h3_os_package_live_probe_result.v0",
        "live_probe_result_id": f"h3.os_package_live_probe_result.{source_id}.{_short_hash(str(response_metadata) + json.dumps(response_payload, sort_keys=True))}.v0",
        "live_probe_request_ref": request_ref,
        "source_id": source_id,
        "connector_family": cfg["connector_family"],
        "ecosystem": cfg["ecosystem"],
        "distribution": cfg["distribution"],
        "result_status": "live_probe_completed",
        "request_count": int(response_metadata.get("request_count") or 1),
        "network_used": response_metadata.get("network_used") is True,
        "endpoint_or_index_used": response_metadata.get("endpoint_or_index_used") or response_metadata.get("endpoint_used") or cfg["endpoint_or_index_class"],
        "response_status_code": response_metadata.get("status_code"),
        "response_fingerprint": response_metadata.get("response_sha256") or _fingerprint(response_payload),
        "response_summary": {
            "metadata_only": True,
            "repository_index_sync_used": False,
            "package_download_used": False,
            "package_manager_invoked": False,
            "normalized_package": normalized.get("package_name"),
        },
        "normalized_record": normalized,
        "os_package_identity_candidate": identity,
        "os_platform_compatibility_candidate": compatibility,
        "dependency_candidate_preview": dependencies,
        "package_file_candidate_preview": files,
        "source_cache_candidate_preview": source_cache,
        "evidence_candidate_preview": evidence,
        "review_queue_seed_preview": build_h3_review_queue_seed_preview_from_probe({"source_id": source_id, "live_probe_result_id": None}, source_cache, evidence, policy_bundle),
        "connector_health_summary": build_h3_connector_health_summary(source_id, "live_probe_completed", int(response_metadata.get("request_count") or 1), response_metadata.get("network_used") is True, []),
        "blocked_reason": None,
        "blocked_reasons": [],
        "warnings": [],
        "limitations": ["Live metadata observation requires review before any downstream use."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["No repository index sync, package download, package-manager invocation, install, or execution occurred."],
    }
    result["review_queue_seed_preview"]["review_subject_ref"] = result["live_probe_result_id"]
    result["connector_health_summary"]["health_summary_id"] = f"h3.connector_health.{source_id}.live_probe_completed.v0"
    _raise_on_boundary_errors(result)
    return result


def normalize_h3_os_package_live_probe_result(result: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    normalized = result.get("normalized_record")
    if not isinstance(normalized, Mapping):
        raise ValueError("live probe result has no normalized record")
    _raise_on_boundary_errors(normalized)
    return dict(normalized)


def build_h3_os_package_identity_candidate_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    candidate = _fixture_identity_candidate(normalized_record, policy_bundle)
    candidate["schema_version"] = "h3_os_package_live_probe_identity_candidate_preview.v0"
    candidate["mapping_status"] = "live_probe_preview_only"
    candidate["limitations"] = list(candidate.get("limitations") or []) + ["Live-probe identity output is still a candidate only."]
    _raise_on_boundary_errors(candidate)
    return candidate


def build_h3_os_platform_compatibility_candidate_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    candidate = _fixture_compatibility_candidate(normalized_record, policy_bundle)
    candidate["schema_version"] = "h3_os_package_live_probe_compatibility_candidate_preview.v0"
    candidate["mapping_status"] = "live_probe_preview_only"
    candidate["limitations"] = list(candidate.get("limitations") or []) + ["Live-probe compatibility output is not verified compatibility."]
    _raise_on_boundary_errors(candidate)
    return candidate


def build_h3_dependency_candidate_preview_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> list[dict[str, Any]]:
    candidates = _fixture_dependency_candidates(normalized_record, policy_bundle)
    for item in candidates:
        item["schema_version"] = "h3_os_package_live_probe_dependency_candidate_preview.v0"
        item["mapping_status"] = "live_probe_preview_only"
        item["limitations"] = list(item.get("limitations") or []) + ["Live-probe dependency output is not correctness proof."]
        _raise_on_boundary_errors(item)
    return candidates


def build_h3_package_file_candidate_preview_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> list[dict[str, Any]]:
    candidates = _fixture_file_candidates(normalized_record, policy_bundle)
    for item in candidates:
        item["schema_version"] = "h3_os_package_live_probe_file_candidate_preview.v0"
        item["mapping_status"] = "live_probe_preview_only"
        item["download_allowed_current"] = False
        item["payload_available_current"] = False
        item["limitations"] = list(item.get("limitations") or []) + ["Live-probe file metadata is not download permission."]
        _raise_on_boundary_errors(item)
    return candidates


def build_h3_source_cache_candidate_preview_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    preview = _fixture_source_cache_preview(normalized_record, policy_bundle)
    preview["schema_version"] = "h3_os_package_live_probe_source_cache_candidate_preview.v0"
    preview["mapping_status"] = "live_probe_preview_only"
    preview["source_cache_write_enabled"] = False
    preview["accepted_source_truth"] = False
    _raise_on_boundary_errors(preview)
    return preview


def build_h3_evidence_candidate_preview_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    preview = _fixture_evidence_preview(normalized_record, policy_bundle)
    preview["schema_version"] = "h3_os_package_live_probe_evidence_candidate_preview.v0"
    preview["evidence_ledger_write_enabled"] = False
    preview["accepted_evidence"] = False
    _raise_on_boundary_errors(preview)
    return preview


def build_h3_review_queue_seed_preview_from_probe(result: Mapping[str, Any], source_cache_preview: Mapping[str, Any], evidence_preview: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    source_id = str(result.get("source_id") or source_cache_preview.get("source_id") or "unknown")
    seed = {
        "schema_version": "h3_os_package_live_probe_review_queue_seed_preview.v0",
        "seed_id": f"h3.review_seed.{source_id}.{_short_hash(str(result.get('live_probe_result_id') or source_id))}.v0",
        "source_id": source_id,
        "review_subject_type": "h3_os_package_live_probe_result",
        "review_subject_ref": result.get("live_probe_result_id"),
        "review_required": True,
        "review_queue_runtime_mutated": False,
        "review_queue_seed_is_review_decision": False,
        "source_cache_candidate_ref": source_cache_preview.get("candidate_id"),
        "evidence_preview_ref": evidence_preview.get("evidence_preview_id"),
        "required_reviews": {
            "source_cache_persistence": True,
            "evidence_acceptance": True,
            "candidate_acceptance": True,
            "package_identity_acceptance": True,
            "compatibility_fact_acceptance": True,
            "public_index_use": True,
            "master_index": True,
        },
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["Review seed preview only; no review queue runtime write occurred."],
    }
    _raise_on_boundary_errors(seed)
    return seed


def build_h3_connector_health_summary(source_id: str, status: str, request_count: int, network_used: bool, blocked_reasons: list[str]) -> dict[str, Any]:
    health = {
        "schema_version": "h3_os_package_connector_health_summary.v0",
        "health_summary_id": f"h3.connector_health.{source_id}.{_slug(status)}.v0",
        "source_id": source_id,
        "connector_family": SOURCE_CONFIGS.get(source_id, {}).get("connector_family", "os_package_archive"),
        "live_probe_status": status,
        "request_count": request_count,
        "network_used": bool(network_used),
        "response_status_summary": "blocked_before_network" if status.startswith("blocked") else "metadata_probe_observed",
        "policy_blockers": list(blocked_reasons),
        "warnings": [],
        "source_limitations": ["Connector health is not production readiness."],
        "next_recommended_action": "operator_approval_required" if status.startswith("blocked") else "review_live_probe_output",
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["Connector health is operational evidence only, not production readiness."],
    }
    _raise_on_boundary_errors(health)
    return health


def build_not_created_preview(kind: str, source_id: str, request_key: str, blocked_reasons: list[str]) -> dict[str, Any]:
    preview = {
        "schema_version": f"h3_os_package_live_probe_{kind}.not_created.v0",
        "status": "not_created_blocked_by_policy",
        "kind": kind,
        "source_id": source_id,
        "request_key": request_key,
        "blocked_reasons": list(blocked_reasons),
        "accepted_source_truth": False,
        "accepted_evidence": False,
        "review_seed_is_review_decision": False,
        "runtime_mutated": False,
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
    }
    _raise_on_boundary_errors(preview)
    return preview


def build_h3_os_package_live_probe_output_bundle(result: Mapping[str, Any]) -> dict[str, Any]:
    bundle = {
        "schema_version": "h3_os_package_live_probe_output_bundle.v0",
        "output_bundle_id": f"h3.os_package_live_probe_output_bundle.{result.get('source_id', 'unknown')}.{_short_hash(str(result.get('live_probe_result_id')))}.v0",
        "live_probe_result": dict(result),
        "normalized_record": result.get("normalized_record"),
        "os_package_identity_candidate": result.get("os_package_identity_candidate"),
        "os_platform_compatibility_candidate": result.get("os_platform_compatibility_candidate"),
        "dependency_candidate_preview": result.get("dependency_candidate_preview"),
        "package_file_candidate_preview": result.get("package_file_candidate_preview"),
        "source_cache_candidate_preview": result.get("source_cache_candidate_preview"),
        "evidence_candidate_preview": result.get("evidence_candidate_preview"),
        "review_queue_seed_preview": result.get("review_queue_seed_preview"),
        "connector_health_summary": result.get("connector_health_summary"),
        "validation_summary": {
            "status": "pass",
            "network_used": result.get("network_used") is True,
            "request_count": result.get("request_count", 0),
            "repository_index_sync_used": False,
            "package_download_used": False,
            "package_manager_invoked": False,
        },
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["Bundle groups preview outputs only; it imports or accepts nothing."],
    }
    _raise_on_boundary_errors(bundle)
    return bundle


def summarize_h3_os_package_live_probe_result(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "source_id": result.get("source_id"),
        "result_status": result.get("result_status"),
        "request_count": int(result.get("request_count") or 0),
        "network_used": result.get("network_used") is True,
        "blocked_reasons": list(result.get("blocked_reasons") or ([] if not result.get("blocked_reason") else [result.get("blocked_reason")])),
        "identity_candidate_created": isinstance(result.get("os_package_identity_candidate"), Mapping) and result.get("os_package_identity_candidate", {}).get("status") != "not_created_blocked_by_policy",
        "compatibility_candidate_created": isinstance(result.get("os_platform_compatibility_candidate"), Mapping) and result.get("os_platform_compatibility_candidate", {}).get("status") != "not_created_blocked_by_policy",
        "dependency_candidate_count": len(result.get("dependency_candidate_preview", []) or []),
        "file_candidate_count": len(result.get("package_file_candidate_preview", []) or []),
        "source_cache_candidate_created": isinstance(result.get("source_cache_candidate_preview"), Mapping) and result.get("source_cache_candidate_preview", {}).get("status") != "not_created_blocked_by_policy",
        "evidence_candidate_created": isinstance(result.get("evidence_candidate_preview"), Mapping) and result.get("evidence_candidate_preview", {}).get("status") != "not_created_blocked_by_policy",
        "review_seed_created": isinstance(result.get("review_queue_seed_preview"), Mapping) and result.get("review_queue_seed_preview", {}).get("status") != "not_created_blocked_by_policy",
        "repository_index_sync_used": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
    }


def build_request_url_or_metadata_request(source_id: str, request: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    cfg = SOURCE_CONFIGS[source_id]
    request_key = str(request.get("approved_request_key") or cfg["request_key"])
    detail = _request_detail(_source_policy(source_id, policy_bundle), request_key)
    identifier = _mapping(_mapping(detail.get("request_shape")).get("identifier") or detail.get("identifier_or_query") or cfg.get("identifier"))
    url = ENDPOINT_URL_TEMPLATES[source_id]
    values = {"source_id": source_id, **{str(k): str(v) for k, v in identifier.items()}}
    for key, value in values.items():
        url = url.replace("{" + str(key) + "}", _safe_url_component(str(value)))
    return {"method": "GET", "url": url, "endpoint_or_index_class": cfg["endpoint_or_index_class"], "request_key": request_key}


def fetch_h3_os_package_metadata_once(request: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    validation = validate_h3_os_package_live_probe_request(request, policy_bundle)
    if not validation["approved"]:
        raise H3OSPackageLiveProbeBlocked(build_h3_os_package_live_probe_blocked_result(request, validation["blocked_reasons"], policy_bundle))
    source_id = str(request["source_id"])
    metadata_request = build_request_url_or_metadata_request(source_id, request, policy_bundle)
    rate = _source_policy(source_id, policy_bundle, "rate_limit_policy")
    timeout = float(rate.get("timeout_seconds") or 10)
    request_obj = urllib.request.Request(metadata_request["url"], headers={"User-Agent": "Eureka-H3-OS-Package-Metadata-Probe/0 fixture-review"}, method="GET")
    start = time.monotonic()
    try:
        with urllib.request.urlopen(request_obj, timeout=timeout) as response:
            raw = response.read()
            payload = json.loads(raw.decode("utf-8"))
            if not isinstance(payload, dict):
                raise ValueError("H3 live-probe response must be a JSON object")
            return payload, {
                "endpoint_or_index_used": metadata_request["endpoint_or_index_class"],
                "status_code": getattr(response, "status", None),
                "content_type": response.headers.get("Content-Type", ""),
                "duration_ms": round((time.monotonic() - start) * 1000, 3),
                "response_sha256": hashlib.sha256(raw).hexdigest(),
                "fetched_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                "request_count": 1,
                "network_used": True,
                "request_key": request.get("approved_request_key"),
                "live_probe_request_ref": request.get("live_probe_request_id"),
            }
    except urllib.error.URLError as exc:
        raise RuntimeError(f"H3 OS package metadata request failed: {exc}") from exc


def _source_parse_response_payload(source_id: str, response_payload: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    cfg = SOURCE_CONFIGS[source_id]
    payload = dict(response_payload.get("fixture_payload") if isinstance(response_payload.get("fixture_payload"), Mapping) else response_payload)
    package_name = str(payload.get("package_name") or payload.get("name") or payload.get("id") or cfg["package_name"])
    version = str(payload.get("version") or payload.get("latest_version") or cfg["version"])
    native_id = str(payload.get("source_native_id") or payload.get("native_id") or f"{source_id}/{package_name}/{version}/live-probe")
    relations = list(payload.get("relations") or payload.get("dependencies") or [])
    files = list(payload.get("files") or payload.get("distribution_files") or [])
    return {
        "ecosystem": str(payload.get("ecosystem") or cfg["ecosystem"]),
        "distribution": str(payload.get("distribution") or cfg["distribution"]),
        "distribution_release": str(payload.get("distribution_release") or cfg["distribution_release"]),
        "repository_component": str(payload.get("repository_component") or cfg["repository_component"]),
        "repository_channel": str(payload.get("repository_channel") or cfg["repository_channel"]),
        "package_name": package_name,
        "source_package_name": str(payload.get("source_package_name") or f"{package_name}-src"),
        "binary_package_name": str(payload.get("binary_package_name") or package_name),
        "architecture": str(payload.get("architecture") or cfg["architecture"]),
        "version": version,
        "epoch": str(payload.get("epoch") or "0"),
        "release_revision": str(payload.get("release_revision") or "live-probe"),
        "build_id": str(payload.get("build_id") or f"{source_id}-live-probe-build"),
        "source_native_id": native_id,
        "package_locator": str(payload.get("package_locator") or f"live_probe:h3:{source_id}:{_slug(native_id)}"),
        "title": str(payload.get("title") or f"{package_name} {version}"),
        "description_summary": str(payload.get("description_summary") or payload.get("summary") or "metadata-only OS package live-probe response"),
        "project_urls": list(payload.get("project_urls") or []),
        "upstream_urls": list(payload.get("upstream_urls") or []),
        "repository_urls": list(payload.get("repository_urls") or []),
        "license_metadata": payload.get("license_metadata") if isinstance(payload.get("license_metadata"), Mapping) else {"license_claimed": "unknown", "rights_clearance_claimed": False},
        "maintainer_or_packager_metadata": list(payload.get("maintainer_or_packager_metadata") or []),
        "relations": relations,
        "files": files,
        "hash_metadata": payload.get("hash_metadata") if isinstance(payload.get("hash_metadata"), Mapping) else {},
        "changelog_or_news_refs": list(payload.get("changelog_or_news_refs") or []),
        "platform_or_environment_markers": list(payload.get("platform_or_environment_markers") or []),
        "source_metadata": payload.get("source_metadata") if isinstance(payload.get("source_metadata"), Mapping) else {"response_shape": "metadata_only"},
        "limitations": list(payload.get("limitations") or ["live metadata response requires review before downstream use"]),
    }


def _source_normalize_response_payload(source_id: str, response_payload: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    fixture_payload = _source_parse_response_payload(source_id, response_payload, policy_bundle)
    cfg = SOURCE_CONFIGS[source_id]
    fixture = {
        "schema_version": "h3_os_package_fixture.v0",
        "fixture_id": f"h3.live_probe_response.{source_id}.{_slug(fixture_payload['source_native_id'])}.v0",
        "source_id": source_id,
        "connector_family": cfg["connector_family"],
        "fixture_kind": "live_probe_metadata_response",
        "fixture_status": "live_probe_observation",
        "fixture_public_safe": True,
        "live_call_used": False,
        "network_used": False,
        "external_api_used": False,
        "repository_index_payload_included": False,
        "package_payload_included": False,
        "package_manager_invoked": False,
        "fixture_payload": fixture_payload,
        "expected_normalized_ref": None,
        "limitations": ["normalized from bounded H3 OS package metadata live-probe response", "live response is not source truth"],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _fixture_product_boundary(),
        "notes": ["Converted to fixture shape for deterministic H3 normalizer reuse."],
    }
    record = normalize_h3_os_package_fixture(fixture, source_id, policy_bundle)
    record["source_observation_origin"] = "h3_bundle_03_live_probe"
    record["notes"] = ["Normalized from an H3 OS package metadata live-probe result.", "No repository index sync, downloads, package manager invocation, install, or execution occurred."]
    _raise_on_boundary_errors(record)
    return record


def detect_h3_os_package_live_probe_truth_boundary_violations(result: Mapping[str, Any], policy_bundle: Mapping[str, Any] | None = None) -> list[str]:
    return [f"truth boundary violation: {path}=true" for path, key, value in _iter_key_values(result) if key in FORBIDDEN_TRUTH_TRUE_KEYS and value is True]


def detect_h3_os_package_live_probe_product_boundary_violations(result: Mapping[str, Any], policy_bundle: Mapping[str, Any] | None = None) -> list[str]:
    return [f"product boundary violation: {path}=true" for path, key, value in _iter_key_values(result) if key in FORBIDDEN_PRODUCT_TRUE_KEYS and value is True]


def _raise_on_boundary_errors(result: Mapping[str, Any]) -> None:
    errors = detect_h3_os_package_live_probe_truth_boundary_violations(result) + detect_h3_os_package_live_probe_product_boundary_violations(result)
    if errors:
        raise ValueError("; ".join(errors))


def _source_policy(source_id: str, policy_bundle: Mapping[str, Any], bundle_key: str = "allowed_requests") -> Mapping[str, Any]:
    root = _mapping(policy_bundle.get(bundle_key))
    for item in root.get("sources", []):
        if isinstance(item, Mapping) and item.get("source_id") == source_id:
            return item
    return {}


def _request_detail(source_policy: Mapping[str, Any], request_key: str) -> Mapping[str, Any]:
    return _mapping(_mapping(source_policy.get("requests")).get(request_key))


def _blocked_status(reasons: list[str]) -> str:
    joined = " ".join(reasons).lower()
    if "repository index" in joined or "repository_index" in joined or "mirror" in joined or "sync" in joined:
        return "blocked_by_index_sync_policy"
    if "download" in joined or "container_layer" in joined or "source_archive" in joined:
        return "blocked_by_download_policy"
    if "package_manager" in joined or "install_execute" in joined:
        return "blocked_by_package_manager_policy"
    if "approval" in joined or "approved" in joined:
        return "blocked_by_missing_approval"
    if "kill switch" in joined:
        return "blocked_by_kill_switch"
    if "endpoint/index class is forbidden" in joined or "endpoint/index" in joined or "endpoint" in joined:
        return "blocked_by_endpoint_policy"
    return "blocked_by_policy"


def _truth_boundary() -> dict[str, bool]:
    return {
        "live_probe_result_is_public_truth": False,
        "normalized_record_is_public_truth": False,
        "os_package_identity_candidate_is_truth": False,
        "purl_candidate_is_truth": False,
        "os_platform_compatibility_candidate_is_truth": False,
        "compatibility_candidate_is_verified_compatibility": False,
        "dependency_candidate_is_correctness_proof": False,
        "file_hash_candidate_is_malware_safety": False,
        "license_metadata_is_rights_clearance": False,
        "source_cache_candidate_is_accepted_source": False,
        "evidence_candidate_preview_is_accepted_evidence": False,
        "review_seed_is_review_decision": False,
        "live_probe_can_mutate_public_index": False,
        "live_probe_can_mutate_master_index": False,
        "live_probe_can_claim_rights_clearance": False,
        "live_probe_can_claim_malware_safety": False,
        "live_probe_can_claim_verified_installability": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "rights_clearance_claimed": False,
        "malware_safety_claimed": False,
        "verified_installability_claimed": False,
        "dependency_correctness_claimed": False,
        "compatibility_correctness_claimed": False,
    }


def _product_boundary() -> dict[str, bool]:
    return {
        "changed_public_search_behavior": False,
        "enabled_hosting": False,
        "enabled_source_sync": False,
        "enabled_repository_index_sync": False,
        "enabled_downloads": False,
        "enabled_uploads": False,
        "enabled_accounts": False,
        "enabled_telemetry": False,
        "enabled_public_query_fanout": False,
        "enabled_scraping": False,
        "enabled_crawling": False,
        "enabled_installers": False,
        "enabled_execution": False,
        "mutated_public_index": False,
        "mutated_master_index": False,
        "package_download_enabled": False,
        "artifact_download_enabled": False,
        "source_archive_download_enabled": False,
        "container_layer_download_enabled": False,
        "package_manager_invocation_enabled": False,
        "install_execute_enabled": False,
        "repository_index_sync_enabled": False,
        "repository_mirror_enabled": False,
    }


def _fixture_product_boundary() -> dict[str, bool]:
    boundary = _product_boundary()
    boundary.update({
        "network_calls_made": False,
        "api_calls_made": False,
        "downloads_made": False,
        "repository_index_fetch_used": False,
        "package_manager_invoked": False,
        "scraping_made": False,
        "enabled_live_probes": False,
        "enabled_source_connectors": False,
    })
    return boundary


def _fingerprint(payload: Mapping[str, Any]) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()


def _short_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:12]


def _slug(value: str) -> str:
    text = "".join(ch.lower() if ch.isalnum() else "_" for ch in str(value)).strip("_")
    return text[:80] or _short_hash(str(value))


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _safe_url_component(value: str) -> str:
    allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-:/@+")
    if not value or any(ch not in allowed for ch in value):
        raise ValueError("identifier contains characters outside the approved safe URL component set")
    return value


def _iter_key_values(value: Any, prefix: str = ""):
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            path = f"{prefix}.{key_text}" if prefix else key_text
            yield path, key_text, child
            yield from _iter_key_values(child, path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _iter_key_values(child, f"{prefix}[{index}]")
