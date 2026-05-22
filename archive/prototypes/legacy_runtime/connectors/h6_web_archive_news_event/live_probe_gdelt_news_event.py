"""Source-specific H6 live-probe metadata wrapper for gdelt_news_event."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from archive.prototypes.legacy_runtime.connectors.h6_web_archive_news_event.live_probe_common import build_metadata_request, normalize_h6_web_archive_live_probe_result, parse_metadata_response

SOURCE_ID = "gdelt_news_event"


def build_request_url_or_metadata_request(request: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return build_metadata_request(SOURCE_ID, request, policy_bundle)


def parse_response_payload(response_payload: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return parse_metadata_response(SOURCE_ID, response_payload, policy_bundle)


def normalize_response_payload(response_payload: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return normalize_h6_web_archive_live_probe_result({"source_id": SOURCE_ID, "response_payload": parse_response_payload(response_payload, policy_bundle), "response_metadata": {"network_used": False}}, policy_bundle)
