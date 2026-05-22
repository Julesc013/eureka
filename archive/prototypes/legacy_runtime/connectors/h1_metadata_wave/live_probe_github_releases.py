"""H1 metadata live-probe wrapper for GitHub Releases."""

from __future__ import annotations

from typing import Any, Mapping

from archive.prototypes.legacy_runtime.connectors.h1_metadata_wave.live_probe_common import (
    _source_normalize_response_payload,
    _source_parse_response_payload,
    build_request_url_or_metadata_request as _build_request,
)


SOURCE_ID = "github_releases"


def build_request_url_or_metadata_request(request: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return _build_request(SOURCE_ID, request, policy_bundle)


def parse_response_payload(response_payload: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return _source_parse_response_payload(SOURCE_ID, response_payload, policy_bundle)


def normalize_response_payload(response_payload: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return _source_normalize_response_payload(SOURCE_ID, policy_bundle=policy_bundle, response_payload=response_payload)
