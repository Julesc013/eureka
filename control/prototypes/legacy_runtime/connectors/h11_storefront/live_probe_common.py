"""Fail-closed H11 storefront live-probe helpers."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any

from control.prototypes.legacy_runtime.connectors.h11_storefront.normalizer_common import (
    H11_SOURCE_CONFIGS,
    build_h11_acquisition_path_candidate as _fixture_acquisition_candidate,
    build_h11_account_entitlement_boundary_candidate as _fixture_account_candidate,
    build_h11_app_product_identity_candidate as _fixture_app_candidate,
    build_h11_evidence_candidate_preview as _fixture_evidence_preview,
    build_h11_price_availability_region_candidate as _fixture_price_candidate,
    build_h11_review_rating_metadata_candidate as _fixture_review_candidate,
    build_h11_source_cache_candidate_preview as _fixture_source_cache_preview,
    build_h11_storefront_listing_identity_candidate as _fixture_listing_candidate,
    build_h11_storefront_rights_safety_candidate as _fixture_rights_candidate,
    build_h11_version_release_channel_candidate as _fixture_version_candidate,
    normalize_h11_storefront_fixture,
)

POLICY_PATHS = {
    "live_probe_policy": "control/inventory/connectors/h11_storefront_live_probe_policy.json",
    "allowed_requests": "control/inventory/connectors/h11_storefront_live_probe_allowed_requests.json",
    "endpoint_policy": "control/inventory/connectors/h11_storefront_live_probe_endpoint_policy.json",
    "rate_limit_policy": "control/inventory/connectors/h11_storefront_live_probe_rate_limit_policy.json",
    "cache_policy": "control/inventory/connectors/h11_storefront_live_probe_cache_policy.json",
    "kill_switch_policy": "control/inventory/connectors/h11_storefront_live_probe_kill_switch_policy.json",
    "output_policy": "control/inventory/connectors/h11_storefront_live_probe_output_policy.json",
    "path_policy": "control/inventory/connectors/h11_storefront_live_probe_path_policy.json",
    "review_policy": "control/inventory/connectors/h11_storefront_live_probe_review_policy.json",
    "truth_policy": "control/inventory/connectors/h11_storefront_live_probe_truth_policy.json",
    "no_purchase_download_account_policy": "control/inventory/connectors/h11_storefront_live_probe_no_purchase_download_account_policy.json",
    "restricted_source_policy": "control/inventory/connectors/h11_storefront_live_probe_restricted_source_policy.json",
}
SOURCE_CONFIGS = {'microsoft_store_metadata': {'source_id': 'microsoft_store_metadata', 'source_label': 'Microsoft Store metadata', 'connector_family': 'app_store_metadata', 'source_record_kind': 'storefront_metadata', 'endpoint': 'listing_metadata_lookup_future', 'request_key': 'example_listing_metadata'}, 'mac_app_store_metadata': {'source_id': 'mac_app_store_metadata', 'source_label': 'Mac App Store metadata', 'connector_family': 'app_store_metadata', 'source_record_kind': 'storefront_metadata', 'endpoint': 'listing_metadata_lookup_future', 'request_key': 'example_listing_metadata'}, 'apple_app_store_metadata': {'source_id': 'apple_app_store_metadata', 'source_label': 'Apple App Store metadata', 'connector_family': 'app_store_metadata', 'source_record_kind': 'storefront_metadata', 'endpoint': 'listing_metadata_lookup_future', 'request_key': 'example_listing_metadata'}, 'google_play_metadata': {'source_id': 'google_play_metadata', 'source_label': 'Google Play metadata', 'connector_family': 'app_store_metadata', 'source_record_kind': 'storefront_metadata', 'endpoint': 'listing_metadata_lookup_future', 'request_key': 'example_listing_metadata'}, 'fdroid_metadata': {'source_id': 'fdroid_metadata', 'source_label': 'F-Droid metadata', 'connector_family': 'linux_app_store_metadata', 'source_record_kind': 'storefront_metadata', 'endpoint': 'app_metadata_lookup_future', 'request_key': 'example_app_metadata'}, 'steam_store_metadata': {'source_id': 'steam_store_metadata', 'source_label': 'Steam Store metadata', 'connector_family': 'game_storefront_metadata', 'source_record_kind': 'storefront_metadata', 'endpoint': 'public_app_metadata_lookup_future', 'request_key': 'example_storefront_metadata'}, 'gog_store_metadata': {'source_id': 'gog_store_metadata', 'source_label': 'GOG Store metadata', 'connector_family': 'game_storefront_metadata', 'source_record_kind': 'storefront_metadata', 'endpoint': 'public_listing_metadata_lookup_future', 'request_key': 'example_storefront_metadata'}, 'itchio_storefront_metadata': {'source_id': 'itchio_storefront_metadata', 'source_label': 'itch.io storefront metadata', 'connector_family': 'game_storefront_metadata', 'source_record_kind': 'storefront_metadata', 'endpoint': 'public_listing_metadata_lookup_future', 'request_key': 'example_storefront_metadata'}, 'epic_games_store_policy_limited': {'source_id': 'epic_games_store_policy_limited', 'source_label': 'Epic Games Store metadata, policy-limited', 'connector_family': 'game_storefront_metadata', 'source_record_kind': 'storefront_metadata', 'endpoint': 'public_listing_metadata_policy_limited_future', 'request_key': 'example_policy_limited_metadata'}, 'humble_store_policy_limited': {'source_id': 'humble_store_policy_limited', 'source_label': 'Humble Store metadata, policy-limited', 'connector_family': 'software_marketplace_metadata', 'source_record_kind': 'storefront_metadata', 'endpoint': 'marketplace_listing_metadata_policy_limited_future', 'request_key': 'example_policy_limited_metadata'}, 'chrome_web_store_metadata': {'source_id': 'chrome_web_store_metadata', 'source_label': 'Chrome Web Store metadata', 'connector_family': 'browser_extension_store_metadata', 'source_record_kind': 'storefront_metadata', 'endpoint': 'extension_metadata_lookup_future', 'request_key': 'example_extension_metadata'}, 'mozilla_addons_metadata': {'source_id': 'mozilla_addons_metadata', 'source_label': 'Mozilla Add-ons metadata', 'connector_family': 'browser_extension_store_metadata', 'source_record_kind': 'storefront_metadata', 'endpoint': 'extension_metadata_lookup_future', 'request_key': 'example_extension_metadata'}, 'flathub_metadata': {'source_id': 'flathub_metadata', 'source_label': 'Flathub metadata', 'connector_family': 'linux_app_store_metadata', 'source_record_kind': 'storefront_metadata', 'endpoint': 'app_metadata_lookup_future', 'request_key': 'example_app_metadata'}, 'snapcraft_metadata': {'source_id': 'snapcraft_metadata', 'source_label': 'Snapcraft metadata', 'connector_family': 'linux_app_store_metadata', 'source_record_kind': 'storefront_metadata', 'endpoint': 'app_metadata_lookup_future', 'request_key': 'example_app_metadata'}, 'generic_vendor_product_page': {'source_id': 'generic_vendor_product_page', 'source_label': 'Generic vendor product page metadata', 'connector_family': 'vendor_product_page_metadata', 'source_record_kind': 'storefront_metadata', 'endpoint': 'product_metadata_fixture_future', 'request_key': 'example_product_metadata'}, 'generic_commercial_software_marketplace': {'source_id': 'generic_commercial_software_marketplace', 'source_label': 'Generic commercial software marketplace metadata', 'connector_family': 'software_marketplace_metadata', 'source_record_kind': 'storefront_metadata', 'endpoint': 'marketplace_metadata_fixture_future', 'request_key': 'example_marketplace_metadata'}}
H11_SOURCE_IDS = tuple(SOURCE_CONFIGS)
REQUEST_FORBIDDEN_TRUE_KEYS = {
    "screenshot_fetch_requested",
    "media_fetch_requested",
    "app_download_requested",
    "game_download_requested",
    "package_download_requested",
    "installer_download_requested",
    "account_access_requested",
    "credential_or_token_handling_requested",
    "receipt_license_entitlement_handling_requested",
    "purchase_automation_requested",
    "checkout_automation_requested",
    "cart_wishlist_automation_requested",
    "redemption_subscription_requested",
    "install_execute_requested",
    "launch_execute_requested",
    "review_rating_write_requested",
    "user_data_upload_requested",
    "scraping_or_crawling_requested",
    "restricted_source_requested",
    "bypass_or_automation_requested",
}
CONDITIONAL_REQUEST_KEYS = {
    "api_query_requested": "api_query_approved",
    "catalog_fetch_requested": "catalog_fetch_approved",
    "storefront_search_requested": "storefront_search_approved",
    "product_page_fetch_requested": "product_page_fetch_approved",
}
FORBIDDEN_TRUTH_TRUE_KEYS = {
    "live_probe_result_is_public_truth",
    "normalized_record_is_public_truth",
    "listing_identity_candidate_is_truth",
    "storefront_listing_identity_candidate_is_truth",
    "app_product_identity_candidate_is_truth",
    "version_release_channel_candidate_is_truth",
    "version_release_candidate_is_truth",
    "price_availability_region_candidate_is_truth",
    "price_availability_candidate_is_truth",
    "acquisition_path_candidate_is_action_permission",
    "review_rating_metadata_candidate_is_quality_truth",
    "review_rating_candidate_is_quality_truth",
    "account_entitlement_boundary_candidate_is_license_truth",
    "account_entitlement_candidate_is_license_truth",
    "storefront_rights_safety_candidate_is_rights_or_safety_truth",
    "rights_safety_candidate_is_rights_or_safety_truth",
    "storefront_metadata_grants_acquisition_permission",
    "source_cache_candidate_is_accepted_source",
    "source_cache_preview_is_accepted_source",
    "evidence_candidate_preview_is_accepted_evidence",
    "evidence_preview_is_accepted_evidence",
    "review_seed_is_review_decision",
    "accepted_source_truth",
    "accepted_evidence_truth",
    "accepted_candidate_truth",
    "accepted_listing_identity_truth",
    "accepted_app_product_truth",
    "accepted_version_release_truth",
    "accepted_price_availability_truth",
    "accepted_acquisition_permission",
    "accepted_review_rating_truth",
    "accepted_account_entitlement_truth",
    "accepted_rights_safety_truth",
    "accepted_public_record",
    "public_index_mutated",
    "master_index_mutated",
    "rights_clearance_claimed",
    "current_price_claimed",
    "current_availability_claimed",
    "license_entitlement_claimed",
    "legal_acquisition_claimed",
    "installability_claimed",
    "malware_safety_claimed",
    "content_safety_claimed",
    "privacy_safety_claimed",
    "verified_authenticity_claimed",
    "production_readiness_claimed",
    "download_permission_granted",
    "account_access_permission_granted",
    "purchase_permission_granted",
    "install_launch_permission_granted",
    "price_metadata_is_current_price_truth",
    "availability_metadata_is_current_availability_truth",
}
FORBIDDEN_PRODUCT_TRUE_KEYS = {
    "changed_public_search_behavior",
    "enabled_hosting",
    "enabled_source_sync",
    "enabled_downloads",
    "enabled_accounts",
    "enabled_purchase_actions",
    "enabled_entitlement_checks",
    "enabled_install_launch",
    "enabled_crawling",
    "enabled_uploads",
    "enabled_telemetry",
    "mutated_public_index",
    "mutated_master_index",
    "network_calls_made",
    "api_calls_made",
    "catalog_fetch_used",
    "storefront_search_used",
    "product_page_fetch_used",
    "screenshot_media_fetch_used",
    "download_used",
    "account_access_used",
    "purchase_action_used",
    "entitlement_check_used",
    "install_launch_used",
    "review_rating_write_used",
    "scraping_used",
    "crawling_used",
    "restricted_source_access_used",
    "bypass_or_automation_used",
}


def load_h11_storefront_live_probe_policy_bundle(root: str | Path | None = None) -> dict[str, Any]:
    base = Path(root) if root is not None else Path(__file__).resolve().parents[5]
    return {key: json.loads((base / rel).read_text(encoding="utf-8")) for key, rel in POLICY_PATHS.items()}


def build_h11_storefront_live_probe_request(source_id: str, request_key: str, policy_bundle: Mapping[str, Any] | None = None, live_requested: bool = False) -> dict[str, Any]:
    if source_id not in SOURCE_CONFIGS:
        raise ValueError(f"unknown H11 source_id: {source_id}")
    cfg = SOURCE_CONFIGS[source_id]
    request = {
        "schema_version": "h11_storefront_live_probe_request.v0",
        "live_probe_request_id": f"h11.live_probe_request.{source_id}.{_slug(request_key)}.v0",
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
        "listing_or_product_identifier": f"metadata-only-candidate:{source_id}:{request_key}",
        "app_or_package_context": "candidate_metadata_context_only_no_package_payload",
        "version_or_channel_context": "candidate_metadata_context_only",
        "region_or_availability_context": "candidate_metadata_context_only_not_current_availability_truth",
        "acquisition_or_account_context": "blocked_current_no_account_no_purchase_no_entitlement",
        "approval_refs": [POLICY_PATHS["allowed_requests"]],
        "policy_refs": list(POLICY_PATHS.values()),
        "live_requested": bool(live_requested),
        "dry_run_only": not bool(live_requested),
        "api_query_requested": False,
        "catalog_fetch_requested": False,
        "storefront_search_requested": False,
        "product_page_fetch_requested": False,
        "screenshot_fetch_requested": False,
        "media_fetch_requested": False,
        "app_download_requested": False,
        "game_download_requested": False,
        "package_download_requested": False,
        "installer_download_requested": False,
        "account_access_requested": False,
        "credential_or_token_handling_requested": False,
        "receipt_license_entitlement_handling_requested": False,
        "purchase_automation_requested": False,
        "checkout_automation_requested": False,
        "cart_wishlist_automation_requested": False,
        "redemption_subscription_requested": False,
        "install_execute_requested": False,
        "launch_execute_requested": False,
        "review_rating_write_requested": False,
        "user_data_upload_requested": False,
        "scraping_or_crawling_requested": False,
        "restricted_source_requested": False,
        "bypass_or_automation_requested": False,
        "output_policy_ref": POLICY_PATHS["output_policy"],
        "review_policy_ref": POLICY_PATHS["review_policy"],
        "truth_policy_ref": POLICY_PATHS["truth_policy"],
        "limitations": ["Request envelope is fail-closed unless committed source policy approves the exact metadata-only request."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["H11-BUNDLE-03 examples are dry preflight by default and do not call networks."],
    }
    _raise_on_boundary_errors(request)
    return request


def validate_h11_storefront_live_probe_request(request: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []
    source_id = str(request.get("source_id") or "")
    request_key = str(request.get("approved_request_key") or "")
    allowed = _source_policy(source_id, policy_bundle, "allowed_requests") if source_id in SOURCE_CONFIGS else {}
    if source_id not in SOURCE_CONFIGS:
        reasons.append(f"{source_id or 'missing_source'} is not a known H11 storefront source")
    else:
        cfg = SOURCE_CONFIGS[source_id]
        if request.get("operation_scope") != "metadata_only":
            reasons.append("approved_operation_scope must be metadata_only")
        endpoint = str(request.get("endpoint_or_metadata_class") or "")
        if endpoint != cfg["endpoint"]:
            lower = endpoint.casefold()
            if "download" in lower or "payload" in lower:
                reasons.append("endpoint_or_metadata_class download/payload class is forbidden")
            else:
                reasons.append("endpoint_or_metadata_class is not the planned source metadata class")
    for request_field, approval_field in CONDITIONAL_REQUEST_KEYS.items():
        if request.get(request_field) is True and allowed.get(approval_field) is not True:
            reasons.append(f"{request_field} is not approved without exact committed bounded metadata policy")
    for key in sorted(REQUEST_FORBIDDEN_TRUE_KEYS):
        if request.get(key) is True:
            reasons.append(f"{key} is forbidden for H11-BUNDLE-03 live probes")
    if source_id in SOURCE_CONFIGS:
        reasons.extend(validate_h11_source_approval(source_id, request_key, policy_bundle)["blocked_reasons"])
    reasons = _dedupe(reasons)
    return {"approved": not reasons, "result_status": _status_for_reasons(reasons), "blocked_reasons": reasons}


def validate_h11_source_approval(source_id: str, request_key: str, policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []
    if source_id not in SOURCE_CONFIGS:
        return {"approved": False, "result_status": "blocked_by_policy", "blocked_reasons": [f"{source_id} is not a known H11 source"]}
    cfg = SOURCE_CONFIGS[source_id]
    allowed = _source_policy(source_id, policy_bundle, "allowed_requests")
    if not allowed:
        reasons.append("source is not listed in H11 allowed request policy")
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
            "screenshot_fetch_approved",
            "media_fetch_approved",
            "app_download_approved",
            "game_download_approved",
            "package_download_approved",
            "installer_download_approved",
            "account_access_approved",
            "credential_or_token_handling_approved",
            "receipt_license_entitlement_handling_approved",
            "purchase_automation_approved",
            "checkout_automation_approved",
            "cart_wishlist_automation_approved",
            "redemption_subscription_approved",
            "install_execute_approved",
            "launch_execute_approved",
            "review_rating_write_approved",
            "user_data_upload_approved",
            "scraping_approved",
            "crawling_approved",
            "browser_automation_approved",
            "restricted_rights_sensitive_source_approved",
            "grey_market_or_piracy_adjacent_source_approved",
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


def build_h11_storefront_live_probe_blocked_result(request: Mapping[str, Any], reason: str | list[str], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    source_id = str(request.get("source_id") or "unknown")
    cfg = SOURCE_CONFIGS.get(source_id, {"connector_family": request.get("connector_family", "unknown"), "source_record_kind": request.get("source_record_kind", "unknown"), "endpoint": request.get("endpoint_or_metadata_class", "unknown")})
    reasons = reason if isinstance(reason, list) else [str(reason)]
    status = _status_for_reasons(reasons)
    normalized = _normal_record_from_request(request)
    result: dict[str, Any] = {
        "schema_version": "h11_storefront_live_probe_result.v0",
        "live_probe_result_id": f"h11.live_probe_result.{source_id}.blocked.{_short_fingerprint(request)}.v0",
        "live_probe_request_ref": request.get("live_probe_request_id"),
        "source_id": source_id,
        "connector_family": str(cfg.get("connector_family") or "unknown"),
        "source_record_kind": str(cfg.get("source_record_kind") or "unknown"),
        "result_status": status,
        "request_count": 0,
        "network_used": False,
        "endpoint_or_metadata_used": cfg.get("endpoint"),
        "response_status_code": None,
        "response_fingerprint": _short_fingerprint(request),
        "response_summary": "No external request was made; output is blocked/preflight metadata preview only.",
        "normalized_record": normalized,
        "storefront_listing_identity_candidate": normalized["storefront_listing_identity_candidate"],
        "app_product_identity_candidate": normalized["app_product_identity_candidate"],
        "version_release_channel_candidate": normalized["version_release_channel_candidate"],
        "price_availability_region_candidate": normalized["price_availability_region_candidate"],
        "acquisition_path_candidate": normalized["acquisition_path_candidate"],
        "review_rating_metadata_candidate": normalized["review_rating_metadata_candidate"],
        "account_entitlement_boundary_candidate": normalized["account_entitlement_boundary_candidate"],
        "storefront_rights_safety_candidate": normalized["storefront_rights_safety_candidate"],
        "source_cache_candidate_preview": normalized["source_cache_candidate_preview"],
        "evidence_candidate_preview": normalized["evidence_candidate_preview"],
        "review_queue_seed_preview": None,
        "connector_health_summary": None,
        "blocked_reason": "; ".join(reasons),
        "blocked_reasons": reasons,
        "warnings": [],
        "limitations": ["Live probe blocked by committed fail-closed policy. Fixture-equivalent preview only."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["No download, account access, purchase, entitlement check, install, launch, review write, scraping, crawling, restricted-source access, or bypass occurred."],
    }
    result["review_queue_seed_preview"] = build_h11_review_queue_seed_preview_from_probe(result, result["source_cache_candidate_preview"], result["evidence_candidate_preview"], policy_bundle)
    result["connector_health_summary"] = build_h11_connector_health_summary(result, policy_bundle)
    _raise_on_boundary_errors(result)
    return result


def build_h11_storefront_live_probe_result(source_id: str, response_payload: Mapping[str, Any], response_metadata: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    if source_id not in SOURCE_CONFIGS:
        raise ValueError(f"unknown H11 source_id: {source_id}")
    cfg = SOURCE_CONFIGS[source_id]
    normalized = _normal_record_from_response(source_id, response_payload, response_metadata)
    network_used = bool(response_metadata.get("network_used"))
    result: dict[str, Any] = {
        "schema_version": "h11_storefront_live_probe_result.v0",
        "live_probe_result_id": f"h11.live_probe_result.{source_id}.{_short_fingerprint(response_payload)}.v0",
        "live_probe_request_ref": response_metadata.get("live_probe_request_ref"),
        "source_id": source_id,
        "connector_family": cfg["connector_family"],
        "source_record_kind": cfg["source_record_kind"],
        "result_status": str(response_metadata.get("result_status") or ("live_probe_completed" if network_used else "dry_run_preflight_pass")),
        "request_count": int(response_metadata.get("request_count") or (1 if network_used else 0)),
        "network_used": network_used,
        "endpoint_or_metadata_used": response_metadata.get("endpoint_or_metadata_used", cfg["endpoint"]),
        "response_status_code": response_metadata.get("response_status_code"),
        "response_fingerprint": _short_fingerprint(response_payload),
        "response_summary": str(response_metadata.get("response_summary") or "Bounded metadata-only response payload normalized through H11 normalizers."),
        "normalized_record": normalized,
        "storefront_listing_identity_candidate": normalized["storefront_listing_identity_candidate"],
        "app_product_identity_candidate": normalized["app_product_identity_candidate"],
        "version_release_channel_candidate": normalized["version_release_channel_candidate"],
        "price_availability_region_candidate": normalized["price_availability_region_candidate"],
        "acquisition_path_candidate": normalized["acquisition_path_candidate"],
        "review_rating_metadata_candidate": normalized["review_rating_metadata_candidate"],
        "account_entitlement_boundary_candidate": normalized["account_entitlement_boundary_candidate"],
        "storefront_rights_safety_candidate": normalized["storefront_rights_safety_candidate"],
        "source_cache_candidate_preview": normalized["source_cache_candidate_preview"],
        "evidence_candidate_preview": normalized["evidence_candidate_preview"],
        "review_queue_seed_preview": None,
        "connector_health_summary": None,
        "blocked_reason": None,
        "blocked_reasons": [],
        "warnings": list(response_metadata.get("warnings") or []),
        "limitations": ["Probe output remains candidate/preview material only."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(network_used=network_used),
        "notes": ["No source cache, evidence ledger, review queue, public index, or master index mutation occurs."],
    }
    result["review_queue_seed_preview"] = build_h11_review_queue_seed_preview_from_probe(result, result["source_cache_candidate_preview"], result["evidence_candidate_preview"], policy_bundle)
    result["connector_health_summary"] = build_h11_connector_health_summary(result, policy_bundle)
    _raise_on_boundary_errors(result)
    return result


def normalize_h11_storefront_live_probe_result(result: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    normalized = result.get("normalized_record")
    if not isinstance(normalized, Mapping):
        raise ValueError("live probe result is missing normalized_record")
    return dict(normalized)


def build_h11_storefront_listing_identity_candidate_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return _fixture_listing_candidate(normalized_record, policy_bundle)


def build_h11_app_product_identity_candidate_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return _fixture_app_candidate(normalized_record, policy_bundle)


def build_h11_version_release_channel_candidate_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return _fixture_version_candidate(normalized_record, policy_bundle)


def build_h11_price_availability_region_candidate_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return _fixture_price_candidate(normalized_record, policy_bundle)


def build_h11_acquisition_path_candidate_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return _fixture_acquisition_candidate(normalized_record, policy_bundle)


def build_h11_review_rating_metadata_candidate_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return _fixture_review_candidate(normalized_record, policy_bundle)


def build_h11_account_entitlement_boundary_candidate_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return _fixture_account_candidate(normalized_record, policy_bundle)


def build_h11_storefront_rights_safety_candidate_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return _fixture_rights_candidate(normalized_record, policy_bundle)


def build_h11_source_cache_candidate_preview_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return _fixture_source_cache_preview(normalized_record, policy_bundle)


def build_h11_evidence_candidate_preview_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return _fixture_evidence_preview(normalized_record, policy_bundle)


def build_h11_review_queue_seed_preview_from_probe(result: Mapping[str, Any], source_cache_preview: Mapping[str, Any], evidence_preview: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    seed = {
        "schema_version": "h11_storefront_live_probe_review_seed.v0",
        "review_seed_id": f"h11.review_seed.{result.get('source_id')}.{_short_fingerprint(result)}.v0",
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


def build_h11_connector_health_summary(result: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    status = str(result.get("result_status") or "not_evaluable")
    blockers = list(result.get("blocked_reasons") or [])
    health = {
        "schema_version": "h11_storefront_connector_health_summary.v0",
        "health_summary_id": f"h11.connector_health.{result.get('source_id')}.{_short_fingerprint(result)}.v0",
        "source_id": result.get("source_id"),
        "connector_family": result.get("connector_family"),
        "live_probe_status": status,
        "request_count": int(result.get("request_count") or 0),
        "response_status_summary": "blocked" if status.startswith("blocked_") else status,
        "policy_blockers": blockers,
        "warnings": list(result.get("warnings") or []),
        "source_limitations": list(result.get("limitations") or []),
        "restricted_source_status": "blocked_current",
        "account_boundary_status": "blocked_current",
        "next_recommended_action": "Use fixture-equivalent outputs for H11-BUNDLE-04 or obtain explicit operator approval before any live source call.",
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
    }
    _raise_on_boundary_errors(health)
    return health


def build_h11_storefront_live_probe_output_bundle(result: Mapping[str, Any]) -> dict[str, Any]:
    bundle = {
        "schema_version": "h11_storefront_live_probe_output_bundle.v0",
        "live_probe_result": result,
        "normalized_record": result.get("normalized_record"),
        "storefront_listing_identity_candidate": result.get("storefront_listing_identity_candidate"),
        "app_product_identity_candidate": result.get("app_product_identity_candidate"),
        "version_release_channel_candidate": result.get("version_release_channel_candidate"),
        "price_availability_region_candidate": result.get("price_availability_region_candidate"),
        "acquisition_path_candidate": result.get("acquisition_path_candidate"),
        "review_rating_metadata_candidate": result.get("review_rating_metadata_candidate"),
        "account_entitlement_boundary_candidate": result.get("account_entitlement_boundary_candidate"),
        "storefront_rights_safety_candidate": result.get("storefront_rights_safety_candidate"),
        "source_cache_candidate_preview": result.get("source_cache_candidate_preview"),
        "evidence_candidate_preview": result.get("evidence_candidate_preview"),
        "review_queue_seed_preview": result.get("review_queue_seed_preview"),
        "connector_health_summary": result.get("connector_health_summary"),
        "validation_summary": summarize_h11_storefront_live_probe_result(result),
    }
    _raise_on_boundary_errors(bundle)
    return bundle


def summarize_h11_storefront_live_probe_result(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "source_id": result.get("source_id"),
        "result_status": result.get("result_status"),
        "request_count": int(result.get("request_count") or 0),
        "network_used": bool(result.get("network_used")),
        "blocked_reasons": list(result.get("blocked_reasons") or []),
        "has_listing_candidate": isinstance(result.get("storefront_listing_identity_candidate"), Mapping),
        "has_app_product_candidate": isinstance(result.get("app_product_identity_candidate"), Mapping),
        "has_version_candidate": isinstance(result.get("version_release_channel_candidate"), Mapping),
        "has_price_availability_candidate": isinstance(result.get("price_availability_region_candidate"), Mapping),
        "has_acquisition_candidate": isinstance(result.get("acquisition_path_candidate"), Mapping),
        "has_review_rating_candidate": isinstance(result.get("review_rating_metadata_candidate"), Mapping),
        "has_account_boundary_candidate": isinstance(result.get("account_entitlement_boundary_candidate"), Mapping),
        "has_rights_safety_candidate": isinstance(result.get("storefront_rights_safety_candidate"), Mapping),
        "truth_boundary_violations": detect_h11_storefront_live_probe_truth_boundary_violations(result, {}),
        "product_boundary_violations": detect_h11_storefront_live_probe_product_boundary_violations(result, {}),
    }


def detect_h11_storefront_live_probe_truth_boundary_violations(result: Mapping[str, Any], policy_bundle: Mapping[str, Any] | None = None) -> list[str]:
    errors: list[str] = []
    _collect_true_keys(result, FORBIDDEN_TRUTH_TRUE_KEYS, "truth", errors)
    return errors


def detect_h11_storefront_live_probe_product_boundary_violations(result: Mapping[str, Any], policy_bundle: Mapping[str, Any] | None = None) -> list[str]:
    errors: list[str] = []
    _collect_true_keys(result, FORBIDDEN_PRODUCT_TRUE_KEYS, "product", errors)
    return errors


def _normal_record_from_request(request: Mapping[str, Any]) -> dict[str, Any]:
    source_id = str(request.get("source_id") or "")
    cfg = SOURCE_CONFIGS.get(source_id)
    if not cfg:
        return _unknown_normalized_record(request)
    payload = {
        "source_native_id": str(request.get("listing_or_product_identifier") or request.get("approved_request_key") or "blocked"),
        "source_record_kind": cfg["source_record_kind"],
        "listing_title": f"Blocked metadata preview for {source_id}",
        "listing_id": str(request.get("approved_request_key") or "unknown"),
        "storefront_id": source_id,
        "storefront_native_id": str(request.get("approved_request_key") or "unknown"),
        "product_page_url_candidate": "unknown",
        "developer_or_publisher": "unknown",
        "seller_or_distributor": "unknown",
        "platform": "unknown",
        "category_or_genre": "unknown",
        "listing_type": "metadata_only_preflight",
        "listing_status_candidate": "not_evaluable",
        "region_candidate": "unknown",
        "language_candidate": "unknown",
        "app_or_product_name": f"{source_id} metadata candidate",
        "version_candidate": "unknown",
        "price_candidate": "unknown",
        "availability_status_candidate": "not_current_availability_truth",
        "purchase_or_license_model_candidate": "not_evaluable",
        "metadata_summary": "Blocked preflight request envelope; no source response payload.",
    }
    return _normalize_fixture_payload(source_id, payload, "blocked_live_probe_preflight", "blocked_by_policy")


def _normal_record_from_response(source_id: str, response_payload: Mapping[str, Any], response_metadata: Mapping[str, Any]) -> dict[str, Any]:
    payload = dict(response_payload.get("fixture_payload") if isinstance(response_payload.get("fixture_payload"), Mapping) else response_payload)
    payload.setdefault("source_native_id", response_metadata.get("source_native_id") or response_metadata.get("request_key") or "live-probe-response")
    payload.setdefault("source_record_kind", SOURCE_CONFIGS[source_id]["source_record_kind"])
    payload.setdefault("listing_title", payload.get("app_or_product_name") or f"Metadata response for {source_id}")
    payload.setdefault("storefront_id", source_id)
    payload.setdefault("storefront_native_id", payload.get("source_native_id"))
    payload.setdefault("listing_type", "metadata_only_response")
    payload.setdefault("metadata_summary", "Bounded metadata-only response payload.")
    return _normalize_fixture_payload(source_id, payload, "live_probe_metadata_response", "synthetic_or_mocked_metadata_payload")


def _normalize_fixture_payload(source_id: str, payload: Mapping[str, Any], fixture_kind: str, status: str) -> dict[str, Any]:
    fixture = {
        "schema_version": "h11_storefront_fixture.v0",
        "fixture_id": f"h11.live_probe.fixture_equivalent.{source_id}.{_slug(payload.get('source_native_id'))}.v0",
        "source_id": source_id,
        "connector_family": SOURCE_CONFIGS[source_id]["connector_family"],
        "fixture_kind": fixture_kind,
        "fixture_status": status,
        "live_call_used": False,
        "network_used": False,
        "external_api_used": False,
        "catalog_payload_included": False,
        "storefront_search_payload_included": False,
        "product_page_payload_included": False,
        "screenshot_payload_included": False,
        "media_payload_included": False,
        "app_package_payload_included": False,
        "game_package_payload_included": False,
        "installer_payload_included": False,
        "account_payload_included": False,
        "credential_or_token_payload_included": False,
        "receipt_payload_included": False,
        "license_key_payload_included": False,
        "entitlement_payload_included": False,
        "payment_payload_included": False,
        "user_library_payload_included": False,
        "purchase_action_performed": False,
        "checkout_action_performed": False,
        "cart_wishlist_action_performed": False,
        "redemption_subscription_action_performed": False,
        "install_execute_performed": False,
        "launch_execute_performed": False,
        "review_rating_write_performed": False,
        "scraping_output_included": False,
        "crawling_output_included": False,
        "restricted_source_accessed": False,
        "bypass_or_automation_used": False,
        "fixture_payload": dict(payload),
        "limitations": ["Fixture-equivalent live-probe preview only; no external request payload is included."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
    }
    return normalize_h11_storefront_fixture(fixture, source_id)


def _unknown_normalized_record(request: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "h11_storefront_normalized_record.v0",
        "normalized_record_id": f"h11.normalized.unknown.{_short_fingerprint(request)}.v0",
        "source_id": request.get("source_id", "unknown"),
        "connector_family": request.get("connector_family", "unknown"),
        "source_record_kind": request.get("source_record_kind", "unknown"),
        "source_limitations": ["Unknown source request could not be normalized."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "storefront_listing_identity_candidate": {"status": "not_created_blocked_by_policy"},
        "app_product_identity_candidate": {"status": "not_created_blocked_by_policy"},
        "version_release_channel_candidate": {"status": "not_created_blocked_by_policy"},
        "price_availability_region_candidate": {"status": "not_created_blocked_by_policy"},
        "acquisition_path_candidate": {"status": "not_created_blocked_by_policy"},
        "review_rating_metadata_candidate": {"status": "not_created_blocked_by_policy"},
        "account_entitlement_boundary_candidate": {"status": "not_created_blocked_by_policy"},
        "storefront_rights_safety_candidate": {"status": "not_created_blocked_by_policy"},
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
        "download" in text
        or "payload class" in text
        or "screenshot_fetch_requested" in text
        or "media_fetch_requested" in text
    ):
        return "blocked_by_download_policy"
    if "account" in text or "credential" in text:
        return "blocked_by_account_policy"
    if "purchase" in text or "checkout" in text or "wishlist" in text or "subscription" in text or "redemption" in text:
        return "blocked_by_purchase_policy"
    if "entitlement" in text or "receipt" in text or "license" in text:
        return "blocked_by_entitlement_policy"
    if "install" in text or "launch" in text:
        return "blocked_by_install_launch_policy"
    if "review_rating_write" in text or "review write" in text:
        return "blocked_by_review_write_policy"
    if "restricted" in text:
        return "blocked_by_restricted_source_policy"
    if "bypass" in text or "automation" in text:
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


def _product_boundary(network_used: bool = False) -> dict[str, bool]:
    boundary = {key: False for key in FORBIDDEN_PRODUCT_TRUE_KEYS}
    boundary["network_calls_made"] = False
    return boundary


def _raise_on_boundary_errors(record: Mapping[str, Any]) -> None:
    errors = detect_h11_storefront_live_probe_truth_boundary_violations(record, {}) + detect_h11_storefront_live_probe_product_boundary_violations(record, {})
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
