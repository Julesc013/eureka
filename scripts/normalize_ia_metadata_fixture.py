#!/usr/bin/env python3
"""Normalize committed Internet Archive metadata fixtures without live calls."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.connectors.internet_archive import (  # noqa: E402
    load_fixture,
    map_normalized_to_source_cache_candidate,
    normalize_ia_metadata,
    preview_evidence_candidates,
    summarize_ia_normalized_record,
)


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
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Committed IA metadata fixture path.")
    parser.add_argument("--output", help="Optional normalized JSON output path.")
    parser.add_argument("--source-cache-output", help="Optional source-cache candidate preview output path.")
    parser.add_argument("--evidence-preview-output", help="Optional evidence candidate preview output path.")
    parser.add_argument("--check", action="store_true", help="Validate only; do not write outputs.")
    parser.add_argument("--json", action="store_true", help="Emit JSON summary.")
    args = parser.parse_args(argv)

    try:
        fixture = load_fixture(args.input)
        normalized = normalize_ia_metadata(fixture)
        source_cache = map_normalized_to_source_cache_candidate(normalized)
        evidence = preview_evidence_candidates(normalized)
        if not args.check:
            _write_optional(args.output, normalized)
            _write_optional(args.source_cache_output, source_cache)
            _write_optional(args.evidence_preview_output, evidence)
        summary = {
            "status": "valid",
            "input": _display_path(Path(args.input)),
            "check_mode": args.check,
            "wrote_files": bool(not args.check and (args.output or args.source_cache_output or args.evidence_preview_output)),
            "normalized_summary": summarize_ia_normalized_record(normalized),
        }
        if args.json:
            print(json.dumps(summary, indent=2, sort_keys=True), file=stdout)
        else:
            print("IA metadata fixture normalization", file=stdout)
            print(f"status: {summary['status']}", file=stdout)
            print(f"input: {summary['input']}", file=stdout)
            print(f"item_identifier: {summary['normalized_summary']['item_identifier']}", file=stdout)
            print(f"file_count: {summary['normalized_summary']['file_count']}", file=stdout)
            print(f"check_mode: {str(args.check).lower()}", file=stdout)
        return 0
    except Exception as exc:  # noqa: BLE001 - command-line validation surface.
        if args.json:
            print(json.dumps({"status": "invalid", "error": str(exc)}, indent=2, sort_keys=True), file=stdout)
        else:
            print("IA metadata fixture normalization", file=stdout)
            print("status: invalid", file=stdout)
            print(f"ERROR: {exc}", file=stdout)
        return 1


def _write_optional(path_text: str | None, payload: dict[str, Any]) -> None:
    if not path_text:
        return
    path = _safe_output_path(Path(path_text))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _safe_output_path(path: Path) -> Path:
    resolved = (REPO_ROOT / path).resolve() if not path.is_absolute() else path.resolve()
    try:
        rel = resolved.relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError as exc:
        raise ValueError(f"refusing output outside repository: {resolved}") from exc
    rel_lower = rel.casefold()
    for forbidden in FORBIDDEN_OUTPUT_ROOTS:
        forbidden_lower = forbidden.casefold().rstrip("/")
        if rel_lower == forbidden_lower or rel_lower.startswith(forbidden_lower + "/"):
            raise ValueError(f"refusing forbidden output root: {forbidden}")
    return resolved


def _display_path(path: Path) -> str:
    candidate = (REPO_ROOT / path).resolve() if not path.is_absolute() else path.resolve()
    try:
        return candidate.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
