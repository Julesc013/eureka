#!/usr/bin/env python3
"""Build dry-run F0 WorkUnit seed suggestions from a member manifest."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Mapping, Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.extraction_safe_fixtures import build_workunit_seed_suggestions  # noqa: E402


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--from-manifest", required=True)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output")
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help=argparse.SUPPRESS)
    args = parser.parse_args(argv)

    if not args.dry_run:
        raise SystemExit("--dry-run is required for F0 WorkUnit seed suggestions")
    root = Path(args.repo_root).resolve()
    manifest = json.loads(_resolve(root, args.from_manifest).read_text(encoding="utf-8"))
    result = build_workunit_seed_suggestions(manifest)
    if args.output:
        _write_json(root, args.output, result)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print("F0 WorkUnit seed suggestions", file=stdout)
        print(f"dry_run: {result['dry_run']}", file=stdout)
        print(f"seed_count: {len(result['seeds'])}", file=stdout)
    return 0


def _write_json(root: Path, path_text: str, payload: Mapping[str, object]) -> None:
    path = _resolve(root, path_text)
    rel = path.relative_to(root).as_posix() if path.is_relative_to(root) else path.as_posix()
    if rel.startswith(("site/dist/", "data/public_index/", "runtime/extraction/")):
        raise ValueError(f"refusing forbidden output root: {rel}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _resolve(root: Path, path_text: str | Path) -> Path:
    path = Path(path_text)
    if not path.is_absolute():
        path = root / path
    return path.resolve()


if __name__ == "__main__":
    raise SystemExit(main())
