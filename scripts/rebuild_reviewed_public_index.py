#!/usr/bin/env python3
"""Rebuild a local reviewed public index from explicit local stores."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.public_index import rebuild_reviewed_public_index
from runtime.public_index.validation import validate_public_index_path


FORBIDDEN_OUTPUT_ROOTS = {
    "runtime",
    "contracts",
    "surfaces",
    "site",
    "native",
    "crates",
    "examples",
    ".git",
    ".env",
    "secrets",
    ".aide.local",
    ".local",
    ".cache",
}


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--source-cache-db", required=True)
    parser.add_argument("--evidence-db", required=True)
    parser.add_argument("--review-db", required=True)
    parser.add_argument("--public-index-db", required=True)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--output")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    root = Path(args.repo_root).resolve()
    if args.dry_run and args.apply:
        print("choose --dry-run or --apply, not both", file=stderr)
        return 2
    dry_run = not args.apply
    errors = validate_public_index_path(args.public_index_db)
    if errors:
        print(json.dumps({"status": "fail", "errors": list(errors)}, indent=2, sort_keys=True), file=stderr)
        return 2
    output = resolve_output_path(root, args.output) if args.output else None
    if output and is_forbidden_output(root, output):
        print(f"refusing forbidden output root: {output}", file=stderr)
        return 2

    try:
        result = rebuild_reviewed_public_index(
            args.source_cache_db,
            args.evidence_db,
            args.review_db,
            args.public_index_db,
            dry_run=dry_run,
        )
    except Exception as exc:
        print(json.dumps({"status": "fail", "error": str(exc)}, indent=2, sort_keys=True), file=stderr)
        return 1
    text = json.dumps(result, indent=2, sort_keys=True)
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text + "\n", encoding="utf-8")
    if args.json:
        print(text, file=stdout)
    else:
        print(f"reviewed public index rebuild: {result['status']}", file=stdout)
        print(f"included: {result['included_count']}", file=stdout)
        print(f"excluded: {result['excluded_count']}", file=stdout)
    return 0


def resolve_output_path(root: Path, value: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = root / path
    return path.resolve()


def is_forbidden_output(root: Path, output: Path) -> bool:
    try:
        rel = output.relative_to(root).as_posix()
    except ValueError:
        return False
    return any(rel == item or rel.startswith(item.rstrip("/") + "/") for item in FORBIDDEN_OUTPUT_ROOTS)


if __name__ == "__main__":
    raise SystemExit(main())
