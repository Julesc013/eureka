#!/usr/bin/env python3
"""Normalize one committed H1 metadata-wave fixture offline."""

from __future__ import annotations

import argparse
import importlib
import json
from pathlib import Path
import sys
import tempfile
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from control.prototypes.legacy_runtime.connectors.h1_metadata_wave.fixture_loader import load_h1_fixture  # noqa: E402
from control.prototypes.legacy_runtime.connectors.h1_metadata_wave.normalizer_common import (  # noqa: E402
    H1_SOURCE_IDS,
    build_h1_evidence_candidate_preview,
    build_h1_source_cache_candidate_preview,
    summarize_h1_normalized_record,
)


FORBIDDEN_OUTPUT_ROOTS = (
    "site/dist",
    "data/public_index",
    "runtime",
    "contracts",
    "data/master_index",
    "master_index",
    "control/inventory/publication",
    "control/inventory/sources",
    ".aide.local",
    ".local/eureka",
    ".cache/eureka",
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-id", required=True, choices=H1_SOURCE_IDS)
    parser.add_argument("--input", required=True, help="Committed fixture JSON path.")
    parser.add_argument("--output", help="Optional normalized record output path.")
    parser.add_argument("--source-cache-output", help="Optional source-cache preview output path.")
    parser.add_argument("--evidence-preview-output", help="Optional evidence preview output path.")
    parser.add_argument("--check", action="store_true", help="Validate only; do not write outputs.")
    parser.add_argument("--json", action="store_true", help="Print normalized record JSON.")
    args = parser.parse_args(argv)
    try:
        fixture = load_h1_fixture(_repo_path(args.input))
        normalizer = _normalizer(args.source_id)
        record = normalizer(fixture)
        source_cache = build_h1_source_cache_candidate_preview(record)
        evidence_preview = build_h1_evidence_candidate_preview(record)
        if not args.check:
            if args.output:
                _write_json(args.output, record, allowed_kinds={"normalized", "audit_generated", "temp"})
            if args.source_cache_output:
                _write_json(args.source_cache_output, source_cache, allowed_kinds={"audit_generated", "temp"})
            if args.evidence_preview_output:
                _write_json(args.evidence_preview_output, evidence_preview, allowed_kinds={"audit_generated", "temp"})
        if args.json:
            print(json.dumps(record, indent=2, sort_keys=True), file=stdout)
        else:
            summary = summarize_h1_normalized_record(record)
            print("H1 metadata fixture normalizer", file=stdout)
            print("status: pass", file=stdout)
            print(f"source_id: {summary['source_id']}", file=stdout)
            print(f"source_native_id: {summary['source_native_id']}", file=stdout)
            print("network_used: false", file=stdout)
        return 0
    except Exception as exc:  # noqa: BLE001
        if args.json:
            print(json.dumps({"status": "invalid", "error": str(exc)}, indent=2, sort_keys=True), file=stdout)
        else:
            print("H1 metadata fixture normalizer", file=stdout)
            print("status: invalid", file=stdout)
            print(f"ERROR: {exc}", file=stdout)
        return 1


def _normalizer(source_id: str):
    module = importlib.import_module(f"control.prototypes.legacy_runtime.connectors.h1_metadata_wave.{source_id}")
    return module.normalize


def _repo_path(path_text: str | Path) -> Path:
    path = Path(path_text)
    return path if path.is_absolute() else REPO_ROOT / path


def _write_json(path_text: str, payload: Mapping[str, Any], allowed_kinds: set[str]) -> None:
    path = _safe_output_path(Path(path_text), allowed_kinds)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _safe_output_path(path: Path, allowed_kinds: set[str]) -> Path:
    resolved = (REPO_ROOT / path).resolve() if not path.is_absolute() else path.resolve()
    repo_resolved = REPO_ROOT.resolve()
    try:
        rel = resolved.relative_to(repo_resolved).as_posix()
        rel_lower = rel.casefold()
        for forbidden in FORBIDDEN_OUTPUT_ROOTS:
            forbidden_lower = forbidden.casefold().rstrip("/")
            if rel_lower == forbidden_lower or rel_lower.startswith(forbidden_lower + "/"):
                raise ValueError(f"refusing forbidden output root: {forbidden}")
        if "audit_generated" in allowed_kinds and rel_lower.startswith("control/audits/") and "/generated/" in rel_lower:
            return resolved
        if "normalized" in allowed_kinds and rel_lower.startswith("examples/connectors/h1_metadata_wave/normalized/"):
            return resolved
        if "replay" in allowed_kinds and rel_lower.startswith("examples/connectors/h1_metadata_wave/replay_results/"):
            return resolved
        raise ValueError(f"refusing output outside approved H1 fixture roots: {rel}")
    except ValueError as exc:
        if str(exc).startswith("refusing"):
            raise
        temp_root = Path(tempfile.gettempdir()).resolve()
        try:
            resolved.relative_to(temp_root)
            return resolved
        except ValueError as temp_exc:
            raise ValueError(f"refusing output outside approved roots or temp directory: {resolved}") from temp_exc


if __name__ == "__main__":
    raise SystemExit(main())
