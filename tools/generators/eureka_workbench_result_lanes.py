#!/usr/bin/env python3
"""Build deterministic Workbench result lane projections."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local.service.workbench_result_lanes import build_demo_lane_page


PROJECTIONS = ("operator_workbench", "public_web", "native_desktop_read_only")


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query", required=True)
    parser.add_argument("--projection", choices=PROJECTIONS, default="operator_workbench")
    parser.add_argument("--from-play-demo", action="store_true")
    parser.add_argument("--from-ia-examples", action="store_true")
    parser.add_argument("--json", action="store_true", dest="json_output")
    parser.add_argument("--output")
    parser.add_argument("--boundary-output")
    args = parser.parse_args(argv)

    page = build_demo_lane_page(
        args.query,
        args.projection,
        from_play_demo=args.from_play_demo,
        from_ia_examples=args.from_ia_examples,
    )
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(page, indent=2) + "\n", encoding="utf-8")
    if args.boundary_output:
        boundary_path = Path(args.boundary_output)
        boundary_path.parent.mkdir(parents=True, exist_ok=True)
        boundary_path.write_text(json.dumps(page["boundary_report"], indent=2) + "\n", encoding="utf-8")

    if args.json_output:
        print(json.dumps(page, indent=2, sort_keys=True), file=stdout)
    else:
        print(f"Workbench result lane projection: {page['projection_profile']}", file=stdout)
        print(f"query: {page['query']}", file=stdout)
        print(f"lanes: {page['visible_lane_count']}/{page['lane_count']} visible", file=stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
