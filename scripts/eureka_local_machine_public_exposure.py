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
from runtime.local.local_machine_public_exposure import DEFAULT_OPERATOR_CHOICE_OUT
from runtime.local.local_machine_public_exposure import DEFAULT_TUNNEL_OUT
from runtime.local.local_machine_public_exposure import EXPOSURE_MODES
from runtime.local.local_machine_public_exposure import OPS_POSTURES
from runtime.local.local_machine_public_exposure import OPERATOR_CHOICE_JSON
from runtime.local.local_machine_public_exposure import PROVIDER_CLASSES
from runtime.local.local_machine_public_exposure import PLAN_JSON
from runtime.local.local_machine_public_exposure import REPORT_JSON
from runtime.local.local_machine_public_exposure import TLS_STATUSES
from runtime.local.local_machine_public_exposure import TUNNEL_PLAN_JSON
from runtime.local.local_machine_public_exposure import build_operator_choice
from runtime.local.local_machine_public_exposure import build_plan
from runtime.local.local_machine_public_exposure import build_report
from runtime.local.local_machine_public_exposure import build_tunnel_plan
from runtime.local.local_machine_public_exposure import load_json
from runtime.local.local_machine_public_exposure import render_operator_choice_markdown_report
from runtime.local.local_machine_public_exposure import render_operator_choice_status
from runtime.local.local_machine_public_exposure import render_plan_status
from runtime.local.local_machine_public_exposure import render_tunnel_markdown_report
from runtime.local.local_machine_public_exposure import render_tunnel_plan_status
from runtime.local.local_machine_public_exposure import validate_operator_choice
from runtime.local.local_machine_public_exposure import validate_plan
from runtime.local.local_machine_public_exposure import validate_report
from runtime.local.local_machine_public_exposure import validate_tunnel_plan
from runtime.local.local_machine_public_exposure import write_operator_choice
from runtime.local.local_machine_public_exposure import write_plan
from runtime.local.local_machine_public_exposure import write_report
from runtime.local.local_machine_public_exposure import write_tunnel_plan


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    plan_parser = subparsers.add_parser("plan", help="Write a local-machine public exposure plan.")
    plan_parser.add_argument("--local-machine-staging-report", default="")
    plan_parser.add_argument("--release-check-report", default="")
    plan_parser.add_argument("--launch-gate-report", default="")
    plan_parser.add_argument("--out", default="")
    plan_parser.add_argument("--mode", "--exposure-mode", dest="mode", choices=EXPOSURE_MODES, default=None)
    plan_parser.add_argument("--public-base-url", default="")
    plan_parser.add_argument("--public-url", default="")
    plan_parser.add_argument("--bind-host", default="127.0.0.1")
    plan_parser.add_argument("--bind-port", type=int, default=8765)
    plan_parser.add_argument("--operator", default="")
    plan_parser.add_argument("--approve-risky-mode", action="store_true")
    plan_parser.add_argument("--staging-bundle", default=".eureka/staging/public-alpha")
    plan_parser.add_argument("--domain", default="")
    plan_parser.add_argument("--tls-status", choices=TLS_STATUSES, default="missing")
    plan_parser.add_argument("--production-auth-posture", choices=AUTH_POSTURES, default="missing")
    plan_parser.add_argument("--rate-limit-posture", choices=OPS_POSTURES, default="missing")
    plan_parser.add_argument("--ops-posture", default="")
    plan_parser.add_argument("--operator-approval-file", default="")
    plan_parser.add_argument("--allow-public-exposure-plan", action="store_true")
    plan_parser.add_argument("--json", action="store_true")

    validate_parser = subparsers.add_parser("validate", help="Validate a public tunnel exposure plan.")
    validate_parser.add_argument("--plan", required=True)
    validate_parser.add_argument("--json", action="store_true")
    validate_parser.add_argument("--strict", action="store_true")

    choose_parser = subparsers.add_parser("choose", help="Write an operator-choice artifact for future tunnel rehearsal.")
    choose_parser.add_argument("--plan", required=True)
    choose_parser.add_argument("--ops-posture", required=True)
    choose_parser.add_argument("--mode", choices=EXPOSURE_MODES, default="reverse_tunnel")
    choose_parser.add_argument("--provider-class", choices=PROVIDER_CLASSES, default="provider_managed_https_tunnel")
    choose_parser.add_argument("--provider-name", default="OPERATOR_REQUIRED")
    choose_parser.add_argument("--provider-url", default="")
    choose_parser.add_argument("--public-url", default="OPERATOR_REQUIRED")
    choose_parser.add_argument("--local-bind-host", default="")
    choose_parser.add_argument("--local-bind-port", type=int, default=0)
    choose_parser.add_argument("--staging-bundle", default="")
    choose_parser.add_argument("--staged-record-id", default="")
    choose_parser.add_argument("--operator", default="")
    choose_parser.add_argument("--approve-risky-mode", action="store_true")
    choose_parser.add_argument("--confirm-remote-synced", action="store_true")
    choose_parser.add_argument("--out", default=DEFAULT_OPERATOR_CHOICE_OUT)
    choose_parser.add_argument("--json", action="store_true")

    validate_choice_parser = subparsers.add_parser("validate-choice", help="Validate an operator-choice artifact.")
    validate_choice_parser.add_argument("--choice", required=True)
    validate_choice_parser.add_argument("--json", action="store_true")
    validate_choice_parser.add_argument("--strict", action="store_true")

    choice_status_parser = subparsers.add_parser("choice-status", help="Print operator-choice status.")
    choice_status_parser.add_argument("--choice", required=True)
    choice_status_parser.add_argument("--json", action="store_true")

    choice_report_parser = subparsers.add_parser("choice-report", help="Render an operator-choice report.")
    choice_report_parser.add_argument("--choice", required=True)
    choice_report_parser.add_argument("--out", default="")
    choice_report_parser.add_argument("--json", action="store_true")

    validate_plan_parser = subparsers.add_parser("validate-plan", help="Validate a local-machine public exposure plan.")
    validate_plan_parser.add_argument("--plan", required=True)
    validate_plan_parser.add_argument("--json", action="store_true")

    status_parser = subparsers.add_parser("status", help="Print a concise public exposure plan summary.")
    status_parser.add_argument("--plan", required=True)
    status_parser.add_argument("--json", action="store_true")

    report_parser = subparsers.add_parser("report", help="Write a public exposure report from a plan.")
    report_parser.add_argument("--plan", required=True)
    report_parser.add_argument("--out", default="")
    report_parser.add_argument("--json", action="store_true")

    validate_report_parser = subparsers.add_parser("validate-report", help="Validate a public exposure report.")
    validate_report_parser.add_argument("--report", required=True)
    validate_report_parser.add_argument("--json", action="store_true")

    args = parser.parse_args(argv)
    if args.command == "plan":
        legacy_mode = bool(args.local_machine_staging_report or args.release_check_report or args.launch_gate_report)
        if legacy_mode:
            missing = [
                name
                for name, value in (
                    ("--local-machine-staging-report", args.local_machine_staging_report),
                    ("--release-check-report", args.release_check_report),
                    ("--launch-gate-report", args.launch_gate_report),
                )
                if not value
            ]
            if missing:
                print(f"legacy exposure plan mode missing required args: {', '.join(missing)}", file=stderr)
                return 2
            out_dir = args.out or DEFAULT_OUT
            plan = build_plan(
                local_machine_staging_report=args.local_machine_staging_report,
                release_check_report=args.release_check_report,
                launch_gate_report=args.launch_gate_report,
                out_dir=out_dir,
                exposure_mode=args.mode or "loopback_only",
                public_base_url=args.public_base_url or args.public_url,
                domain=args.domain,
                tls_status=args.tls_status,
                production_auth_posture=args.production_auth_posture,
                rate_limit_posture=args.rate_limit_posture,
                ops_posture=args.ops_posture or None,
                operator_approval_file=args.operator_approval_file or None,
                allow_public_exposure_plan=args.allow_public_exposure_plan,
            )
            plan_path = write_plan(plan, out_dir)
        else:
            out_dir = args.out or DEFAULT_TUNNEL_OUT
            plan = build_tunnel_plan(
                ops_posture=args.ops_posture or None,
                out_dir=out_dir,
                exposure_mode=args.mode or "reverse_tunnel",
                public_url=args.public_url or args.public_base_url,
                bind_host=args.bind_host,
                bind_port=args.bind_port,
                operator=args.operator,
                approve_risky_mode=args.approve_risky_mode,
                staging_bundle=args.staging_bundle,
            )
            plan_path = write_tunnel_plan(plan, out_dir)
        if args.json:
            print(json.dumps(plan, indent=2, sort_keys=True, ensure_ascii=True), file=stdout)
        else:
            print(f"Local-machine public exposure plan: {plan_path}", file=stdout)
            print(f"status: {plan.get('status')}", file=stdout)
            print(f"exposure_mode: {plan.get('exposure_mode')}", file=stdout)
            print(f"public_exposure_enabled: {str(plan.get('public_exposure_enabled')).lower()}", file=stdout)
            print(f"blockers: {len(plan.get('blockers') or plan.get('remaining_blockers') or [])}", file=stdout)
            print(f"next_recommended_task: {plan.get('next_recommended_task')}", file=stdout)
        return 0

    if args.command == "validate":
        try:
            plan = load_json(args.plan)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"Could not read public tunnel exposure plan: {type(exc).__name__}", file=stderr)
            return 1
        validation = validate_tunnel_plan(plan)
        strict_blocked = args.strict and validation.get("plan_status") == "BLOCKED"
        if args.json:
            print(json.dumps(validation, indent=2, sort_keys=True, ensure_ascii=True), file=stdout)
        elif validation.get("errors"):
            print(f"Public tunnel exposure plan validation failed: {args.plan}", file=stderr)
            for error in validation.get("errors") or []:
                print(f"- {error}", file=stderr)
        else:
            print(f"Public tunnel exposure plan validation passed: {args.plan}", file=stdout)
            print(f"status: {validation.get('plan_status')}", file=stdout)
            print(f"blockers: {len(validation.get('blockers') or [])}", file=stdout)
            print(f"next_recommended_task: {validation.get('next_recommended_task')}", file=stdout)
            if strict_blocked:
                print("strict validation found blocked tunnel plan", file=stderr)
        return 1 if validation.get("errors") or strict_blocked else 0

    if args.command == "choose":
        choice = build_operator_choice(
            exposure_plan=args.plan,
            ops_posture=args.ops_posture,
            out_dir=args.out,
            selected_exposure_mode=args.mode,
            provider_class=args.provider_class,
            provider_name=args.provider_name,
            provider_url=args.provider_url,
            public_url=args.public_url,
            local_bind_host=args.local_bind_host,
            local_bind_port=args.local_bind_port or None,
            staging_bundle=args.staging_bundle,
            staged_record_id=args.staged_record_id,
            operator=args.operator,
            approve_risky_mode=args.approve_risky_mode,
            confirm_remote_synced=args.confirm_remote_synced,
        )
        choice_path = write_operator_choice(choice, args.out)
        if args.json:
            print(json.dumps(choice, indent=2, sort_keys=True, ensure_ascii=True), file=stdout)
        else:
            print(f"Local-machine public tunnel operator choice: {choice_path}", file=stdout)
            print(f"status: {choice.get('status')}", file=stdout)
            print(f"selected_exposure_mode: {choice.get('selected_exposure_mode')}", file=stdout)
            print(f"provider_class: {choice.get('provider_class')}", file=stdout)
            print(f"provider_name: {choice.get('provider_name')}", file=stdout)
            print(f"public_url_status: {choice.get('public_url_status')}", file=stdout)
            print(f"remote_sync_status: {choice.get('remote_sync_status')}", file=stdout)
            print(f"public_exposure_enabled: {str(choice.get('public_exposure_enabled')).lower()}", file=stdout)
            print(f"blockers: {len(choice.get('blockers') or [])}", file=stdout)
            print(f"next_recommended_task: {choice.get('recommended_next_task')}", file=stdout)
        return 0

    if args.command == "validate-choice":
        try:
            choice = load_json(args.choice)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"Could not read operator choice: {type(exc).__name__}", file=stderr)
            return 1
        validation = validate_operator_choice(choice)
        if args.json:
            print(json.dumps(validation, indent=2, sort_keys=True, ensure_ascii=True), file=stdout)
        elif validation.get("errors"):
            print(f"Operator choice validation failed: {args.choice}", file=stderr)
            for error in validation.get("errors") or []:
                print(f"- {error}", file=stderr)
        else:
            print(f"Operator choice validation passed: {args.choice}", file=stdout)
            print(f"status: {validation.get('choice_status')}", file=stdout)
            print(f"blockers: {len(validation.get('blockers') or [])}", file=stdout)
            print(f"next_recommended_task: {validation.get('recommended_next_task')}", file=stdout)
        return 1 if validation.get("errors") else 0

    if args.command == "choice-status":
        try:
            choice = load_json(args.choice)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"Could not read operator choice: {type(exc).__name__}", file=stderr)
            return 1
        if args.json:
            print(json.dumps(choice, indent=2, sort_keys=True, ensure_ascii=True), file=stdout)
        else:
            print(render_operator_choice_status(choice), end="", file=stdout)
        return 0

    if args.command == "choice-report":
        try:
            choice = load_json(args.choice)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"Could not read operator choice: {type(exc).__name__}", file=stderr)
            return 1
        markdown = render_operator_choice_markdown_report(choice)
        if args.json:
            print(json.dumps({"report": markdown}, indent=2, sort_keys=True, ensure_ascii=True), file=stdout)
        elif args.out:
            output = Path(args.out)
            output.mkdir(parents=True, exist_ok=True)
            path = output / "OPERATOR_CHOICE_REPORT.md"
            path.write_text(markdown, encoding="utf-8")
            print(f"Operator choice report: {path}", file=stdout)
        else:
            print(markdown, end="", file=stdout)
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
        elif plan.get("schema_version") == "eureka.local_machine_public_tunnel_plan.v0":
            print(render_tunnel_plan_status(plan), end="", file=stdout)
        else:
            print(render_plan_status(plan), end="", file=stdout)
        return 0

    if args.command == "report":
        plan = load_json(args.plan)
        if plan.get("schema_version") == "eureka.local_machine_public_tunnel_plan.v0":
            report = plan
            out_dir = args.out or str(Path(args.plan).parent)
            output = Path(out_dir)
            output.mkdir(parents=True, exist_ok=True)
            report_path = output / "EXPOSURE_PLAN_REPORT.md"
            report_path.write_text(render_tunnel_markdown_report(plan), encoding="utf-8")
        else:
            out_dir = args.out or DEFAULT_OUT
            report = build_report(args.plan)
            report_path = write_report(report, out_dir)
        if args.json:
            print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=True), file=stdout)
        else:
            print(f"Local-machine public exposure report: {report_path}", file=stdout)
            print(f"status: {report.get('status')}", file=stdout)
            if report.get("schema_version") == "eureka.local_machine_public_tunnel_plan.v0":
                print(f"public_url_status: {report.get('public_url_status')}", file=stdout)
                print(f"provider_https_status: {report.get('provider_https_status')}", file=stdout)
            else:
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
