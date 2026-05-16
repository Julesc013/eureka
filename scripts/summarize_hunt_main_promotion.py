#!/usr/bin/env python3
"""Print a compact summary of HUNT-to-main promotion evidence."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
RESULT = Path("control/inventory/hunt_main_promotion_result.json")
GATES = Path("control/inventory/hunt_main_promotion_gate_matrix.json")


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    root = Path(args.repo_root).resolve()
    result = load_json(root / RESULT)
    gates = load_json(root / GATES).get("gates", [])
    failed = [gate for gate in gates if gate.get("status") == "fail" and gate.get("blocks_promotion")]
    summary = {
        "schema_version": "hunt_main_promotion_summary.v0",
        "status": result.get("status", "missing"),
        "promotion_gates_passed": result.get("promotion_gates_passed", False),
        "main_promoted": result.get("main_promoted", False),
        "origin_main_equals_origin_dev": result.get("origin_main_equals_origin_dev", False),
        "failed_blocking_gates": [gate.get("gate_id") for gate in failed],
        "recommended_next_task": result.get("recommended_next_task", ""),
    }
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True), file=stdout)
    else:
        print(f"status: {summary['status']}", file=stdout)
        print(f"promotion_gates_passed: {summary['promotion_gates_passed']}", file=stdout)
        print(f"main_promoted: {summary['main_promoted']}", file=stdout)
        print(f"origin_main_equals_origin_dev: {summary['origin_main_equals_origin_dev']}", file=stdout)
        print(f"recommended_next_task: {summary['recommended_next_task']}", file=stdout)
    return 0 if summary["status"] == "pass" and not failed else 1


def load_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(main())
