#!/usr/bin/env python3
"""Summarize H1 metadata-wave sources and policy-pack posture offline."""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import sys
import tempfile
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_INVENTORY = REPO_ROOT / "control/inventory/source_packs/h1_metadata_wave_sources.json"
CONNECTOR_FAMILIES = REPO_ROOT / "control/inventory/source_packs/h1_metadata_wave_connector_families.json"
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
            print("H1 metadata wave source summary", file=stdout)
            print(f"status: {summary['status']}", file=stdout)
            print(f"source_count: {summary['source_count']}", file=stdout)
            print(f"live_access_enabled_count: {summary['live_access_enabled_count']}", file=stdout)
            print(f"source_sync_enabled_count: {summary['source_sync_enabled_count']}", file=stdout)
            print(f"connector_runtime_enabled_count: {summary['connector_runtime_enabled_count']}", file=stdout)
        return 0
    except Exception as exc:  # noqa: BLE001
        if args.json:
            print(json.dumps({"status": "invalid", "error": str(exc)}, indent=2, sort_keys=True), file=stdout)
        else:
            print("H1 metadata wave source summary", file=stdout)
            print("status: invalid", file=stdout)
            print(f"ERROR: {exc}", file=stdout)
        return 1


def build_summary() -> dict[str, Any]:
    inventory = _load_json(SOURCE_INVENTORY)
    connector_mapping = _load_json(CONNECTOR_FAMILIES)
    sources = inventory.get("sources", [])
    if not isinstance(sources, list):
        raise ValueError("H1 source inventory must contain a sources list")
    source_family_counts = Counter(str(item.get("source_family", "unknown")) for item in sources if isinstance(item, Mapping))
    connector_family_counts = Counter(str(item.get("connector_family", "unknown")) for item in sources if isinstance(item, Mapping))
    trust_lane_counts = Counter(str(item.get("trust_lane", "unknown")) for item in sources if isinstance(item, Mapping))
    access_mode_counts = Counter(str(item.get("current_access_mode", "unknown")) for item in sources if isinstance(item, Mapping))
    index_depth_counts = Counter(str(item.get("current_index_depth", "unknown")) for item in sources if isinstance(item, Mapping))
    future_live_probe_count = sum(1 for item in sources if isinstance(item, Mapping) and item.get("live_probe_required_future") is True)
    fixture_required_count = sum(1 for item in sources if isinstance(item, Mapping) and item.get("fixture_required") is True)
    scorecard_required_count = sum(1 for item in sources if isinstance(item, Mapping) and item.get("scorecard_required") is True)
    coverage_required_count = sum(1 for item in sources if isinstance(item, Mapping) and item.get("coverage_required") is True)
    mappings = connector_mapping.get("source_connector_family_mappings", connector_mapping.get("mappings", []))
    if not isinstance(mappings, list):
        mappings = []
    live_access_enabled_count = sum(1 for item in sources if isinstance(item, Mapping) and item.get("live_access_enabled") is True)
    source_sync_enabled_count = sum(1 for item in sources if isinstance(item, Mapping) and item.get("source_sync_enabled") is True)
    connector_runtime_enabled_count = sum(1 for item in sources if isinstance(item, Mapping) and item.get("connector_runtime_enabled") is True)
    return {
        "schema_version": "h1_metadata_wave_source_summary.v0",
        "status": "pass",
        "wave_id": inventory.get("wave_id", "H1"),
        "current_status": inventory.get("current_status", "policy_pack_only"),
        "source_count": len(sources),
        "source_ids": sorted(str(item.get("source_id", "")) for item in sources if isinstance(item, Mapping)),
        "source_family_counts": dict(sorted(source_family_counts.items())),
        "connector_family_counts": dict(sorted(connector_family_counts.items())),
        "trust_lane_counts": dict(sorted(trust_lane_counts.items())),
        "access_mode_counts": dict(sorted(access_mode_counts.items())),
        "index_depth_counts": dict(sorted(index_depth_counts.items())),
        "fixture_required_count": fixture_required_count,
        "future_live_probe_required_count": future_live_probe_count,
        "scorecard_required_count": scorecard_required_count,
        "coverage_required_count": coverage_required_count,
        "connector_mapping_count": len(mappings),
        "live_access_enabled_count": live_access_enabled_count,
        "source_sync_enabled_count": source_sync_enabled_count,
        "connector_runtime_enabled_count": connector_runtime_enabled_count,
        "blockers": [
            "fixture runtime not implemented",
            "live access not approved",
            "connector runtime not enabled"
        ],
        "readiness": "READY_FOR_H1_FIXTURE_RUNTIME",
        "truth_boundary": {
            "source_pack_is_truth": False,
            "policy_pack_grants_live_access": False,
            "coverage_preview_is_exhaustive": False,
            "scorecard_preview_is_production_ready": False,
            "public_index_mutated": False,
            "master_index_mutated": False
        },
        "product_boundary": {
            "changed_public_search_behavior": False,
            "enabled_live_probes": False,
            "enabled_source_sync": False,
            "enabled_source_connectors": False,
            "enabled_downloads": False,
            "mutated_public_index": False,
            "mutated_master_index": False
        },
    }


def render_summary_markdown(summary: Mapping[str, Any]) -> str:
    lines = [
        "# H1 Metadata Wave Source Summary",
        "",
        f"- status: `{summary.get('status')}`",
        f"- source_count: `{summary.get('source_count', 0)}`",
        f"- current_status: `{summary.get('current_status')}`",
        f"- live_access_enabled_count: `{summary.get('live_access_enabled_count', 0)}`",
        f"- source_sync_enabled_count: `{summary.get('source_sync_enabled_count', 0)}`",
        f"- connector_runtime_enabled_count: `{summary.get('connector_runtime_enabled_count', 0)}`",
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
                raise ValueError(f"refusing forbidden output root: {forbidden}")
        if rel_lower.startswith("control/audits/") and "/generated/" in rel_lower:
            return resolved
        if rel_lower.startswith("examples/packs/source/"):
            return resolved
        raise ValueError(f"refusing output outside approved H1 roots: {rel}")
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
