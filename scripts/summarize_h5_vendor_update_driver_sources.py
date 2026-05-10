#!/usr/bin/env python3
"""Summarize H5 vendor/update/driver/firmware policy-pack sources offline."""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import sys
import tempfile
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_INVENTORY = REPO_ROOT / "control/inventory/source_packs/h5_vendor_update_driver_sources.json"
CONNECTOR_FAMILIES = REPO_ROOT / "control/inventory/source_packs/h5_vendor_update_driver_connector_families.json"
VENDOR_IDENTITY_POLICY = REPO_ROOT / "control/inventory/source_packs/h5_vendor_identity_policy.json"
COMPATIBILITY_POLICY = REPO_ROOT / "control/inventory/source_packs/h5_driver_device_compatibility_policy.json"
FIRMWARE_POLICY = REPO_ROOT / "control/inventory/source_packs/h5_firmware_update_policy.json"
RUNTIME_POLICY = REPO_ROOT / "control/inventory/source_packs/h5_runtime_redistributable_policy.json"
FORBIDDEN_OUTPUT_ROOTS = (
    "site/dist",
    "data/public_index",
    "runtime",
    "contracts",
    "data/master_index",
    "master_index",
    ".aide.local",
    ".local/eureka",
    ".cache/eureka",
    "vendor_downloads",
    "firmware_staging",
    "package_cache",
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", help="Optional JSON summary output path.")
    parser.add_argument("--summary-output", help="Optional Markdown summary output path.")
    parser.add_argument("--check", action="store_true", help="Summarize without writing files.")
    parser.add_argument("--json", action="store_true", help="Print JSON summary.")
    args = parser.parse_args(argv)
    try:
        summary = build_summary()
        if not args.check:
            if args.output:
                _write_json(args.output, summary)
            if args.summary_output:
                _write_text(args.summary_output, render_summary_markdown(summary))
        if args.json:
            print(json.dumps(summary, indent=2, sort_keys=True), file=stdout)
        else:
            print("H5 vendor/update/driver source summary", file=stdout)
            print(f"status: {summary['status']}", file=stdout)
            print(f"source_count: {summary['source_count']}", file=stdout)
            print(f"live_access_enabled_count: {summary['live_access_enabled_count']}", file=stdout)
            print(f"catalog_fetch_enabled_count: {summary['catalog_fetch_enabled_count']}", file=stdout)
            print(f"download_enabled_count: {summary['download_enabled_count']}", file=stdout)
            print(f"firmware_flash_enabled_count: {summary['firmware_flash_enabled_count']}", file=stdout)
        return 0
    except Exception as exc:  # noqa: BLE001
        if args.json:
            print(json.dumps({"status": "invalid", "error": str(exc)}, indent=2, sort_keys=True), file=stdout)
        else:
            print("H5 vendor/update/driver source summary", file=stdout)
            print("status: invalid", file=stdout)
            print(f"ERROR: {exc}", file=stdout)
        return 1


def build_summary() -> dict[str, Any]:
    inventory = _load_json(SOURCE_INVENTORY)
    connector_mapping = _load_json(CONNECTOR_FAMILIES)
    vendor_identity_policy = _load_json(VENDOR_IDENTITY_POLICY)
    compatibility_policy = _load_json(COMPATIBILITY_POLICY)
    firmware_policy = _load_json(FIRMWARE_POLICY)
    runtime_policy = _load_json(RUNTIME_POLICY)
    sources = inventory.get("sources", [])
    if not isinstance(sources, list):
        raise ValueError("H5 source inventory must contain a sources list")
    source_family_counts = Counter(str(item.get("source_family", "unknown")) for item in sources if isinstance(item, Mapping))
    connector_family_counts = Counter(str(item.get("connector_family", "unknown")) for item in sources if isinstance(item, Mapping))
    trust_lane_counts = Counter(str(item.get("trust_lane", "unknown")) for item in sources if isinstance(item, Mapping))
    access_mode_counts = Counter(str(item.get("current_access_mode", "unknown")) for item in sources if isinstance(item, Mapping))
    index_depth_counts = Counter(str(item.get("current_index_depth", "unknown")) for item in sources if isinstance(item, Mapping))
    mappings = connector_mapping.get("source_connector_family_mappings", connector_mapping.get("mappings", []))
    if not isinstance(mappings, list):
        mappings = []
    def count_true(key: str) -> int:
        return sum(1 for item in sources if isinstance(item, Mapping) and item.get(key) is True)
    download_keys = (
        "driver_download_enabled",
        "firmware_download_enabled",
        "runtime_download_enabled",
        "installer_download_enabled",
        "update_package_download_enabled",
    )
    download_enabled_count = sum(
        1
        for item in sources
        if isinstance(item, Mapping) and any(item.get(key) is True for key in download_keys)
    )
    return {
        "schema_version": "h5_vendor_update_driver_source_summary.v0",
        "status": "pass",
        "wave_id": inventory.get("wave_id", "H5"),
        "current_status": inventory.get("current_status", "policy_pack_only"),
        "source_count": len(sources),
        "source_ids": sorted(str(item.get("source_id", "")) for item in sources if isinstance(item, Mapping)),
        "source_family_counts": dict(sorted(source_family_counts.items())),
        "connector_family_counts": dict(sorted(connector_family_counts.items())),
        "trust_lane_counts": dict(sorted(trust_lane_counts.items())),
        "access_mode_counts": dict(sorted(access_mode_counts.items())),
        "index_depth_counts": dict(sorted(index_depth_counts.items())),
        "fixture_required_count": count_true("fixture_required"),
        "future_live_probe_required_count": count_true("live_probe_required_future"),
        "scorecard_required_count": count_true("scorecard_required"),
        "coverage_required_count": count_true("coverage_required"),
        "vendor_identity_support_count": sum(1 for item in sources if isinstance(item, Mapping) and isinstance(item.get("vendor_identity_support"), Mapping)),
        "driver_device_compatibility_support_count": sum(1 for item in sources if isinstance(item, Mapping) and isinstance(item.get("driver_device_compatibility_support"), Mapping) and item["driver_device_compatibility_support"].get("driver_metadata_future") is True),
        "firmware_update_support_count": sum(1 for item in sources if isinstance(item, Mapping) and isinstance(item.get("firmware_update_support"), Mapping) and item["firmware_update_support"].get("firmware_metadata_future") is True),
        "runtime_redistributable_support_count": sum(1 for item in sources if isinstance(item, Mapping) and isinstance(item.get("runtime_redistributable_support"), Mapping) and item["runtime_redistributable_support"].get("runtime_metadata_future") is True),
        "signature_or_hash_metadata_support_count": sum(1 for item in sources if isinstance(item, Mapping) and isinstance(item.get("signature_or_hash_metadata_support"), Mapping) and item["signature_or_hash_metadata_support"].get("hash_metadata_future") is True),
        "vendor_identity_concepts": vendor_identity_policy.get("identity_concepts", []),
        "compatibility_concepts": compatibility_policy.get("compatibility_candidate_concepts", []),
        "firmware_update_concepts": firmware_policy.get("firmware_update_candidate_concepts", []),
        "runtime_concepts": runtime_policy.get("runtime_candidate_concepts", []),
        "connector_mapping_count": len(mappings),
        "live_access_enabled_count": count_true("live_access_enabled"),
        "source_sync_enabled_count": count_true("source_sync_enabled"),
        "connector_runtime_enabled_count": count_true("connector_runtime_enabled"),
        "catalog_fetch_enabled_count": count_true("vendor_catalog_fetch_enabled"),
        "download_enabled_count": download_enabled_count,
        "vendor_tool_invocation_enabled_count": count_true("vendor_tool_invocation_enabled"),
        "firmware_flash_enabled_count": count_true("firmware_flash_enabled"),
        "install_execute_enabled_count": count_true("install_execute_enabled"),
        "blockers": [
            "fixture runtime not implemented",
            "live access not approved",
            "vendor catalog fetch forbidden",
            "driver, firmware, runtime, installer, and update package downloads forbidden",
            "vendor tool and package manager invocation forbidden",
            "install, execution, and firmware flashing forbidden",
            "public and master index mutation forbidden",
        ],
        "readiness": "READY_FOR_H5_FIXTURE_RUNTIME",
        "truth_boundary": {
            "source_pack_is_truth": False,
            "policy_pack_grants_live_access": False,
            "vendor_identity_candidate_is_truth": False,
            "driver_identity_candidate_is_truth": False,
            "firmware_identity_candidate_is_truth": False,
            "runtime_identity_candidate_is_truth": False,
            "compatibility_candidate_is_truth": False,
            "hash_metadata_proves_malware_safety": False,
            "signature_metadata_proves_authenticity": False,
            "coverage_preview_is_exhaustive": False,
            "scorecard_preview_is_production_ready": False,
            "public_index_mutated": False,
            "master_index_mutated": False,
            "rights_clearance_claimed": False,
            "malware_safety_claimed": False,
            "verified_installability_claimed": False,
            "verified_compatibility_claimed": False,
            "verified_authenticity_claimed": False,
        },
        "product_boundary": {
            "changed_public_search_behavior": False,
            "enabled_live_probes": False,
            "enabled_source_sync": False,
            "enabled_source_connectors": False,
            "enabled_catalog_fetch": False,
            "enabled_downloads": False,
            "enabled_execution": False,
            "enabled_firmware_flashing": False,
            "mutated_public_index": False,
            "mutated_master_index": False,
        },
    }


def render_summary_markdown(summary: Mapping[str, Any]) -> str:
    lines = [
        "# H5 Vendor Update Driver Source Summary",
        "",
        f"- status: `{summary.get('status')}`",
        f"- source_count: `{summary.get('source_count', 0)}`",
        f"- current_status: `{summary.get('current_status')}`",
        f"- live_access_enabled_count: `{summary.get('live_access_enabled_count', 0)}`",
        f"- source_sync_enabled_count: `{summary.get('source_sync_enabled_count', 0)}`",
        f"- connector_runtime_enabled_count: `{summary.get('connector_runtime_enabled_count', 0)}`",
        f"- catalog_fetch_enabled_count: `{summary.get('catalog_fetch_enabled_count', 0)}`",
        f"- download_enabled_count: `{summary.get('download_enabled_count', 0)}`",
        f"- vendor_tool_invocation_enabled_count: `{summary.get('vendor_tool_invocation_enabled_count', 0)}`",
        f"- firmware_flash_enabled_count: `{summary.get('firmware_flash_enabled_count', 0)}`",
        f"- install_execute_enabled_count: `{summary.get('install_execute_enabled_count', 0)}`",
        f"- readiness: `{summary.get('readiness')}`",
        "",
        "## Sources",
    ]
    lines.extend(f"- {source_id}" for source_id in summary.get("source_ids", []))
    lines.extend(["", "## Source Families"])
    lines.extend(f"- {key}: {value}" for key, value in summary.get("source_family_counts", {}).items())
    lines.extend(["", "## Connector Families"])
    lines.extend(f"- {key}: {value}" for key, value in summary.get("connector_family_counts", {}).items())
    lines.extend(["", "## Blockers"])
    lines.extend(f"- {item}" for item in summary.get("blockers", []))
    return "\n".join(lines) + "\n"


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _write_json(path_text: str, payload: Mapping[str, Any]) -> None:
    path = _safe_output_path(Path(path_text))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text(path_text: str, text: str) -> None:
    path = _safe_output_path(Path(path_text))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _safe_output_path(path: Path) -> Path:
    resolved = (REPO_ROOT / path).resolve() if not path.is_absolute() else path.resolve()
    repo_root = REPO_ROOT.resolve()
    try:
        rel = resolved.relative_to(repo_root).as_posix()
        rel_lower = rel.casefold()
        for forbidden in FORBIDDEN_OUTPUT_ROOTS:
            forbidden_lower = forbidden.casefold().rstrip("/")
            if rel_lower == forbidden_lower or rel_lower.startswith(forbidden_lower + "/"):
                raise ValueError(f"refusing forbidden H5 output root: {rel}")
    except ValueError as exc:
        if str(exc).startswith("refusing"):
            raise
        temp_root = Path(tempfile.gettempdir()).resolve()
        try:
            resolved.relative_to(temp_root)
        except ValueError as temp_exc:
            raise ValueError(f"refusing output outside repository or temp directory: {path}") from temp_exc
    return resolved


if __name__ == "__main__":
    raise SystemExit(main())
