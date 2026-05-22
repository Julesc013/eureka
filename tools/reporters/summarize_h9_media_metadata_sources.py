#!/usr/bin/env python3
"""Summarize H9 media metadata source policy packs offline."""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import sys
import tempfile
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_INVENTORY = REPO_ROOT / "control/inventory/source_packs/h9_media_metadata_sources.json"
CONNECTOR_FAMILIES = REPO_ROOT / "control/inventory/source_packs/h9_media_metadata_connector_families.json"
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
    "media_downloads",
    "media_uploads",
    "fingerprint_cache",
    "image_cache",
    "video_cache",
    "audio_cache",
    "map_downloads",
    "ocr_cache",
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
            print("H9 media metadata source summary", file=stdout)
            print(f"status: {summary['status']}", file=stdout)
            print(f"source_count: {summary['source_count']}", file=stdout)
            print(f"live_access_enabled_count: {summary['live_access_enabled_count']}", file=stdout)
            print(f"api_catalog_query_enabled_count: {summary['api_catalog_query_enabled_count']}", file=stdout)
            print(f"media_download_enabled_count: {summary['media_download_enabled_count']}", file=stdout)
            print(f"media_upload_enabled_count: {summary['media_upload_enabled_count']}", file=stdout)
            print(f"fingerprinting_enabled_count: {summary['fingerprinting_enabled_count']}", file=stdout)
            print(f"scraping_crawling_enabled_count: {summary['scraping_crawling_enabled_count']}", file=stdout)
        return 0
    except Exception as exc:  # noqa: BLE001
        if args.json:
            print(json.dumps({"status": "invalid", "error": str(exc)}, indent=2, sort_keys=True), file=stdout)
        else:
            print("H9 media metadata source summary", file=stdout)
            print("status: invalid", file=stdout)
            print(f"ERROR: {exc}", file=stdout)
        return 1


def build_summary() -> dict[str, Any]:
    inventory = _load_json(SOURCE_INVENTORY)
    connector_mapping = _load_json(CONNECTOR_FAMILIES)
    sources = inventory.get("sources", [])
    if not isinstance(sources, list):
        raise ValueError("H9 source inventory must contain a sources list")
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

    media_download_keys = ("media_download_enabled", "image_download_enabled", "video_download_enabled", "audio_download_enabled", "map_download_enabled", "score_download_enabled", "thumbnail_fetch_enabled")
    fingerprint_keys = ("fingerprint_lookup_enabled", "fingerprint_submission_enabled", "fingerprint_generation_enabled")
    return {
        "schema_version": "h9_media_metadata_source_summary.v0",
        "status": "pass",
        "wave_id": inventory.get("wave_id", "H9"),
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
        "media_object_identity_support_count": support_count("media_object_identity_support", "media_object_identity_metadata_future"),
        "music_identity_support_count": support_count("music_identity_support", "music_identity_metadata_future"),
        "image_video_map_identity_support_count": support_count("image_video_map_identity_support", "image_video_map_identity_metadata_future"),
        "creator_collection_relation_support_count": support_count("creator_collection_relation_support", "creator_collection_relation_metadata_future"),
        "fingerprint_metadata_support_count": support_count("fingerprint_metadata_support", "fingerprint_metadata_future"),
        "rights_license_support_count": support_count("rights_license_support", "rights_license_metadata_future"),
        "safety_privacy_support_count": support_count("safety_privacy_support", "safety_privacy_metadata_future"),
        "restricted_or_licensed_source_count": sum(1 for item in sources if isinstance(item, Mapping) and str(item.get("restricted_or_licensed_source_posture", "")).startswith("policy_blocked")),
        "connector_mapping_count": len(connector_mapping.get("source_connector_family_mappings", [])),
        "live_access_enabled_count": count_true("live_access_enabled"),
        "source_sync_enabled_count": count_true("source_sync_enabled"),
        "connector_runtime_enabled_count": count_true("connector_runtime_enabled"),
        "api_catalog_query_enabled_count": count_true("api_query_enabled") + count_true("catalog_fetch_enabled"),
        "media_download_enabled_count": sum(1 for item in sources if isinstance(item, Mapping) and any(item.get(key) is True for key in media_download_keys)),
        "media_upload_enabled_count": count_true("media_upload_enabled") + count_true("user_media_upload_enabled"),
        "fingerprinting_enabled_count": sum(1 for item in sources if isinstance(item, Mapping) and any(item.get(key) is True for key in fingerprint_keys)),
        "scraping_crawling_enabled_count": count_true("scraping_enabled") + count_true("metadata_scraping_enabled") + count_true("crawling_enabled") + count_true("bypass_or_automation_enabled"),
        "restricted_source_enabled_count": count_true("restricted_rights_sensitive_source_enabled"),
        "blockers": [
            "fixture runtime not implemented",
            "live access not approved",
            "API/catalog queries forbidden",
            "media downloads and uploads forbidden",
            "fingerprint lookup, submission, and generation forbidden",
            "thumbnail and preview fetches forbidden",
            "scraping, crawling, browser automation, and bypass forbidden",
            "rights, license, media identity, safety, and public truth acceptance forbidden",
        ],
        "readiness": "READY_FOR_H9_FIXTURE_RUNTIME",
        "wrote_files": False,
    }


def render_summary_markdown(summary: Mapping[str, Any]) -> str:
    lines = [
        "# H9 Media Metadata Source Summary",
        "",
        f"- status: `{summary['status']}`",
        f"- source_count: `{summary['source_count']}`",
        f"- live_access_enabled_count: `{summary['live_access_enabled_count']}`",
        f"- api_catalog_query_enabled_count: `{summary['api_catalog_query_enabled_count']}`",
        f"- media_download_enabled_count: `{summary['media_download_enabled_count']}`",
        f"- media_upload_enabled_count: `{summary['media_upload_enabled_count']}`",
        f"- fingerprinting_enabled_count: `{summary['fingerprinting_enabled_count']}`",
        f"- scraping_crawling_enabled_count: `{summary['scraping_crawling_enabled_count']}`",
        f"- readiness: `{summary['readiness']}`",
        "",
        "H9-BUNDLE-01 is policy-pack-only and does not accept media, rights, fingerprint, safety, source, evidence, candidate, public, or master truth.",
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
    allowed_prefix = "control/audits/h9-bundle-01-media-metadata-policy-packs-v0/generated/"
    if rel_lower.startswith(allowed_prefix):
        return resolved
    for prefix in FORBIDDEN_OUTPUT_ROOTS:
        if rel_lower == prefix or rel_lower.startswith(prefix + "/"):
            raise ValueError(f"refusing forbidden output root: {prefix}")
    raise ValueError("repo output path must be under the H9 audit generated root")


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
