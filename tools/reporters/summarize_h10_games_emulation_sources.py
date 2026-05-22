#!/usr/bin/env python3
"""Summarize H10 games/emulation source policy packs offline."""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import sys
import tempfile
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_INVENTORY = REPO_ROOT / "control/inventory/source_packs/h10_games_emulation_sources.json"
CONNECTOR_FAMILIES = REPO_ROOT / "control/inventory/source_packs/h10_games_emulation_connector_families.json"
FORBIDDEN_OUTPUT_ROOTS = (
    "site/dist",
    "site/dist/data/public_index",
    "runtime",
    "contracts",
    "data/master_index",
    "master_index",
    ".aide.local",
    ".local/eureka",
    ".cache/eureka",
    "roms",
    "isos",
    "disc_images",
    "emulators",
    "bios",
    "game_installs",
    "launchers",
    "hash_submissions",
    "storefront_accounts",
    "restricted_sources",
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
                summary["wrote_files"] = True
            if args.summary_output:
                _write_text(args.summary_output, render_summary_markdown(summary))
                summary["wrote_files"] = True
        if args.json:
            print(json.dumps(summary, indent=2, sort_keys=True), file=stdout)
        else:
            print("H10 games emulation source summary", file=stdout)
            print(f"status: {summary['status']}", file=stdout)
            print(f"source_count: {summary['source_count']}", file=stdout)
            print(f"live_access_enabled_count: {summary['live_access_enabled_count']}", file=stdout)
            print(f"software_list_hashset_fetch_enabled_count: {summary['software_list_hashset_fetch_enabled_count']}", file=stdout)
            print(f"downloads_enabled_count: {summary['downloads_enabled_count']}", file=stdout)
            print(f"uploads_enabled_count: {summary['uploads_enabled_count']}", file=stdout)
            print(f"execution_enabled_count: {summary['execution_enabled_count']}", file=stdout)
            print(f"acquisition_action_enabled_count: {summary['acquisition_action_enabled_count']}", file=stdout)
        return 0
    except Exception as exc:  # noqa: BLE001
        if args.json:
            print(json.dumps({"status": "invalid", "error": str(exc)}, indent=2, sort_keys=True), file=stdout)
        else:
            print("H10 games emulation source summary", file=stdout)
            print("status: invalid", file=stdout)
            print(f"ERROR: {exc}", file=stdout)
        return 1


def build_summary() -> dict[str, Any]:
    inventory = _load_json(SOURCE_INVENTORY)
    connector_mapping = _load_json(CONNECTOR_FAMILIES)
    sources = inventory.get("sources", [])
    if not isinstance(sources, list):
        raise ValueError("H10 source inventory must contain a sources list")
    source_family_counts = Counter(str(item.get("source_family", "unknown")) for item in sources if isinstance(item, Mapping))
    connector_family_counts = Counter(str(item.get("connector_family", "unknown")) for item in sources if isinstance(item, Mapping))
    trust_lane_counts = Counter(str(item.get("trust_lane", "unknown")) for item in sources if isinstance(item, Mapping))
    access_mode_counts = Counter(str(item.get("current_access_mode", "unknown")) for item in sources if isinstance(item, Mapping))
    index_depth_counts = Counter(str(item.get("current_index_depth", "unknown")) for item in sources if isinstance(item, Mapping))

    def count_true(key: str) -> int:
        return sum(1 for item in sources if isinstance(item, Mapping) and item.get(key) is True)

    def support_count(key: str, future_key: str) -> int:
        return sum(
            1
            for item in sources
            if isinstance(item, Mapping)
            and isinstance(item.get(key), Mapping)
            and item[key].get(future_key) is True
            and item[key].get("accepted_truth") is False
        )

    fetch_keys = ("software_list_fetch_enabled", "hashset_fetch_enabled")
    download_keys = (
        "rom_download_enabled",
        "iso_download_enabled",
        "disc_image_download_enabled",
        "chd_download_enabled",
        "bios_firmware_download_enabled",
        "game_binary_download_enabled",
        "emulator_download_enabled",
        "installer_download_enabled",
        "patch_download_enabled",
        "media_asset_download_enabled",
        "downloads_enabled",
    )
    execution_keys = ("emulator_execution_enabled", "game_execution_enabled", "install_execute_enabled")
    return {
        "schema_version": "h10_games_emulation_source_summary.v0",
        "status": "pass",
        "wave_id": inventory.get("wave_id", "H10"),
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
        "game_software_identity_support_count": support_count("game_software_identity_support", "game_software_identity_metadata_future"),
        "platform_release_edition_support_count": support_count("platform_release_edition_support", "platform_release_edition_metadata_future"),
        "emulator_compatibility_support_count": support_count("emulator_compatibility_support", "emulator_compatibility_metadata_future"),
        "preservation_hashset_support_count": support_count("preservation_hashset_support", "preservation_hashset_metadata_future"),
        "rom_disc_media_identity_support_count": support_count("rom_disc_media_identity_support", "rom_disc_media_identity_metadata_future"),
        "game_relation_support_count": support_count("game_relation_support", "game_relation_metadata_future"),
        "emulator_action_candidate_support_count": support_count("emulator_action_candidate_support", "emulator_action_candidate_metadata_future"),
        "rights_safety_support_count": support_count("rights_safety_support", "rights_safety_metadata_future"),
        "restricted_or_rights_sensitive_source_count": sum(1 for item in sources if isinstance(item, Mapping) and str(item.get("restricted_or_rights_sensitive_source_posture", "")).startswith(("policy", "rights"))),
        "connector_mapping_count": len(connector_mapping.get("source_connector_family_mappings", [])),
        "live_access_enabled_count": count_true("live_access_enabled"),
        "source_sync_enabled_count": count_true("source_sync_enabled"),
        "connector_runtime_enabled_count": count_true("connector_runtime_enabled"),
        "api_catalog_query_enabled_count": count_true("api_query_enabled") + count_true("catalog_fetch_enabled"),
        "software_list_hashset_fetch_enabled_count": sum(1 for item in sources if isinstance(item, Mapping) and any(item.get(key) is True for key in fetch_keys)),
        "downloads_enabled_count": sum(1 for item in sources if isinstance(item, Mapping) and any(item.get(key) is True for key in download_keys)),
        "uploads_enabled_count": count_true("uploads_enabled") + count_true("file_upload_enabled") + count_true("hash_submission_enabled"),
        "execution_enabled_count": sum(1 for item in sources if isinstance(item, Mapping) and any(item.get(key) is True for key in execution_keys)),
        "acquisition_action_enabled_count": count_true("acquisition_action_enabled"),
        "scraping_crawling_enabled_count": count_true("scraping_enabled") + count_true("crawling_enabled") + count_true("bypass_or_automation_enabled"),
        "restricted_source_enabled_count": count_true("restricted_rights_sensitive_source_enabled"),
        "blockers": [
            "fixture runtime not implemented",
            "live access not approved",
            "API/catalog/software-list/hash-set fetches forbidden",
            "ROM/disc/BIOS/game/emulator/download behavior forbidden",
            "uploads and hash submissions forbidden",
            "execution and acquisition actions forbidden",
            "scraping, crawling, browser automation, and bypass forbidden",
            "game, release, platform, compatibility, hash-set, ROM/disc, action, rights, safety, source, evidence, candidate, public, and master truth acceptance forbidden",
        ],
        "readiness": "READY_FOR_H10_FIXTURE_RUNTIME",
        "wrote_files": False,
    }


def render_summary_markdown(summary: Mapping[str, Any]) -> str:
    lines = [
        "# H10 Games Emulation Source Summary",
        "",
        f"- status: `{summary['status']}`",
        f"- source_count: `{summary['source_count']}`",
        f"- live_access_enabled_count: `{summary['live_access_enabled_count']}`",
        f"- software_list_hashset_fetch_enabled_count: `{summary['software_list_hashset_fetch_enabled_count']}`",
        f"- downloads_enabled_count: `{summary['downloads_enabled_count']}`",
        f"- uploads_enabled_count: `{summary['uploads_enabled_count']}`",
        f"- execution_enabled_count: `{summary['execution_enabled_count']}`",
        f"- acquisition_action_enabled_count: `{summary['acquisition_action_enabled_count']}`",
        f"- readiness: `{summary['readiness']}`",
        "",
        "H10-BUNDLE-01 is policy-pack-only and does not accept game, release, platform, emulator, hash-set, ROM/disc, action, rights, safety, source, evidence, candidate, public, or master truth.",
    ]
    return "\n".join(lines) + "\n"


def safe_output_path(raw: str) -> Path:
    path = Path(raw)
    resolved = path if path.is_absolute() else REPO_ROOT / path
    resolved = resolved.resolve()
    repo = REPO_ROOT.resolve()
    try:
        rel = resolved.relative_to(repo).as_posix()
    except ValueError:
        temp_root = Path(tempfile.gettempdir()).resolve()
        try:
            resolved.relative_to(temp_root)
        except ValueError as exc:
            raise ValueError("output path must be in repo allowed audit generated root or an explicit temp directory") from exc
        return resolved
    rel_lower = rel.lower()
    allowed_prefix = "control/audits/h10-bundle-01-games-emulation-policy-packs-v0/generated/"
    if rel_lower.startswith(allowed_prefix):
        return resolved
    for prefix in FORBIDDEN_OUTPUT_ROOTS:
        if rel_lower == prefix or rel_lower.startswith(prefix + "/"):
            raise ValueError(f"refusing forbidden output root: {prefix}")
    raise ValueError("repo output path must be under the H10 audit generated root")


def _write_json(raw: str, payload: Mapping[str, Any]) -> None:
    path = safe_output_path(raw)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text(raw: str, text: str) -> None:
    path = safe_output_path(raw)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(main())
