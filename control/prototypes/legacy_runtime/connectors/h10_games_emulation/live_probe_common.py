"""Fail-closed H10 games/emulation live-probe helpers."""

from __future__ import annotations

from collections.abc import Mapping
import hashlib
import json
from pathlib import Path
from typing import Any
import urllib.error
import urllib.request

from control.prototypes.legacy_runtime.connectors.h10_games_emulation.normalizer_common import (
    build_h10_evidence_candidate_preview as _fixture_evidence_preview,
    build_h10_game_relation_candidates as _fixture_relation_candidates,
    build_h10_game_software_identity_candidate as _fixture_game_candidate,
    build_h10_emulator_action_candidate as _fixture_action_candidate,
    build_h10_emulator_compatibility_candidate as _fixture_compatibility_candidate,
    build_h10_games_rights_safety_candidate as _fixture_rights_safety_candidate,
    build_h10_platform_release_edition_candidate as _fixture_release_candidate,
    build_h10_preservation_hashset_candidate as _fixture_hashset_candidate,
    build_h10_rom_disc_media_identity_candidate as _fixture_media_candidate,
    build_h10_source_cache_candidate_preview as _fixture_source_cache_preview,
    detect_h10_product_boundary_violations as _fixture_product_violations,
    detect_h10_truth_boundary_violations as _fixture_truth_violations,
    normalize_h10_games_emulation_fixture,
)

POLICY_PATHS = {
    "live_probe_policy": "control/inventory/connectors/h10_games_emulation_live_probe_policy.json",
    "allowed_requests": "control/inventory/connectors/h10_games_emulation_live_probe_allowed_requests.json",
    "endpoint_policy": "control/inventory/connectors/h10_games_emulation_live_probe_endpoint_policy.json",
    "rate_limit_policy": "control/inventory/connectors/h10_games_emulation_live_probe_rate_limit_policy.json",
    "cache_policy": "control/inventory/connectors/h10_games_emulation_live_probe_cache_policy.json",
    "kill_switch_policy": "control/inventory/connectors/h10_games_emulation_live_probe_kill_switch_policy.json",
    "output_policy": "control/inventory/connectors/h10_games_emulation_live_probe_output_policy.json",
    "path_policy": "control/inventory/connectors/h10_games_emulation_live_probe_path_policy.json",
    "review_policy": "control/inventory/connectors/h10_games_emulation_live_probe_review_policy.json",
    "truth_policy": "control/inventory/connectors/h10_games_emulation_live_probe_truth_policy.json",
    "no_download_execute_policy": "control/inventory/connectors/h10_games_emulation_live_probe_no_download_execute_policy.json",
    "restricted_source_policy": "control/inventory/connectors/h10_games_emulation_live_probe_restricted_source_policy.json",
}
SOURCE_CONFIGS = {'mobygames': {'label': 'MobyGames metadata', 'connector_family': 'game_database_api', 'source_record_kind': 'game_metadata', 'endpoint': 'game_metadata_lookup_future', 'request_key': 'example_game_metadata', 'fixture_kind': 'game_identity'}, 'mame_software_lists': {'label': 'MAME software lists metadata', 'connector_family': 'software_list_metadata', 'source_record_kind': 'software_list_metadata', 'endpoint': 'software_list_metadata_lookup_future', 'request_key': 'example_software_list_metadata', 'fixture_kind': 'platform_release_edition'}, 'scummvm_compatibility': {'label': 'ScummVM compatibility metadata', 'connector_family': 'emulator_compatibility_metadata', 'source_record_kind': 'emulator_compatibility_metadata', 'endpoint': 'compatibility_metadata_lookup_future', 'request_key': 'example_compatibility_metadata', 'fixture_kind': 'emulator_compatibility'}, 'redump_hash_sets': {'label': 'Redump hash-set metadata', 'connector_family': 'preservation_hashset_metadata', 'source_record_kind': 'preservation_hashset_metadata', 'endpoint': 'hashset_metadata_lookup_future', 'request_key': 'example_hashset_metadata', 'fixture_kind': 'preservation_hashset'}, 'no_intro_hash_sets': {'label': 'No-Intro hash-set metadata', 'connector_family': 'preservation_hashset_metadata', 'source_record_kind': 'preservation_hashset_metadata', 'endpoint': 'hashset_metadata_lookup_future', 'request_key': 'example_hashset_metadata', 'fixture_kind': 'preservation_hashset'}, 'tosec_hash_sets': {'label': 'TOSEC hash-set metadata', 'connector_family': 'preservation_hashset_metadata', 'source_record_kind': 'preservation_hashset_metadata', 'endpoint': 'hashset_metadata_lookup_future', 'request_key': 'example_hashset_metadata', 'fixture_kind': 'preservation_hashset'}, 'flashpoint_metadata': {'label': 'Flashpoint metadata', 'connector_family': 'web_game_archive_metadata', 'source_record_kind': 'web_game_metadata', 'endpoint': 'web_game_metadata_lookup_future', 'request_key': 'example_web_game_metadata', 'fixture_kind': 'game_identity'}, 'steam_game_metadata_policy_limited': {'label': 'Steam game metadata, policy-limited', 'connector_family': 'game_storefront_metadata', 'source_record_kind': 'storefront_game_metadata', 'endpoint': 'storefront_metadata_lookup_future', 'request_key': 'example_storefront_metadata', 'fixture_kind': 'game_identity'}, 'gog_game_metadata_policy_limited': {'label': 'GOG game metadata, policy-limited', 'connector_family': 'game_storefront_metadata', 'source_record_kind': 'storefront_game_metadata', 'endpoint': 'storefront_metadata_lookup_future', 'request_key': 'example_storefront_metadata', 'fixture_kind': 'game_identity'}, 'itchio_game_metadata_policy_limited': {'label': 'itch.io game metadata, policy-limited', 'connector_family': 'game_storefront_metadata', 'source_record_kind': 'storefront_game_metadata', 'endpoint': 'storefront_metadata_lookup_future', 'request_key': 'example_storefront_metadata', 'fixture_kind': 'game_identity'}, 'generic_game_database': {'label': 'Generic game database metadata', 'connector_family': 'game_database_api', 'source_record_kind': 'game_metadata', 'endpoint': 'game_metadata_fixture_future', 'request_key': 'example_game_metadata', 'fixture_kind': 'game_identity'}, 'generic_emulator_compatibility': {'label': 'Generic emulator compatibility metadata', 'connector_family': 'emulator_compatibility_metadata', 'source_record_kind': 'emulator_compatibility_metadata', 'endpoint': 'emulator_compatibility_fixture_future', 'request_key': 'example_compatibility_metadata', 'fixture_kind': 'game_identity'}, 'generic_preservation_hashset': {'label': 'Generic preservation hash-set metadata', 'connector_family': 'preservation_hashset_metadata', 'source_record_kind': 'preservation_hashset_metadata', 'endpoint': 'hashset_metadata_fixture_future', 'request_key': 'example_hashset_metadata', 'fixture_kind': 'preservation_hashset'}, 'games_emulation_policy_blocked': {'label': 'Generic game/software identity policy-blocked source', 'connector_family': 'restricted_manifest_only', 'source_record_kind': 'policy_blocked_game_software_identity', 'endpoint': 'manifest_only_policy_blocked_current', 'request_key': 'example_manifest_metadata', 'fixture_kind': 'policy_blocked'}}
H10_SOURCE_IDS = tuple(SOURCE_CONFIGS)
REQUEST_FORBIDDEN_TRUE_KEYS = {
    "rom_download_requested",
    "iso_download_requested",
    "disc_image_download_requested",
    "chd_download_requested",
    "bios_firmware_download_requested",
    "game_binary_download_requested",
    "emulator_download_requested",
    "installer_download_requested",
    "patch_download_requested",
    "asset_download_requested",
    "file_upload_requested",
    "hash_submission_requested",
    "emulator_execution_requested",
    "game_execution_requested",
    "install_execute_requested",
    "acquisition_action_requested",
    "scraping_or_crawling_requested",
    "restricted_source_requested",
    "bypass_or_automation_requested",
}
CONDITIONAL_REQUEST_KEYS = {
    "api_query_requested": "api_query_approved",
    "catalog_fetch_requested": "catalog_fetch_approved",
    "software_list_fetch_requested": "software_list_fetch_approved",
    "hashset_fetch_requested": "hashset_fetch_approved",
}
FORBIDDEN_TRUTH_TRUE_KEYS = {'accepted_hashset_truth', 'playability_claimed', 'verified_authenticity_claimed', 'emulator_compatibility_candidate_is_truth', 'installability_claimed', 'compatibility_correctness_claimed', 'game_relation_candidate_is_truth', 'evidence_preview_is_accepted_evidence', 'acquisition_permission_granted', 'download_permission_granted', 'accepted_release_truth', 'accepted_emulator_compatibility_truth', 'normalized_record_is_public_truth', 'production_readiness_claimed', 'platform_release_edition_candidate_is_truth', 'storefront_metadata_grants_acquisition_permission', 'source_cache_candidate_is_accepted_source', 'disc_authenticity_claimed', 'privacy_safety_claimed', 'accepted_candidate_truth', 'rom_disc_media_candidate_is_truth', 'legal_acquisition_claimed', 'media_identity_grants_download_permission', 'evidence_candidate_preview_is_accepted_evidence', 'accepted_game_relation_truth', 'accepted_action_permission', 'rights_clearance_claimed', 'rom_disc_media_identity_candidate_is_truth', 'rights_safety_candidate_is_rights_or_safety_truth', 'malware_safety_claimed', 'accepted_public_record', 'game_software_identity_candidate_is_truth', 'accepted_source_truth', 'content_safety_claimed', 'accepted_game_identity_truth', 'rom_authenticity_claimed', 'compatibility_metadata_proves_playability', 'review_seed_is_review_decision', 'live_probe_result_is_public_truth', 'source_cache_preview_is_accepted_source', 'master_index_mutated', 'public_index_mutated', 'hash_metadata_proves_authenticity', 'hash_submission_permission_granted', 'upload_permission_granted', 'accepted_evidence_truth', 'accepted_rom_disc_media_truth', 'execution_permission_granted', 'accepted_platform_truth', 'preservation_hashset_candidate_is_truth', 'emulator_action_candidate_is_action_permission', 'accepted_rights_safety_truth'}
FORBIDDEN_PRODUCT_TRUE_KEYS = {'emulator_download_used', 'enabled_live_probes', 'enabled_downloads', 'enabled_execution', 'game_execution_used', 'changed_public_search_behavior', 'install_execute_used', 'hash_submission_used', 'patch_download_used', 'enabled_accounts', 'emulator_execution_used', 'rom_download_used', 'enabled_uploads', 'enabled_crawling', 'acquisition_action_used', 'software_list_fetch_used', 'catalog_fetch_used', 'mutated_public_index', 'game_binary_download_used', 'enabled_source_sync', 'bios_firmware_download_used', 'disc_image_download_used', 'chd_download_used', 'browser_automation_used', 'mutated_master_index', 'asset_download_used', 'enabled_acquisition_actions', 'enabled_hosting', 'api_calls_made', 'enabled_scraping', 'file_upload_used', 'hashset_fetch_used', 'restricted_source_access_used', 'installer_download_used', 'enabled_telemetry', 'network_calls_made', 'iso_download_used', 'scraping_used', 'bypass_or_automation_used', 'crawling_used'}
TRUTH_BOUNDARY = {'live_probe_result_is_public_truth': False, 'normalized_record_is_public_truth': False, 'game_software_identity_candidate_is_truth': False, 'platform_release_edition_candidate_is_truth': False, 'emulator_compatibility_candidate_is_truth': False, 'preservation_hashset_candidate_is_truth': False, 'rom_disc_media_identity_candidate_is_truth': False, 'rom_disc_media_candidate_is_truth': False, 'game_relation_candidate_is_truth': False, 'emulator_action_candidate_is_action_permission': False, 'rights_safety_candidate_is_rights_or_safety_truth': False, 'hash_metadata_proves_authenticity': False, 'storefront_metadata_grants_acquisition_permission': False, 'compatibility_metadata_proves_playability': False, 'media_identity_grants_download_permission': False, 'source_cache_candidate_is_accepted_source': False, 'source_cache_preview_is_accepted_source': False, 'evidence_candidate_preview_is_accepted_evidence': False, 'evidence_preview_is_accepted_evidence': False, 'review_seed_is_review_decision': False, 'accepted_source_truth': False, 'accepted_evidence_truth': False, 'accepted_candidate_truth': False, 'accepted_game_identity_truth': False, 'accepted_release_truth': False, 'accepted_platform_truth': False, 'accepted_emulator_compatibility_truth': False, 'accepted_hashset_truth': False, 'accepted_rom_disc_media_truth': False, 'accepted_game_relation_truth': False, 'accepted_action_permission': False, 'accepted_rights_safety_truth': False, 'accepted_public_record': False, 'public_index_mutated': False, 'master_index_mutated': False, 'rights_clearance_claimed': False, 'legal_acquisition_claimed': False, 'rom_authenticity_claimed': False, 'disc_authenticity_claimed': False, 'compatibility_correctness_claimed': False, 'playability_claimed': False, 'installability_claimed': False, 'malware_safety_claimed': False, 'content_safety_claimed': False, 'privacy_safety_claimed': False, 'verified_authenticity_claimed': False, 'production_readiness_claimed': False, 'download_permission_granted': False, 'upload_permission_granted': False, 'hash_submission_permission_granted': False, 'execution_permission_granted': False, 'acquisition_permission_granted': False}
PRODUCT_BOUNDARY = {'changed_public_search_behavior': False, 'enabled_hosting': False, 'enabled_live_probes': False, 'enabled_source_sync': False, 'enabled_downloads': False, 'enabled_uploads': False, 'enabled_execution': False, 'enabled_acquisition_actions': False, 'enabled_crawling': False, 'enabled_scraping': False, 'enabled_accounts': False, 'enabled_telemetry': False, 'mutated_public_index': False, 'mutated_master_index': False, 'network_calls_made': False, 'api_calls_made': False, 'catalog_fetch_used': False, 'software_list_fetch_used': False, 'hashset_fetch_used': False, 'rom_download_used': False, 'iso_download_used': False, 'disc_image_download_used': False, 'chd_download_used': False, 'bios_firmware_download_used': False, 'game_binary_download_used': False, 'emulator_download_used': False, 'installer_download_used': False, 'patch_download_used': False, 'asset_download_used': False, 'file_upload_used': False, 'hash_submission_used': False, 'emulator_execution_used': False, 'game_execution_used': False, 'install_execute_used': False, 'acquisition_action_used': False, 'scraping_used': False, 'crawling_used': False, 'browser_automation_used': False, 'restricted_source_access_used': False, 'bypass_or_automation_used': False}


def load_h10_games_emulation_live_probe_policy_bundle(root: str | Path | None = None) -> dict[str, Any]:
    base = Path(root) if root is not None else Path(__file__).resolve().parents[5]
    return {key: json.loads((base / rel).read_text(encoding="utf-8")) for key, rel in POLICY_PATHS.items()}


def build_h10_games_emulation_live_probe_request(source_id: str, request_key: str, policy_bundle: Mapping[str, Any], live_requested: bool = False) -> dict[str, Any]:
    if source_id not in SOURCE_CONFIGS:
        raise ValueError(f"unknown H10 source_id: {source_id}")
    cfg = SOURCE_CONFIGS[source_id]
    request = {
        "schema_version": "h10_games_emulation_live_probe_request.v0",
        "live_probe_request_id": f"h10.live_probe_request.{source_id}.{_slug(request_key)}.v0",
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
        "game_or_software_identifier": f"metadata-only-candidate:{source_id}:{request_key}",
        "platform_or_release_context": "candidate_metadata_context_only",
        "emulator_or_compatibility_context": "candidate_metadata_context_only_no_execution",
        "hashset_or_media_context": "candidate_metadata_context_only_no_payload_no_hash_submission",
        "storefront_or_availability_context": "candidate_metadata_context_only_no_account_no_acquisition",
        "approval_refs": [POLICY_PATHS["allowed_requests"]],
        "policy_refs": list(POLICY_PATHS.values()),
        "live_requested": bool(live_requested),
        "dry_run_only": not bool(live_requested),
        "api_query_requested": False,
        "catalog_fetch_requested": False,
        "software_list_fetch_requested": False,
        "hashset_fetch_requested": False,
        "rom_download_requested": False,
        "iso_download_requested": False,
        "disc_image_download_requested": False,
        "chd_download_requested": False,
        "bios_firmware_download_requested": False,
        "game_binary_download_requested": False,
        "emulator_download_requested": False,
        "installer_download_requested": False,
        "patch_download_requested": False,
        "asset_download_requested": False,
        "file_upload_requested": False,
        "hash_submission_requested": False,
        "emulator_execution_requested": False,
        "game_execution_requested": False,
        "install_execute_requested": False,
        "acquisition_action_requested": False,
        "scraping_or_crawling_requested": False,
        "restricted_source_requested": False,
        "bypass_or_automation_requested": False,
        "output_policy_ref": POLICY_PATHS["output_policy"],
        "review_policy_ref": POLICY_PATHS["review_policy"],
        "truth_policy_ref": POLICY_PATHS["truth_policy"],
        "limitations": ["Request envelope is fail-closed unless committed source policy approves the exact metadata-only request."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["H10-BUNDLE-03 examples are dry preflight by default and do not call networks."],
    }
    _raise_on_boundary_errors(request, policy_bundle)
    return request


def validate_h10_games_emulation_live_probe_request(request: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []
    source_id = str(request.get("source_id") or "")
    request_key = str(request.get("approved_request_key") or "")
    allowed = _source_policy(source_id, policy_bundle, "allowed_requests") if source_id in SOURCE_CONFIGS else {}
    if source_id not in SOURCE_CONFIGS:
        reasons.append(f"{source_id or 'missing_source'} is not a known H10 games/emulation source")
    else:
        cfg = SOURCE_CONFIGS[source_id]
        if request.get("operation_scope") != "metadata_only":
            reasons.append("approved_operation_scope must be metadata_only")
        endpoint = str(request.get("endpoint_or_metadata_class") or "")
        if endpoint != cfg["endpoint"]:
            if "download" in endpoint.lower() or "payload" in endpoint.lower():
                reasons.append("endpoint_or_metadata_class download/payload class is forbidden")
            else:
                reasons.append("endpoint_or_metadata_class is not the planned source metadata class")
    for request_field, approval_field in CONDITIONAL_REQUEST_KEYS.items():
        if request.get(request_field) is True and allowed.get(approval_field) is not True:
            reasons.append(f"{request_field} is not approved without exact committed bounded metadata policy")
    for key in sorted(REQUEST_FORBIDDEN_TRUE_KEYS):
        if request.get(key) is True:
            reasons.append(f"{key} is forbidden for H10-BUNDLE-03 live probes")
    if source_id in SOURCE_CONFIGS:
        reasons.extend(validate_h10_source_approval(source_id, request_key, policy_bundle)["blocked_reasons"])
    reasons = _dedupe(reasons)
    return {"approved": not reasons, "result_status": _status_for_reasons(reasons), "blocked_reasons": reasons}


def validate_h10_source_approval(source_id: str, request_key: str, policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []
    if source_id not in SOURCE_CONFIGS:
        return {"approved": False, "result_status": "blocked_by_policy", "blocked_reasons": [f"{source_id} is not a known H10 source"]}
    cfg = SOURCE_CONFIGS[source_id]
    allowed = _source_policy(source_id, policy_bundle, "allowed_requests")
    if not allowed:
        reasons.append("source is not listed in H10 allowed request policy")
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
            "rom_download_approved",
            "iso_download_approved",
            "disc_image_download_approved",
            "chd_download_approved",
            "bios_firmware_download_approved",
            "game_binary_download_approved",
            "emulator_download_approved",
            "installer_download_approved",
            "patch_download_approved",
            "asset_download_approved",
            "file_upload_approved",
            "hash_submission_approved",
            "emulator_execution_approved",
            "game_execution_approved",
            "install_execute_approved",
            "acquisition_action_approved",
            "scraping_approved",
            "crawling_approved",
            "browser_automation_approved",
            "restricted_rights_sensitive_source_approved",
            "drm_or_access_control_bypass_approved",
            "bypass_or_automation_approved",
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


def build_h10_games_emulation_live_probe_blocked_result(request: Mapping[str, Any], reason: str | list[str], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    source_id = str(request.get("source_id") or "unknown")
    cfg = SOURCE_CONFIGS.get(source_id, {"connector_family": request.get("connector_family", "unknown"), "source_record_kind": request.get("source_record_kind", "unknown"), "endpoint": request.get("endpoint_or_metadata_class", "unknown")})
    reasons = reason if isinstance(reason, list) else [str(reason)]
    status = _status_for_reasons(reasons)
    result: dict[str, Any] = {
        "schema_version": "h10_games_emulation_live_probe_result.v0",
        "live_probe_result_id": f"h10.live_probe_result.{source_id}.blocked.{_short_fingerprint(request)}.v0",
        "live_probe_request_ref": request.get("live_probe_request_id"),
        "source_id": source_id,
        "connector_family": str(cfg.get("connector_family") or "unknown"),
        "source_record_kind": str(cfg.get("source_record_kind") or "unknown"),
        "result_status": status,
        "request_count": 0,
        "network_used": False,
        "endpoint_or_metadata_used": request.get("endpoint_or_metadata_class"),
        "response_status_code": None,
        "response_fingerprint": "",
        "response_summary": "blocked before network",
        "normalized_record": _blocked_candidate(),
        "game_software_identity_candidate": _blocked_candidate(),
        "platform_release_edition_candidate": _blocked_candidate(),
        "emulator_compatibility_candidate": _blocked_candidate(),
        "preservation_hashset_candidate": _blocked_candidate(),
        "rom_disc_media_identity_candidate": _blocked_candidate(),
        "game_relation_candidate": [_blocked_candidate()],
        "emulator_action_candidate": _blocked_candidate(),
        "games_rights_safety_candidate": _blocked_candidate(),
        "source_cache_candidate_preview": _blocked_candidate(),
        "evidence_candidate_preview": _blocked_candidate(),
        "review_queue_seed_preview": _blocked_review_seed(source_id, status, reasons),
        "connector_health_summary": {},
        "blocked_reason": "; ".join(reasons),
        "blocked_reasons": reasons,
        "warnings": [],
        "limitations": ["No network call was made. Live probe is blocked unless every committed approval gate passes."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["Fail-closed blocked H10 live-probe result."],
    }
    result["connector_health_summary"] = build_h10_connector_health_summary(result, policy_bundle)
    _raise_on_boundary_errors(result, policy_bundle)
    return result


def build_h10_games_emulation_live_probe_result(source_id: str, response_payload: Mapping[str, Any], response_metadata: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    if source_id not in SOURCE_CONFIGS:
        raise ValueError(f"unknown H10 source_id: {source_id}")
    payload = _metadata_payload_defaults(source_id, response_payload)
    fixture = _fixture_from_payload(source_id, payload)
    normalized = normalize_h10_games_emulation_fixture(fixture, source_id)
    source_cache = build_h10_source_cache_candidate_preview_from_probe(normalized, policy_bundle)
    evidence = build_h10_evidence_candidate_preview_from_probe(normalized, policy_bundle)
    status = str(response_metadata.get("result_status") or "live_probe_completed")
    request_count = int(response_metadata.get("request_count") if response_metadata.get("request_count") is not None else (1 if response_metadata.get("network_used") else 0))
    result: dict[str, Any] = {
        "schema_version": "h10_games_emulation_live_probe_result.v0",
        "live_probe_result_id": f"h10.live_probe_result.{source_id}.{_slug(str(payload.get('source_native_id') or 'metadata'))}.{_short_fingerprint(payload)}.v0",
        "live_probe_request_ref": response_metadata.get("live_probe_request_ref") or f"h10.live_probe_request.{source_id}.{_slug(str(response_metadata.get('request_key') or SOURCE_CONFIGS[source_id]['request_key']))}.v0",
        "source_id": source_id,
        "connector_family": SOURCE_CONFIGS[source_id]["connector_family"],
        "source_record_kind": SOURCE_CONFIGS[source_id]["source_record_kind"],
        "result_status": status,
        "request_count": request_count,
        "network_used": bool(response_metadata.get("network_used")),
        "endpoint_or_metadata_used": response_metadata.get("endpoint_or_metadata_used") or SOURCE_CONFIGS[source_id]["endpoint"],
        "response_status_code": response_metadata.get("response_status_code"),
        "response_fingerprint": _fingerprint(payload),
        "response_summary": response_metadata.get("response_summary") or "metadata-only response payload normalized as candidate previews",
        "normalized_record": normalized,
        "game_software_identity_candidate": build_h10_game_software_identity_candidate_from_probe(normalized, policy_bundle),
        "platform_release_edition_candidate": build_h10_platform_release_edition_candidate_from_probe(normalized, policy_bundle),
        "emulator_compatibility_candidate": build_h10_emulator_compatibility_candidate_from_probe(normalized, policy_bundle),
        "preservation_hashset_candidate": build_h10_preservation_hashset_candidate_from_probe(normalized, policy_bundle),
        "rom_disc_media_identity_candidate": build_h10_rom_disc_media_identity_candidate_from_probe(normalized, policy_bundle),
        "game_relation_candidate": build_h10_game_relation_candidate_from_probe(normalized, policy_bundle),
        "emulator_action_candidate": build_h10_emulator_action_candidate_from_probe(normalized, policy_bundle),
        "games_rights_safety_candidate": build_h10_games_rights_safety_candidate_from_probe(normalized, policy_bundle),
        "source_cache_candidate_preview": source_cache,
        "evidence_candidate_preview": evidence,
        "review_queue_seed_preview": {},
        "connector_health_summary": {},
        "blocked_reason": None,
        "blocked_reasons": [],
        "warnings": list(response_metadata.get("warnings") or []),
        "limitations": list(normalized.get("source_limitations") or []) + ["Live-probe result remains a candidate preview and does not accept truth or grant permissions."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["Built from bounded metadata response payload; no media/game payload is included."],
    }
    result["review_queue_seed_preview"] = build_h10_review_queue_seed_preview_from_probe(result, source_cache, evidence, policy_bundle)
    result["connector_health_summary"] = build_h10_connector_health_summary(result, policy_bundle)
    _raise_on_boundary_errors(result, policy_bundle)
    return result


def normalize_h10_games_emulation_live_probe_result(result: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    _raise_on_boundary_errors(result, policy_bundle)
    return dict(result)


def build_h10_game_software_identity_candidate_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return _fixture_game_candidate(normalized_record)


def build_h10_platform_release_edition_candidate_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return _fixture_release_candidate(normalized_record)


def build_h10_emulator_compatibility_candidate_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return _fixture_compatibility_candidate(normalized_record)


def build_h10_preservation_hashset_candidate_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return _fixture_hashset_candidate(normalized_record)


def build_h10_rom_disc_media_identity_candidate_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return _fixture_media_candidate(normalized_record)


def build_h10_game_relation_candidate_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> list[dict[str, Any]]:
    return _fixture_relation_candidates(normalized_record)


def build_h10_emulator_action_candidate_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return _fixture_action_candidate(normalized_record)


def build_h10_games_rights_safety_candidate_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return _fixture_rights_safety_candidate(normalized_record)


def build_h10_source_cache_candidate_preview_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return _fixture_source_cache_preview(normalized_record)


def build_h10_evidence_candidate_preview_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return _fixture_evidence_preview(normalized_record)


def build_h10_review_queue_seed_preview_from_probe(result: Mapping[str, Any], source_cache_preview: Mapping[str, Any], evidence_preview: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    source_id = str(result.get("source_id") or "unknown")
    seed = {
        "schema_version": "h10_games_emulation_live_probe_review_seed.v0",
        "review_queue_seed_preview_id": f"h10.review_seed_preview.{source_id}.{_short_fingerprint(result)}.v0",
        "source_id": source_id,
        "live_probe_result_ref": result.get("live_probe_result_id"),
        "source_cache_candidate_preview_ref": source_cache_preview.get("preview_id") if isinstance(source_cache_preview, Mapping) else None,
        "evidence_candidate_preview_ref": evidence_preview.get("preview_id") if isinstance(evidence_preview, Mapping) else None,
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


def build_h10_connector_health_summary(result: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    source_id = str(result.get("source_id") or "unknown")
    cfg = SOURCE_CONFIGS.get(source_id, {})
    health = {
        "schema_version": "h10_games_emulation_connector_health_summary.v0",
        "health_summary_id": f"h10.connector_health.{source_id}.{_short_fingerprint(result)}.v0",
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


def build_h10_games_emulation_live_probe_output_bundle(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "h10_games_emulation_live_probe_output_bundle.v0",
        "live_probe_result": dict(result),
        "normalized_record": result.get("normalized_record", {}),
        "game_software_identity_candidate": result.get("game_software_identity_candidate", {}),
        "platform_release_edition_candidate": result.get("platform_release_edition_candidate", {}),
        "emulator_compatibility_candidate": result.get("emulator_compatibility_candidate", {}),
        "preservation_hashset_candidate": result.get("preservation_hashset_candidate", {}),
        "rom_disc_media_identity_candidate": result.get("rom_disc_media_identity_candidate", {}),
        "game_relation_candidate": result.get("game_relation_candidate", []),
        "emulator_action_candidate": result.get("emulator_action_candidate", {}),
        "games_rights_safety_candidate": result.get("games_rights_safety_candidate", {}),
        "source_cache_candidate_preview": result.get("source_cache_candidate_preview", {}),
        "evidence_candidate_preview": result.get("evidence_candidate_preview", {}),
        "review_queue_seed_preview": result.get("review_queue_seed_preview", {}),
        "connector_health_summary": result.get("connector_health_summary", {}),
        "validation_summary": {
            "truth_boundary_violations": detect_h10_games_emulation_live_probe_truth_boundary_violations(result, {}),
            "product_boundary_violations": detect_h10_games_emulation_live_probe_product_boundary_violations(result, {}),
        },
    }


def summarize_h10_games_emulation_live_probe_result(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "h10_games_emulation_live_probe_summary.v0",
        "source_id": result.get("source_id"),
        "result_status": result.get("result_status"),
        "request_count": int(result.get("request_count") or 0),
        "network_used": bool(result.get("network_used")),
        "blocked_reasons": list(result.get("blocked_reasons") or []),
        "game_software_identity_candidate_present": _present(result.get("game_software_identity_candidate")),
        "platform_release_edition_candidate_present": _present(result.get("platform_release_edition_candidate")),
        "emulator_compatibility_candidate_present": _present(result.get("emulator_compatibility_candidate")),
        "preservation_hashset_candidate_present": _present(result.get("preservation_hashset_candidate")),
        "rom_disc_media_identity_candidate_present": _present(result.get("rom_disc_media_identity_candidate")),
        "game_relation_candidate_present": bool(result.get("game_relation_candidate")) and not _blocked(result.get("game_relation_candidate")),
        "emulator_action_candidate_present": _present(result.get("emulator_action_candidate")),
        "rights_safety_candidate_present": _present(result.get("games_rights_safety_candidate")),
        "source_cache_preview_present": _present(result.get("source_cache_candidate_preview")),
        "evidence_preview_present": _present(result.get("evidence_candidate_preview")),
        "review_seed_present": _present(result.get("review_queue_seed_preview")),
        "connector_health_present": _present(result.get("connector_health_summary")),
    }


def detect_h10_games_emulation_live_probe_truth_boundary_violations(result: Mapping[str, Any], policy_bundle: Mapping[str, Any] | None = None) -> list[str]:
    return _fixture_truth_violations(result) + _detect_true_keys(result, FORBIDDEN_TRUTH_TRUE_KEYS, "truth")


def detect_h10_games_emulation_live_probe_product_boundary_violations(result: Mapping[str, Any], policy_bundle: Mapping[str, Any] | None = None) -> list[str]:
    return _fixture_product_violations(result) + _detect_true_keys(result, FORBIDDEN_PRODUCT_TRUE_KEYS, "product")


def _metadata_payload_defaults(source_id: str, response_payload: Mapping[str, Any]) -> dict[str, Any]:
    payload = dict(response_payload)
    cfg = SOURCE_CONFIGS[source_id]
    payload.setdefault("source_record_kind", cfg["source_record_kind"])
    payload.setdefault("source_native_id", f"{source_id}-metadata-candidate")
    payload.setdefault("game_title", f"Synthetic {cfg['label']} record")
    payload.setdefault("alternate_title", [f"{cfg['label']} metadata preview"])
    payload.setdefault("series_or_franchise", "unknown")
    payload.setdefault("developer", cfg["label"])
    payload.setdefault("publisher", cfg["label"])
    payload.setdefault("platform", "metadata-only-platform-candidate")
    payload.setdefault("release_date_candidate", "2026-05-11")
    payload.setdefault("region_candidate", "unknown")
    payload.setdefault("language_candidate", "en")
    payload.setdefault("genre_or_category", "metadata_only")
    payload.setdefault("game_database_id_candidate", f"game-db-candidate-{source_id}")
    payload.setdefault("mobygames_id_candidate", f"mobygames-candidate-{source_id}" if source_id == "mobygames" else "unknown")
    payload.setdefault("steam_app_id_candidate", f"steam-candidate-{source_id}" if source_id == "steam_game_metadata_policy_limited" else "unknown")
    payload.setdefault("gog_id_candidate", f"gog-candidate-{source_id}" if source_id == "gog_game_metadata_policy_limited" else "unknown")
    payload.setdefault("itch_id_candidate", f"itch-candidate-{source_id}" if source_id == "itchio_game_metadata_policy_limited" else "unknown")
    payload.setdefault("software_list_id_candidate", f"software-list-candidate-{source_id}" if source_id == "mame_software_lists" else "unknown")
    payload.setdefault("platform_family", "metadata_only")
    payload.setdefault("platform_name", payload.get("platform", "metadata-only-platform-candidate"))
    payload.setdefault("hardware_or_os_version", "unknown")
    payload.setdefault("release_title", payload.get("game_title", f"{cfg['label']} release candidate"))
    payload.setdefault("release_region", payload.get("region_candidate", "unknown"))
    payload.setdefault("release_language", payload.get("language_candidate", "en"))
    payload.setdefault("edition_name", "metadata_only")
    payload.setdefault("version_or_revision", "unknown")
    payload.setdefault("media_type", "metadata_record")
    payload.setdefault("emulator_or_runtime", "metadata_only_no_execution")
    payload.setdefault("emulator_version_candidate", "unknown")
    payload.setdefault("compatibility_status_candidate", "candidate_only_not_verified")
    payload.setdefault("supported_features_candidate", [])
    payload.setdefault("unsupported_features_candidate", [])
    payload.setdefault("known_issue_candidate", "unknown")
    payload.setdefault("required_bios_or_firmware_candidate", "unknown_not_acquisition_permission")
    payload.setdefault("required_patch_candidate", "unknown_not_download_permission")
    payload.setdefault("configuration_hint_candidate", "metadata_only_not_execution_permission")
    payload.setdefault("hashset_name", "metadata_only_hashset_candidate")
    payload.setdefault("hash_algorithm", "sha256-candidate")
    payload.setdefault("hash_value_candidate", "candidate-only-not-authenticity-proof")
    payload.setdefault("file_name_candidate", "metadata-only-file-candidate")
    payload.setdefault("file_size_candidate", "unknown")
    payload.setdefault("dump_status_candidate", "candidate_only_source_specific")
    payload.setdefault("disc_id_candidate", "unknown")
    payload.setdefault("serial_candidate", "unknown")
    payload.setdefault("product_code_candidate", "unknown")
    payload.setdefault("storefront_availability_candidate", "candidate_only_not_acquisition_permission")
    payload.setdefault("rights_safety_metadata", {
        "rights_statement_candidate": "candidate only",
        "rights_clearance_claimed": False,
        "legal_acquisition_claimed": False,
        "content_safety_claimed": False,
        "privacy_safety_claimed": False,
        "malware_safety_claimed": False,
    })
    payload.setdefault("source_metadata", {"source_label": cfg["label"], "metadata_only_probe_preview": True})
    payload.setdefault("metadata_summary", f"Metadata-only observation candidate for {cfg['label']}.")
    return payload


def _fixture_from_payload(source_id: str, payload: Mapping[str, Any]) -> dict[str, Any]:
    cfg = SOURCE_CONFIGS[source_id]
    return {
        "schema_version": "h10_games_emulation_fixture.v0",
        "fixture_id": f"h10.live_probe_fixture_equivalent.{source_id}.{_slug(str(payload.get('source_native_id') or 'metadata'))}.v0",
        "source_id": source_id,
        "connector_family": cfg["connector_family"],
        "fixture_kind": cfg["fixture_kind"],
        "fixture_status": "ready",
        "fixture_public_safe": True,
        "live_call_used": False,
        "network_used": False,
        "external_api_used": False,
        "catalog_payload_included": False,
        "software_list_payload_included": False,
        "hashset_payload_included": False,
        "rom_payload_included": False,
        "iso_payload_included": False,
        "disc_image_payload_included": False,
        "chd_payload_included": False,
        "bios_firmware_payload_included": False,
        "game_binary_payload_included": False,
        "emulator_payload_included": False,
        "installer_payload_included": False,
        "patch_payload_included": False,
        "crack_key_serial_payload_included": False,
        "asset_payload_included": False,
        "file_upload_performed": False,
        "hash_submission_performed": False,
        "emulator_execution_performed": False,
        "game_execution_performed": False,
        "install_execute_performed": False,
        "acquisition_action_performed": False,
        "scraping_output_included": False,
        "crawling_output_included": False,
        "restricted_source_accessed": False,
        "bypass_or_automation_used": False,
        "fixture_payload": dict(payload),
        "expected_normalized_ref": f"h10.normalized.{source_id}.candidate.v0",
        "limitations": ["Fixture-equivalent live-probe preview; no network or game/media payload included."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["Built from mocked or dry-run metadata response only."],
    }


def _source_policy(source_id: str, policy_bundle: Mapping[str, Any], bundle_key: str) -> dict[str, Any]:
    for item in policy_bundle.get(bundle_key, {}).get("sources", []):
        if isinstance(item, Mapping) and item.get("source_id") == source_id:
            return dict(item)
    return {}


def _status_for_reasons(reasons: list[str]) -> str:
    joined = " ".join(reasons).lower()
    if not reasons:
        return "dry_run_preflight_pass"
    if "download" in joined or "payload" in joined:
        return "blocked_by_download_policy"
    if "upload" in joined or "hash submission" in joined:
        return "blocked_by_upload_policy"
    if "execution" in joined or "execute" in joined or "emulator_execution" in joined or "game_execution" in joined:
        return "blocked_by_execution_policy"
    if "acquisition" in joined:
        return "blocked_by_acquisition_policy"
    if "restricted" in joined:
        return "blocked_by_restricted_source_policy"
    if "bypass" in joined or "automation" in joined or "drm" in joined:
        return "blocked_by_bypass_policy"
    if "kill switch" in joined:
        return "blocked_by_kill_switch"
    if "endpoint" in joined:
        return "blocked_by_endpoint_policy"
    if "approval" in joined or "approved" in joined or "request key" in joined:
        return "blocked_by_missing_approval"
    return "blocked_by_policy"


def _blocked_candidate() -> dict[str, Any]:
    return {
        "schema_version": "h10_games_emulation_blocked_candidate.v0",
        "status": "not_created_blocked_by_policy",
        "preview_only": True,
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
    }


def _blocked_review_seed(source_id: str, status: str, reasons: list[str]) -> dict[str, Any]:
    return {
        "schema_version": "h10_games_emulation_live_probe_review_seed.v0",
        "review_queue_seed_preview_id": f"h10.review_seed_preview.{source_id}.blocked.{_short_fingerprint(reasons)}.v0",
        "source_id": source_id,
        "preview_only": True,
        "review_seed_is_review_decision": False,
        "review_queue_write_allowed_current": False,
        "blocked_status": status,
        "blocked_reasons": reasons,
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
    }


def _present(value: object) -> bool:
    return isinstance(value, Mapping) and value.get("status") != "not_created_blocked_by_policy"


def _blocked(value: object) -> bool:
    if isinstance(value, list):
        return all(_blocked(item) for item in value)
    return isinstance(value, Mapping) and value.get("status") == "not_created_blocked_by_policy"


def _truth_boundary() -> dict[str, bool]:
    return TRUTH_BOUNDARY.copy()


def _product_boundary() -> dict[str, bool]:
    return PRODUCT_BOUNDARY.copy()


def _detect_true_keys(value: Any, forbidden: set[str], prefix: str = "") -> list[str]:
    errors: list[str] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = f"{prefix}.{key}" if prefix else str(key)
            if key in forbidden and child is True:
                errors.append(f"forbidden true boundary key: {child_path}")
            errors.extend(_detect_true_keys(child, forbidden, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            errors.extend(_detect_true_keys(child, forbidden, f"{prefix}[{index}]"))
    return errors


def _raise_on_boundary_errors(record: Mapping[str, Any], policy_bundle: Mapping[str, Any] | None = None) -> None:
    errors = detect_h10_games_emulation_live_probe_truth_boundary_violations(record, policy_bundle) + detect_h10_games_emulation_live_probe_product_boundary_violations(record, policy_bundle)
    if errors:
        raise ValueError("; ".join(errors))


def _fingerprint(payload: Mapping[str, Any]) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode("utf-8")).hexdigest()


def _short_fingerprint(payload: object) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode("utf-8")).hexdigest()[:16]


def _slug(value: object) -> str:
    text = str(value or "unknown")
    safe = "".join(ch.lower() if ch.isalnum() else "-" for ch in text).strip("-")
    return safe[:64].strip("-") or "unknown"


def _dedupe(values: list[object]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        text = str(value).strip()
        if text and text not in seen:
            result.append(text)
            seen.add(text)
    return result
