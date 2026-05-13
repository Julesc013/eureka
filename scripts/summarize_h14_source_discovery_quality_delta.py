#!/usr/bin/env python3
"""Summarize H14 Source OS review quality delta offline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile
from typing import Any, Mapping, Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from control.prototypes.legacy_runtime.connectors.h14_source_discovery.quality_delta import build_h14_quality_delta, summarize_h14_quality_delta  # noqa: E402

FORBIDDEN_OUTPUT_ROOTS = (
    "site/dist", "data/public_index", "runtime", "contracts", "control/inventory/sources",
    "control/inventory/connectors", "source_registry_mutation", "connector_registry_mutation",
    "pack_import_staging", "pack_export_staging", "source_cache", "evidence_ledger",
    "review_queue", "public_index", "master_index", ".aide.local", ".local/eureka",
    ".cache/eureka", "local_sources", "private_sources",
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", action="append", default=[], help="Explicit H14 integration output JSON file. May be repeated.")
    parser.add_argument("--input-dir", action="append", default=[], help="Directory containing H14 integration output JSON files. May be repeated.")
    parser.add_argument("--output", help="Optional JSON output path.")
    parser.add_argument("--summary-output", help="Optional Markdown output path.")
    parser.add_argument("--check", action="store_true", help="Validate only and write no files.")
    parser.add_argument("--json", action="store_true", help="Emit JSON summary.")
    args = parser.parse_args(argv)
    try:
        review = _load_review_result(args.input, args.input_dir)
        delta = build_h14_quality_delta({"review_integration_result": review})
        summary = summarize_h14_quality_delta(delta)
        wrote = False
        if args.output and not args.check:
            _write_json(args.output, delta)
            wrote = True
        if args.summary_output and not args.check:
            _write_text(args.summary_output, render_summary(summary))
            wrote = True
        summary["wrote_files"] = wrote
        if args.json:
            print(json.dumps(summary, indent=2, sort_keys=True), file=stdout)
        else:
            print("H14 Source OS quality delta", file=stdout)
            print(f"status: {summary['status']}", file=stdout)
            print(f"source_count: {summary['source_count']}", file=stdout)
            print(f"blocked_sources_count: {summary['blocked_sources_count']}", file=stdout)
            print(f"review_seed_count: {summary['review_seed_count']}", file=stdout)
            print(f"wrote_files: {str(wrote).lower()}", file=stdout)
        return 0 if summary["status"] == "pass" else 1
    except Exception as exc:  # noqa: BLE001
        if args.json:
            print(json.dumps({"status": "invalid", "error": str(exc)}, indent=2, sort_keys=True), file=stdout)
        else:
            print("H14 Source OS quality delta", file=stdout)
            print("status: invalid", file=stdout)
            print(f"ERROR: {exc}", file=stdout)
        return 1


def _load_review_result(inputs: Sequence[str], input_dirs: Sequence[str]) -> dict[str, Any]:
    paths = _collect_input_paths(inputs, input_dirs)
    objects = [_load_json(path) for path in paths]
    for item in objects:
        if item.get("schema_version") == "h14_source_discovery_review_integration_result.v0":
            return item
    for item in objects:
        if "source_need_review_seeds" in item:
            return item
    raise ValueError("no H14 review integration result found")


def render_summary(summary: Mapping[str, Any]) -> str:
    return "\n".join([
        "# H14 Quality Delta Summary",
        "",
        f"- status: `{summary.get('status')}`",
        f"- source_count: `{summary.get('source_count')}`",
        f"- blocked_sources_count: `{summary.get('blocked_sources_count')}`",
        f"- review_seed_count: `{summary.get('review_seed_count')}`",
        "- production_source_discovery_quality: `false`",
        "- source_coverage_completeness: `false`",
        "- connector_reliability_verified: `false`",
        "- freshness_verified: `false`",
        "- rights_clearance: `false`",
        "- production_readiness: `false`",
        "",
    ])


def _collect_input_paths(inputs: Sequence[str], input_dirs: Sequence[str]) -> list[Path]:
    paths = [_resolve_input(Path(item)) for item in inputs]
    for item in input_dirs:
        directory = _resolve_input(Path(item))
        if not directory.is_dir():
            raise ValueError(f"input-dir is not a directory: {directory}")
        paths.extend(sorted(path for path in directory.glob("*.json") if path.is_file()))
    if not paths:
        raise ValueError("at least one --input or --input-dir is required")
    return paths


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, Mapping):
        raise ValueError(f"{path} must contain a JSON object")
    return dict(payload)


def _resolve_input(path: Path) -> Path:
    resolved = (REPO_ROOT / path).resolve() if not path.is_absolute() else path.resolve()
    if not resolved.exists():
        raise ValueError(f"input path does not exist: {resolved}")
    return resolved


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
        if rel_lower.startswith("examples/connectors/h14_source_discovery/review_integration/") or rel_lower.startswith("control/audits/"):
            return resolved
        raise ValueError(f"refusing output outside approved H14 review roots: {rel}")
    except ValueError as exc:
        if str(exc).startswith("refusing"):
            raise
        temp_root = Path(tempfile.gettempdir()).resolve()
        try:
            resolved.relative_to(temp_root)
            return resolved
        except ValueError as temp_exc:
            raise ValueError(f"refusing output outside repository approved roots or temp directory: {resolved}") from temp_exc


def _write_json(path_text: str, payload: Mapping[str, Any]) -> None:
    path = _safe_output_path(Path(path_text))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text(path_text: str, text: str) -> None:
    path = _safe_output_path(Path(path_text))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
