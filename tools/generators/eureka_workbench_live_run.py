#!/usr/bin/env python3
"""Create a local Workbench live-run projection from the headless run kernel."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from runtime.local_service.workbench_live_run import create_workbench_resolution_run


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query", required=True)
    parser.add_argument("--projection", default="operator_workbench", choices=("operator_workbench", "public_web", "native_desktop_read_only"))
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--from-fixtures", action="store_true")
    parser.add_argument("--include-ia-hunt-dry-run", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output")
    parser.add_argument("--events-output")
    parser.add_argument("--lanes-output")
    parser.add_argument("--workunits-output")
    parser.add_argument("--boundary-output")
    args = parser.parse_args(argv)

    packet = create_workbench_resolution_run(
        args.query,
        args.projection,
        include_ia_hunt_dry_run=bool(args.include_ia_hunt_dry_run),
    )
    _write_json(args.output, packet)
    _write_json(args.events_output, packet["events"])
    _write_json(args.lanes_output, packet["lane_snapshot"])
    _write_json(args.workunits_output, packet["workunits"])
    _write_json(args.boundary_output, packet["boundary_report"])
    if args.json:
        print(json.dumps(packet, indent=2, sort_keys=True), file=stdout)
    else:
        print(f"run_id: {packet['run_id']}", file=stdout)
        print(f"state: {packet['state']}", file=stdout)
        print(f"lanes: {packet['lane_count']}", file=stdout)
        print(f"workunits: {packet['workunit_count']}", file=stdout)
    return 0


def _write_json(path_value: str | None, payload: Any) -> None:
    if not path_value:
        return
    path = Path(path_value)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
