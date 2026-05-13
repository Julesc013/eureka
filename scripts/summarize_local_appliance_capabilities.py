#!/usr/bin/env python3
"""Summarize the LOCAL-14 capability matrix."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--closeout", default="control/inventory/local_appliance_closeout_result.json")
    parser.add_argument("--capabilities", default="control/inventory/local_appliance_capability_matrix.json")
    parser.add_argument("--output")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    root = Path(args.repo_root).resolve()
    payload = build_summary(load_json(root / args.closeout), load_json(root / args.capabilities))
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(build_markdown_summary(payload), encoding="utf-8")
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True), file=stdout)
    else:
        print(build_markdown_summary(payload), file=stdout)
    return 0


def build_summary(closeout: Mapping[str, Any], capabilities: Mapping[str, Any]) -> dict[str, Any]:
    rows = list(capabilities.get("capabilities", []))
    implemented = [row["capability_id"] for row in rows if row.get("implemented")]
    missing = [row["capability_id"] for row in rows if not row.get("implemented")]
    return {
        "schema_version": "local_appliance_capability_summary.v0",
        "task": "LOCAL-14",
        "status": closeout.get("status", "unknown"),
        "implemented_count": len(implemented),
        "missing_count": len(missing),
        "implemented_capabilities": implemented,
        "missing_capabilities": missing,
        "recommended_next_task": closeout.get("recommended_next_task", ""),
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def build_markdown_summary(payload: Mapping[str, Any]) -> str:
    lines = [
        "# Local Appliance Capability Summary",
        "",
        f"Status: {payload.get('status')}",
        f"Implemented capabilities: {payload.get('implemented_count')}",
        f"Missing capabilities: {payload.get('missing_count')}",
        f"Recommended next task: {payload.get('recommended_next_task')}",
        "",
        "This summary is a LOCAL closeout record, not a production or public launch claim.",
        "",
        "## Implemented",
    ]
    for item in payload.get("implemented_capabilities", []):
        lines.append(f"- {item}")
    if payload.get("missing_capabilities"):
        lines.append("")
        lines.append("## Missing")
        for item in payload.get("missing_capabilities", []):
            lines.append(f"- {item}")
    return "\n".join(lines) + "\n"


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(main())
