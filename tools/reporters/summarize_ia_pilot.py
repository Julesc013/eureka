#!/usr/bin/env python3
"""Summarize the Internet Archive metadata pilot closeout."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Sequence, TextIO
import sys

REPO_ROOT = Path(__file__).resolve().parents[2]


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit JSON summary.")
    parser.add_argument("--output", type=Path, help="Optional output path.")
    args = parser.parse_args(argv)
    summary = build_summary(REPO_ROOT)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True), file=stdout)
    else:
        print(_markdown(summary), file=stdout)
    return 0


def build_summary(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    result = _load_json(repo_root / "control/inventory/ia_pilot_closeout_result.json")
    capability = _load_json(repo_root / "control/inventory/ia_pilot_capability_matrix.json")
    boundary = _load_json(repo_root / "control/inventory/ia_pilot_boundary_matrix.json")
    decision = _load_json(repo_root / "control/inventory/ia_pilot_next_task_decision.json")
    rows = capability.get("rows", []) if isinstance(capability.get("rows"), list) else []
    return {
        "schema_version": "ia_pilot_summary.v0",
        "task": "IA-PILOT-CLOSEOUT-01",
        "status": result.get("status", "unknown"),
        "capability_count": len(rows),
        "full_ia_metadata_vertical_slice_complete": result.get("full_ia_metadata_vertical_slice_complete") is True,
        "full_archive_org_integration_claimed": result.get("full_archive_org_integration_claimed") is True,
        "total_http_requests": result.get("total_http_requests", 0),
        "forbidden_boundaries": boundary.get("forbidden_boundaries", {}),
        "intentionally_allowed_actions": boundary.get("intentionally_allowed_actions", {}),
        "recommended_next_task": decision.get("recommended_next_task", ""),
    }


def _markdown(summary: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# IA Pilot Summary",
            "",
            f"Status: {summary.get('status')}",
            f"Capabilities closed: {summary.get('capability_count')}",
            f"Vertical slice complete: {str(summary.get('full_ia_metadata_vertical_slice_complete')).lower()}",
            f"Full Archive.org integration claimed: {str(summary.get('full_archive_org_integration_claimed')).lower()}",
            f"Recommended next task: {summary.get('recommended_next_task')}",
        ]
    )


def _load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


if __name__ == "__main__":
    raise SystemExit(main())
