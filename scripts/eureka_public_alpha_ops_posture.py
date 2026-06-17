#!/usr/bin/env python3
"""Generate and validate the read-only public-alpha ops posture."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local.public_alpha_ops_posture import AUTH_POSTURES
from runtime.local.public_alpha_ops_posture import DEFAULT_OUT
from runtime.local.public_alpha_ops_posture import DEFAULT_REPORT_CHANNEL
from runtime.local.public_alpha_ops_posture import DEFAULT_TAKEDOWN_CHANNEL
from runtime.local.public_alpha_ops_posture import EXPOSURE_MODES
from runtime.local.public_alpha_ops_posture import PLAN_JSON
from runtime.local.public_alpha_ops_posture import REPORT_MD
from runtime.local.public_alpha_ops_posture import build_default_plan
from runtime.local.public_alpha_ops_posture import load_json
from runtime.local.public_alpha_ops_posture import render_markdown_report
from runtime.local.public_alpha_ops_posture import render_status
from runtime.local.public_alpha_ops_posture import status_summary
from runtime.local.public_alpha_ops_posture import validate_ops_posture
from runtime.local.public_alpha_ops_posture import write_plan


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    plan_parser = subparsers.add_parser("plan", help="Write ops_posture.json and OPS_POSTURE_REPORT.md.")
    plan_parser.add_argument("--out", default=DEFAULT_OUT)
    plan_parser.add_argument("--operator", default="")
    plan_parser.add_argument("--public-url", default="")
    plan_parser.add_argument("--exposure-mode", choices=EXPOSURE_MODES, default="loopback_only")
    plan_parser.add_argument("--auth-posture", choices=AUTH_POSTURES, default="public_no_auth")
    plan_parser.add_argument("--report-issue-channel", default=DEFAULT_REPORT_CHANNEL)
    plan_parser.add_argument("--takedown-channel", default=DEFAULT_TAKEDOWN_CHANNEL)
    plan_parser.add_argument("--bind-host", default="127.0.0.1")
    plan_parser.add_argument("--bind-port", type=int, default=8765)
    plan_parser.add_argument("--allow-public-exposure-plan", action="store_true")
    plan_parser.add_argument("--json", action="store_true")

    validate_parser = subparsers.add_parser("validate", help="Validate an ops posture plan.")
    validate_parser.add_argument("--plan", required=True)
    validate_parser.add_argument("--json", action="store_true")
    validate_parser.add_argument("--strict", action="store_true")

    status_parser = subparsers.add_parser("status", help="Print a concise ops posture status.")
    status_parser.add_argument("--plan", required=True)
    status_parser.add_argument("--json", action="store_true")

    report_parser = subparsers.add_parser("report", help="Render the Markdown ops posture report.")
    report_parser.add_argument("--plan", required=True)
    report_parser.add_argument("--out", default="")
    report_parser.add_argument("--json", action="store_true")

    args = parser.parse_args(argv)
    if args.command == "plan":
        plan = build_default_plan(
            operator=args.operator,
            public_url=args.public_url,
            exposure_mode=args.exposure_mode,
            auth_posture=args.auth_posture,
            report_issue_channel=args.report_issue_channel,
            takedown_channel=args.takedown_channel,
            bind_host=args.bind_host,
            bind_port=args.bind_port,
            allow_public_exposure_plan=args.allow_public_exposure_plan,
        )
        plan_path = write_plan(plan, args.out)
        if args.json:
            print(json.dumps(plan, indent=2, sort_keys=True, ensure_ascii=True), file=stdout)
        else:
            print(f"Public-alpha ops posture plan: {plan_path}", file=stdout)
            print(f"status: {plan.get('status')}", file=stdout)
            print(f"public_read_only: {str(plan.get('public_read_only')).lower()}", file=stdout)
            print(f"public_exposure_enabled: {str(plan.get('public_exposure_enabled')).lower()}", file=stdout)
            print(f"blockers: {len(plan.get('blockers') or [])}", file=stdout)
            print(f"next_recommended_task: {plan.get('next_recommended_task')}", file=stdout)
            print(f"report: {Path(args.out) / REPORT_MD}", file=stdout)
        return 0

    if args.command == "validate":
        try:
            plan = load_json(args.plan)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"Could not read ops posture plan: {type(exc).__name__}", file=stderr)
            return 1
        validation = validate_ops_posture(plan)
        strict_blocked = args.strict and bool(validation.get("ops_blockers"))
        if args.json:
            print(json.dumps(validation, indent=2, sort_keys=True, ensure_ascii=True), file=stdout)
        elif validation.get("errors"):
            print(f"Public-alpha ops posture validation failed: {args.plan}", file=stderr)
            for error in validation.get("errors") or []:
                print(f"- {error}", file=stderr)
        else:
            print(f"Public-alpha ops posture validation passed: {args.plan}", file=stdout)
            print(f"status: {validation.get('plan_status')}", file=stdout)
            print(f"ops_blockers: {len(validation.get('ops_blockers') or [])}", file=stdout)
            print(f"launch_blockers: {len(validation.get('launch_blockers') or [])}", file=stdout)
            print(f"next_recommended_task: {validation.get('next_recommended_task')}", file=stdout)
            if strict_blocked:
                print("strict validation found unresolved ops blockers", file=stderr)
        return 1 if validation.get("errors") or strict_blocked else 0

    if args.command == "status":
        try:
            summary = status_summary(args.plan)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"Could not read ops posture plan: {type(exc).__name__}", file=stderr)
            return 1
        if args.json:
            print(json.dumps(summary, indent=2, sort_keys=True, ensure_ascii=True), file=stdout)
        else:
            print(render_status(summary), end="", file=stdout)
        return 0

    if args.command == "report":
        try:
            plan = load_json(args.plan)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"Could not read ops posture plan: {type(exc).__name__}", file=stderr)
            return 1
        markdown = render_markdown_report(plan)
        if args.json:
            print(json.dumps({"report": markdown}, indent=2, sort_keys=True, ensure_ascii=True), file=stdout)
        elif args.out:
            output = Path(args.out)
            output.mkdir(parents=True, exist_ok=True)
            path = output / REPORT_MD
            path.write_text(markdown, encoding="utf-8")
            print(f"Public-alpha ops posture report: {path}", file=stdout)
        else:
            print(markdown, end="", file=stdout)
        return 0

    parser.error(f"unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
