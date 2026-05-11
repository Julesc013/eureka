"""Source-specific fail-closed H11 live-probe wrapper for Generic vendor product page metadata."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from runtime.connectors.h11_storefront.live_probe_common import SOURCE_CONFIGS, build_h11_storefront_live_probe_result

SOURCE_ID = "generic_vendor_product_page"


def build_request_url_or_metadata_request(request: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    cfg = SOURCE_CONFIGS[SOURCE_ID]
    if request.get("source_id") != SOURCE_ID:
        raise ValueError("request source_id does not match generic_vendor_product_page")
    if request.get("endpoint_or_metadata_class") != cfg["endpoint"]:
        raise ValueError("endpoint_or_metadata_class is not allowlisted for this source wrapper")
    return {
        "source_id": SOURCE_ID,
        "request_key": request.get("approved_request_key"),
        "endpoint_or_metadata_class": cfg["endpoint"],
        "metadata_only": True,
        "arbitrary_url_allowed": False,
        "locator": None,
        "storefront_search_allowed": False,
        "product_page_fetch_allowed": False,
        "screenshot_media_fetch_allowed": False,
        "downloads_allowed": False,
        "account_access_allowed": False,
        "purchase_automation_allowed": False,
        "entitlement_verification_allowed": False,
        "install_launch_allowed": False,
        "review_rating_write_allowed": False,
        "scraping_crawling_allowed": False,
        "restricted_source_access_allowed": False,
        "bypass_or_automation_allowed": False,
    }


def parse_response_payload(response_payload: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(response_payload, Mapping):
        raise ValueError("response_payload must be an object")
    return dict(response_payload)


def normalize_response_payload(response_payload: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    result = build_h11_storefront_live_probe_result(
        SOURCE_ID,
        parse_response_payload(response_payload, policy_bundle),
        {"request_key": SOURCE_CONFIGS[SOURCE_ID]["request_key"], "network_used": False, "result_status": "dry_run_preflight_pass"},
        policy_bundle,
    )
    return result["normalized_record"]
