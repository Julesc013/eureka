#!/usr/bin/env python3
"""Plan local-machine public exposure without enabling it."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local.local_machine_public_exposure import AUTH_POSTURES
from runtime.local.local_machine_public_exposure import DEFAULT_OUT
from runtime.local.local_machine_public_exposure import EXPOSURE_MODES
from runtime.local.local_machine_public_exposure import OPS_POSTURES
from runtime.local.local_machine_public_exposure import PLAN_JSON
from runtime.local.local_machine_public_exposure import REPORT_JSON
from runtime.local.local_machine_public_exposure import TLS_STATUSES
from runtime.local.local_machine_public_exposure import build_plan
from runtime.local.local_machine_public_exposure import build_report
from runtime.local.local_machine_public_exposure import load_json
from runtime.local.local_machine_public_exposure import render_plan_status
from runtime.local.local_machine_public_exposure import validate_plan
from runtime.local.local_machine_public_exposure import validate_report
from runtime.local.local_machine_public_exposure import write_plan
from runtime.local.local_machine_public_exposure import write_report


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    plan_parser = subparsers.add_parser("plan", help="Write a local-machine public exposure plan.")
    plan_parser.add_argument("--local-machine-staging-report", required=True)
    plan_parser.add_argument("--release-check-report", required=True)
    plan_parser.add_argument("--launch-gate-report", required=True)
    plan_parser.add_argument("--out", default=DEFAULT_OUT)
    plan_parser.add_argument("--exposure-mode", choices=EXPOSURE_MODES, default="loopback_only")
    plan_parser.add_argument("--public-base-url", default="")
    plan_parser.add_argument("--domain", default="")
    plan_parser.add_argument("--tls-status", choices=TLS_STATUSES, default="missing")
    plan_parser.add_argument("--production-auth-posture", choices=AUTH_POSTURES, default="missing")
    plan_parser.add_argument("--rate-limit-posture", choices=OPS_POSTURES, default="missing")
    plan_parser.add_argument("--ops-posture", default="")
    plan_parser.add_argument("--operator-approval-file", default="")
    plan_parser.add_argument("--allow-public-exposure-plan", action="store_true")
    plan_parser.add_argument("--json", action="store_true")

    validate_plan_parser = subparsers.add_parser("validate-plan", help="Validate a local-machine public exposure plan.")
    validate_plan_parser.add_argument("--plan", required=True)
    validate_plan_parser.add_argument("--json", action="store_true")

    status_parser = subparsers.add_parser("status", help="Print a concise public exposure plan summary.")
    status_parser.add_argument("--plan", required=True)
    status_parser.add_argument("--json", action="store_true")

    report_parser = subparsers.add_parser("report", help="Write a public exposure report from a plan.")
    report_parser.add_argument("--plan", required=True)
    report_parser.add_argument("--out", default=DEFAULT_OUT)
    report_parser.add_argument("--json", action="store_true")

    validate_report_parser = subparsers.add_parser("validate-report", help="Validate a public exposure report.")
    validate_report_parser.add_argument("--report", required=True)
    validate_report_parser.add_argument("--json", action="store_true")

    args = parser.parse_args(argv)
    if args.command == "plan":
        plan = build_plan(
            local_machine_staging_report=args.local_machine_staging_report,
            release_check_report=args.release_check_report,
            launch_gate_report=args.launch_gate_report,
            out_dir=args.out,
            exposure_mode=args.exposure_mode,
            public_base_url=args.public_base_url,
            domain=args.domain,
            tls_status=args.tls_status,
            production_auth_posture=args.production_auth_posture,
            rate_limit_posture=args.rate_limit_posture,
            ops_posture=args.ops_posture or None,
            operator_approval_file=args.operator_approval_file or None,
            allow_public_exposure_plan=args.allow_public_exposure_plan,
        )
        plan_path = write_plan(plan, args.out)
        if args.json:
            print(json.dumps(plan, indent=2, sort_keys=True, ensure_ascii=True), file=stdout)
        else:
            print(f"Local-machine public exposure plan: {plan_path}", file=stdout)
            print(f"selected_hosting_path: {plan.get('selected_hosting_path')}", file=stdout)
            print(f"exposure_mode: {plan.get('exposure_mode')}", file=stdout)
            print(f"public_exposure_enabled: {str(plan.get('public_exposure_enabled')).lower()}", file=stdout)
            print(f"remaining_blockers: {len(plan.get('remaining_blockers') or [])}", file=stdout)
            print(f"next_recommended_task: {plan.get('next_recommended_task')}", file=stdout)
        return 0

    if args.command == "validate-plan":
        errors = validate_plan(args.plan)
        payload = {
            "schema_version": "eureka.local_machine_public_exposure_plan_validation.v0",
            "status": "pass" if not errors else "fail",
            "plan": str(args.plan),
            "errors": errors,
        }
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True), file=stdout)
        elif errors:
            print(f"Local-machine public exposure plan validation failed: {args.plan}", file=stderr)
            for error in errors:
                print(f"- {error}", file=stderr)
        else:
            print(f"Local-machine public exposure plan validation passed: {args.plan}", file=stdout)
        return 0 if not errors else 1

    if args.command == "status":
        try:
            plan = load_json(args.plan)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"Could not read local-machine public exposure plan: {type(exc).__name__}", file=stderr)
            return 1
        if args.json:
            print(json.dumps(plan, indent=2, sort_keys=True, ensure_ascii=True), file=stdout)
        else:
            print(render_plan_status(plan), end="", file=stdout)
        return 0

    if args.command == "report":
        report = build_report(args.plan)
        report_path = write_report(report, args.out)
        if args.json:
            print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=True), file=stdout)
        else:
            print(f"Local-machine public exposure report: {report_path}", file=stdout)
            print(f"status: {report.get('status')}", file=stdout)
            print(f"public_readiness_status: {report.get('public_readiness_status')}", file=stdout)
            print(f"blockers: {len(report.get('blockers') or [])}", file=stdout)
            print(f"next_recommended_task: {report.get('next_recommended_task')}", file=stdout)
        if report.get("status") == "FAIL":
            for blocker in report.get("blockers") or []:
                if isinstance(blocker, dict) and blocker.get("status") == "failed":
                    print(f"- {blocker.get('id')}: {blocker.get('message')}", file=stderr)
            return 1
        return 0

    if args.command == "validate-report":
        errors = validate_report(args.report)
        payload = {
            "schema_version": "eureka.local_machine_public_exposure_report_validation.v0",
            "status": "pass" if not errors else "fail",
            "report": str(args.report),
            "errors": errors,
        }
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True), file=stdout)
        elif errors:
            print(f"Local-machine public exposure report validation failed: {args.report}", file=stderr)
            for error in errors:
                print(f"- {error}", file=stderr)
        else:
            print(f"Local-machine public exposure report validation passed: {args.report}", file=stdout)
        return 0 if not errors else 1

    parser.error(f"unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
