#!/usr/bin/env python3
"""Run and validate public-alpha release checks."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local.public_alpha_release_checks import DEFAULT_OUT, REPORT_JSON
from runtime.local.public_alpha_release_checks import render_status
from runtime.local.public_alpha_release_checks import run_release_checks
from runtime.local.public_alpha_release_checks import validate_release_check_report
from runtime.local.public_alpha_release_checks import _read_json as _load_release_json


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run public-alpha release checks and write reports.")
    run_parser.add_argument("--bundle", required=True)
    run_parser.add_argument("--corpus-gate-closeout", required=True)
    run_parser.add_argument("--rehearsal-report", required=True)
    run_parser.add_argument("--external-staging-report", required=True)
    run_parser.add_argument("--local-machine-staging-report", default="")
    run_parser.add_argument("--local-machine-public-exposure-report", default="")
    run_parser.add_argument("--launch-gate-report", required=True)
    run_parser.add_argument("--out", default=DEFAULT_OUT)
    run_parser.add_argument("--full-discovery-report", default="")
    run_parser.add_argument("--release-promotion-report", default="")
    run_parser.add_argument("--run-tests", dest="run_tests", action="store_true", default=True)
    run_parser.add_argument("--skip-tests", dest="run_tests", action="store_false")
    run_parser.add_argument("--allow-dirty", action="store_true")
    run_parser.add_argument("--require-origin-sync", dest="require_origin_sync", action="store_true", default=True)
    run_parser.add_argument("--no-require-origin-sync", dest="require_origin_sync", action="store_false")
    run_parser.add_argument("--fail-on-blocked", action="store_true")
    run_parser.add_argument("--json", action="store_true")

    validate_parser = subparsers.add_parser("validate-report", help="Validate a release-check JSON report.")
    validate_parser.add_argument("--report", required=True)
    validate_parser.add_argument("--json", action="store_true")

    status_parser = subparsers.add_parser("status", help="Print a concise release-check report summary.")
    status_parser.add_argument("--report", required=True)
    status_parser.add_argument("--json", action="store_true")

    args = parser.parse_args(argv)
    if args.command == "run":
        report = run_release_checks(
            bundle=args.bundle,
            corpus_gate_closeout=args.corpus_gate_closeout,
            rehearsal_report=args.rehearsal_report,
            external_staging_report=args.external_staging_report,
            local_machine_staging_report=args.local_machine_staging_report or None,
            local_machine_public_exposure_report=args.local_machine_public_exposure_report or None,
            launch_gate_report=args.launch_gate_report,
            out_dir=args.out,
            full_discovery_report=args.full_discovery_report or None,
            release_promotion_report=args.release_promotion_report or None,
            run_tests=args.run_tests,
            allow_dirty=args.allow_dirty,
            require_origin_sync=args.require_origin_sync,
        )
        report_path = Path(args.out) / REPORT_JSON
        if args.json:
            print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=True), file=stdout)
        else:
            print(f"Public alpha release-check report: {report_path}", file=stdout)
            print(f"status: {report.get('status')}", file=stdout)
            print(f"release_status: {report.get('release_status')}", file=stdout)
            print(f"blockers: {len(report.get('blockers') or [])}", file=stdout)
            print(f"next_recommended_task: {report.get('next_recommended_task')}", file=stdout)
        if report.get("status") == "FAIL":
            for blocker in report.get("blockers") or []:
                if isinstance(blocker, dict) and blocker.get("status") == "failed":
                    print(f"- {blocker.get('id')}: {blocker.get('message')}", file=stderr)
            return 1
        if args.fail_on_blocked and report.get("release_status") != "ready":
            print("public alpha release remains blocked", file=stderr)
            return 1
        return 0

    if args.command == "validate-report":
        errors = validate_release_check_report(args.report)
        payload = {
            "schema_version": "eureka.public_alpha_release_check_validate_report.v0",
            "status": "pass" if not errors else "fail",
            "report": str(args.report),
            "errors": errors,
        }
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True), file=stdout)
        elif errors:
            print(f"Public alpha release-check report validation failed: {args.report}", file=stderr)
            for error in errors:
                print(f"- {error}", file=stderr)
        else:
            print(f"Public alpha release-check report validation passed: {args.report}", file=stdout)
        return 0 if not errors else 1

    if args.command == "status":
        try:
            report = _load_release_json(args.report)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"Could not read release-check report: {type(exc).__name__}", file=stderr)
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
