#!/usr/bin/env python3
"""Summarize H14 source discovery policy-pack sources offline."""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import sys
import tempfile
from typing import Any, Mapping, Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_INVENTORY = REPO_ROOT / "control/inventory/source_packs/h14_source_discovery_sources.json"
CONNECTOR_FAMILIES = REPO_ROOT / "control/inventory/source_packs/h14_source_discovery_connector_families.json"
FORBIDDEN_OUTPUT_ROOTS = (
    "site/dist",
    "site/dist/data/public_index",
    "runtime",
    "contracts",
    "data/master_index",
    "master_index",
    "source_registry_mutation",
    "connector_registry_mutation",
    "pack_import_staging",
    "pack_export_staging",
    ".aide.local",
    ".local/eureka",
    ".cache/eureka",
    "local_sources",
    "private_sources",
    "cas_store",
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
            print("H14 source discovery source summary", file=stdout)
            print(f"status: {summary['status']}", file=stdout)
            print(f"source_count: {summary['source_count']}", file=stdout)
            print(f"source_discovery_enabled_count: {summary['source_discovery_enabled_count']}", file=stdout)
            print(f"pack_export_import_enabled_count: {summary['pack_export_import_enabled_count']}", file=stdout)
            print(f"registry_mutation_enabled_count: {summary['registry_mutation_enabled_count']}", file=stdout)
            print(f"wrote_files: {str(summary['wrote_files']).lower()}", file=stdout)
        return 0
    except Exception as exc:  # noqa: BLE001
        if args.json:
            print(json.dumps({"status": "invalid", "error": str(exc)}, indent=2, sort_keys=True), file=stdout)
        else:
            print("H14 source discovery source summary", file=stdout)
            print("status: invalid", file=stdout)
            print(f"ERROR: {exc}", file=stdout)
        return 1


def build_summary() -> dict[str, Any]:
    inventory = _load_json(SOURCE_INVENTORY)
    connector_mapping = _load_json(CONNECTOR_FAMILIES)
    sources = inventory.get("sources", [])
    if not isinstance(sources, list):
        raise ValueError("H14 source inventory must contain a sources list")
    def count_true(key: str) -> int:
        return sum(1 for item in sources if isinstance(item, Mapping) and item.get(key) is True)
    def support_count(key: str) -> int:
        return sum(1 for item in sources if isinstance(item, Mapping) and isinstance(item.get(key), Mapping) and item[key].get("planned") is True and item[key].get("accepted_truth") is False)
    source_family_counts = Counter(str(item.get("source_family", "unknown")) for item in sources if isinstance(item, Mapping))
    connector_family_counts = Counter(str(item.get("connector_family", "unknown")) for item in sources if isinstance(item, Mapping))
    trust_lane_counts = Counter(str(item.get("trust_lane", "unknown")) for item in sources if isinstance(item, Mapping))
    access_mode_counts = Counter(str(item.get("current_access_mode", "unknown")) for item in sources if isinstance(item, Mapping))
    index_depth_counts = Counter(str(item.get("current_index_depth", "unknown")) for item in sources if isinstance(item, Mapping))
    return {
        "schema_version": "h14_source_discovery_source_summary.v0",
        "status": "pass",
        "wave_id": inventory.get("wave_id", "H14"),
        "current_status": inventory.get("current_status", "policy_pack_only"),
        "source_count": len(sources),
        "source_ids": sorted(str(item.get("source_id", "")) for item in sources if isinstance(item, Mapping)),
        "source_family_counts": dict(sorted(source_family_counts.items())),
        "connector_family_counts": dict(sorted(connector_family_counts.items())),
        "trust_lane_counts": dict(sorted(trust_lane_counts.items())),
        "access_mode_counts": dict(sorted(access_mode_counts.items())),
        "index_depth_counts": dict(sorted(index_depth_counts.items())),
        "source_need_support_count": support_count("source_need_support"),
        "source_candidate_support_count": support_count("source_candidate_support"),
        "source_discovery_support_count": support_count("source_discovery_support"),
        "source_pack_manifest_support_count": support_count("source_pack_manifest_support"),
        "connector_pack_manifest_support_count": support_count("connector_pack_manifest_support"),
        "coverage_manifest_support_count": support_count("coverage_manifest_support"),
        "connector_scorecard_support_count": support_count("connector_scorecard_support"),
        "reliability_freshness_support_count": support_count("reliability_freshness_support"),
        "dispute_revocation_support_count": support_count("dispute_revocation_support"),
        "lineage_provenance_support_count": support_count("lineage_provenance_support"),
        "pack_import_export_boundary_support_count": support_count("pack_import_export_boundary_support"),
        "connector_mapping_count": len(connector_mapping.get("source_connector_family_mappings", [])),
        "source_discovery_enabled_count": count_true("source_discovery_enabled"),
        "live_access_enabled_count": count_true("live_access_enabled"),
        "network_access_enabled_count": count_true("network_access_enabled"),
        "model_provider_enabled_count": count_true("model_provider_enabled"),
        "source_sync_enabled_count": count_true("source_sync_enabled"),
        "pack_export_import_enabled_count": count_true("source_pack_export_enabled") + count_true("source_pack_import_enabled") + count_true("connector_pack_export_enabled") + count_true("connector_pack_import_enabled"),
        "registry_mutation_enabled_count": count_true("source_registry_mutation_enabled") + count_true("connector_registry_mutation_enabled"),
        "source_cache_writes_enabled_count": count_true("source_cache_write_enabled"),
        "public_index_writes_enabled_count": count_true("public_index_write_enabled"),
        "blockers": [
            "fixture runtime not implemented",
            "source discovery runtime forbidden",
            "pack import/export forbidden",
            "source and connector registry mutation forbidden",
            "source cache, evidence, public index, and master index writes forbidden",
            "source/candidate/coverage/scorecard/reliability/freshness/dispute/revocation/lineage/pack truth acceptance forbidden",
        ],
        "readiness": "READY_FOR_H14_FIXTURE_RUNTIME",
        "wrote_files": False,
    }


def render_summary_markdown(summary: Mapping[str, Any]) -> str:
    return "\n".join([
        "# H14 Source Discovery Source Summary",
        "",
        f"- status: `{summary['status']}`",
        f"- source_count: `{summary['source_count']}`",
        f"- source_discovery_enabled_count: `{summary['source_discovery_enabled_count']}`",
        f"- pack_export_import_enabled_count: `{summary['pack_export_import_enabled_count']}`",
        f"- registry_mutation_enabled_count: `{summary['registry_mutation_enabled_count']}`",
        f"- readiness: `{summary['readiness']}`",
        "",
        "H14-BUNDLE-01 is policy-pack-only and does not accept source, candidate, coverage, scorecard, reliability, freshness, dispute, revocation, lineage, pack, evidence, or public truth.",
        "",
    ])


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
    allowed_prefix = "control/audits/h14-bundle-01-source-discovery-policy-packs-v0/generated/"
    if rel_lower.startswith(allowed_prefix):
        return resolved
    for prefix in FORBIDDEN_OUTPUT_ROOTS:
        if rel_lower == prefix or rel_lower.startswith(prefix + "/"):
            raise ValueError(f"refusing forbidden output root: {prefix}")
    raise ValueError("repo output path must be under the H14 audit generated root")


def _write_json(raw: str, payload: Mapping[str, Any]) -> None:
    path = safe_output_path(raw)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text(raw: str, payload: str) -> None:
    path = safe_output_path(raw)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(payload, encoding="utf-8")


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(main())
