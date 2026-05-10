#!/usr/bin/env python3
"""Summarize MVP alpha operator-review artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.validate_mvp_alpha_operator_review import validate_output_path, write_json_output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", action="append", default=[])
    parser.add_argument("--output")
    parser.add_argument("--summary-output")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    inputs = args.input or ["examples/audits/mvp_alpha_operator"]
    report = summarize(inputs)
    if args.output:
        write_json_output(validate_output_path(args.output), report)
    if args.summary_output:
        validate_output_path(args.summary_output).write_text(format_summary(report) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    elif args.check:
        print(f"MVP alpha operator review summary status: {report['status']}")
    else:
        print(format_summary(report))
    return 0


def summarize(inputs: list[str]) -> dict[str, Any]:
    decisions: list[str] = []
    signoffs: list[str] = []
    blockers: list[str] = []
    next_tasks: list[str] = []
    for raw in inputs:
        path = Path(raw)
        if not path.is_absolute():
            path = REPO_ROOT / path
        files = sorted(path.rglob("*.json")) if path.is_dir() else [path]
        for file_path in files:
            payload = json.loads(file_path.read_text(encoding="utf-8"))
            schema = payload.get("schema_version")
            if schema == "mvp_alpha_operator_decision.v0":
                decisions.append(payload.get("selected_decision", "unknown"))
            elif schema == "mvp_alpha_operator_signoff_packet.v0":
                signoffs.append(payload.get("signoff_status", "unknown"))
            elif schema == "mvp_alpha_launch_blocker_register.v0":
                blockers.extend(payload.get("launch_blockers", []))
            elif schema == "mvp_alpha_operator_next_task.v0":
                next_tasks.append(payload.get("next_task_id", "unknown"))
    return {
        "schema_version": "mvp_alpha_operator_review_summary.v0",
        "status": "pass",
        "decision_statuses": sorted(set(decisions)),
        "signoff_statuses": sorted(set(signoffs)),
        "launch_blockers": sorted(set(blockers)),
        "next_tasks": sorted(set(next_tasks)),
        "signoff_inferred": False,
        "deployment_allowed_current": False,
        "launch_allowed_current": False,
    }


def format_summary(report: dict[str, Any]) -> str:
    lines = [
        "# MVP Alpha Operator Review Summary",
        "",
        f"- status: {report['status']}",
        f"- decisions: {', '.join(report['decision_statuses'])}",
        f"- signoffs: {', '.join(report['signoff_statuses'])}",
        f"- next_tasks: {', '.join(report['next_tasks'])}",
        "- signoff_inferred: false",
        "- deployment_allowed_current: false",
        "- launch_allowed_current: false",
    ]
    if report["launch_blockers"]:
        lines.append("")
        lines.append("## Launch Blockers")
        lines.extend(f"- {item}" for item in report["launch_blockers"])
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
