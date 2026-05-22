"""Fail-closed H4 code/source/release metadata live-probe helpers."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time
from typing import Any, Mapping
import urllib.error
import urllib.request

from archive.prototypes.legacy_runtime.connectors.h4_code_source_release.normalizer_common import (
    H4_SOURCE_CONFIGS,
    H4_SOURCE_IDS,
    build_h4_evidence_candidate_preview as _fixture_evidence_preview,
    build_h4_release_asset_candidates as _fixture_release_asset_candidates,
    build_h4_release_identity_candidate as _fixture_release_identity_candidate,
    build_h4_source_cache_candidate_preview as _fixture_source_cache_preview,
    build_h4_source_identity_candidate as _fixture_source_identity_candidate,
    build_h4_source_to_binary_relation_candidates as _fixture_relation_candidates,
    normalize_h4_code_source_fixture,
)

POLICY_PATHS = {
    "live_probe_policy": "control/inventory/connectors/h4_code_source_live_probe_policy.json",
    "allowed_requests": "control/inventory/connectors/h4_code_source_live_probe_allowed_requests.json",
    "endpoint_policy": "control/inventory/connectors/h4_code_source_live_probe_endpoint_policy.json",
    "rate_limit_policy": "control/inventory/connectors/h4_code_source_live_probe_rate_limit_policy.json",
    "cache_policy": "control/inventory/connectors/h4_code_source_live_probe_cache_policy.json",
    "kill_switch_policy": "control/inventory/connectors/h4_code_source_live_probe_kill_switch_policy.json",
    "output_policy": "control/inventory/connectors/h4_code_source_live_probe_output_policy.json",
    "path_policy": "control/inventory/connectors/h4_code_source_live_probe_path_policy.json",
    "review_policy": "control/inventory/connectors/h4_code_source_live_probe_review_policy.json",
    "truth_policy": "control/inventory/connectors/h4_code_source_live_probe_truth_policy.json",
    "no_clone_download_policy": "control/inventory/connectors/h4_code_source_live_probe_no_clone_download_policy.json",
}

ENDPOINT_CLASSES = {'software_heritage_identity': 'swhid_resolution_metadata_future', 'github_repository': 'repository_metadata_lookup_future', 'github_releases': 'release_metadata_lookup_future', 'gitlab_repository': 'repository_metadata_lookup_future', 'gitlab_releases': 'release_metadata_lookup_future', 'sourceforge': 'project_metadata_lookup_future', 'fosshub': 'project_metadata_lookup_future', 'github_archive_program': 'archive_presence_metadata_lookup_future', 'generic_git_repository': 'repository_metadata_fixture_future', 'generic_release_host': 'release_page_metadata_fixture_future'}
REQUEST_KEYS = {'software_heritage_identity': 'example_swhid_resolution_metadata', 'github_repository': 'example_repository_metadata', 'github_releases': 'example_release_metadata', 'gitlab_repository': 'example_repository_metadata', 'gitlab_releases': 'example_release_metadata', 'sourceforge': 'example_project_metadata', 'fosshub': 'example_project_metadata', 'github_archive_program': 'example_archive_presence_metadata', 'generic_git_repository': 'example_repository_metadata', 'generic_release_host': 'example_release_metadata'}
SOURCE_CONFIGS = {
    source_id: {
        "label": H4_SOURCE_CONFIGS[source_id]["label"],
        "connector_family": H4_SOURCE_CONFIGS[source_id]["connector_family"],
        "source_host": H4_SOURCE_CONFIGS[source_id]["source_host"],
        "owner_or_namespace": H4_SOURCE_CONFIGS[source_id]["owner"],
        "repository_or_project": H4_SOURCE_CONFIGS[source_id]["repository"],
        "project_name": H4_SOURCE_CONFIGS[source_id]["project"],
        "trust_lane": H4_SOURCE_CONFIGS[source_id]["trust_lane"],
        "endpoint_or_metadata_class": ENDPOINT_CLASSES[source_id],
        "request_key": REQUEST_KEYS[source_id],
        "release_or_tag_identifier": "v1.0.0-fixture" if H4_SOURCE_CONFIGS[source_id].get("has_release") else "main-fixture",
        "swhid_or_git_object_identifier": "swh:1:rev:fixture0000000000000000000000000000000000000000" if H4_SOURCE_CONFIGS[source_id].get("has_swhid") else "git:fixture:object:0000001",
    }
    for source_id in H4_SOURCE_IDS
}
ENDPOINT_URL_TEMPLATES = {
    source_id: "https://example.invalid/eureka/h4/{source_id}/{owner_or_namespace}/{repository_or_project}?metadata_class={metadata_class}"
    for source_id in H4_SOURCE_IDS
}

FORBIDDEN_TRUTH_TRUE_KEYS = {
    "accepted_candidate_truth",
    "accepted_evidence_truth",
    "accepted_public_record",
    "accepted_public_truth",
    "accepted_release_identity_truth",
    "accepted_source_identity_truth",
    "accepted_source_to_binary_relation_truth",
    "accepted_source_truth",
    "asset_hash_proves_malware_safety",
    "asset_presence_proves_source_relationship",
    "download_allowed_current",
    "evidence_candidate_preview_is_accepted_evidence",
    "evidence_preview_is_accepted_evidence",
    "git_object_candidate_is_accepted_provenance",
    "git_object_candidate_is_provenance_truth",
    "license_metadata_is_rights_clearance",
    "live_probe_result_is_public_truth",
    "malware_safety_claimed",
    "master_index_mutated",
    "mutated_master_index",
    "mutated_public_index",
    "normalized_record_is_public_truth",
    "payload_available_current",
    "production_readiness_claimed",
    "public_index_mutated",
    "relation_candidate_is_accepted_provenance",
    "release_asset_hash_candidate_is_malware_safety",
    "release_asset_metadata_grants_download_permission",
    "release_identity_candidate_is_accepted_release_truth",
    "release_identity_candidate_is_truth",
    "release_notes_prove_installability",
    "repository_url_proves_official_status",
    "review_queue_seed_is_review_decision",
    "review_seed_is_review_decision",
    "rights_clearance_claimed",
    "sbom_metadata_is_provenance",
    "sbom_signature_metadata_proves_trust",
    "signature_metadata_is_authenticity",
    "signature_metadata_proves_authenticity",
    "source_cache_candidate_is_accepted_source",
    "source_cache_preview_is_accepted_source",
    "source_identity_candidate_is_accepted_identity",
    "source_identity_candidate_is_truth",
    "source_to_binary_relation_candidate_is_provenance_truth",
    "swhid_candidate_is_accepted_object_truth",
    "swhid_candidate_is_object_truth",
    "tag_release_match_proves_build_relation",
    "verified_authenticity_claimed",
    "verified_build_reproducibility_claimed",
    "verified_installability_claimed",
}

FORBIDDEN_PRODUCT_TRUE_KEYS = {
    "build_tool_invocation_enabled",
    "build_tool_invoked",
    "changed_public_search_behavior",
    "enabled_accounts",
    "enabled_crawling",
    "enabled_downloads",
    "enabled_execution",
    "enabled_hosting",
    "enabled_installers",
    "enabled_public_query_fanout",
    "enabled_repository_clone",
    "enabled_scraping",
    "enabled_source_connectors",
    "enabled_source_sync",
    "enabled_telemetry",
    "enabled_uploads",
    "git_command_invocation_enabled",
    "git_command_invoked",
    "install_execute_enabled",
    "install_execute_used",
    "mutated_master_index",
    "mutated_public_index",
    "package_download_enabled",
    "release_asset_download_enabled",
    "release_asset_download_used",
    "repository_clone_enabled",
    "repository_clone_used",
    "source_archive_download_enabled",
    "source_archive_download_used",
    "source_sync_enabled",
}


class H4CodeSourceLiveProbeBlocked(RuntimeError):
    """Raised when H4 live-probe policy blocks before network use."""

    def __init__(self, result: Mapping[str, Any]):
        super().__init__("H4 code/source/release metadata live probe blocked by committed policy")
        self.result = dict(result)


def load_h4_code_source_live_probe_policy_bundle(repo_root: str | Path | None = None) -> dict[str, Any]:
    root = Path(repo_root) if repo_root is not None else Path(__file__).resolve().parents[5]
    bundle: dict[str, Any] = {}
    for key, rel_path in POLICY_PATHS.items():
        with (root / rel_path).open("r", encoding="utf-8") as handle:
            bundle[key] = json.load(handle)
    return bundle


def build_h4_code_source_live_probe_request(source_id: str, request_key: str, policy_bundle: Mapping[str, Any], live_requested: bool = False) -> dict[str, Any]:
    source_policy = _source_policy(source_id, policy_bundle)
    request_detail = _request_detail(source_policy, request_key)
    cfg = SOURCE_CONFIGS.get(source_id, {})
    endpoint_class = str(request_detail.get("endpoint_or_metadata_class") or request_detail.get("metadata_class") or cfg.get("endpoint_or_metadata_class") or "metadata_lookup_future")
    identifier = _mapping(_mapping(request_detail.get("request_shape")).get("identifier") or request_detail.get("identifier_or_query"))
    request = {
        "schema_version": "h4_code_source_live_probe_request.v0",
        "live_probe_request_id": f"h4.code_source_live_probe_request.{source_id}.{_slug(request_key)}.v0",
        "source_id": source_id,
        "connector_family": str(cfg.get("connector_family") or "code_source_release_host"),
        "source_host": str(identifier.get("source_host") or cfg.get("source_host") or "unknown"),
        "operation_scope": "metadata_only",
        "endpoint_or_metadata_class": endpoint_class,
        "request_shape": request_detail.get("request_shape") or {"kind": "bounded_metadata_lookup", "identifier": dict(identifier)},
        "approved_request_key": request_key,
        "owner_or_namespace": str(identifier.get("owner_or_namespace") or cfg.get("owner_or_namespace") or "unknown"),
        "repository_or_project": str(identifier.get("repository_or_project") or cfg.get("repository_or_project") or "unknown"),
        "release_or_tag_identifier": str(identifier.get("release_or_tag_identifier") or cfg.get("release_or_tag_identifier") or "unknown"),
        "swhid_or_git_object_identifier": str(identifier.get("swhid_or_git_object_identifier") or cfg.get("swhid_or_git_object_identifier") or "unknown"),
        "approval_refs": ["control/inventory/connectors/h4_code_source_live_probe_allowed_requests.json"],
        "policy_refs": list(POLICY_PATHS.values()),
        "live_requested": bool(live_requested),
        "dry_run_only": not bool(live_requested),
        "repository_clone_requested": False,
        "source_archive_download_requested": False,
        "release_asset_download_requested": False,
        "git_command_invocation_requested": False,
        "build_tool_invocation_requested": False,
        "output_policy_ref": POLICY_PATHS["output_policy"],
        "review_policy_ref": POLICY_PATHS["review_policy"],
        "truth_policy_ref": POLICY_PATHS["truth_policy"],
        "product_boundary": _product_boundary(),
        "truth_boundary": _truth_boundary(),
        "limitations": ["Request envelope does not grant live access."],
        "notes": ["H4 code/source/release live probes fail closed unless committed source policy approves this exact metadata request."],
    }
    _raise_on_boundary_errors(request)
    return request


def validate_h4_code_source_live_probe_request(request: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []
    source_id = str(request.get("source_id") or "")
    request_key = str(request.get("approved_request_key") or "")
    endpoint_class = str(request.get("endpoint_or_metadata_class") or "")
    if source_id not in H4_SOURCE_IDS:
        reasons.append(f"source is not in H4 allowlist: {source_id}")
        return {"approved": False, "blocked_reasons": reasons, "result_status": "blocked_by_policy"}
    if request.get("operation_scope") != "metadata_only":
        reasons.append("approved_operation_scope must be metadata_only")
    for key in ("repository_clone_requested", "source_archive_download_requested", "release_asset_download_requested", "git_command_invocation_requested", "build_tool_invocation_requested"):
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
        "repository_clone_approved",
        "source_archive_download_approved",
        "release_asset_download_approved",
        "binary_download_approved",
        "package_download_approved",
        "git_command_invocation_approved",
        "build_tool_invocation_approved",
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

    allowlisted = list(endpoint.get("allowlisted_endpoint_or_metadata_classes_current") or endpoint.get("allowlisted_metadata_classes_current") or [])
    if endpoint_class not in allowlisted:
        reasons.append(f"endpoint/metadata class is not currently allowlisted: {endpoint_class}")
    forbidden_classes = list(endpoint.get("forbidden_endpoint_or_metadata_classes_current") or endpoint.get("forbidden_metadata_classes_current") or [])
    forbidden_terms = ("download", "payload", "clone", "git_", "git-", "build", "install", "sync", "scraping", "crawling")
    if endpoint_class in forbidden_classes or any(term in endpoint_class for term in forbidden_terms):
        reasons.append(f"endpoint/metadata class is forbidden: {endpoint_class}")
    for key in ("arbitrary_url_fetch_allowed", "broad_search_allowed", "public_query_fanout_allowed", "repository_clone_allowed", "source_archive_download_allowed", "release_asset_download_allowed", "git_command_invocation_allowed", "build_tool_invocation_allowed", "scraping_allowed", "crawling_allowed"):
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
    if rate.get("auth_posture") not in {"approved_public_no_auth", "approved", "not_required_documented"}:
        reasons.append("auth/no-auth posture is not approved")

    if cache.get("decision_status") not in {"approved_for_bounded_metadata_probe", "approved"}:
        reasons.append("cache policy decision is not approved")
    if cache.get("cache_ttl") in {None, "", "not_approved"} and cache.get("no_cache_decision") not in {"approved", "not_required_documented"}:
        reasons.append("cache TTL or no-cache decision must be approved")

    if kill.get("failure_mode") != "fail_closed":
        reasons.append("kill switch failure_mode must be fail_closed")
    if kill.get("default_enabled") is not True or kill.get("live_probe_kill_switch_engaged") is True:
        reasons.append("kill switch blocks live call")

    if detect_h4_code_source_live_probe_truth_boundary_violations(request, policy_bundle) or detect_h4_code_source_live_probe_product_boundary_violations(request, policy_bundle):
        reasons.append("request has truth/product boundary violations")
    return {"approved": not reasons, "blocked_reasons": reasons, "result_status": _blocked_status(reasons)}


def validate_h4_source_approval(source_id: str, request_key: str, policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    request = build_h4_code_source_live_probe_request(source_id, request_key, policy_bundle, live_requested=True)
    return validate_h4_code_source_live_probe_request(request, policy_bundle)


def build_h4_code_source_live_probe_blocked_result(request: Mapping[str, Any], reason: str | list[str], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    reasons = [reason] if isinstance(reason, str) else list(reason)
    source_id = str(request.get("source_id") or "unknown")
    request_key = str(request.get("approved_request_key") or "not_selected")
    cfg = SOURCE_CONFIGS.get(source_id, {})
    status = _blocked_status(reasons)
    result = {
        "schema_version": "h4_code_source_live_probe_result.v0",
        "live_probe_result_id": f"h4.code_source_live_probe_result.{source_id}.{_slug(request_key)}.blocked.v0",
        "live_probe_request_ref": request.get("live_probe_request_id"),
        "source_id": source_id,
        "connector_family": request.get("connector_family") or cfg.get("connector_family"),
        "source_host": request.get("source_host") or cfg.get("source_host"),
        "result_status": status,
        "request_count": 0,
        "network_used": False,
        "endpoint_or_metadata_used": None,
        "response_status_code": None,
        "response_fingerprint": None,
        "response_summary": None,
        "normalized_record": None,
        "source_identity_candidate": build_not_created_preview("source_identity_candidate", source_id, request_key, reasons),
        "release_identity_candidate": build_not_created_preview("release_identity_candidate", source_id, request_key, reasons),
        "source_to_binary_relation_candidate_preview": [],
        "release_asset_candidate_preview": [],
        "source_cache_candidate_preview": build_not_created_preview("source_cache_candidate_preview", source_id, request_key, reasons),
        "evidence_candidate_preview": build_not_created_preview("evidence_candidate_preview", source_id, request_key, reasons),
        "review_queue_seed_preview": build_not_created_preview("review_queue_seed_preview", source_id, request_key, reasons),
        "connector_health_summary": build_h4_connector_health_summary(source_id, status, 0, False, reasons),
        "blocked_reason": "; ".join(reasons),
        "blocked_reasons": reasons,
        "warnings": [],
        "limitations": ["No network call was made.", "Committed policy did not approve this H4 code/source/release metadata live probe."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["Blocked result is deterministic offline evidence."],
    }
    _raise_on_boundary_errors(result)
    return result


def build_h4_code_source_live_probe_result(source_id: str, response_payload: Mapping[str, Any], response_metadata: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    cfg = SOURCE_CONFIGS[source_id]
    request_key = str(response_metadata.get("request_key") or cfg["request_key"])
    request_ref = str(response_metadata.get("live_probe_request_ref") or f"h4.code_source_live_probe_request.{source_id}.{_slug(request_key)}.v0")
    normalized = _source_normalize_response_payload(source_id, response_payload, policy_bundle)
    source_identity = build_h4_source_identity_candidate_from_probe(normalized, policy_bundle)
    release_identity = build_h4_release_identity_candidate_from_probe(normalized, policy_bundle)
    relations = build_h4_source_to_binary_relation_candidate_from_probe(normalized, policy_bundle)
    assets = build_h4_release_asset_candidate_from_probe(normalized, policy_bundle)
    source_cache = build_h4_source_cache_candidate_preview_from_probe(normalized, policy_bundle)
    evidence = build_h4_evidence_candidate_preview_from_probe(normalized, policy_bundle)
    result_status = str(response_metadata.get("result_status") or "live_probe_completed")
    request_count = int(response_metadata.get("request_count") or (1 if response_metadata.get("network_used") is True else 0))
    result = {
        "schema_version": "h4_code_source_live_probe_result.v0",
        "live_probe_result_id": f"h4.code_source_live_probe_result.{source_id}.{_short_hash(str(response_metadata) + json.dumps(response_payload, sort_keys=True))}.v0",
        "live_probe_request_ref": request_ref,
        "source_id": source_id,
        "connector_family": cfg["connector_family"],
        "source_host": cfg["source_host"],
        "result_status": result_status,
        "request_count": request_count,
        "network_used": response_metadata.get("network_used") is True,
        "endpoint_or_metadata_used": response_metadata.get("endpoint_or_metadata_used") or cfg["endpoint_or_metadata_class"],
        "response_status_code": response_metadata.get("status_code"),
        "response_fingerprint": response_metadata.get("response_sha256") or _fingerprint(response_payload),
        "response_summary": {
            "metadata_only": True,
            "repository_clone_used": False,
            "source_archive_download_used": False,
            "release_asset_download_used": False,
            "git_command_invoked": False,
            "build_tool_invoked": False,
            "normalized_source_native_id": normalized.get("source_native_id"),
        },
        "normalized_record": normalized,
        "source_identity_candidate": source_identity,
        "release_identity_candidate": release_identity,
        "source_to_binary_relation_candidate_preview": relations,
        "release_asset_candidate_preview": assets,
        "source_cache_candidate_preview": source_cache,
        "evidence_candidate_preview": evidence,
        "review_queue_seed_preview": build_h4_review_queue_seed_preview_from_probe({"source_id": source_id, "live_probe_result_id": None}, source_cache, evidence, policy_bundle),
        "connector_health_summary": build_h4_connector_health_summary(source_id, result_status, request_count, response_metadata.get("network_used") is True, []),
        "blocked_reason": None,
        "blocked_reasons": [],
        "warnings": [],
        "limitations": ["Live metadata observation requires review before any downstream use."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["No repository clone, source archive download, release asset download, git command, build command, install, or execution occurred."],
    }
    result["review_queue_seed_preview"]["review_subject_ref"] = result["live_probe_result_id"]
    result["connector_health_summary"]["health_summary_id"] = f"h4.connector_health.{source_id}.{_slug(result_status)}.v0"
    _raise_on_boundary_errors(result)
    return result


def normalize_h4_code_source_live_probe_result(result: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    normalized = result.get("normalized_record")
    if not isinstance(normalized, Mapping):
        raise ValueError("live probe result has no normalized record")
    _raise_on_boundary_errors(normalized)
    return dict(normalized)


def build_h4_source_identity_candidate_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    candidate = _fixture_source_identity_candidate(normalized_record, policy_bundle)
    candidate["schema_version"] = "h4_code_source_live_probe_source_identity_candidate_preview.v0"
    candidate["mapping_status"] = "live_probe_preview_only"
    candidate["limitations"] = list(candidate.get("limitations") or []) + ["Live-probe source identity output is still a candidate only."]
    _raise_on_boundary_errors(candidate)
    return candidate


def build_h4_release_identity_candidate_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    candidate = _fixture_release_identity_candidate(normalized_record, policy_bundle)
    candidate["schema_version"] = "h4_code_source_live_probe_release_identity_candidate_preview.v0"
    candidate["mapping_status"] = "live_probe_preview_only"
    candidate["limitations"] = list(candidate.get("limitations") or []) + ["Live-probe release identity output is not release truth."]
    _raise_on_boundary_errors(candidate)
    return candidate


def build_h4_source_to_binary_relation_candidate_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> list[dict[str, Any]]:
    candidates = _fixture_relation_candidates(normalized_record, policy_bundle)
    for item in candidates:
        item["schema_version"] = "h4_code_source_live_probe_relation_candidate_preview.v0"
        item["mapping_status"] = "live_probe_preview_only"
        item["limitations"] = list(item.get("limitations") or []) + ["Live-probe relation output is not accepted provenance."]
        _raise_on_boundary_errors(item)
    return candidates


def build_h4_release_asset_candidate_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> list[dict[str, Any]]:
    candidates = _fixture_release_asset_candidates({"normalized_record": normalized_record, "release_assets": _release_assets_from_record(normalized_record)}, policy_bundle)
    for item in candidates:
        item["schema_version"] = "h4_code_source_live_probe_release_asset_candidate_preview.v0"
        item["mapping_status"] = "live_probe_preview_only"
        item["download_allowed_current"] = False
        item["payload_available_current"] = False
        item["limitations"] = list(item.get("limitations") or []) + ["Live-probe asset metadata grants no download or safety permission."]
        _raise_on_boundary_errors(item)
    return candidates


def build_h4_source_cache_candidate_preview_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    preview = _fixture_source_cache_preview(normalized_record, policy_bundle)
    preview["schema_version"] = "h4_code_source_live_probe_source_cache_candidate_preview.v0"
    preview["mapping_status"] = "live_probe_preview_only"
    preview["source_cache_write_enabled"] = False
    preview["accepted_source_truth"] = False
    _raise_on_boundary_errors(preview)
    return preview


def build_h4_evidence_candidate_preview_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    preview = _fixture_evidence_preview(normalized_record, policy_bundle)
    preview["schema_version"] = "h4_code_source_live_probe_evidence_candidate_preview.v0"
    preview["evidence_ledger_write_enabled"] = False
    preview["accepted_evidence"] = False
    _raise_on_boundary_errors(preview)
    return preview


def build_h4_review_queue_seed_preview_from_probe(result: Mapping[str, Any], source_cache_preview: Mapping[str, Any], evidence_preview: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    source_id = str(result.get("source_id") or source_cache_preview.get("source_id") or "unknown")
    seed = {
        "schema_version": "h4_code_source_live_probe_review_queue_seed_preview.v0",
        "seed_id": f"h4.review_seed.{source_id}.{_short_hash(str(result.get('live_probe_result_id') or source_id))}.v0",
        "source_id": source_id,
        "review_subject_type": "h4_code_source_live_probe_result",
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
            "source_identity_acceptance": True,
            "release_identity_acceptance": True,
            "source_to_binary_relation_acceptance": True,
            "public_index_use": True,
            "master_index": True,
        },
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["Review seed preview only; no review queue runtime write occurred."],
    }
    _raise_on_boundary_errors(seed)
    return seed


def build_h4_connector_health_summary(source_id: str, status: str, request_count: int, network_used: bool, blocked_reasons: list[str]) -> dict[str, Any]:
    health = {
        "schema_version": "h4_code_source_connector_health_summary.v0",
        "health_summary_id": f"h4.connector_health.{source_id}.{_slug(status)}.v0",
        "source_id": source_id,
        "connector_family": SOURCE_CONFIGS.get(source_id, {}).get("connector_family", "code_source_release_host"),
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
        "schema_version": f"h4_code_source_live_probe_{kind}.not_created.v0",
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


def build_h4_code_source_live_probe_output_bundle(result: Mapping[str, Any]) -> dict[str, Any]:
    bundle = {
        "schema_version": "h4_code_source_live_probe_output_bundle.v0",
        "output_bundle_id": f"h4.code_source_live_probe_output_bundle.{result.get('source_id', 'unknown')}.{_short_hash(str(result.get('live_probe_result_id')))}.v0",
        "live_probe_result": dict(result),
        "normalized_record": result.get("normalized_record"),
        "source_identity_candidate": result.get("source_identity_candidate"),
        "release_identity_candidate": result.get("release_identity_candidate"),
        "source_to_binary_relation_candidate_preview": result.get("source_to_binary_relation_candidate_preview"),
        "release_asset_candidate_preview": result.get("release_asset_candidate_preview"),
        "source_cache_candidate_preview": result.get("source_cache_candidate_preview"),
        "evidence_candidate_preview": result.get("evidence_candidate_preview"),
        "review_queue_seed_preview": result.get("review_queue_seed_preview"),
        "connector_health_summary": result.get("connector_health_summary"),
        "validation_summary": {
            "status": "pass",
            "network_used": result.get("network_used") is True,
            "request_count": result.get("request_count", 0),
            "repository_clone_used": False,
            "source_archive_download_used": False,
            "release_asset_download_used": False,
            "git_command_invoked": False,
            "build_tool_invoked": False,
        },
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["Bundle groups preview outputs only; it imports or accepts nothing."],
    }
    _raise_on_boundary_errors(bundle)
    return bundle


def summarize_h4_code_source_live_probe_result(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "source_id": result.get("source_id"),
        "result_status": result.get("result_status"),
        "request_count": int(result.get("request_count") or 0),
        "network_used": result.get("network_used") is True,
        "blocked_reasons": list(result.get("blocked_reasons") or ([] if not result.get("blocked_reason") else [result.get("blocked_reason")])),
        "source_identity_candidate_created": isinstance(result.get("source_identity_candidate"), Mapping) and result.get("source_identity_candidate", {}).get("status") != "not_created_blocked_by_policy",
        "release_identity_candidate_created": isinstance(result.get("release_identity_candidate"), Mapping) and result.get("release_identity_candidate", {}).get("status") != "not_created_blocked_by_policy",
        "relation_candidate_count": len(result.get("source_to_binary_relation_candidate_preview", []) or []),
        "release_asset_candidate_count": len(result.get("release_asset_candidate_preview", []) or []),
        "source_cache_candidate_created": isinstance(result.get("source_cache_candidate_preview"), Mapping) and result.get("source_cache_candidate_preview", {}).get("status") != "not_created_blocked_by_policy",
        "evidence_candidate_created": isinstance(result.get("evidence_candidate_preview"), Mapping) and result.get("evidence_candidate_preview", {}).get("status") != "not_created_blocked_by_policy",
        "review_seed_created": isinstance(result.get("review_queue_seed_preview"), Mapping) and result.get("review_queue_seed_preview", {}).get("status") != "not_created_blocked_by_policy",
        "repository_clone_used": False,
        "source_archive_download_used": False,
        "release_asset_download_used": False,
        "git_command_invoked": False,
        "build_tool_invoked": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
    }


def build_request_url_or_metadata_request(source_id: str, request: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    cfg = SOURCE_CONFIGS[source_id]
    request_key = str(request.get("approved_request_key") or cfg["request_key"])
    detail = _request_detail(_source_policy(source_id, policy_bundle), request_key)
    identifier = _mapping(_mapping(detail.get("request_shape")).get("identifier") or detail.get("identifier_or_query"))
    url = ENDPOINT_URL_TEMPLATES[source_id]
    values = {
        "source_id": source_id,
        "owner_or_namespace": str(identifier.get("owner_or_namespace") or cfg["owner_or_namespace"]),
        "repository_or_project": str(identifier.get("repository_or_project") or cfg["repository_or_project"]),
        "metadata_class": str(detail.get("endpoint_or_metadata_class") or cfg["endpoint_or_metadata_class"]),
    }
    for key, value in values.items():
        url = url.replace("{" + str(key) + "}", _safe_url_component(str(value)))
    return {
        "method": "GET",
        "url": url,
        "endpoint_or_metadata_class": str(detail.get("endpoint_or_metadata_class") or cfg["endpoint_or_metadata_class"]),
        "request_key": request_key,
        "metadata_only": True,
        "repository_clone_requested": False,
        "source_archive_download_requested": False,
        "release_asset_download_requested": False,
    }


def fetch_h4_code_source_metadata_once(request: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    validation = validate_h4_code_source_live_probe_request(request, policy_bundle)
    if not validation["approved"]:
        raise H4CodeSourceLiveProbeBlocked(build_h4_code_source_live_probe_blocked_result(request, validation["blocked_reasons"], policy_bundle))
    source_id = str(request["source_id"])
    metadata_request = build_request_url_or_metadata_request(source_id, request, policy_bundle)
    rate = _source_policy(source_id, policy_bundle, "rate_limit_policy")
    timeout = float(rate.get("timeout_seconds") or 10)
    request_obj = urllib.request.Request(metadata_request["url"], headers={"User-Agent": "Eureka-H4-Code-Source-Metadata-Probe/0 fixture-review"}, method="GET")
    start = time.monotonic()
    try:
        with urllib.request.urlopen(request_obj, timeout=timeout) as response:
            raw = response.read()
            payload = json.loads(raw.decode("utf-8"))
            if not isinstance(payload, dict):
                raise ValueError("H4 live-probe response must be a JSON object")
            return payload, {
                "endpoint_or_metadata_used": metadata_request["endpoint_or_metadata_class"],
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
        raise RuntimeError(f"H4 code/source metadata request failed: {exc}") from exc


def _source_parse_response_payload(source_id: str, response_payload: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    cfg = SOURCE_CONFIGS[source_id]
    payload = dict(response_payload.get("fixture_payload") if isinstance(response_payload.get("fixture_payload"), Mapping) else response_payload)
    release_assets = payload.get("release_assets") if isinstance(payload.get("release_assets"), list) else []
    return {
        "source_host": str(payload.get("source_host") or cfg["source_host"]),
        "owner_or_namespace": str(payload.get("owner_or_namespace") or cfg["owner_or_namespace"]),
        "repository_name": str(payload.get("repository_name") or cfg["repository_or_project"]),
        "project_name": str(payload.get("project_name") or cfg["project_name"]),
        "origin_url_candidate": str(payload.get("origin_url_candidate") or f"live_probe:h4:{source_id}:origin"),
        "repository_url_candidate": str(payload.get("repository_url_candidate") or f"live_probe:h4:{source_id}:repository"),
        "source_native_id": str(payload.get("source_native_id") or f"{source_id}/live-probe-metadata"),
        "git_commit_id_candidate": str(payload.get("git_commit_id_candidate") or cfg["swhid_or_git_object_identifier"]),
        "git_tree_id_candidate": str(payload.get("git_tree_id_candidate") or "unknown"),
        "git_tag_candidate": str(payload.get("git_tag_candidate") or cfg["release_or_tag_identifier"]),
        "branch_name_candidate": str(payload.get("branch_name_candidate") or "unknown"),
        "release_id": str(payload.get("release_id") or f"{source_id}-metadata-release"),
        "release_tag": str(payload.get("release_tag") or cfg["release_or_tag_identifier"]),
        "release_name": str(payload.get("release_name") or f"{cfg['project_name']} metadata release"),
        "release_version": str(payload.get("release_version") or "1.0.0-fixture"),
        "release_timestamp": str(payload.get("release_timestamp") or "unknown"),
        "release_actor_or_author": str(payload.get("release_actor_or_author") or "unknown"),
        "release_notes_ref": str(payload.get("release_notes_ref") or "unknown"),
        "release_notes_summary": str(payload.get("release_notes_summary") or "metadata-only code/source/release live-probe response"),
        "release_asset_summary": payload.get("release_asset_summary") if isinstance(payload.get("release_asset_summary"), Mapping) else {"asset_count": len(release_assets), "download_allowed_current": False, "payload_available_current": False},
        "release_assets": release_assets,
        "swhid_candidate": str(payload.get("swhid_candidate") or (cfg["swhid_or_git_object_identifier"] if str(cfg["swhid_or_git_object_identifier"]).startswith("swh:") else "unknown")),
        "archived_origin_candidate": str(payload.get("archived_origin_candidate") or "unknown"),
        "license_metadata": payload.get("license_metadata") if isinstance(payload.get("license_metadata"), Mapping) else {"declared_license": "unknown", "rights_clearance_claimed": False},
        "readme_ref": str(payload.get("readme_ref") or "unknown"),
        "changelog_ref": str(payload.get("changelog_ref") or "unknown"),
        "source_archive_locator_candidate": str(payload.get("source_archive_locator_candidate") or "unknown"),
        "source_to_binary_relation": payload.get("source_to_binary_relation") if isinstance(payload.get("source_to_binary_relation"), Mapping) else {"relation_kind": H4_SOURCE_CONFIGS[source_id].get("relation_kind", "not_evaluable"), "relation_confidence_or_uncertainty": "candidate_from_live_probe_metadata_no_provenance"},
        "project_urls": list(payload.get("project_urls") or []),
        "source_metadata": payload.get("source_metadata") if isinstance(payload.get("source_metadata"), Mapping) else {"response_shape": "metadata_only", "source_label": cfg["label"]},
    }


def _source_normalize_response_payload(source_id: str, response_payload: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    fixture_payload = _source_parse_response_payload(source_id, response_payload, policy_bundle)
    cfg = SOURCE_CONFIGS[source_id]
    fixture = {
        "schema_version": "h4_code_source_fixture.v0",
        "fixture_id": f"h4.live_probe_response.{source_id}.{_slug(fixture_payload['source_native_id'])}.v0",
        "source_id": source_id,
        "connector_family": cfg["connector_family"],
        "fixture_kind": "live_probe_metadata_response",
        "fixture_status": "live_probe_observation",
        "fixture_public_safe": True,
        "live_call_used": False,
        "network_used": False,
        "external_api_used": False,
        "repository_payload_included": False,
        "source_archive_payload_included": False,
        "release_asset_payload_included": False,
        "git_command_invoked": False,
        "build_tool_invoked": False,
        "fixture_payload": fixture_payload,
        "expected_normalized_ref": None,
        "limitations": ["normalized from bounded H4 code/source/release metadata live-probe response", "live response is not source truth"],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _fixture_product_boundary(),
        "notes": ["Converted to fixture shape for deterministic H4 normalizer reuse."],
    }
    record = normalize_h4_code_source_fixture(fixture, source_id, policy_bundle)
    record["source_observation_origin"] = "h4_bundle_03_live_probe"
    record["notes"] = ["Normalized from an H4 code/source/release metadata live-probe result.", "No repository clone, downloads, git/build commands, install, or execution occurred."]
    _raise_on_boundary_errors(record)
    return record


def detect_h4_code_source_live_probe_truth_boundary_violations(result: Mapping[str, Any], policy_bundle: Mapping[str, Any] | None = None) -> list[str]:
    return [f"truth boundary violation: {path}=true" for path, key, value in _iter_key_values(result) if key in FORBIDDEN_TRUTH_TRUE_KEYS and value is True]


def detect_h4_code_source_live_probe_product_boundary_violations(result: Mapping[str, Any], policy_bundle: Mapping[str, Any] | None = None) -> list[str]:
    return [f"product boundary violation: {path}=true" for path, key, value in _iter_key_values(result) if key in FORBIDDEN_PRODUCT_TRUE_KEYS and value is True]


def _raise_on_boundary_errors(result: Mapping[str, Any]) -> None:
    errors = detect_h4_code_source_live_probe_truth_boundary_violations(result) + detect_h4_code_source_live_probe_product_boundary_violations(result)
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
    if "clone" in joined or "repository_clone" in joined:
        return "blocked_by_clone_policy"
    if "download" in joined or "release_asset" in joined or "source_archive" in joined or "payload" in joined:
        return "blocked_by_download_policy"
    if "git_command" in joined or "git command" in joined or "git_" in joined:
        return "blocked_by_git_command_policy"
    if "build_tool" in joined or "build tool" in joined:
        return "blocked_by_build_tool_policy"
    if "approval" in joined or "approved" in joined:
        return "blocked_by_missing_approval"
    if "kill switch" in joined:
        return "blocked_by_kill_switch"
    if "endpoint/metadata" in joined or "metadata class" in joined or "endpoint" in joined:
        return "blocked_by_endpoint_policy"
    return "blocked_by_policy"


def _truth_boundary() -> dict[str, bool]:
    return {'live_probe_result_is_public_truth': False, 'normalized_record_is_public_truth': False, 'source_identity_candidate_is_truth': False, 'source_identity_candidate_is_accepted_identity': False, 'release_identity_candidate_is_truth': False, 'release_identity_candidate_is_accepted_release_truth': False, 'source_to_binary_relation_candidate_is_provenance_truth': False, 'relation_candidate_is_accepted_provenance': False, 'git_object_candidate_is_accepted_provenance': False, 'git_object_candidate_is_provenance_truth': False, 'swhid_candidate_is_accepted_object_truth': False, 'swhid_candidate_is_object_truth': False, 'repository_url_proves_official_status': False, 'release_asset_metadata_grants_download_permission': False, 'release_notes_prove_installability': False, 'tag_release_match_proves_build_relation': False, 'asset_presence_proves_source_relationship': False, 'sbom_signature_metadata_proves_trust': False, 'asset_hash_proves_malware_safety': False, 'release_asset_hash_candidate_is_malware_safety': False, 'signature_metadata_proves_authenticity': False, 'signature_metadata_is_authenticity': False, 'sbom_metadata_is_provenance': False, 'license_metadata_is_rights_clearance': False, 'source_cache_candidate_is_accepted_source': False, 'source_cache_preview_is_accepted_source': False, 'evidence_candidate_preview_is_accepted_evidence': False, 'evidence_preview_is_accepted_evidence': False, 'review_seed_is_review_decision': False, 'review_queue_seed_is_review_decision': False, 'accepted_source_truth': False, 'accepted_evidence_truth': False, 'accepted_candidate_truth': False, 'accepted_source_identity_truth': False, 'accepted_release_identity_truth': False, 'accepted_source_to_binary_relation_truth': False, 'accepted_public_record': False, 'public_index_mutated': False, 'master_index_mutated': False, 'rights_clearance_claimed': False, 'malware_safety_claimed': False, 'verified_installability_claimed': False, 'verified_authenticity_claimed': False, 'verified_build_reproducibility_claimed': False, 'production_readiness_claimed': False}


def _product_boundary() -> dict[str, bool]:
    return {'changed_public_search_behavior': False, 'enabled_hosting': False, 'enabled_live_probes': False, 'enabled_source_sync': False, 'enabled_source_connectors': False, 'enabled_repository_clone': False, 'enabled_downloads': False, 'enabled_installers': False, 'enabled_execution': False, 'enabled_uploads': False, 'enabled_accounts': False, 'enabled_telemetry': False, 'enabled_public_query_fanout': False, 'enabled_scraping': False, 'enabled_crawling': False, 'mutated_public_index': False, 'mutated_master_index': False, 'source_sync_enabled': False, 'repository_clone_enabled': False, 'source_archive_download_enabled': False, 'release_asset_download_enabled': False, 'binary_download_enabled': False, 'package_download_enabled': False, 'git_command_invocation_enabled': False, 'build_tool_invocation_enabled': False, 'install_execute_enabled': False}


def _fixture_product_boundary() -> dict[str, bool]:
    boundary = _product_boundary()
    boundary.update({
        "network_calls_made": False,
        "api_calls_made": False,
        "repository_clone_used": False,
        "source_archive_download_used": False,
        "release_asset_download_used": False,
        "git_command_invoked": False,
        "build_tool_invoked": False,
        "install_execute_used": False,
    })
    return boundary


def _release_assets_from_record(record: Mapping[str, Any]) -> list[dict[str, Any]]:
    existing = record.get("release_asset_candidate_preview")
    if isinstance(existing, list) and existing:
        return [
            {
                "asset_name": item.get("asset_name", "unknown"),
                "asset_kind": item.get("asset_kind", "metadata_only"),
                "asset_size": item.get("asset_size", "unknown"),
                "asset_hashes": item.get("asset_hashes", {}),
                "asset_locator": item.get("asset_locator", "unknown"),
                "signature_metadata": item.get("signature_metadata", {"present": False, "verified_current": False}),
                "sbom_metadata": item.get("sbom_metadata", {"present": False, "verified_current": False}),
            }
            for item in existing if isinstance(item, Mapping)
        ]
    summary = record.get("release_asset_summary") if isinstance(record.get("release_asset_summary"), Mapping) else {}
    if int(summary.get("asset_count") or 0) > 0:
        return [{"asset_name": f"{record.get('project_name', 'unknown')}-metadata-asset", "asset_kind": "metadata_only", "asset_size": "unknown", "asset_hashes": {}, "asset_locator": "metadata-only", "signature_metadata": {"present": False, "verified_current": False}, "sbom_metadata": {"present": False, "verified_current": False}}]
    return []


def _fingerprint(payload: Mapping[str, Any]) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()


def _short_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:12]


def _slug(value: Any) -> str:
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
