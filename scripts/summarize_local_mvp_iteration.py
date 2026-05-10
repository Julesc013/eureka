#!/usr/bin/env python3
"""Summarize local MVP iteration examples or audit outputs."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.validate_local_mvp_iteration import load_json, validate_output_path, write_json_output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", action="append", default=[])
    parser.add_argument("--output")
    parser.add_argument("--summary-output")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    inputs = args.input or ["examples/audits/local_mvp"]
    records = _load_records(inputs)
    result = summarize(records)
    if args.output:
        write_json_output(validate_output_path(args.output), result)
    if args.summary_output:
        validate_output_path(args.summary_output).write_text(format_summary(result), encoding="utf-8")
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    elif args.check:
        print(f"Local MVP iteration summary status: {result['status']}")
        print(f"recommended_next_task: {result['recommended_next_task']}")
    else:
        print(format_summary(result))
    return 0 if result["status"] == "pass" else 1


def summarize(records: list[dict[str, Any]]) -> dict[str, Any]:
    recommended = None
    option_statuses: dict[str, str] = {}
    deployment_deferred = None
    for record in records:
        if record.get("schema_version") == "local_mvp_iteration_plan.v0":
            if record.get("plan_status") in {"ready_for_next_local_bundle", "planning_only"} or recommended is None:
                recommended = record.get("recommended_next_task")
        if record.get("schema_version") == "local_mvp_next_wave_option.v0":
            option_statuses[record.get("option_task_id", "unknown")] = record.get("option_status", "unknown")
        if record.get("schema_version") == "local_mvp_deployment_deferral.v0":
            deployment_deferred = record.get("deployment_deferred")
    errors: list[str] = []
    if recommended != "H2-BUNDLE-01":
        errors.append("H2-BUNDLE-01 must be the current recommended next task.")
    if deployment_deferred is not True:
        errors.append("deployment must remain deferred.")
    return {
        "schema_version": "local_mvp_iteration_summary.v0",
        "status": "fail" if errors else "pass",
        "record_count": len(records),
        "recommended_next_task": recommended,
        "option_statuses": option_statuses,
        "deployment_deferred": deployment_deferred,
        "errors": errors,
    }


def format_summary(result: dict[str, Any]) -> str:
    lines = [
        "# Local MVP Iteration Summary",
        "",
        f"- status: {result['status']}",
        f"- recommended_next_task: {result['recommended_next_task']}",
        f"- deployment_deferred: {result['deployment_deferred']}",
    ]
    for task, status in sorted(result["option_statuses"].items()):
        lines.append(f"- option: {task} = {status}")
    lines.extend(f"- error: {error}" for error in result["errors"])
    return "\n".join(lines) + "\n"


def _load_records(inputs: list[str]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for raw in inputs:
        path = Path(raw)
        if not path.is_absolute():
            path = REPO_ROOT / path
        if path.is_dir():
            for child in sorted(path.glob("*.json")):
                records.append(load_json(child))
        else:
            records.append(load_json(path))
    return records


if __name__ == "__main__":
    raise SystemExit(main())
