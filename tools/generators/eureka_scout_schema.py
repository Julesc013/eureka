#!/usr/bin/env python3
"""List and validate deterministic SCOUT schema seed examples."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local_eval.scout_schema import (  # noqa: E402
    load_scout_seed_manifest,
    load_scout_seed_records,
    validate_scout_seed,
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", default="examples/scout/scout_seed_manifest.json")
    parser.add_argument("--list", action="store_true", help="List SCOUT seed ids.")
    parser.add_argument("--validate", action="store_true", help="Validate every seed in the manifest.")
    parser.add_argument("--json", action="store_true", help="Emit JSON.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help=argparse.SUPPRESS)
    args = parser.parse_args(argv)

    root = Path(args.repo_root).resolve()
    manifest_path = Path(args.manifest)
    if not manifest_path.is_absolute():
        manifest_path = root / manifest_path

    manifest = load_scout_seed_manifest(manifest_path)
    seeds = load_scout_seed_records(manifest_path)
    reports = [validate_scout_seed(seed) for seed in seeds] if args.validate else []
    result = {
        "schema_version": "scout_schema_cli_result.v0",
        "manifest": str(manifest_path.relative_to(root) if manifest_path.is_relative_to(root) else manifest_path),
        "seed_ids": [str(seed.get("seed_id", "")) for seed in seeds],
        "seed_count": len(seeds),
        "manifest_seed_status": manifest.get("seed_status", ""),
        "validation_requested": bool(args.validate),
        "validation_passed": all(report["status"] == "valid" for report in reports) if reports else None,
        "validation_reports": reports,
    }

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    elif args.list:
        for seed_id in result["seed_ids"]:
            print(seed_id, file=stdout)
    else:
        print("SCOUT schema seed examples", file=stdout)
        print(f"count: {result['seed_count']}", file=stdout)
        if args.validate:
            print(f"validation_passed: {result['validation_passed']}", file=stdout)
    return 0 if not reports or bool(result["validation_passed"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
