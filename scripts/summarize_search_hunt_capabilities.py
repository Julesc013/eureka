#!/usr/bin/env python3
"""Summarize Search Hunt closeout capabilities."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Sequence, TextIO
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--closeout-result", default="control/inventory/search_hunt_closeout_result.json")
    parser.add_argument("--capability-matrix", default="control/inventory/search_hunt_capability_matrix.json")
    parser.add_argument("--output")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    root = Path(args.repo_root).resolve()
    result = summarize(root, args.closeout_result, args.capability_matrix)
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(result["markdown"], encoding="utf-8")
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    elif not args.output:
        print(result["markdown"], file=stdout)
    return 0 if result["status"] in {"pass", "pass_with_warnings"} else 1


def summarize(root: Path = REPO_ROOT, closeout_rel: str = "control/inventory/search_hunt_closeout_result.json", capability_rel: str = "control/inventory/search_hunt_capability_matrix.json") -> dict[str, Any]:
    closeout = load_json(root / closeout_rel)
    capability_matrix = load_json(root / capability_rel)
    rows = capability_matrix.get("capabilities", [])
    recommended_next = str(closeout.get("recommended_next_task", "unknown")).replace("\u2014", "-")
    lines = [
        "# Search Hunt Capability Summary",
        "",
        f"- status: {closeout.get('status', 'unknown')}",
        f"- hunt_track_complete: {str(closeout.get('hunt_track_complete') is True).lower()}",
        f"- hard_blockers_remaining: {closeout.get('hard_blockers_remaining', 'unknown')}",
        f"- warnings_remaining: {closeout.get('warnings_remaining', 'unknown')}",
        f"- recommended_next_task: {recommended_next}",
        "",
        "## Capabilities",
        "",
    ]
    for row in rows:
        lines.append(f"- {row.get('capability_id')}: implemented={str(row.get('implemented') is True).lower()}, tested={str(row.get('tested') is True).lower()}, proof={row.get('proof_level')}")
    lines.extend(
        [
            "",
            "## Boundaries",
            "",
            "- source probes: not executed",
            "- extraction: not executed",
            "- model/provider calls: not used",
            "- deployment: not performed",
            "- production/public launch readiness: not claimed",
            "",
        ]
    )
    return {
        "schema_version": "search_hunt_capability_summary.v0",
        "task": "HUNT-12",
        "status": closeout.get("status", "fail"),
        "capability_count": len(rows),
        "markdown": "\n".join(lines),
    }


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


if __name__ == "__main__":
    raise SystemExit(main())
