"""H4 code/source/release metadata live-probe wrapper for sourceforge."""

from __future__ import annotations

from typing import Any, Mapping

from control.prototypes.legacy_runtime.connectors.h4_code_source_release.live_probe_common import (
    _source_normalize_response_payload,
    _source_parse_response_payload,
    build_request_url_or_metadata_request as _build_request,
)

SOURCE_ID = "sourceforge"


def build_request_url_or_metadata_request(request: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return _build_request(SOURCE_ID, request, policy_bundle)


def parse_response_payload(response_payload: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return _source_parse_response_payload(SOURCE_ID, response_payload, policy_bundle)


def normalize_response_payload(response_payload: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return _source_normalize_response_payload(SOURCE_ID, response_payload, policy_bundle)
