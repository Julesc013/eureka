#!/usr/bin/env python3
"""Run the headless Eureka resolution-run kernel in dry-run mode."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from runtime.resolution_run import run_resolution_dry_run


PROJECTIONS = ("operator_workbench", "public_web", "native_desktop_read_only")


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query", required=True)
    parser.add_argument("--projection", choices=PROJECTIONS, default="operator_workbench")
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--no-ia-hunt", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output")
    args = parser.parse_args(argv)

    result = run_resolution_dry_run(
        args.query,
        projection_profile=args.projection,
        include_ia_hunt=not args.no_ia_hunt,
    )
    if args.output:
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print("Resolution run dry-run", file=stdout)
        print(f"run_id: {result['run']['run_id']}", file=stdout)
        print(f"state: {result['run']['state']}", file=stdout)
        print(f"workunit_count: {result['workunit_schedule'].get('workunit_count', 0)}", file=stdout)
        print(f"lane_count: {result['lane_snapshot'].get('lane_count', 0)}", file=stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
