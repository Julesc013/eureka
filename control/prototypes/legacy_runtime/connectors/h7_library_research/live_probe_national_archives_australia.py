"""Fail-closed H7 metadata live-probe wrapper for national_archives_australia."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .live_probe_common import (
    build_h7_library_research_live_probe_result,
    load_h7_library_research_live_probe_policy_bundle,
)

SOURCE_ID = "national_archives_australia"
DEFAULT_ENDPOINT_OR_METADATA_CLASS = "cultural_object_metadata_lookup_future"


def build_request_url_or_metadata_request(request: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "source_id": SOURCE_ID,
        "endpoint_or_metadata_class": str(request.get("endpoint_or_metadata_class") or DEFAULT_ENDPOINT_OR_METADATA_CLASS),
        "request_shape": dict(request.get("request_shape") or {}),
        "network_request_allowed": False,
        "metadata_only": True,
        "notes": ["Metadata request descriptor only; committed H7 policies currently block live source calls."],
    }


def parse_response_payload(response_payload: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return dict(response_payload)


def normalize_response_payload(response_payload: Mapping[str, Any], policy_bundle: Mapping[str, Any] | None = None) -> dict[str, Any]:
    bundle = dict(policy_bundle) if policy_bundle is not None else load_h7_library_research_live_probe_policy_bundle()
    result = build_h7_library_research_live_probe_result(
        SOURCE_ID,
        parse_response_payload(response_payload, bundle),
        {"endpoint_or_metadata_used": DEFAULT_ENDPOINT_OR_METADATA_CLASS, "network_used": False, "request_count": 0},
        bundle,
    )
    return result["normalized_record"]
