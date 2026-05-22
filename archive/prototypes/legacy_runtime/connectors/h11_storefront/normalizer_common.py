"""Offline H11 storefront fixture normalization helpers."""

from __future__ import annotations

import hashlib
from collections.abc import Mapping
from typing import Any


H11_SOURCE_CONFIGS = {'microsoft_store_metadata': {'source_id': 'microsoft_store_metadata', 'source_label': 'Microsoft Store metadata', 'connector_family': 'app_store_metadata', 'source_family': 'storefront_app_store_metadata', 'trust_lane': 'official'}, 'mac_app_store_metadata': {'source_id': 'mac_app_store_metadata', 'source_label': 'Mac App Store metadata', 'connector_family': 'app_store_metadata', 'source_family': 'storefront_app_store_metadata', 'trust_lane': 'official'}, 'apple_app_store_metadata': {'source_id': 'apple_app_store_metadata', 'source_label': 'Apple App Store metadata', 'connector_family': 'app_store_metadata', 'source_family': 'storefront_app_store_metadata', 'trust_lane': 'official'}, 'google_play_metadata': {'source_id': 'google_play_metadata', 'source_label': 'Google Play metadata', 'connector_family': 'app_store_metadata', 'source_family': 'storefront_app_store_metadata', 'trust_lane': 'official'}, 'fdroid_metadata': {'source_id': 'fdroid_metadata', 'source_label': 'F-Droid metadata', 'connector_family': 'linux_app_store_metadata', 'source_family': 'storefront_app_store_metadata', 'trust_lane': 'community'}, 'steam_store_metadata': {'source_id': 'steam_store_metadata', 'source_label': 'Steam Store metadata', 'connector_family': 'game_storefront_metadata', 'source_family': 'storefront_app_store_metadata', 'trust_lane': 'official'}, 'gog_store_metadata': {'source_id': 'gog_store_metadata', 'source_label': 'GOG Store metadata', 'connector_family': 'game_storefront_metadata', 'source_family': 'storefront_app_store_metadata', 'trust_lane': 'official'}, 'itchio_storefront_metadata': {'source_id': 'itchio_storefront_metadata', 'source_label': 'itch.io storefront metadata', 'connector_family': 'game_storefront_metadata', 'source_family': 'storefront_app_store_metadata', 'trust_lane': 'community'}, 'epic_games_store_policy_limited': {'source_id': 'epic_games_store_policy_limited', 'source_label': 'Epic Games Store metadata, policy-limited', 'connector_family': 'game_storefront_metadata', 'source_family': 'storefront_app_store_metadata', 'trust_lane': 'official'}, 'humble_store_policy_limited': {'source_id': 'humble_store_policy_limited', 'source_label': 'Humble Store metadata, policy-limited', 'connector_family': 'software_marketplace_metadata', 'source_family': 'storefront_app_store_metadata', 'trust_lane': 'official'}, 'chrome_web_store_metadata': {'source_id': 'chrome_web_store_metadata', 'source_label': 'Chrome Web Store metadata', 'connector_family': 'browser_extension_store_metadata', 'source_family': 'storefront_app_store_metadata', 'trust_lane': 'official'}, 'mozilla_addons_metadata': {'source_id': 'mozilla_addons_metadata', 'source_label': 'Mozilla Add-ons metadata', 'connector_family': 'browser_extension_store_metadata', 'source_family': 'storefront_app_store_metadata', 'trust_lane': 'official'}, 'flathub_metadata': {'source_id': 'flathub_metadata', 'source_label': 'Flathub metadata', 'connector_family': 'linux_app_store_metadata', 'source_family': 'storefront_app_store_metadata', 'trust_lane': 'community'}, 'snapcraft_metadata': {'source_id': 'snapcraft_metadata', 'source_label': 'Snapcraft metadata', 'connector_family': 'linux_app_store_metadata', 'source_family': 'storefront_app_store_metadata', 'trust_lane': 'community'}, 'generic_vendor_product_page': {'source_id': 'generic_vendor_product_page', 'source_label': 'Generic vendor product page metadata', 'connector_family': 'vendor_product_page_metadata', 'source_family': 'storefront_app_store_metadata', 'trust_lane': 'unknown'}, 'generic_commercial_software_marketplace': {'source_id': 'generic_commercial_software_marketplace', 'source_label': 'Generic commercial software marketplace metadata', 'connector_family': 'software_marketplace_metadata', 'source_family': 'storefront_app_store_metadata', 'trust_lane': 'unknown'}}
H11_SOURCE_IDS = tuple(H11_SOURCE_CONFIGS)
H11_FIXTURE_KINDS = ('minimal', 'listing_identity', 'app_product_identity', 'version_release_channel', 'price_availability_region', 'acquisition_path_blocked', 'review_rating_metadata', 'account_entitlement_boundary', 'rights_safety', 'policy_blocked')
FIXTURE_FORBIDDEN_TRUE_KEYS = {'entitlement_payload_included', 'redemption_subscription_action_performed', 'app_package_payload_included', 'catalog_payload_included', 'credential_or_token_payload_included', 'product_page_payload_included', 'screenshot_payload_included', 'network_used', 'user_library_payload_included', 'scraping_output_included', 'payment_payload_included', 'game_package_payload_included', 'live_call_used', 'cart_wishlist_action_performed', 'install_execute_performed', 'restricted_source_accessed', 'media_payload_included', 'installer_payload_included', 'checkout_action_performed', 'review_rating_write_performed', 'account_payload_included', 'license_key_payload_included', 'bypass_or_automation_used', 'purchase_action_performed', 'external_api_used', 'crawling_output_included', 'receipt_payload_included', 'storefront_search_payload_included', 'launch_execute_performed'}
TRUTH_FORBIDDEN_TRUE_KEYS = {'privacy_safety_claimed', 'accepted_evidence_truth', 'version_release_channel_candidate_is_truth', 'app_product_identity_candidate_is_truth', 'accepted_price_availability_truth', 'review_rating_metadata_candidate_is_quality_truth', 'acquisition_path_candidate_is_action_permission', 'storefront_metadata_grants_acquisition_permission', 'source_cache_preview_is_accepted_source', 'price_availability_region_candidate_is_truth', 'availability_metadata_is_current_availability_truth', 'production_readiness_claimed', 'accepted_app_product_truth', 'accepted_source_truth', 'purchase_permission_granted', 'accepted_account_entitlement_truth', 'public_index_mutated', 'storefront_rights_safety_candidate_is_rights_or_safety_truth', 'account_entitlement_boundary_candidate_is_license_truth', 'current_price_claimed', 'accepted_public_record', 'accepted_acquisition_permission', 'malware_safety_claimed', 'verified_authenticity_claimed', 'evidence_preview_is_accepted_evidence', 'accepted_candidate_truth', 'storefront_listing_identity_candidate_is_truth', 'master_index_mutated', 'accepted_rights_safety_truth', 'accepted_listing_identity_truth', 'install_launch_permission_granted', 'account_access_permission_granted', 'accepted_review_rating_truth', 'download_permission_granted', 'rights_clearance_claimed', 'license_entitlement_claimed', 'accepted_version_release_truth', 'current_availability_claimed', 'installability_claimed', 'price_metadata_is_current_price_truth', 'legal_acquisition_claimed', 'normalized_record_is_public_truth', 'content_safety_claimed'}
PRODUCT_FORBIDDEN_TRUE_KEYS = {'enabled_telemetry', 'crawling_used', 'changed_public_search_behavior', 'enabled_entitlement_checks', 'entitlement_check_used', 'purchase_action_used', 'network_calls_made', 'catalog_fetch_used', 'enabled_live_probes', 'product_page_fetch_used', 'enabled_purchase_actions', 'enabled_uploads', 'storefront_search_used', 'account_access_used', 'install_launch_used', 'review_rating_write_used', 'enabled_downloads', 'enabled_crawling', 'screenshot_media_fetch_used', 'enabled_source_sync', 'bypass_or_automation_used', 'enabled_accounts', 'mutated_master_index', 'enabled_install_launch', 'api_calls_made', 'mutated_public_index', 'restricted_source_access_used', 'enabled_hosting', 'download_used', 'scraping_used'}
NORMALIZED_SCALAR_FIELDS = ('source_native_id', 'listing_title', 'listing_id', 'storefront_id', 'storefront_native_id', 'product_page_url_candidate', 'developer_or_publisher', 'seller_or_distributor', 'platform', 'category_or_genre', 'listing_type', 'listing_status_candidate', 'region_candidate', 'language_candidate', 'app_or_product_name', 'bundle_id_candidate', 'package_name_candidate', 'app_id_candidate', 'sku_candidate', 'product_id_candidate', 'version_candidate', 'release_date_candidate', 'channel_candidate', 'branch_or_track_candidate', 'minimum_os_candidate', 'supported_device_candidate', 'architecture_candidate', 'build_number_candidate', 'price_candidate', 'currency_candidate', 'sale_or_discount_candidate', 'availability_status_candidate', 'account_or_device_condition_candidate', 'subscription_or_membership_condition_candidate', 'purchase_or_license_model_candidate', 'rating_value_candidate', 'rating_count_candidate', 'review_count_candidate', 'review_snippet_candidate', 'license_or_terms_metadata_candidate', 'age_rating_candidate', 'content_warning_candidate', 'privacy_label_candidate', 'security_or_malware_risk_candidate')


def normalize_h11_storefront_fixture(raw_fixture: Mapping[str, Any], source_id: str, policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Normalize a committed H11 fixture without live access or side effects."""
    _require_fixture_boundaries(raw_fixture)
    if source_id not in H11_SOURCE_CONFIGS:
        raise ValueError(f"unknown H11 source_id: {source_id}")
    if raw_fixture.get("source_id") != source_id:
        raise ValueError("fixture source_id does not match requested source")
    config = H11_SOURCE_CONFIGS[source_id]
    payload = _mapping(raw_fixture.get("fixture_payload"), "fixture_payload")
    native_id = _text(payload.get("source_native_id")) or _text(raw_fixture.get("fixture_id")) or "unknown"
    fixture_kind = _text(raw_fixture.get("fixture_kind")) or "unknown"
    record: dict[str, Any] = {
        "schema_version": "h11_storefront_normalized_record.v0",
        "normalized_record_id": f"h11.normalized.{source_id}.{_slug(native_id)}.v0",
        "source_id": source_id,
        "connector_family": config["connector_family"],
        "source_record_kind": _text(payload.get("source_record_kind")) or fixture_kind,
        "source_metadata": {
            "fixture_id": raw_fixture.get("fixture_id", "unknown"),
            "fixture_kind": fixture_kind,
            "fixture_status": raw_fixture.get("fixture_status", "unknown"),
            "source_label": config["source_label"],
            "trust_lane": config["trust_lane"],
            "metadata_summary": payload.get("metadata_summary", "synthetic fixture metadata only"),
        },
        "source_limitations": _dedupe(_list(raw_fixture.get("limitations")) + _missing_optional_limitations(payload)),
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": [
            "Offline fixture normalization only.",
            "Candidate and preview outputs require review and do not grant live access, downloads, account access, purchase, entitlement, install, launch, review-write, evidence acceptance, or public truth.",
        ],
    }
    for field in NORMALIZED_SCALAR_FIELDS:
        record[field] = _text(payload.get(field)) or "unknown"
    record["storefront_listing_identity_candidate"] = build_h11_storefront_listing_identity_candidate(record, policy)
    record["app_product_identity_candidate"] = build_h11_app_product_identity_candidate(record, policy)
    record["version_release_channel_candidate"] = build_h11_version_release_channel_candidate(record, policy)
    record["price_availability_region_candidate"] = build_h11_price_availability_region_candidate(record, policy)
    record["acquisition_path_candidate"] = build_h11_acquisition_path_candidate(record, policy)
    record["review_rating_metadata_candidate"] = build_h11_review_rating_metadata_candidate(record, policy)
    record["account_entitlement_boundary_candidate"] = build_h11_account_entitlement_boundary_candidate(record, policy)
    record["storefront_rights_safety_candidate"] = build_h11_storefront_rights_safety_candidate(record, policy)
    record["source_cache_candidate_preview"] = build_h11_source_cache_candidate_preview(record, policy)
    record["evidence_candidate_preview"] = build_h11_evidence_candidate_preview(record, policy)
    _raise_on_boundary_errors(record)
    return record


def build_h11_storefront_listing_identity_candidate(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    fields = ("listing_title", "listing_id", "storefront_id", "storefront_native_id", "product_page_url_candidate", "developer_or_publisher", "seller_or_distributor", "platform", "category_or_genre", "listing_type", "listing_status_candidate", "region_candidate", "language_candidate", "source_native_id")
    return _candidate(normalized_record, "storefront_listing_identity", "h11_storefront_listing_identity_candidate.v0", fields, "Storefront listing identity candidate only; listing presence does not prove availability or acquisition permission.")


def build_h11_app_product_identity_candidate(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    fields = ("app_or_product_name", "bundle_id_candidate", "package_name_candidate", "app_id_candidate", "sku_candidate", "product_id_candidate", "developer_or_publisher", "seller_or_distributor", "platform", "source_native_id")
    return _candidate(normalized_record, "app_product_identity", "h11_app_product_identity_candidate.v0", fields, "App/product identity candidate only; identifiers require review and do not prove entitlement, installability, or safety.")


def build_h11_version_release_channel_candidate(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    fields = ("version_candidate", "release_date_candidate", "channel_candidate", "branch_or_track_candidate", "minimum_os_candidate", "supported_device_candidate", "architecture_candidate", "build_number_candidate", "app_or_product_name", "platform")
    return _candidate(normalized_record, "version_release_channel", "h11_version_release_channel_candidate.v0", fields, "Version/release/channel candidate only; version metadata can vary by region, account, device, channel, and time.")


def build_h11_price_availability_region_candidate(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    fields = ("price_candidate", "currency_candidate", "sale_or_discount_candidate", "availability_status_candidate", "region_candidate", "account_or_device_condition_candidate", "subscription_or_membership_condition_candidate", "purchase_or_license_model_candidate", "listing_id")
    return _candidate(normalized_record, "price_availability_region", "h11_price_availability_region_candidate.v0", fields, "Price/availability/region candidate only; it is not current price, current availability, legal acquisition, or download permission.")


def build_h11_acquisition_path_candidate(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    fields = ("listing_id", "product_id_candidate", "product_page_url_candidate", "account_or_device_condition_candidate", "purchase_or_license_model_candidate", "region_candidate")
    candidate = _candidate(normalized_record, "acquisition_path", "h11_acquisition_path_candidate.v0", fields, "Acquisition path candidate is blocked by H11 fixture policy and is not action permission.")
    candidate["action_kind"] = "not_evaluable" if normalized_record.get("source_record_kind") == "policy_blocked" else "inspect_metadata"
    candidate["action_status_current"] = "blocked_current"
    candidate["blocked_reason"] = "H11-BUNDLE-02 fixture runtime does not authorize purchase, checkout, cart, wishlist, redemption, subscription, download, install, launch, account, entitlement, or review-write behavior."
    candidate["j_track_required"] = True
    _raise_on_boundary_errors(candidate)
    return candidate


def build_h11_review_rating_metadata_candidate(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    fields = ("rating_value_candidate", "rating_count_candidate", "review_count_candidate", "review_snippet_candidate", "listing_id", "region_candidate", "language_candidate")
    return _candidate(normalized_record, "review_rating_metadata", "h11_review_rating_metadata_candidate.v0", fields, "Review/rating metadata candidate only; it is not quality truth and Eureka must not write reviews, ratings, votes, comments, or feedback.")


def build_h11_account_entitlement_boundary_candidate(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    fields = ("account_or_device_condition_candidate", "subscription_or_membership_condition_candidate", "purchase_or_license_model_candidate", "listing_id", "product_id_candidate")
    candidate = _candidate(normalized_record, "account_entitlement_boundary", "h11_account_entitlement_boundary_candidate.v0", fields, "Account/entitlement boundary candidate only; no account, credential, receipt, license key, entitlement, payment, subscription, device registration, or user library access is allowed.")
    candidate["account_access_current"] = "blocked_current"
    candidate["entitlement_verification_current"] = "blocked_current"
    candidate["private_data_handling_current"] = "blocked_current"
    _raise_on_boundary_errors(candidate)
    return candidate


def build_h11_storefront_rights_safety_candidate(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    fields = ("license_or_terms_metadata_candidate", "age_rating_candidate", "content_warning_candidate", "privacy_label_candidate", "security_or_malware_risk_candidate", "listing_id", "app_or_product_name")
    return _candidate(normalized_record, "storefront_rights_safety", "h11_storefront_rights_safety_candidate.v0", fields, "Storefront rights/safety metadata candidate only; storefront presence does not prove rights clearance, legal acquisition, malware safety, content safety, privacy safety, or quality.")


def build_h11_source_cache_candidate_preview(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    preview = {
        "schema_version": "h11_storefront_source_cache_candidate_preview.v0",
        "preview_id": f"h11.source_cache.preview.{normalized_record.get('source_id')}.{_slug(normalized_record.get('source_native_id'))}.v0",
        "source_id": normalized_record.get("source_id"),
        "source_record_ref": normalized_record.get("normalized_record_id"),
        "preview_only": True,
        "accepted_source": False,
        "mutates_source_cache": False,
        "supporting_fields": {
            "source_native_id": normalized_record.get("source_native_id"),
            "source_record_kind": normalized_record.get("source_record_kind"),
            "listing_title": normalized_record.get("listing_title"),
        },
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "limitations": ["Source-cache preview only; no source cache write or source truth acceptance occurs."],
    }
    _raise_on_boundary_errors(preview)
    return preview


def build_h11_evidence_candidate_preview(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    preview = {
        "schema_version": "h11_storefront_evidence_candidate_preview.v0",
        "preview_id": f"h11.evidence.preview.{normalized_record.get('source_id')}.{_slug(normalized_record.get('source_native_id'))}.v0",
        "source_id": normalized_record.get("source_id"),
        "source_record_ref": normalized_record.get("normalized_record_id"),
        "preview_only": True,
        "accepted_evidence": False,
        "mutates_evidence_ledger": False,
        "claim_summary": "Storefront fixture metadata candidate only.",
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "limitations": ["Evidence preview only; no evidence acceptance occurs."],
    }
    _raise_on_boundary_errors(preview)
    return preview


def build_h11_fixture_replay_result(fixture: Mapping[str, Any], normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    result = {
        "schema_version": "h11_storefront_fixture_replay_result.v0",
        "fixture_replay_result_id": f"h11.replay.{fixture.get('source_id')}.{fixture.get('fixture_kind')}.v0",
        "source_id": fixture.get("source_id"),
        "connector_family": normalized_record.get("connector_family"),
        "fixture_ref": fixture.get("fixture_id"),
        "normalized_record_ref": normalized_record.get("normalized_record_id"),
        "result_status": "normalized_fixture",
        "network_used": False,
        "download_account_purchase_install_launch_used": False,
        "candidate_counts": {
            "storefront_listing_identity_candidate": 1,
            "app_product_identity_candidate": 1,
            "version_release_channel_candidate": 1,
            "price_availability_region_candidate": 1,
            "acquisition_path_candidate": 1,
            "review_rating_metadata_candidate": 1,
            "account_entitlement_boundary_candidate": 1,
            "storefront_rights_safety_candidate": 1,
        },
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "limitations": ["Fixture replay output is not source, evidence, candidate, public, or master truth."],
    }
    _raise_on_boundary_errors(result)
    return result


def summarize_h11_normalized_record(record: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "source_id": record.get("source_id"),
        "source_record_kind": record.get("source_record_kind"),
        "listing_title": record.get("listing_title"),
        "app_or_product_name": record.get("app_or_product_name"),
        "candidate_count": 8,
        "truth_boundary_violations": detect_h11_truth_boundary_violations(record),
        "product_boundary_violations": detect_h11_product_boundary_violations(record),
    }


def detect_h11_truth_boundary_violations(record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    violations: list[str] = []
    _collect_true_keys(record, TRUTH_FORBIDDEN_TRUE_KEYS, "truth", violations)
    return violations


def detect_h11_product_boundary_violations(record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    violations: list[str] = []
    _collect_true_keys(record, PRODUCT_FORBIDDEN_TRUE_KEYS, "product", violations)
    return violations


def _candidate(normalized_record: Mapping[str, Any], kind: str, schema_version: str, fields: tuple[str, ...], limitation: str) -> dict[str, Any]:
    supporting = {field: normalized_record.get(field) for field in fields if normalized_record.get(field) not in (None, "", [], {}, "unknown")}
    missing = [field for field in fields if field not in supporting]
    candidate = {
        "schema_version": schema_version,
        "candidate_id": f"h11.{kind}.{normalized_record.get('source_id')}.{_slug(normalized_record.get('source_native_id'))}.v0",
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
    errors = []
    _collect_true_keys(raw_fixture, FIXTURE_FORBIDDEN_TRUE_KEYS, "fixture", errors)
    _collect_true_keys(raw_fixture, TRUTH_FORBIDDEN_TRUE_KEYS, "truth", errors)
    _collect_true_keys(raw_fixture, PRODUCT_FORBIDDEN_TRUE_KEYS, "product", errors)
    if errors:
        raise ValueError("; ".join(errors))


def _raise_on_boundary_errors(record: Mapping[str, Any]) -> None:
    errors = detect_h11_truth_boundary_violations(record) + detect_h11_product_boundary_violations(record)
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
    return [f"Missing optional storefront fixture fields are unknown, not fabricated: {', '.join(missing[:8])}"]


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
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]
    return digest
