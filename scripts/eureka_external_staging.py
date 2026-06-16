#!/usr/bin/env python3
"""Prepare and audit an external staging path for the public-alpha bundle."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local.external_staging_mvp import (
    DEFAULT_OUT,
    LOCAL_CONFIG_EXAMPLE_JSON,
    PLAN_JSON,
    REPORT_JSON,
    config_status,
    create_plan,
    deploy_from_plan,
    init_config_template,
    package_for_transfer,
    read_external_config,
    render_config_status,
    render_status,
    smoke_from_plan,
    validate_plan,
    validate_report,
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_config_parser = subparsers.add_parser("init-config", help="Write a redacted local external staging config template.")
    init_config_parser.add_argument("--out", default=str(Path(DEFAULT_OUT) / LOCAL_CONFIG_EXAMPLE_JSON))
    init_config_parser.add_argument("--json", action="store_true")

    validate_config_parser = subparsers.add_parser("validate-config", help="Validate a local external staging config.")
    validate_config_parser.add_argument("--config", required=True)
    validate_config_parser.add_argument("--json", action="store_true")

    config_status_parser = subparsers.add_parser("config-status", help="Print redacted external staging config status.")
    config_status_parser.add_argument("--config", required=True)
    config_status_parser.add_argument("--json", action="store_true")

    plan_parser = subparsers.add_parser("plan", help="Create an external staging deployment plan.")
    plan_parser.add_argument("--bundle", required=True)
    plan_parser.add_argument("--out", default=DEFAULT_OUT)
    plan_parser.add_argument("--config", default="")
    _add_config_args(plan_parser)
    plan_parser.add_argument("--json", action="store_true")

    validate_plan_parser = subparsers.add_parser("validate-plan", help="Validate an external staging plan.")
    validate_plan_parser.add_argument("--plan", required=True)
    validate_plan_parser.add_argument("--json", action="store_true")

    package_parser = subparsers.add_parser("package", help="Create a transfer package from a staging bundle.")
    package_parser.add_argument("--bundle", required=True)
    package_parser.add_argument("--out", required=True)
    package_parser.add_argument("--plan", default="")
    package_parser.add_argument("--json", action="store_true")

    deploy_parser = subparsers.add_parser("deploy", help="Dry-run or apply the external staging deployment.")
    deploy_parser.add_argument("--plan", required=True)
    mode = deploy_parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    deploy_parser.add_argument("--confirm-apply", action="store_true")
    deploy_parser.add_argument("--json", action="store_true")

    smoke_parser = subparsers.add_parser("smoke", help="Probe external staging routes when a base URL is configured.")
    smoke_parser.add_argument("--plan", required=True)
    smoke_parser.add_argument("--json", action="store_true")

    validate_report_parser = subparsers.add_parser("validate-report", help="Validate an external staging report.")
    validate_report_parser.add_argument("--report", required=True)
    validate_report_parser.add_argument("--json", action="store_true")

    status_parser = subparsers.add_parser("status", help="Print external staging report status.")
    status_parser.add_argument("--report", required=True)
    status_parser.add_argument("--json", action="store_true")

    args = parser.parse_args(argv)
    if args.command == "init-config":
        try:
            payload = init_config_template(args.out)
        except OSError as exc:
            print(f"External staging config template failed: {exc}", file=stderr)
            return 1
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True), file=stdout)
        else:
            print(f"External staging config template: {args.out}", file=stdout)
            print("status: template_written", file=stdout)
        return 0

    if args.command == "validate-config":
        payload = config_status(args.config)
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True), file=stdout)
        elif payload.get("status") == "fail":
            print(f"External staging config validation failed: {args.config}", file=stderr)
            for error in payload.get("errors") or []:
                print(f"- {error}", file=stderr)
        else:
            print(f"External staging config validation status: {args.config}", file=stdout)
            print(render_config_status(payload), end="", file=stdout)
        return 1 if payload.get("status") == "fail" else 0

    if args.command == "config-status":
        payload = config_status(args.config)
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True), file=stdout)
        else:
            print(render_config_status(payload), end="", file=stdout)
        return 1 if payload.get("status") == "fail" else 0

    if args.command == "plan":
        try:
            config = read_external_config(config_path=args.config or None, overrides=_config_overrides(args))
            payload = create_plan(bundle=args.bundle, out_dir=args.out, config=config)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            print(f"External staging plan failed: {exc}", file=stderr)
            return 1
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True), file=stdout)
        else:
            print(f"External staging plan: {Path(args.out) / PLAN_JSON}", file=stdout)
            _print_plan(payload, stdout)
        return 0

    if args.command == "validate-plan":
        errors = validate_plan(args.plan)
        payload = {"schema_version": "eureka.external_staging_validate_plan.v0", "status": "pass" if not errors else "fail", "plan": str(args.plan), "errors": errors}
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True), file=stdout)
        elif errors:
            print(f"External staging plan validation failed: {args.plan}", file=stderr)
            for error in errors:
                print(f"- {error}", file=stderr)
        else:
            print(f"External staging plan validation passed: {args.plan}", file=stdout)
        return 0 if not errors else 1

    if args.command == "package":
        try:
            plan_payload = _load_json(args.plan) if args.plan else {}
            payload = package_for_transfer(bundle=args.bundle, out_dir=args.out, plan=plan_payload)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            print(f"External staging package failed: {exc}", file=stderr)
            return 1
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True), file=stdout)
        else:
            print(f"External staging package: {args.out}", file=stdout)
            print(f"status: {payload.get('status')}", file=stdout)
            print(f"staging_bundle_id: {payload.get('staging_bundle_id')}", file=stdout)
            print(f"leakage_errors: {json.dumps(payload.get('leakage_errors') or [])}", file=stdout)
        return 0 if payload.get("status") == "pass" else 1

    if args.command == "deploy":
        payload = deploy_from_plan(plan=args.plan, apply=bool(args.apply), confirm_apply=bool(args.confirm_apply))
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True), file=stdout)
        else:
            print(f"External staging report: {Path(args.plan).parent / REPORT_JSON}", file=stdout)
            print(render_status(payload), end="", file=stdout)
        if args.apply and payload.get("deployment_status") not in {"deployed", "transfer_complete_manual_start_required"}:
            return 1
        return 0 if payload.get("status") in {"PASS", "PASS_WITH_WARNINGS"} else 1

    if args.command == "smoke":
        payload = smoke_from_plan(plan=args.plan)
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True), file=stdout)
        else:
            print(f"External staging report: {Path(args.plan).parent / REPORT_JSON}", file=stdout)
            print(render_status(payload), end="", file=stdout)
        return 0 if payload.get("status") in {"PASS", "PASS_WITH_WARNINGS"} else 1

    if args.command == "validate-report":
        errors = validate_report(args.report)
        payload = {"schema_version": "eureka.external_staging_validate_report.v0", "status": "pass" if not errors else "fail", "report": str(args.report), "errors": errors}
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True), file=stdout)
        elif errors:
            print(f"External staging report validation failed: {args.report}", file=stderr)
            for error in errors:
                print(f"- {error}", file=stderr)
        else:
            print(f"External staging report validation passed: {args.report}", file=stdout)
        return 0 if not errors else 1

    if args.command == "status":
        try:
            report = _load_json(args.report)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"Could not read external staging report: {type(exc).__name__}", file=stderr)
            return 1
        if args.json:
            print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=True), file=stdout)
        else:
            print(render_status(report), end="", file=stdout)
        return 0

    parser.error(f"unsupported command: {args.command}")
    return 2


def _add_config_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--host", default="")
    parser.add_argument("--user", default="")
    parser.add_argument("--ssh-key", default="")
    parser.add_argument("--ssh-port", default="")
    parser.add_argument("--remote-dir", default="")
    parser.add_argument("--base-url", default="")
    parser.add_argument("--service-port", default="")
    parser.add_argument("--bind-host", default="")
    parser.add_argument("--exposure-approved", action="store_true")


def _config_overrides(args: argparse.Namespace) -> Mapping[str, object]:
    return {
        "host": args.host,
        "user": args.user,
        "ssh_key": args.ssh_key,
        "ssh_port": args.ssh_port,
        "remote_dir": args.remote_dir,
        "base_url": args.base_url,
        "service_port": args.service_port,
        "bind_host": args.bind_host,
        "exposure_approved": "true" if args.exposure_approved else "",
    }


def _print_plan(payload: Mapping[str, object], stdout: TextIO) -> None:
    print(f"staging_bundle_id: {payload.get('staging_bundle_id')}", file=stdout)
    print(f"deployment_mode: {payload.get('deployment_mode')}", file=stdout)
    print(f"host_configured: {str(payload.get('host_configured')).lower()}", file=stdout)
    print(f"base_url_configured: {str(payload.get('base_url_configured')).lower()}", file=stdout)
    print(f"remote_dir_configured: {str(payload.get('remote_dir_configured')).lower()}", file=stdout)
    print(f"bind_host: {payload.get('bind_host')}", file=stdout)
    print(f"service_port: {payload.get('service_port')}", file=stdout)
    print(f"exposure_approved: {str(payload.get('exposure_approved')).lower()}", file=stdout)
    print(f"corpus_gate_status: {payload.get('corpus_gate_status')}", file=stdout)
    print(f"artifact_verified_count: {payload.get('artifact_verified_count')}", file=stdout)


def _load_json(path: str) -> dict[str, object]:
    if not path:
        return {}
    loaded = json.loads(Path(path).read_text(encoding="utf-8"))
    return loaded if isinstance(loaded, dict) else {}


if __name__ == "__main__":
    raise SystemExit(main())
