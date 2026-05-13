"""Fail-closed H12 retro/community metadata live-probe helpers."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any

from control.prototypes.legacy_runtime.connectors.h12_retro_community.normalizer_common import (
    H12_SOURCE_CONFIGS as _BASE_SOURCE_CONFIGS,
    build_h12_archive_item_member_candidate as _fixture_archive_candidate,
    build_h12_community_review_comment_candidates as _fixture_community_candidate,
    build_h12_compatibility_install_note_candidates as _fixture_compatibility_candidate,
    build_h12_evidence_candidate_preview as _fixture_evidence_preview,
    build_h12_gated_source_boundary_candidate as _fixture_gated_candidate,
    build_h12_hash_checksum_candidate as _fixture_hash_candidate,
    build_h12_ia_wayback_corroboration_candidate as _fixture_corroboration_candidate,
    build_h12_platform_version_edition_candidate as _fixture_platform_candidate,
    build_h12_retro_rights_safety_candidate as _fixture_rights_candidate,
    build_h12_retro_software_identity_candidate as _fixture_software_candidate,
    build_h12_source_cache_candidate_preview as _fixture_source_cache_preview,
    normalize_h12_retro_community_fixture,
)

POLICY_PATHS = {
    "live_probe_policy": "control/inventory/connectors/h12_retro_community_live_probe_policy.json",
    "allowed_requests": "control/inventory/connectors/h12_retro_community_live_probe_allowed_requests.json",
    "endpoint_policy": "control/inventory/connectors/h12_retro_community_live_probe_endpoint_policy.json",
    "rate_limit_policy": "control/inventory/connectors/h12_retro_community_live_probe_rate_limit_policy.json",
    "cache_policy": "control/inventory/connectors/h12_retro_community_live_probe_cache_policy.json",
    "kill_switch_policy": "control/inventory/connectors/h12_retro_community_live_probe_kill_switch_policy.json",
    "output_policy": "control/inventory/connectors/h12_retro_community_live_probe_output_policy.json",
    "path_policy": "control/inventory/connectors/h12_retro_community_live_probe_path_policy.json",
    "review_policy": "control/inventory/connectors/h12_retro_community_live_probe_review_policy.json",
    "truth_policy": "control/inventory/connectors/h12_retro_community_live_probe_truth_policy.json",
    "no_download_execute_policy": "control/inventory/connectors/h12_retro_community_live_probe_no_download_execute_policy.json",
    "restricted_source_policy": "control/inventory/connectors/h12_retro_community_live_probe_restricted_source_policy.json"
}
SOURCE_CONFIGS = {'winworld_metadata': {'source_id': 'winworld_metadata', 'source_label': 'WinWorld metadata', 'connector_family': 'retro_software_catalog', 'source_family': 'retro_community_archive', 'trust_lane': 'community', 'source_record_kind': 'retro_community_metadata', 'endpoint': 'catalog_item_metadata_lookup_future', 'request_key': 'example_catalog_item_metadata'}, 'macintosh_garden_metadata': {'source_id': 'macintosh_garden_metadata', 'source_label': 'Macintosh Garden metadata', 'connector_family': 'community_archive_catalog', 'source_family': 'retro_community_archive', 'trust_lane': 'community', 'source_record_kind': 'retro_community_metadata', 'endpoint': 'catalog_item_metadata_lookup_future', 'request_key': 'example_catalog_item_metadata'}, 'macintosh_repository_metadata': {'source_id': 'macintosh_repository_metadata', 'source_label': 'Macintosh Repository metadata', 'connector_family': 'community_archive_catalog', 'source_family': 'retro_community_archive', 'trust_lane': 'community', 'source_record_kind': 'retro_community_metadata', 'endpoint': 'catalog_item_metadata_lookup_future', 'request_key': 'example_catalog_item_metadata'}, 'vetusware_metadata': {'source_id': 'vetusware_metadata', 'source_label': 'VetusWare metadata', 'connector_family': 'old_version_catalog', 'source_family': 'retro_community_archive', 'trust_lane': 'community', 'source_record_kind': 'retro_community_metadata', 'endpoint': 'catalog_item_metadata_policy_limited_future', 'request_key': 'example_policy_limited_catalog_metadata'}, 'oldversion_metadata': {'source_id': 'oldversion_metadata', 'source_label': 'OldVersion metadata', 'connector_family': 'old_version_catalog', 'source_family': 'retro_community_archive', 'trust_lane': 'community', 'source_record_kind': 'retro_community_metadata', 'endpoint': 'old_version_catalog_metadata_lookup_future', 'request_key': 'example_old_version_catalog_metadata'}, 'my_abandonware_metadata': {'source_id': 'my_abandonware_metadata', 'source_label': 'My Abandonware metadata', 'connector_family': 'abandonware_metadata_policy_limited', 'source_family': 'retro_community_archive', 'trust_lane': 'community', 'source_record_kind': 'retro_community_metadata', 'endpoint': 'game_catalog_metadata_policy_limited_future', 'request_key': 'example_game_catalog_metadata'}, 'dos_games_archive_metadata': {'source_id': 'dos_games_archive_metadata', 'source_label': 'DOS Games Archive metadata', 'connector_family': 'retro_software_catalog', 'source_family': 'retro_community_archive', 'trust_lane': 'community', 'source_record_kind': 'retro_community_metadata', 'endpoint': 'catalog_item_metadata_lookup_future', 'request_key': 'example_catalog_item_metadata'}, 'hobbes_os2_archive_metadata': {'source_id': 'hobbes_os2_archive_metadata', 'source_label': 'Hobbes OS/2 Archive metadata', 'connector_family': 'platform_archive_metadata', 'source_family': 'retro_community_archive', 'trust_lane': 'preservation', 'source_record_kind': 'retro_community_metadata', 'endpoint': 'platform_archive_metadata_lookup_future', 'request_key': 'example_platform_archive_metadata'}, 'aminet_metadata': {'source_id': 'aminet_metadata', 'source_label': 'Aminet metadata', 'connector_family': 'platform_archive_metadata', 'source_family': 'retro_community_archive', 'trust_lane': 'preservation', 'source_record_kind': 'retro_community_metadata', 'endpoint': 'package_catalog_metadata_lookup_future', 'request_key': 'example_package_catalog_metadata'}, 'atarimania_metadata': {'source_id': 'atarimania_metadata', 'source_label': 'Atarimania metadata', 'connector_family': 'retro_software_catalog', 'source_family': 'retro_community_archive', 'trust_lane': 'community', 'source_record_kind': 'retro_community_metadata', 'endpoint': 'catalog_item_metadata_lookup_future', 'request_key': 'example_catalog_item_metadata'}, 'tucows_ia_legacy_metadata': {'source_id': 'tucows_ia_legacy_metadata', 'source_label': 'Tucows legacy library / Internet Archive mirror metadata', 'connector_family': 'ia_mirror_bridge', 'source_family': 'retro_community_archive', 'trust_lane': 'preservation', 'source_record_kind': 'retro_community_metadata', 'endpoint': 'ia_mirror_metadata_lookup_future', 'request_key': 'example_ia_mirror_metadata'}, 'betaarchive_public_metadata_policy_limited': {'source_id': 'betaarchive_public_metadata_policy_limited', 'source_label': 'BetaArchive public metadata / gated-community boundary, policy-limited', 'connector_family': 'gated_community_boundary', 'source_family': 'retro_community_archive', 'trust_lane': 'community', 'source_record_kind': 'retro_community_metadata', 'endpoint': 'public_metadata_manifest_only_future', 'request_key': 'example_public_metadata_manifest'}, 'generic_retro_community_archive': {'source_id': 'generic_retro_community_archive', 'source_label': 'Generic retro/community archive metadata', 'connector_family': 'community_archive_catalog', 'source_family': 'retro_community_archive', 'trust_lane': 'community', 'source_record_kind': 'retro_community_metadata', 'endpoint': 'retro_catalog_fixture_future', 'request_key': 'example_catalog_item_metadata'}}
H12_SOURCE_IDS = tuple(SOURCE_CONFIGS)
REQUEST_FORBIDDEN_TRUE_KEYS = {'driver_download_requested', 'acquisition_action_requested', 'iso_download_requested', 'disc_image_download_requested', 'file_upload_requested', 'hash_submission_requested', 'execution_requested', 'crack_key_serial_handling_requested', 'gated_source_access_requested', 'bios_firmware_download_requested', 'rom_download_requested', 'restricted_source_requested', 'download_requested', 'installer_download_requested', 'account_access_requested', 'extraction_requested', 'archive_download_requested', 'bypass_or_automation_requested', 'scraping_or_crawling_requested', 'software_binary_download_requested', 'patch_download_requested'}
CONDITIONAL_REQUEST_KEYS = {'api_query_requested': 'api_query_approved', 'catalog_fetch_requested': 'catalog_fetch_approved', 'html_catalog_fetch_requested': 'html_catalog_fetch_approved', 'forum_or_comment_fetch_requested': 'forum_or_comment_fetch_approved', 'web_archive_trace_fetch_requested': 'web_archive_trace_fetch_approved'}
FORBIDDEN_TRUTH_TRUE_KEYS = {'accepted_gated_source_access_truth', 'gated_source_boundary_candidate_grants_access_permission', 'public_index_mutated', 'archive_item_member_candidate_is_truth', 'installability_claimed', 'platform_version_edition_candidate_is_truth', 'compatibility_install_note_candidate_is_truth', 'malware_safety_claimed', 'retro_rights_safety_candidate_is_rights_or_safety_truth', 'source_cache_candidate_is_accepted_source', 'community_download_metadata_grants_acquisition_permission', 'review_seed_is_review_decision', 'accepted_compatibility_install_truth', 'hash_checksum_candidate_is_truth', 'accepted_public_record', 'playability_claimed', 'compatibility_correctness_claimed', 'checksum_correctness_claimed', 'accepted_source_truth', 'accepted_archive_item_member_truth', 'verified_authenticity_claimed', 'source_cache_preview_is_accepted_source', 'live_probe_result_is_public_truth', 'privacy_safety_claimed', 'evidence_candidate_preview_is_accepted_evidence', 'master_index_mutated', 'rights_clearance_claimed', 'ia_wayback_corroboration_candidate_is_truth', 'legal_acquisition_claimed', 'accepted_rights_safety_truth', 'abandonware_label_is_legal_permission', 'retro_software_identity_candidate_is_truth', 'file_authenticity_claimed', 'mutated_public_index', 'accepted_community_review_truth', 'archive_item_metadata_grants_download_or_extraction_permission', 'mutated_master_index', 'accepted_candidate_truth', 'accepted_retro_software_identity_truth', 'accepted_platform_version_truth', 'normalized_record_is_public_truth', 'accepted_evidence_truth', 'accepted_ia_wayback_corroboration_truth', 'content_safety_claimed', 'accepted_hash_checksum_truth', 'production_readiness_claimed', 'community_review_comment_candidate_is_truth', 'community_reputation_claimed', 'evidence_preview_is_accepted_evidence'}
FORBIDDEN_PRODUCT_TRUE_KEYS = {'enabled_accounts', 'hash_submission_used', 'catalog_fetch_used', 'crawling_used', 'execution_used', 'enabled_telemetry', 'enabled_acquisition_actions', 'api_calls_made', 'enabled_extraction', 'html_catalog_fetch_used', 'network_calls_made', 'acquisition_action_used', 'download_used', 'changed_public_search_behavior', 'extraction_used', 'upload_used', 'enabled_hosting', 'enabled_execution', 'enabled_uploads', 'forum_comment_fetch_used', 'scraping_used', 'account_access_used', 'enabled_source_sync', 'mutated_public_index', 'mutated_master_index', 'enabled_live_probes', 'restricted_source_access_used', 'enabled_downloads', 'gated_source_access_used', 'enabled_crawling', 'web_archive_trace_fetch_used', 'bypass_or_automation_used'}


def load_h12_retro_community_live_probe_policy_bundle(root: str | Path | None = None) -> dict[str, Any]:
    base = Path(root) if root is not None else Path(__file__).resolve().parents[5]
    return {key: json.loads((base / rel).read_text(encoding="utf-8")) for key, rel in POLICY_PATHS.items()}


def build_h12_retro_community_live_probe_request(source_id: str, request_key: str, policy_bundle: Mapping[str, Any] | None = None, live_requested: bool = False) -> dict[str, Any]:
    if source_id not in SOURCE_CONFIGS:
        raise ValueError(f"unknown H12 source_id: {source_id}")
    cfg = SOURCE_CONFIGS[source_id]
    request = {
        "schema_version": "h12_retro_community_live_probe_request.v0",
        "live_probe_request_id": f"h12.live_probe_request.{source_id}.{_slug(request_key)}.v0",
        "source_id": source_id,
        "connector_family": cfg["connector_family"],
        "source_record_kind": cfg["source_record_kind"],
        "operation_scope": "metadata_only",
        "endpoint_or_metadata_class": cfg["endpoint"],
        "request_shape": {
            "request_key": request_key,
            "identifier_shape": "single_committed_metadata_identifier_future",
            "arbitrary_url_allowed": False,
            "metadata_only": True,
        },
        "approved_request_key": request_key,
        "retro_software_or_platform_identifier": f"metadata-only-candidate:{source_id}:{request_key}",
        "archive_item_or_member_context": "candidate_archive_metadata_context_only_no_payload",
        "compatibility_or_community_context": "candidate_community_metadata_context_only",
        "hash_or_corroboration_context": "candidate_checksum_or_corroboration_context_only_no_hash_submission",
        "gated_or_rights_context": "blocked_current_no_account_no_gated_access_no_acquisition",
        "approval_refs": [POLICY_PATHS["allowed_requests"]],
        "policy_refs": list(POLICY_PATHS.values()),
        "live_requested": bool(live_requested),
        "dry_run_only": not bool(live_requested),
        "api_query_requested": False,
        "catalog_fetch_requested": False,
        "html_catalog_fetch_requested": False,
        "forum_or_comment_fetch_requested": False,
        "web_archive_trace_fetch_requested": False,
        "gated_source_access_requested": False,
        "account_access_requested": False,
        "download_requested": False,
        "software_binary_download_requested": False,
        "rom_download_requested": False,
        "iso_download_requested": False,
        "disc_image_download_requested": False,
        "bios_firmware_download_requested": False,
        "driver_download_requested": False,
        "installer_download_requested": False,
        "patch_download_requested": False,
        "crack_key_serial_handling_requested": False,
        "archive_download_requested": False,
        "extraction_requested": False,
        "execution_requested": False,
        "acquisition_action_requested": False,
        "file_upload_requested": False,
        "hash_submission_requested": False,
        "scraping_or_crawling_requested": False,
        "restricted_source_requested": False,
        "bypass_or_automation_requested": False,
        "output_policy_ref": POLICY_PATHS["output_policy"],
        "review_policy_ref": POLICY_PATHS["review_policy"],
        "truth_policy_ref": POLICY_PATHS["truth_policy"],
        "limitations": ["Request envelope is fail-closed unless committed source policy approves the exact metadata-only request."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["H12-BUNDLE-03 examples are dry preflight by default and do not call networks."],
    }
    _raise_on_boundary_errors(request)
    return request


def validate_h12_retro_community_live_probe_request(request: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []
    source_id = str(request.get("source_id") or "")
    request_key = str(request.get("approved_request_key") or "")
    allowed = _source_policy(source_id, policy_bundle, "allowed_requests") if source_id in SOURCE_CONFIGS else {}
    if source_id not in SOURCE_CONFIGS:
        reasons.append(f"{source_id or 'missing_source'} is not a known H12 retro/community source")
    else:
        cfg = SOURCE_CONFIGS[source_id]
        if request.get("operation_scope") != "metadata_only":
            reasons.append("approved_operation_scope must be metadata_only")
        endpoint = str(request.get("endpoint_or_metadata_class") or "")
        if endpoint != cfg["endpoint"]:
            lower = endpoint.casefold()
            if "download" in lower or "payload" in lower or "binary" in lower or "rom" in lower or "iso" in lower:
                reasons.append("endpoint_or_metadata_class download/payload class is forbidden")
            else:
                reasons.append("endpoint_or_metadata_class is not the planned source metadata class")
    for request_field, approval_field in CONDITIONAL_REQUEST_KEYS.items():
        if request.get(request_field) is True and allowed.get(approval_field) is not True:
            reasons.append(f"{request_field} is not approved without exact committed bounded metadata policy")
    for key in sorted(REQUEST_FORBIDDEN_TRUE_KEYS):
        if request.get(key) is True:
            reasons.append(f"{key} is forbidden for H12-BUNDLE-03 live probes")
    if source_id in SOURCE_CONFIGS:
        reasons.extend(validate_h12_source_approval(source_id, request_key, policy_bundle)["blocked_reasons"])
    reasons = _dedupe(reasons)
    return {"approved": not reasons, "result_status": _status_for_reasons(reasons), "blocked_reasons": reasons}


def validate_h12_source_approval(source_id: str, request_key: str, policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []
    if source_id not in SOURCE_CONFIGS:
        return {"approved": False, "result_status": "blocked_by_policy", "blocked_reasons": [f"{source_id} is not a known H12 source"]}
    cfg = SOURCE_CONFIGS[source_id]
    allowed = _source_policy(source_id, policy_bundle, "allowed_requests")
    if not allowed:
        reasons.append("source is not listed in H12 allowed request policy")
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
        for key in (
            "source_sync_approved",
            "gated_source_access_approved",
            "account_access_approved",
            "download_approved",
            "rom_download_approved",
            "iso_download_approved",
            "disc_image_download_approved",
            "bios_firmware_download_approved",
            "software_binary_download_approved",
            "driver_download_approved",
            "installer_download_approved",
            "patch_download_approved",
            "crack_key_serial_handling_approved",
            "archive_download_approved",
            "extraction_approved",
            "emulator_execution_approved",
            "install_execute_approved",
            "acquisition_action_approved",
            "file_upload_approved",
            "hash_submission_approved",
            "scraping_approved",
            "crawling_approved",
            "browser_automation_approved",
            "restricted_rights_sensitive_source_approved",
            "gated_private_source_approved",
            "piracy_adjacent_or_leaked_source_approved",
            "drm_or_access_control_bypass_approved",
            "public_query_fanout_approved",
        ):
            if allowed.get(key) is not False:
                reasons.append(f"{key} must remain false")
    endpoint = _source_policy(source_id, policy_bundle, "endpoint_policy")
    if cfg["endpoint"] not in (endpoint.get("allowlisted_endpoint_or_metadata_classes_current") or []):
        reasons.append("endpoint/metadata class is not allowlisted for current live access")
    rate = _source_policy(source_id, policy_bundle, "rate_limit_policy")
    if rate.get("decision_status") != "approved_for_bounded_metadata_probe":
        reasons.append("rate limit policy is not approved")
    if int(rate.get("max_requests_per_run") or 0) <= 0:
        reasons.append("request budget is not approved")
    if int(rate.get("timeout_seconds") or 0) <= 0:
        reasons.append("timeout_seconds is not set")
    if not rate.get("retry_policy"):
        reasons.append("retry policy is not set")
    if str(rate.get("auth_posture", "")).startswith("no_auth_only") is False and "no_auth" not in str(rate.get("auth_posture", "")):
        reasons.append("auth/no-auth posture is not approved")
    cache = _source_policy(source_id, policy_bundle, "cache_policy")
    if cache.get("decision_status") != "approved_for_bounded_metadata_probe" and cache.get("no_cache_decision") != "approved":
        reasons.append("cache TTL/no-cache decision is not approved")
    kill = _source_policy(source_id, policy_bundle, "kill_switch_policy")
    if kill.get("default_enabled") is not True or kill.get("live_probe_kill_switch_engaged") is not False:
        reasons.append("kill switch defaults fail-closed or is engaged")
    reasons = _dedupe(reasons)
    return {"approved": not reasons, "result_status": _status_for_reasons(reasons), "blocked_reasons": reasons}


def build_h12_retro_community_live_probe_blocked_result(request: Mapping[str, Any], reason: str | list[str], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    source_id = str(request.get("source_id") or "unknown")
    cfg = SOURCE_CONFIGS.get(source_id, {"connector_family": request.get("connector_family", "unknown"), "source_record_kind": request.get("source_record_kind", "unknown"), "endpoint": request.get("endpoint_or_metadata_class", "unknown")})
    reasons = reason if isinstance(reason, list) else [str(reason)]
    normalized = _normal_record_from_request(request)
    result = {
        "schema_version": "h12_retro_community_live_probe_result.v0",
        "live_probe_result_id": f"h12.live_probe_result.{source_id}.{_short_fingerprint(request)}.v0",
        "live_probe_request_ref": request.get("live_probe_request_id"),
        "source_id": source_id,
        "connector_family": cfg["connector_family"],
        "source_record_kind": cfg["source_record_kind"],
        "result_status": _status_for_reasons(reasons),
        "request_count": 0,
        "network_used": False,
        "endpoint_or_metadata_used": cfg.get("endpoint"),
        "response_status_code": None,
        "response_fingerprint": None,
        "response_summary": "Blocked preflight; no external response payload exists.",
        "normalized_record": normalized,
        "retro_software_identity_candidate": normalized["retro_software_identity_candidate"],
        "platform_version_edition_candidate": normalized["platform_version_edition_candidate"],
        "archive_item_member_candidate": normalized["archive_item_member_candidate"],
        "compatibility_install_note_candidate": normalized["compatibility_install_note_candidate"],
        "community_review_comment_candidate": normalized["community_review_comment_candidate"],
        "hash_checksum_candidate": normalized["hash_checksum_candidate"],
        "ia_wayback_corroboration_candidate": normalized["ia_wayback_corroboration_candidate"],
        "gated_source_boundary_candidate": normalized["gated_source_boundary_candidate"],
        "retro_rights_safety_candidate": normalized["retro_rights_safety_candidate"],
        "source_cache_candidate_preview": normalized["source_cache_candidate_preview"],
        "evidence_candidate_preview": normalized["evidence_candidate_preview"],
        "review_queue_seed_preview": None,
        "connector_health_summary": None,
        "blocked_reason": "; ".join(reasons) if reasons else None,
        "blocked_reasons": reasons,
        "warnings": [],
        "limitations": ["No live source call was made; output is fixture-equivalent candidate/preview material only."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["No source cache, evidence ledger, review queue, public index, or master index mutation occurs."],
    }
    result["review_queue_seed_preview"] = build_h12_review_queue_seed_preview_from_probe(result, result["source_cache_candidate_preview"], result["evidence_candidate_preview"], policy_bundle)
    result["connector_health_summary"] = build_h12_connector_health_summary(result, policy_bundle)
    _raise_on_boundary_errors(result)
    return result


def build_h12_retro_community_live_probe_result(source_id: str, response_payload: Mapping[str, Any], response_metadata: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    if source_id not in SOURCE_CONFIGS:
        raise ValueError(f"unknown H12 source_id: {source_id}")
    cfg = SOURCE_CONFIGS[source_id]
    normalized = _normal_record_from_response(source_id, response_payload, response_metadata)
    result = {
        "schema_version": "h12_retro_community_live_probe_result.v0",
        "live_probe_result_id": f"h12.live_probe_result.{source_id}.{_short_fingerprint(response_payload)}.v0",
        "live_probe_request_ref": response_metadata.get("live_probe_request_ref", "mocked_or_fixture_equivalent_response"),
        "source_id": source_id,
        "connector_family": cfg["connector_family"],
        "source_record_kind": cfg["source_record_kind"],
        "result_status": response_metadata.get("result_status", "live_probe_completed"),
        "request_count": int(response_metadata.get("request_count") or 1),
        "network_used": bool(response_metadata.get("network_used", False)),
        "endpoint_or_metadata_used": cfg["endpoint"],
        "response_status_code": response_metadata.get("response_status_code"),
        "response_fingerprint": _short_fingerprint(response_payload),
        "response_summary": response_metadata.get("response_summary", "Bounded metadata-only response payload."),
        "normalized_record": normalized,
        "retro_software_identity_candidate": normalized["retro_software_identity_candidate"],
        "platform_version_edition_candidate": normalized["platform_version_edition_candidate"],
        "archive_item_member_candidate": normalized["archive_item_member_candidate"],
        "compatibility_install_note_candidate": normalized["compatibility_install_note_candidate"],
        "community_review_comment_candidate": normalized["community_review_comment_candidate"],
        "hash_checksum_candidate": normalized["hash_checksum_candidate"],
        "ia_wayback_corroboration_candidate": normalized["ia_wayback_corroboration_candidate"],
        "gated_source_boundary_candidate": normalized["gated_source_boundary_candidate"],
        "retro_rights_safety_candidate": normalized["retro_rights_safety_candidate"],
        "source_cache_candidate_preview": normalized["source_cache_candidate_preview"],
        "evidence_candidate_preview": normalized["evidence_candidate_preview"],
        "review_queue_seed_preview": None,
        "connector_health_summary": None,
        "blocked_reason": None,
        "blocked_reasons": [],
        "warnings": list(response_metadata.get("warnings") or []),
        "limitations": ["Probe output remains candidate/preview material only."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["No source cache, evidence ledger, review queue, public index, or master index mutation occurs."],
    }
    result["review_queue_seed_preview"] = build_h12_review_queue_seed_preview_from_probe(result, result["source_cache_candidate_preview"], result["evidence_candidate_preview"], policy_bundle)
    result["connector_health_summary"] = build_h12_connector_health_summary(result, policy_bundle)
    _raise_on_boundary_errors(result)
    return result


def normalize_h12_retro_community_live_probe_result(result: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    normalized = result.get("normalized_record")
    if not isinstance(normalized, Mapping):
        raise ValueError("live probe result is missing normalized_record")
    return dict(normalized)


def build_h12_retro_software_identity_candidate_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return _fixture_software_candidate(normalized_record, policy_bundle)


def build_h12_platform_version_edition_candidate_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return _fixture_platform_candidate(normalized_record, policy_bundle)


def build_h12_archive_item_member_candidate_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return _fixture_archive_candidate(normalized_record, policy_bundle)


def build_h12_compatibility_install_note_candidate_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return _fixture_compatibility_candidate(normalized_record, policy_bundle)


def build_h12_community_review_comment_candidate_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return _fixture_community_candidate(normalized_record, policy_bundle)


def build_h12_hash_checksum_candidate_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return _fixture_hash_candidate(normalized_record, policy_bundle)


def build_h12_ia_wayback_corroboration_candidate_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return _fixture_corroboration_candidate(normalized_record, policy_bundle)


def build_h12_gated_source_boundary_candidate_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return _fixture_gated_candidate(normalized_record, policy_bundle)


def build_h12_retro_rights_safety_candidate_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return _fixture_rights_candidate(normalized_record, policy_bundle)


def build_h12_source_cache_candidate_preview_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return _fixture_source_cache_preview(normalized_record, policy_bundle)


def build_h12_evidence_candidate_preview_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return _fixture_evidence_preview(normalized_record, policy_bundle)


def build_h12_review_queue_seed_preview_from_probe(result: Mapping[str, Any], source_cache_preview: Mapping[str, Any], evidence_preview: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    seed = {
        "schema_version": "h12_retro_community_live_probe_review_seed.v0",
        "review_seed_id": f"h12.review_seed.{result.get('source_id')}.{_short_fingerprint(result)}.v0",
        "source_id": result.get("source_id"),
        "live_probe_result_ref": result.get("live_probe_result_id"),
        "source_cache_preview_ref": source_cache_preview.get("preview_id"),
        "evidence_preview_ref": evidence_preview.get("preview_id"),
        "seed_only": True,
        "review_decision": "not_made",
        "mutates_review_queue": False,
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "limitations": ["Review seed preview only; not a review decision and not queue mutation."],
    }
    _raise_on_boundary_errors(seed)
    return seed


def build_h12_connector_health_summary(result: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    status = str(result.get("result_status") or "not_evaluable")
    blockers = list(result.get("blocked_reasons") or [])
    health = {
        "schema_version": "h12_retro_community_connector_health_summary.v0",
        "health_summary_id": f"h12.connector_health.{result.get('source_id')}.{_short_fingerprint(result)}.v0",
        "source_id": result.get("source_id"),
        "connector_family": result.get("connector_family"),
        "live_probe_status": status,
        "request_count": int(result.get("request_count") or 0),
        "response_status_summary": "blocked" if status.startswith("blocked_") else status,
        "policy_blockers": blockers,
        "warnings": list(result.get("warnings") or []),
        "source_limitations": list(result.get("limitations") or []),
        "gated_source_status": "blocked_current",
        "restricted_source_status": "blocked_current",
        "community_lane_status": "candidate_metadata_only",
        "next_recommended_action": "Use fixture-equivalent outputs for H12-BUNDLE-04 or obtain explicit operator approval before any live source call.",
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
    }
    _raise_on_boundary_errors(health)
    return health


def build_h12_retro_community_live_probe_output_bundle(result: Mapping[str, Any]) -> dict[str, Any]:
    bundle = {
        "schema_version": "h12_retro_community_live_probe_output_bundle.v0",
        "live_probe_result": result,
        "normalized_record": result.get("normalized_record"),
        "retro_software_identity_candidate": result.get("retro_software_identity_candidate"),
        "platform_version_edition_candidate": result.get("platform_version_edition_candidate"),
        "archive_item_member_candidate": result.get("archive_item_member_candidate"),
        "compatibility_install_note_candidate": result.get("compatibility_install_note_candidate"),
        "community_review_comment_candidate": result.get("community_review_comment_candidate"),
        "hash_checksum_candidate": result.get("hash_checksum_candidate"),
        "ia_wayback_corroboration_candidate": result.get("ia_wayback_corroboration_candidate"),
        "gated_source_boundary_candidate": result.get("gated_source_boundary_candidate"),
        "retro_rights_safety_candidate": result.get("retro_rights_safety_candidate"),
        "source_cache_candidate_preview": result.get("source_cache_candidate_preview"),
        "evidence_candidate_preview": result.get("evidence_candidate_preview"),
        "review_queue_seed_preview": result.get("review_queue_seed_preview"),
        "connector_health_summary": result.get("connector_health_summary"),
        "validation_summary": summarize_h12_retro_community_live_probe_result(result),
    }
    _raise_on_boundary_errors(bundle)
    return bundle


def summarize_h12_retro_community_live_probe_result(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "source_id": result.get("source_id"),
        "result_status": result.get("result_status"),
        "request_count": int(result.get("request_count") or 0),
        "network_used": bool(result.get("network_used")),
        "blocked_reasons": list(result.get("blocked_reasons") or []),
        "has_retro_software_identity_candidate": isinstance(result.get("retro_software_identity_candidate"), Mapping),
        "has_platform_version_edition_candidate": isinstance(result.get("platform_version_edition_candidate"), Mapping),
        "has_archive_item_member_candidate": isinstance(result.get("archive_item_member_candidate"), Mapping),
        "has_compatibility_install_note_candidate": isinstance(result.get("compatibility_install_note_candidate"), Mapping),
        "has_community_review_comment_candidate": isinstance(result.get("community_review_comment_candidate"), Mapping),
        "has_hash_checksum_candidate": isinstance(result.get("hash_checksum_candidate"), Mapping),
        "has_ia_wayback_corroboration_candidate": isinstance(result.get("ia_wayback_corroboration_candidate"), Mapping),
        "has_gated_source_boundary_candidate": isinstance(result.get("gated_source_boundary_candidate"), Mapping),
        "has_retro_rights_safety_candidate": isinstance(result.get("retro_rights_safety_candidate"), Mapping),
        "truth_boundary_violations": detect_h12_retro_community_live_probe_truth_boundary_violations(result, {}),
        "product_boundary_violations": detect_h12_retro_community_live_probe_product_boundary_violations(result, {}),
    }


def detect_h12_retro_community_live_probe_truth_boundary_violations(result: Mapping[str, Any], policy_bundle: Mapping[str, Any] | None = None) -> list[str]:
    errors: list[str] = []
    _collect_true_keys(result, FORBIDDEN_TRUTH_TRUE_KEYS, "truth", errors)
    return errors


def detect_h12_retro_community_live_probe_product_boundary_violations(result: Mapping[str, Any], policy_bundle: Mapping[str, Any] | None = None) -> list[str]:
    errors: list[str] = []
    _collect_true_keys(result, FORBIDDEN_PRODUCT_TRUE_KEYS, "product", errors)
    return errors


def _normal_record_from_request(request: Mapping[str, Any]) -> dict[str, Any]:
    source_id = str(request.get("source_id") or "")
    cfg = SOURCE_CONFIGS.get(source_id)
    if not cfg:
        return _unknown_normalized_record(request)
    payload = {
        "source_native_id": str(request.get("retro_software_or_platform_identifier") or request.get("approved_request_key") or "blocked"),
        "source_record_kind": cfg["source_record_kind"],
        "software_title": f"Blocked metadata preview for {source_id}",
        "alternate_title": "unknown",
        "product_family": "unknown",
        "developer": "unknown",
        "publisher": "unknown",
        "platform": "unknown",
        "operating_system": "unknown",
        "version_candidate": "unknown",
        "edition_candidate": "unknown",
        "release_date_candidate": "unknown",
        "language_candidate": "unknown",
        "region_candidate": "unknown",
        "category_or_genre": "retro_community_metadata_preflight",
        "community_item_id_candidate": str(request.get("approved_request_key") or "unknown"),
        "source_locator_candidate": "blocked_preflight_no_url",
        "platform_family": "unknown",
        "platform_name": "unknown",
        "archive_item_id": "blocked_preflight_no_archive_item",
        "archive_title": f"Blocked metadata preview for {source_id}",
        "compatibility_status_candidate": "not_evaluable",
        "claim_type": "not_evaluable",
        "claim_value": "blocked preflight only",
        "hash_algorithm": "not_evaluable",
        "hash_value_candidate": "unknown",
        "corroboration_kind": "not_evaluable",
        "gated_source_ref": source_id,
        "allowed_current_mode": "blocked_current",
        "blocked_action_candidate": "live_probe_blocked_by_policy",
        "rights_statement_candidate": "not_evaluable",
        "acquisition_permission_current": False,
        "metadata_summary": "Blocked preflight request envelope; no source response payload.",
    }
    return _normalize_fixture_payload(source_id, payload, "blocked_live_probe_preflight", "blocked_by_policy")


def _normal_record_from_response(source_id: str, response_payload: Mapping[str, Any], response_metadata: Mapping[str, Any]) -> dict[str, Any]:
    payload = dict(response_payload.get("fixture_payload") if isinstance(response_payload.get("fixture_payload"), Mapping) else response_payload)
    payload.setdefault("source_native_id", response_metadata.get("source_native_id") or response_metadata.get("request_key") or "live-probe-response")
    payload.setdefault("source_record_kind", SOURCE_CONFIGS[source_id]["source_record_kind"])
    payload.setdefault("software_title", payload.get("archive_title") or f"Metadata response for {source_id}")
    payload.setdefault("platform", payload.get("platform_name") or "unknown")
    payload.setdefault("platform_name", payload.get("platform") or "unknown")
    payload.setdefault("metadata_summary", "Bounded metadata-only response payload.")
    return _normalize_fixture_payload(source_id, payload, "live_probe_metadata_response", "synthetic_or_mocked_metadata_payload")


def _normalize_fixture_payload(source_id: str, payload: Mapping[str, Any], fixture_kind: str, status: str) -> dict[str, Any]:
    fixture = {
        "schema_version": "h12_retro_community_fixture.v0",
        "fixture_id": f"h12.live_probe.fixture_equivalent.{source_id}.{_slug(payload.get('source_native_id'))}.v0",
        "source_id": source_id,
        "connector_family": SOURCE_CONFIGS[source_id]["connector_family"],
        "fixture_kind": fixture_kind,
        "fixture_status": status,
        "fixture_public_safe": True,
        "live_call_used": False,
        "network_used": False,
        "external_api_used": False,
        "catalog_payload_included": False,
        "forum_or_comment_payload_included": False,
        "gated_source_payload_included": False,
        "account_payload_included": False,
        "software_binary_payload_included": False,
        "rom_payload_included": False,
        "iso_payload_included": False,
        "disc_image_payload_included": False,
        "chd_payload_included": False,
        "bios_firmware_payload_included": False,
        "driver_payload_included": False,
        "installer_payload_included": False,
        "patch_payload_included": False,
        "crack_key_serial_payload_included": False,
        "archive_payload_included": False,
        "extraction_output_included": False,
        "execution_output_included": False,
        "acquisition_action_performed": False,
        "file_upload_performed": False,
        "hash_submission_performed": False,
        "scraping_output_included": False,
        "crawling_output_included": False,
        "restricted_source_accessed": False,
        "bypass_or_automation_used": False,
        "fixture_payload": dict(payload),
        "expected_normalized_ref": "generated_in_memory_only",
        "limitations": ["Fixture-equivalent live-probe preview only; no external request payload is included."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["No downloaded, extracted, executed, acquired, uploaded, gated, restricted, scraped, or crawled payload is present."],
    }
    return normalize_h12_retro_community_fixture(fixture, source_id)


def _unknown_normalized_record(request: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "h12_retro_community_normalized_record.v0",
        "normalized_record_id": f"h12.normalized.unknown.{_short_fingerprint(request)}.v0",
        "source_id": request.get("source_id", "unknown"),
        "connector_family": request.get("connector_family", "unknown"),
        "source_record_kind": request.get("source_record_kind", "unknown"),
        "source_limitations": ["Unknown source request could not be normalized."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "retro_software_identity_candidate": {"status": "not_created_blocked_by_policy"},
        "platform_version_edition_candidate": {"status": "not_created_blocked_by_policy"},
        "archive_item_member_candidate": {"status": "not_created_blocked_by_policy"},
        "compatibility_install_note_candidate": {"status": "not_created_blocked_by_policy"},
        "community_review_comment_candidate": {"status": "not_created_blocked_by_policy"},
        "hash_checksum_candidate": {"status": "not_created_blocked_by_policy"},
        "ia_wayback_corroboration_candidate": {"status": "not_created_blocked_by_policy"},
        "gated_source_boundary_candidate": {"status": "not_created_blocked_by_policy"},
        "retro_rights_safety_candidate": {"status": "not_created_blocked_by_policy"},
        "source_cache_candidate_preview": {"status": "not_created_blocked_by_policy"},
        "evidence_candidate_preview": {"status": "not_created_blocked_by_policy"},
    }


def _source_policy(source_id: str, policy_bundle: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    payload = policy_bundle.get(key, {})
    for item in payload.get("sources", []) if isinstance(payload, Mapping) else []:
        if isinstance(item, Mapping) and item.get("source_id") == source_id:
            return item
    return {}


def _status_for_reasons(reasons: list[str]) -> str:
    text = " ".join(reasons).casefold()
    if not reasons:
        return "dry_run_preflight_pass"
    if (
        "api_query_requested" in text
        or "catalog_fetch_requested" in text
        or "html_catalog_fetch_requested" in text
        or "forum_or_comment_fetch_requested" in text
        or "web_archive_trace_fetch_requested" in text
    ):
        return "blocked_by_missing_approval"
    if "extraction" in text or "extract" in text:
        return "blocked_by_extraction_policy"
    if "execution" in text or "execute" in text or "emulator" in text or "install_execute" in text:
        return "blocked_by_execution_policy"
    if "acquisition" in text or "mirror" in text:
        return "blocked_by_acquisition_policy"
    if "upload" in text or "hash_submission" in text:
        return "blocked_by_upload_policy"
    if "gated" in text or "account" in text or "credential" in text:
        return "blocked_by_gated_source_policy"
    if "download" in text or "payload" in text or "rom" in text or "iso" in text or "firmware" in text or "driver" in text or "patch" in text or "serial" in text or "archive" in text:
        return "blocked_by_download_policy"
    if "restricted" in text or "piracy" in text or "leaked" in text:
        return "blocked_by_restricted_source_policy"
    if "bypass" in text or "automation" in text or "scraping" in text or "crawling" in text or "browser" in text:
        return "blocked_by_bypass_policy"
    if "approval" in text or "approved" in text or "request key" in text or "not listed" in text:
        return "blocked_by_missing_approval"
    if "endpoint" in text:
        return "blocked_by_endpoint_policy"
    if "kill switch" in text:
        return "blocked_by_kill_switch"
    return "blocked_by_policy"


def _truth_boundary() -> dict[str, bool]:
    return {key: False for key in FORBIDDEN_TRUTH_TRUE_KEYS}


def _product_boundary() -> dict[str, bool]:
    return {key: False for key in FORBIDDEN_PRODUCT_TRUE_KEYS}


def _raise_on_boundary_errors(record: Mapping[str, Any]) -> None:
    errors = detect_h12_retro_community_live_probe_truth_boundary_violations(record, {}) + detect_h12_retro_community_live_probe_product_boundary_violations(record, {})
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


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        text = str(value)
        if text and text not in seen:
            out.append(text)
            seen.add(text)
    return out


def _slug(value: Any) -> str:
    text = str(value or "unknown")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def _short_fingerprint(value: Any) -> str:
    try:
        text = json.dumps(value, sort_keys=True, default=str)
    except TypeError:
        text = str(value)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
