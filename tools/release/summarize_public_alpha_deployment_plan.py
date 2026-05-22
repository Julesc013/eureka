#!/usr/bin/env python3
"""Summarize public alpha deployment planning artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.validate_public_alpha_deployment_plan import validate_output_path, write_json_output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", action="append", default=[])
    parser.add_argument("--output")
    parser.add_argument("--summary-output")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = summarize(args.input or ["examples/hosting/deployment"])
    if args.output:
        write_json_output(validate_output_path(args.output), report)
    if args.summary_output:
        validate_output_path(args.summary_output).write_text(format_summary(report) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    elif args.check:
        print(f"Public alpha deployment plan summary status: {report['status']}")
    else:
        print(format_summary(report))
    return 0


def summarize(inputs: list[str]) -> dict[str, Any]:
    statuses: list[str] = []
    configs = 0
    gates = 0
    noops = 0
    for raw in inputs:
        path = Path(raw)
        if not path.is_absolute():
            path = REPO_ROOT / path
        files = sorted(path.rglob("*.json")) if path.is_dir() else [path]
        for file_path in files:
            payload = json.loads(file_path.read_text(encoding="utf-8"))
            schema = payload.get("schema_version")
            if schema == "public_alpha_deployment_plan.v0":
                statuses.append(payload.get("plan_status", "unknown"))
            elif schema == "public_alpha_config_manifest.v0":
                configs += 1
            elif schema == "public_alpha_rollout_gate.v0":
                gates += 1
            elif schema == "public_alpha_deployment_noop_report.v0":
                noops += 1
    return {
        "schema_version": "public_alpha_deployment_plan_summary.v0",
        "status": "pass",
        "plan_statuses": sorted(set(statuses)),
        "config_manifest_count": configs,
        "rollout_gate_count": gates,
        "noop_report_count": noops,
        "planning_only": True,
        "deployed": False,
        "provider_api_called": False,
        "dns_changed": False,
        "site_dist_mutated": False,
    }


def format_summary(report: dict[str, Any]) -> str:
    return "\n".join([
        "# Public Alpha Deployment Plan Summary",
        "",
        f"- status: {report['status']}",
        f"- plan_statuses: {', '.join(report['plan_statuses'])}",
        "- planning_only: true",
        "- deployed: false",
        "- provider_api_called: false",
        "- dns_changed: false",
        "- site_dist_mutated: false",
    ])


if __name__ == "__main__":
    raise SystemExit(main())
