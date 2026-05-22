"""Source-specific fail-closed H10 live-probe wrapper for Redump hash-set metadata."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from archive.prototypes.legacy_runtime.connectors.h10_games_emulation.live_probe_common import (
    SOURCE_CONFIGS,
    build_h10_games_emulation_live_probe_result,
)

SOURCE_ID = "redump_hash_sets"


def build_request_url_or_metadata_request(request: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    cfg = SOURCE_CONFIGS[SOURCE_ID]
    if request.get("source_id") != SOURCE_ID:
        raise ValueError("request source_id does not match redump_hash_sets")
    if request.get("endpoint_or_metadata_class") != cfg["endpoint"]:
        raise ValueError("endpoint_or_metadata_class is not allowlisted for this source wrapper")
    return {
        "source_id": SOURCE_ID,
        "request_key": request.get("approved_request_key"),
        "endpoint_or_metadata_class": cfg["endpoint"],
        "metadata_only": True,
        "arbitrary_url_allowed": False,
        "url": None,
        "rom_download_allowed": False,
        "iso_download_allowed": False,
        "disc_image_download_allowed": False,
        "bios_firmware_download_allowed": False,
        "game_binary_download_allowed": False,
        "emulator_download_allowed": False,
        "file_upload_allowed": False,
        "hash_submission_allowed": False,
        "execution_allowed": False,
        "acquisition_action_allowed": False,
        "scraping_crawling_allowed": False,
        "restricted_source_access_allowed": False,
    }


def parse_response_payload(response_payload: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(response_payload, Mapping):
        raise ValueError("response_payload must be an object")
    return dict(response_payload)


def normalize_response_payload(response_payload: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    result = build_h10_games_emulation_live_probe_result(
        SOURCE_ID,
        parse_response_payload(response_payload, policy_bundle),
        {"request_key": SOURCE_CONFIGS[SOURCE_ID]["request_key"], "network_used": False, "result_status": "dry_run_preflight_pass"},
        policy_bundle,
    )
    return result["normalized_record"]
