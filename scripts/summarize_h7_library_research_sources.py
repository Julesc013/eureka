#!/usr/bin/env python3
"""Summarize H7 library/cultural/research policy-pack sources offline."""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import sys
import tempfile
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_INVENTORY = REPO_ROOT / "control/inventory/source_packs/h7_library_research_sources.json"
CONNECTOR_FAMILIES = REPO_ROOT / "control/inventory/source_packs/h7_library_research_connector_families.json"
POLICY_FILES = [
    REPO_ROOT / "control/inventory/source_packs/h7_bibliographic_identity_policy.json",
    REPO_ROOT / "control/inventory/source_packs/h7_research_work_identity_policy.json",
    REPO_ROOT / "control/inventory/source_packs/h7_dataset_repository_identity_policy.json",
    REPO_ROOT / "control/inventory/source_packs/h7_cultural_object_identity_policy.json",
    REPO_ROOT / "control/inventory/source_packs/h7_patent_identity_policy.json",
    REPO_ROOT / "control/inventory/source_packs/h7_citation_relation_policy.json",
    REPO_ROOT / "control/inventory/source_packs/h7_access_rights_availability_policy.json",
]
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
    "harvest_cache",
    "pdf_downloads",
    "book_downloads",
    "article_downloads",
    "dataset_downloads",
    "ocr_cache",
    "media_downloads",
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
            print("H7 library/cultural/research source summary", file=stdout)
            print(f"status: {summary['status']}", file=stdout)
            print(f"source_count: {summary['source_count']}", file=stdout)
            print(f"live_access_enabled_count: {summary['live_access_enabled_count']}", file=stdout)
            print(f"harvest_or_api_enabled_count: {summary['harvest_or_api_enabled_count']}", file=stdout)
            print(f"download_enabled_count: {summary['download_enabled_count']}", file=stdout)
            print(f"scraping_crawling_enabled_count: {summary['scraping_crawling_enabled_count']}", file=stdout)
        return 0
    except Exception as exc:  # noqa: BLE001
        if args.json:
            print(json.dumps({"status": "invalid", "error": str(exc)}, indent=2, sort_keys=True), file=stdout)
        else:
            print("H7 library/cultural/research source summary", file=stdout)
            print("status: invalid", file=stdout)
            print(f"ERROR: {exc}", file=stdout)
        return 1


def build_summary() -> dict[str, Any]:
    inventory = _load_json(SOURCE_INVENTORY)
    connector_mapping = _load_json(CONNECTOR_FAMILIES)
    policies = [_load_json(path) for path in POLICY_FILES]
    sources = inventory.get("sources", [])
    if not isinstance(sources, list):
        raise ValueError("H7 source inventory must contain a sources list")
    source_family_counts = Counter(str(item.get("source_family", "unknown")) for item in sources if isinstance(item, Mapping))
    connector_family_counts = Counter(str(item.get("connector_family", "unknown")) for item in sources if isinstance(item, Mapping))
    trust_lane_counts = Counter(str(item.get("trust_lane", "unknown")) for item in sources if isinstance(item, Mapping))
    access_mode_counts = Counter(str(item.get("current_access_mode", "unknown")) for item in sources if isinstance(item, Mapping))
    index_depth_counts = Counter(str(item.get("current_index_depth", "unknown")) for item in sources if isinstance(item, Mapping))
    mappings = connector_mapping.get("source_connector_family_mappings", [])
    if not isinstance(mappings, list):
        mappings = []

    def count_true(key: str) -> int:
        return sum(1 for item in sources if isinstance(item, Mapping) and item.get(key) is True)

    harvest_api_keys = ("oai_pmh_harvest_enabled", "api_query_enabled")
    download_keys = ("full_text_fetch_enabled", "pdf_download_enabled", "book_scan_download_enabled", "article_download_enabled", "dataset_download_enabled", "iiif_manifest_fetch_enabled", "media_download_enabled", "patent_document_download_enabled")
    harvest_api_enabled_count = sum(1 for item in sources if isinstance(item, Mapping) and any(item.get(key) is True for key in harvest_api_keys))
    download_enabled_count = sum(1 for item in sources if isinstance(item, Mapping) and any(item.get(key) is True for key in download_keys))
    scraping_crawling_count = sum(1 for item in sources if isinstance(item, Mapping) and (item.get("scraping_enabled") is True or item.get("crawling_enabled") is True or item.get("bypass_or_automation_enabled") is True))
    return {
        "schema_version": "h7_library_research_source_summary.v0",
        "status": "pass",
        "wave_id": inventory.get("wave_id", "H7"),
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
        "bibliographic_identity_support_count": _support_count(sources, "bibliographic_identity_support", "bibliographic_identity_metadata_future"),
        "research_work_identity_support_count": _support_count(sources, "research_work_identity_support", "research_work_identity_metadata_future"),
        "dataset_identity_support_count": _support_count(sources, "dataset_identity_support", "dataset_identity_metadata_future"),
        "cultural_object_identity_support_count": _support_count(sources, "cultural_object_identity_support", "cultural_object_identity_metadata_future"),
        "patent_identity_support_count": _support_count(sources, "patent_identity_support", "patent_identity_metadata_future"),
        "citation_relation_support_count": _support_count(sources, "citation_relation_support", "citation_relation_metadata_future"),
        "access_rights_availability_support_count": _support_count(sources, "access_rights_availability_support", "access_rights_availability_metadata_future"),
        "restricted_or_licensed_source_count": sum(1 for item in sources if isinstance(item, Mapping) and str(item.get("restricted_or_licensed_source_posture", "")).startswith("policy_blocked")),
        "policy_concept_count": sum(len(policy.get("concepts", [])) for policy in policies),
        "connector_mapping_count": len(mappings),
        "live_access_enabled_count": count_true("live_access_enabled"),
        "source_sync_enabled_count": count_true("source_sync_enabled"),
        "connector_runtime_enabled_count": count_true("connector_runtime_enabled"),
        "harvest_or_api_enabled_count": harvest_api_enabled_count,
        "download_enabled_count": download_enabled_count,
        "scraping_crawling_enabled_count": scraping_crawling_count,
        "restricted_source_enabled_count": count_true("restricted_rights_sensitive_source_enabled"),
        "blockers": [
            "fixture runtime not implemented",
            "live access not approved",
            "OAI-PMH harvests and API queries forbidden",
            "full-text, PDF, book, article, dataset, patent, IIIF, and media downloads forbidden",
            "scraping, crawling, browser automation, and bypass forbidden",
            "public and master index mutation forbidden",
        ],
        "readiness": "READY_FOR_H7_FIXTURE_RUNTIME",
        "truth_boundary": {
            "source_pack_is_truth": False,
            "policy_pack_grants_live_access": False,
            "bibliographic_identity_candidate_is_truth": False,
            "research_work_candidate_is_truth": False,
            "dataset_identity_candidate_is_truth": False,
            "cultural_object_candidate_is_truth": False,
            "patent_identity_candidate_is_truth": False,
            "citation_relation_candidate_is_truth": False,
            "access_metadata_is_rights_truth": False,
            "open_access_metadata_is_rights_clearance": False,
            "coverage_preview_is_exhaustive": False,
            "scorecard_preview_is_production_ready": False,
            "public_index_mutated": False,
            "master_index_mutated": False,
            "rights_clearance_claimed": False,
            "privacy_safety_claimed": False,
            "malware_safety_claimed": False,
            "verified_availability_claimed": False,
        },
        "product_boundary": {
            "changed_public_search_behavior": False,
            "enabled_live_probes": False,
            "enabled_source_sync": False,
            "enabled_harvesting": False,
            "enabled_downloads": False,
            "enabled_crawling": False,
            "mutated_public_index": False,
            "mutated_master_index": False,
        },
    }


def render_summary_markdown(summary: Mapping[str, Any]) -> str:
    lines = [
        "# H7 Library Cultural Research Source Summary",
        "",
        f"- status: `{summary.get('status')}`",
        f"- source_count: `{summary.get('source_count', 0)}`",
        f"- current_status: `{summary.get('current_status')}`",
        f"- live_access_enabled_count: `{summary.get('live_access_enabled_count', 0)}`",
        f"- source_sync_enabled_count: `{summary.get('source_sync_enabled_count', 0)}`",
        f"- connector_runtime_enabled_count: `{summary.get('connector_runtime_enabled_count', 0)}`",
        f"- harvest_or_api_enabled_count: `{summary.get('harvest_or_api_enabled_count', 0)}`",
        f"- download_enabled_count: `{summary.get('download_enabled_count', 0)}`",
        f"- scraping_crawling_enabled_count: `{summary.get('scraping_crawling_enabled_count', 0)}`",
        f"- restricted_source_enabled_count: `{summary.get('restricted_source_enabled_count', 0)}`",
        f"- readiness: `{summary.get('readiness')}`",
        "",
        "## Sources",
    ]
    lines.extend(f"- {source_id}" for source_id in summary.get("source_ids", []))
    lines.extend(["", "## Connector Families"])
    lines.extend(f"- {key}: {value}" for key, value in summary.get("connector_family_counts", {}).items())
    lines.extend(["", "## Blockers"])
    lines.extend(f"- {item}" for item in summary.get("blockers", []))
    return "\n".join(lines) + "\n"


def _support_count(sources: list[Any], section: str, key: str) -> int:
    return sum(1 for item in sources if isinstance(item, Mapping) and isinstance(item.get(section), Mapping) and item[section].get(key) is True)


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
                raise ValueError(f"refusing forbidden output root: {forbidden}")
        if rel_lower.startswith("control/audits/") and "/generated/" in rel_lower:
            return resolved
        raise ValueError(f"refusing output outside approved H7 summary roots: {rel}")
    except ValueError as exc:
        if str(exc).startswith("refusing"):
            raise
        temp_root = Path(tempfile.gettempdir()).resolve()
        try:
            resolved.relative_to(temp_root)
            return resolved
        except ValueError as temp_exc:
            raise ValueError(f"refusing output outside repository approved roots or temp directory: {resolved}") from temp_exc


if __name__ == "__main__":
    raise SystemExit(main())
