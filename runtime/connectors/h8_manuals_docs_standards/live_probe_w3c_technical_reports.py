"""Fail-closed H8 live-probe wrapper for W3C technical report metadata."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from runtime.connectors.h8_manuals_docs_standards.live_probe_common import (
    SOURCE_CONFIGS,
    build_h8_manuals_docs_live_probe_result,
)

SOURCE_ID = "w3c_technical_reports"


def build_request_url_or_metadata_request(request: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    cfg = SOURCE_CONFIGS[SOURCE_ID]
    return {
        "source_id": SOURCE_ID,
        "request_key": request.get("approved_request_key"),
        "endpoint_or_metadata_class": cfg["endpoint_or_metadata_class"],
        "metadata_request_only": True,
        "network_call_allowed": False,
        "arbitrary_url_allowed": False,
        "document_fetch_allowed": False,
        "download_allowed": False,
        "scrape_or_crawl_allowed": False,
        "restricted_source_access_allowed": False,
    }


def parse_response_payload(response_payload: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return dict(response_payload)


def normalize_response_payload(response_payload: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    result = build_h8_manuals_docs_live_probe_result(SOURCE_ID, response_payload, {"network_used": False, "request_key": SOURCE_CONFIGS[SOURCE_ID]["request_key"]}, policy_bundle)
    return dict(result["normalized_record"])
