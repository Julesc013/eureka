#!/usr/bin/env python3
"""Plan, smoke, and validate local-machine public-alpha staging."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local.local_machine_staging_mvp import DEFAULT_OUT
from runtime.local.local_machine_staging_mvp import DEFAULT_QUERY
from runtime.local.local_machine_staging_mvp import PLAN_JSON
from runtime.local.local_machine_staging_mvp import REPORT_JSON
from runtime.local.local_machine_staging_mvp import build_plan
from runtime.local.local_machine_staging_mvp import load_json
from runtime.local.local_machine_staging_mvp import render_status
from runtime.local.local_machine_staging_mvp import smoke_local_machine
from runtime.local.local_machine_staging_mvp import validate_plan
from runtime.local.local_machine_staging_mvp import validate_report
from runtime.local.local_machine_staging_mvp import write_plan


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    plan_parser = subparsers.add_parser("plan", help="Write a loopback local-machine staging plan.")
    plan_parser.add_argument("--bundle", required=True)
    plan_parser.add_argument("--out", default=DEFAULT_OUT)
    plan_parser.add_argument("--host", default="127.0.0.1")
    plan_parser.add_argument("--port", type=int, default=8765)
    plan_parser.add_argument("--json", action="store_true")

    validate_plan_parser = subparsers.add_parser("validate-plan", help="Validate a local-machine staging plan.")
    validate_plan_parser.add_argument("--plan", required=True)
    validate_plan_parser.add_argument("--json", action="store_true")

    smoke_parser = subparsers.add_parser("smoke", help="Smoke public-alpha routes from a loopback local server.")
    smoke_parser.add_argument("--bundle", required=True)
    smoke_parser.add_argument("--host", default="127.0.0.1")
    smoke_parser.add_argument("--port", type=int, default=8765)
    smoke_parser.add_argument("--out", default=DEFAULT_OUT)
    smoke_parser.add_argument("--query", default=DEFAULT_QUERY)
    smoke_parser.add_argument("--json", action="store_true")

    validate_report_parser = subparsers.add_parser("validate-report", help="Validate a local-machine staging report.")
    validate_report_parser.add_argument("--report", required=True)
    validate_report_parser.add_argument("--json", action="store_true")

    status_parser = subparsers.add_parser("status", help="Print a concise local-machine staging report summary.")
    status_parser.add_argument("--report", required=True)
    status_parser.add_argument("--json", action="store_true")

    args = parser.parse_args(argv)

    if args.command == "plan":
        plan = build_plan(args.bundle, out_dir=args.out, host=args.host, port=args.port)
        plan_path = write_plan(plan, args.out)
        if args.json:
            print(json.dumps(plan, indent=2, sort_keys=True, ensure_ascii=True), file=stdout)
        else:
            print(f"Local-machine staging plan: {plan_path}", file=stdout)
            print(f"host: {plan.get('host')}", file=stdout)
            print(f"port: {plan.get('port')}", file=stdout)
            print(f"public_exposure: {str(plan.get('public_exposure')).lower()}", file=stdout)
            print(f"corpus_gate_status: {plan.get('corpus_gate_status')}", file=stdout)
        return 0

    if args.command == "validate-plan":
        errors = validate_plan(args.plan)
        payload = {
            "schema_version": "eureka.local_machine_staging_plan_validation.v0",
            "status": "pass" if not errors else "fail",
            "plan": str(args.plan),
            "errors": errors,
        }
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True), file=stdout)
        elif errors:
            print(f"Local-machine staging plan validation failed: {args.plan}", file=stderr)
            for error in errors:
                print(f"- {error}", file=stderr)
        else:
            print(f"Local-machine staging plan validation passed: {args.plan}", file=stdout)
        return 0 if not errors else 1

    if args.command == "smoke":
        report = smoke_local_machine(args.bundle, host=args.host, port=args.port, out_dir=args.out, query=args.query)
        report_path = Path(args.out) / REPORT_JSON
        if args.json:
            print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=True), file=stdout)
        else:
            print(f"Local-machine staging report: {report_path}", file=stdout)
            print(f"status: {report.get('status')}", file=stdout)
            print(f"local_machine_staging_status: {report.get('local_machine_staging_status')}", file=stdout)
            print(f"route_probes: {len(report.get('route_probe_results') or [])}", file=stdout)
            print(f"blocked_route_probes: {len(report.get('blocked_route_probe_results') or [])}", file=stdout)
        if report.get("status") == "FAIL":
            for blocker in report.get("blockers") or []:
                print(f"- {blocker}", file=stderr)
            return 1
        return 0

    if args.command == "validate-report":
        errors = validate_report(args.report)
        payload = {
            "schema_version": "eureka.local_machine_staging_report_validation.v0",
            "status": "pass" if not errors else "fail",
            "report": str(args.report),
            "errors": errors,
        }
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True), file=stdout)
        elif errors:
            print(f"Local-machine staging report validation failed: {args.report}", file=stderr)
            for error in errors:
                print(f"- {error}", file=stderr)
        else:
            print(f"Local-machine staging report validation passed: {args.report}", file=stdout)
        return 0 if not errors else 1

    if args.command == "status":
        try:
            report = load_json(args.report)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"Could not read local-machine staging report: {type(exc).__name__}", file=stderr)
            return 1
        if args.json:
            print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=True), file=stdout)
        else:
            print(render_status(report), end="", file=stdout)
        return 0

    parser.error(f"unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
