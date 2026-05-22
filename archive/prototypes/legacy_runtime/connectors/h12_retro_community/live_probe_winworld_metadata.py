"""Source-specific H12 live-probe wrapper for winworld_metadata."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from archive.prototypes.legacy_runtime.connectors.h12_retro_community.live_probe_common import SOURCE_CONFIGS, _normal_record_from_response

SOURCE_ID = "winworld_metadata"


def build_request_url_or_metadata_request(request: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    cfg = SOURCE_CONFIGS[SOURCE_ID]
    return {
        "source_id": SOURCE_ID,
        "connector_family": cfg["connector_family"],
        "endpoint_or_metadata_class": cfg["endpoint"],
        "approved_request_key": request.get("approved_request_key"),
        "metadata_request_only": True,
        "network_transport_enabled": False,
        "url": None,
        "notes": ["H12-BUNDLE-03 keeps source transport fail-closed unless future committed approval opens it."],
    }


def parse_response_payload(response_payload: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return dict(response_payload)


def normalize_response_payload(response_payload: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return _normal_record_from_response(SOURCE_ID, response_payload, {"network_used": False, "result_status": "dry_run_preflight_pass"})
