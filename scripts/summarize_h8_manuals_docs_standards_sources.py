#!/usr/bin/env python3
"""Summarize H8 manuals/docs/standards policy-pack sources offline."""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import sys
import tempfile
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_INVENTORY = REPO_ROOT / "control/inventory/source_packs/h8_manuals_docs_standards_sources.json"
CONNECTOR_FAMILIES = REPO_ROOT / "control/inventory/source_packs/h8_manuals_docs_standards_connector_families.json"
POLICY_FILES = [
    REPO_ROOT / "control/inventory/source_packs/h8_technical_document_identity_policy.json",
    REPO_ROOT / "control/inventory/source_packs/h8_manual_artifact_relation_policy.json",
    REPO_ROOT / "control/inventory/source_packs/h8_datasheet_device_identity_policy.json",
    REPO_ROOT / "control/inventory/source_packs/h8_standards_specification_identity_policy.json",
    REPO_ROOT / "control/inventory/source_packs/h8_install_requirement_claim_policy.json",
    REPO_ROOT / "control/inventory/source_packs/h8_repair_service_safety_policy.json",
    REPO_ROOT / "control/inventory/source_packs/h8_access_rights_policy.json",
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
    "document_downloads",
    "standards_downloads",
    "manual_downloads",
    "datasheet_downloads",
    "repair_manual_dumps",
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
            print("H8 manuals/docs/standards source summary", file=stdout)
            print(f"status: {summary['status']}", file=stdout)
            print(f"source_count: {summary['source_count']}", file=stdout)
            print(f"live_access_enabled_count: {summary['live_access_enabled_count']}", file=stdout)
            print(f"api_catalog_query_enabled_count: {summary['api_catalog_query_enabled_count']}", file=stdout)
            print(f"download_enabled_count: {summary['download_enabled_count']}", file=stdout)
            print(f"full_text_ocr_enabled_count: {summary['full_text_ocr_enabled_count']}", file=stdout)
            print(f"scraping_crawling_enabled_count: {summary['scraping_crawling_enabled_count']}", file=stdout)
        return 0
    except Exception as exc:  # noqa: BLE001
        if args.json:
            print(json.dumps({"status": "invalid", "error": str(exc)}, indent=2, sort_keys=True), file=stdout)
        else:
            print("H8 manuals/docs/standards source summary", file=stdout)
            print("status: invalid", file=stdout)
            print(f"ERROR: {exc}", file=stdout)
        return 1


def build_summary() -> dict[str, Any]:
    inventory = _load_json(SOURCE_INVENTORY)
    connector_mapping = _load_json(CONNECTOR_FAMILIES)
    policies = [_load_json(path) for path in POLICY_FILES]
    sources = inventory.get("sources", [])
    if not isinstance(sources, list):
        raise ValueError("H8 source inventory must contain a sources list")
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

    download_keys = ("document_download_enabled", "pdf_download_enabled", "scan_download_enabled", "datasheet_download_enabled", "standards_document_fetch_enabled", "schematic_download_enabled", "service_manual_download_enabled", "iiif_manifest_fetch_enabled")
    download_enabled_count = sum(1 for item in sources if isinstance(item, Mapping) and any(item.get(key) is True for key in download_keys))
    full_text_ocr_enabled_count = sum(1 for item in sources if isinstance(item, Mapping) and (item.get("full_text_fetch_enabled") is True or item.get("ocr_extraction_enabled") is True))
    scraping_crawling_count = sum(1 for item in sources if isinstance(item, Mapping) and (item.get("scraping_enabled") is True or item.get("crawling_enabled") is True or item.get("bypass_or_automation_enabled") is True))
    api_catalog_count = sum(1 for item in sources if isinstance(item, Mapping) and (item.get("api_query_enabled") is True or item.get("catalog_fetch_enabled") is True))
    return {
        "schema_version": "h8_manuals_docs_standards_source_summary.v0",
        "status": "pass",
        "wave_id": inventory.get("wave_id", "H8"),
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
        "technical_document_identity_support_count": _support_count(sources, "technical_document_identity_support", "technical_document_identity_metadata_future"),
        "manual_artifact_relation_support_count": _support_count(sources, "manual_artifact_relation_support", "manual_artifact_relation_metadata_future"),
        "datasheet_device_identity_support_count": _support_count(sources, "datasheet_device_identity_support", "datasheet_device_identity_metadata_future"),
        "standards_specification_identity_support_count": _support_count(sources, "standards_specification_identity_support", "standards_specification_identity_metadata_future"),
        "install_requirement_claim_support_count": _support_count(sources, "install_requirement_claim_support", "install_requirement_claim_metadata_future"),
        "repair_service_safety_support_count": _support_count(sources, "repair_service_safety_support", "repair_service_safety_metadata_future"),
        "access_rights_support_count": _support_count(sources, "access_rights_support", "access_rights_metadata_future"),
        "restricted_or_licensed_source_count": sum(1 for item in sources if isinstance(item, Mapping) and str(item.get("restricted_or_licensed_source_posture", "")).startswith("policy_blocked")),
        "policy_concept_count": sum(len(policy.get("concepts", [])) for policy in policies),
        "connector_mapping_count": len(mappings),
        "live_access_enabled_count": count_true("live_access_enabled"),
        "source_sync_enabled_count": count_true("source_sync_enabled"),
        "connector_runtime_enabled_count": count_true("connector_runtime_enabled"),
        "api_catalog_query_enabled_count": api_catalog_count,
        "download_enabled_count": download_enabled_count,
        "full_text_ocr_enabled_count": full_text_ocr_enabled_count,
        "scraping_crawling_enabled_count": scraping_crawling_count,
        "restricted_source_enabled_count": count_true("restricted_rights_sensitive_source_enabled"),
        "blockers": [
            "fixture runtime not implemented",
            "live access not approved",
            "API/catalog queries forbidden",
            "document, PDF, manual, datasheet, standards, schematic, scan, IIIF, and media downloads forbidden",
            "full-text and OCR extraction forbidden",
            "scraping, crawling, browser automation, and bypass forbidden",
            "repair, install, calibration, flashing, and electrical actions blocked",
            "public and master index mutation forbidden",
        ],
        "readiness": "READY_FOR_H8_FIXTURE_RUNTIME",
        "truth_boundary": {
            "source_pack_is_truth": False,
            "policy_pack_grants_live_access": False,
            "technical_document_identity_candidate_is_truth": False,
            "manual_artifact_relation_candidate_is_truth": False,
            "datasheet_device_candidate_is_truth": False,
            "standards_specification_candidate_is_truth": False,
            "install_requirement_candidate_is_truth": False,
            "repair_service_safety_candidate_is_truth": False,
            "access_metadata_is_rights_truth": False,
            "open_access_metadata_is_rights_clearance": False,
            "coverage_preview_is_exhaustive": False,
            "scorecard_preview_is_production_ready": False,
            "public_index_mutated": False,
            "master_index_mutated": False,
            "rights_clearance_claimed": False,
            "compatibility_correctness_claimed": False,
            "installability_claimed": False,
            "repair_safety_claimed": False,
            "electrical_safety_claimed": False,
            "malware_safety_claimed": False,
            "verified_authenticity_claimed": False,
        },
        "product_boundary": {
            "changed_public_search_behavior": False,
            "enabled_live_probes": False,
            "enabled_source_sync": False,
            "enabled_catalog_queries": False,
            "enabled_downloads": False,
            "enabled_extraction": False,
            "enabled_crawling": False,
            "mutated_public_index": False,
            "mutated_master_index": False,
        },
    }


def render_summary_markdown(summary: Mapping[str, Any]) -> str:
    lines = [
        "# H8 Manuals Docs Standards Source Summary",
        "",
        f"- status: `{summary.get('status')}`",
        f"- source_count: `{summary.get('source_count', 0)}`",
        f"- current_status: `{summary.get('current_status')}`",
        f"- live_access_enabled_count: `{summary.get('live_access_enabled_count', 0)}`",
        f"- source_sync_enabled_count: `{summary.get('source_sync_enabled_count', 0)}`",
        f"- connector_runtime_enabled_count: `{summary.get('connector_runtime_enabled_count', 0)}`",
        f"- api_catalog_query_enabled_count: `{summary.get('api_catalog_query_enabled_count', 0)}`",
        f"- download_enabled_count: `{summary.get('download_enabled_count', 0)}`",
        f"- full_text_ocr_enabled_count: `{summary.get('full_text_ocr_enabled_count', 0)}`",
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
        raise ValueError(f"refusing output outside approved H8 summary roots: {rel}")
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
