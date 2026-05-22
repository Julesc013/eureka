#!/usr/bin/env python3
"""Summarize Source OS registry v2 and source record examples offline."""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import sys
import tempfile
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
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
    parser.add_argument("--input", action="append", required=True, help="Registry, source record, or directory input. Repeatable.")
    parser.add_argument("--output", help="Optional JSON summary output path.")
    parser.add_argument("--summary-output", help="Optional Markdown summary output path.")
    parser.add_argument("--check", action="store_true", help="Summarize without writing files.")
    parser.add_argument("--json", action="store_true", help="Print JSON summary.")
    args = parser.parse_args(argv)
    try:
        records = load_inputs([Path(item) for item in args.input])
        summary = summarize_records(records)
        if not args.check:
            if args.output:
                _write_json(args.output, summary)
            if args.summary_output:
                _write_text(args.summary_output, render_summary_markdown(summary))
        if args.json:
            print(json.dumps(summary, indent=2, sort_keys=True), file=stdout)
        else:
            print("Source registry v2 summary", file=stdout)
            print(f"source_count: {summary['source_count']}", file=stdout)
            print(f"live_access_enabled_count: {summary['live_access_enabled_count']}", file=stdout)
            print(f"source_sync_enabled_count: {summary['source_sync_enabled_count']}", file=stdout)
            print(f"public_index_mutation_count: {summary['public_index_mutation_count']}", file=stdout)
        return 0
    except Exception as exc:  # noqa: BLE001
        if args.json:
            print(json.dumps({"status": "invalid", "error": str(exc)}, indent=2, sort_keys=True), file=stdout)
        else:
            print("Source registry v2 summary", file=stdout)
            print("status: invalid", file=stdout)
            print(f"ERROR: {exc}", file=stdout)
        return 1


def load_inputs(paths: Sequence[Path]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    seen: set[Path] = set()
    for path in paths:
        resolved = (REPO_ROOT / path).resolve() if not path.is_absolute() else path.resolve()
        if resolved.is_dir():
            for child in sorted(resolved.glob("*.json")):
                records.extend(_load_path(child, seen))
        else:
            records.extend(_load_path(resolved, seen))
    return records


def _load_path(path: Path, seen: set[Path]) -> list[dict[str, Any]]:
    if path in seen:
        return []
    seen.add(path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, Mapping):
        raise ValueError(f"{path} must contain a JSON object")
    if payload.get("schema_version") == "source_registry.v2":
        records: list[dict[str, Any]] = []
        for item in payload.get("source_records", []):
            if isinstance(item, Mapping) and item.get("source_record_ref"):
                ref = REPO_ROOT / str(item["source_record_ref"])
                records.extend(_load_path(ref.resolve(), seen))
        return records
    if payload.get("schema_version") == "source_record.v2":
        return [dict(payload)]
    return []


def summarize_records(records: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    family_counts = Counter(str(record.get("source_family", "unknown")) for record in records)
    trust_counts = Counter(str(record.get("trust_lane", "unknown")) for record in records)
    depth_counts = Counter(str(record.get("index_depth_current", "unknown")) for record in records)
    policy_counts = Counter(str(record.get("default_policy_state", "unknown")) for record in records)
    access_counts: Counter[str] = Counter()
    capability_counts: Counter[str] = Counter()
    live_access_enabled_count = 0
    source_sync_enabled_count = 0
    public_index_mutation_count = 0
    master_index_mutation_count = 0
    for record in records:
        access_counts.update(str(item) for item in record.get("access_modes", []) if item)
        capability_counts.update(str(item) for item in record.get("capability_refs", []) if item)
        truth = record.get("truth_boundary", {})
        product = record.get("product_boundary", {})
        if isinstance(truth, Mapping) and truth.get("source_record_grants_live_access") is True:
            live_access_enabled_count += 1
        if isinstance(product, Mapping):
            if product.get("enabled_live_probes") is True:
                live_access_enabled_count += 1
            if product.get("enabled_source_sync") is True:
                source_sync_enabled_count += 1
            if product.get("mutated_public_index") is True:
                public_index_mutation_count += 1
            if product.get("mutated_master_index") is True:
                master_index_mutation_count += 1
    return {
        "schema_version": "source_registry_v2_summary.v0",
        "status": "pass",
        "source_count": len(records),
        "source_ids": sorted(str(record.get("source_id", "")) for record in records),
        "family_counts": dict(sorted(family_counts.items())),
        "trust_lane_counts": dict(sorted(trust_counts.items())),
        "index_depth_counts": dict(sorted(depth_counts.items())),
        "policy_state_counts": dict(sorted(policy_counts.items())),
        "access_mode_counts": dict(sorted(access_counts.items())),
        "capability_counts": dict(sorted(capability_counts.items())),
        "live_access_enabled_count": live_access_enabled_count,
        "source_sync_enabled_count": source_sync_enabled_count,
        "public_index_mutation_count": public_index_mutation_count,
        "master_index_mutation_count": master_index_mutation_count,
        "truth_boundary": {
            "source_records_are_public_truth": False,
            "source_records_accept_evidence": False,
            "source_capabilities_grant_permission": False,
            "public_index_mutated": False,
            "master_index_mutated": False
        },
        "product_boundary": {
            "changed_public_search_behavior": False,
            "enabled_live_probes": False,
            "enabled_source_sync": False,
            "enabled_downloads": False,
            "enabled_hosting": False,
            "mutated_public_index": False,
            "mutated_master_index": False
        }
    }


def render_summary_markdown(summary: Mapping[str, Any]) -> str:
    lines = [
        "# Source Registry V2 Summary",
        "",
        f"- source_count: `{summary.get('source_count', 0)}`",
        f"- live_access_enabled_count: `{summary.get('live_access_enabled_count', 0)}`",
        f"- source_sync_enabled_count: `{summary.get('source_sync_enabled_count', 0)}`",
        f"- public_index_mutation_count: `{summary.get('public_index_mutation_count', 0)}`",
        f"- master_index_mutation_count: `{summary.get('master_index_mutation_count', 0)}`",
        "",
        "## Families",
    ]
    lines.extend(f"- {key}: {value}" for key, value in summary.get("family_counts", {}).items())
    lines.extend(["", "## Trust Lanes"])
    lines.extend(f"- {key}: {value}" for key, value in summary.get("trust_lane_counts", {}).items())
    lines.extend(["", "## Index Depths"])
    lines.extend(f"- {key}: {value}" for key, value in summary.get("index_depth_counts", {}).items())
    return "\n".join(lines) + "\n"


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
    repo_resolved = REPO_ROOT.resolve()
    try:
        rel = resolved.relative_to(repo_resolved).as_posix()
        rel_lower = rel.casefold()
        for forbidden in FORBIDDEN_OUTPUT_ROOTS:
            forbidden_lower = forbidden.casefold().rstrip("/")
            if rel_lower == forbidden_lower or rel_lower.startswith(forbidden_lower + "/"):
                raise ValueError(f"refusing forbidden output root: {forbidden}")
        if rel_lower.startswith("control/audits/") and "/generated/" in rel_lower:
            return resolved
        if rel_lower.startswith("examples/sources/"):
            return resolved
        raise ValueError(f"refusing output outside approved Source OS roots: {rel}")
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
