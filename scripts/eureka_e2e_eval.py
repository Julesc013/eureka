#!/usr/bin/env python
"""Run the deterministic E2E reference evaluation oracle."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from evals.e2e_reference.oracle import (  # noqa: E402
    OracleError,
    compare_oracle_results,
    explain_case,
    list_cases,
    run_oracle,
    status_for_run,
    validate_oracle_run,
)


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "list":
            return _emit(list_cases(), json_output=args.json)
        if args.command == "explain":
            return _emit(explain_case(args.case), json_output=args.json)
        if args.command == "run":
            payload = run_oracle(
                suite_id=args.suite,
                case_id=args.case,
                out_root=args.out,
                fail_on_advisory=args.fail_on_advisory,
            )
            code = _status_code(payload.get("overall_gate_status"), fail_on_advisory=args.fail_on_advisory)
            return _emit(payload, json_output=args.json, exit_code=code)
        if args.command == "validate":
            payload = validate_oracle_run(args.run_dir, strict=args.strict)
            return _emit(payload, json_output=args.json, exit_code=0 if payload["status"] == "pass" else 2)
        if args.command == "status":
            return _emit(status_for_run(args.run_dir), json_output=args.json)
        if args.command == "compare":
            return _emit(compare_oracle_results(args.left, args.right), json_output=args.json)
    except OracleError as exc:
        payload = {
            "schema_version": "eureka.e2e_eval_cli_error.v0",
            "status": "error",
            "error": str(exc),
        }
        _emit(payload, json_output=True, stream=sys.stderr)
        return 2
    parser.error(f"unsupported command: {args.command}")
    return 2


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    list_parser = sub.add_parser("list", help="List oracle suites and cases")
    list_parser.add_argument("--json", action="store_true", help="Emit JSON")

    explain = sub.add_parser("explain", help="Explain one oracle case")
    explain.add_argument("--case", required=True)
    explain.add_argument("--json", action="store_true", help="Emit JSON")

    run = sub.add_parser("run", help="Run an oracle suite or case")
    group = run.add_mutually_exclusive_group(required=True)
    group.add_argument("--suite")
    group.add_argument("--case")
    run.add_argument("--out", default=".eureka/e2e-reference/eval")
    run.add_argument("--json", action="store_true", help="Emit JSON")
    run.add_argument("--fail-on-advisory", action="store_true")

    validate = sub.add_parser("validate", help="Validate a generated oracle run")
    validate.add_argument("--run-dir", required=True)
    validate.add_argument("--strict", action="store_true")
    validate.add_argument("--json", action="store_true", help="Emit JSON")

    status = sub.add_parser("status", help="Summarize a generated oracle run")
    status.add_argument("--run-dir", required=True)
    status.add_argument("--json", action="store_true", help="Emit JSON")

    compare = sub.add_parser("compare", help="Compare two oracle summaries or runs")
    compare.add_argument("--left", required=True)
    compare.add_argument("--right", required=True)
    compare.add_argument("--json", action="store_true", help="Emit JSON")
    return parser


def _status_code(status: Any, *, fail_on_advisory: bool) -> int:
    if status == "PASS":
        return 0
    if status == "PASS_WITH_WARNINGS":
        return 1 if fail_on_advisory else 0
    if status == "FAIL":
        return 1
    return 2


def _emit(payload: dict[str, Any], *, json_output: bool, exit_code: int = 0, stream: Any = sys.stdout) -> int:
    if json_output:
        print(json.dumps(payload, indent=2, sort_keys=True), file=stream)
    else:
        print(_text_summary(payload), file=stream)
    return exit_code


def _text_summary(payload: dict[str, Any]) -> str:
    if "overall_gate_status" in payload:
        return "\n".join(
            [
                f"status: {payload['overall_gate_status']}",
                f"execution_id: {payload.get('execution_id', '')}",
                f"cases: {payload.get('case_count', 0)}",
                f"critical_failures: {payload.get('critical_failures', 0)}",
                f"required_failures: {payload.get('required_failures', 0)}",
                f"advisory_warnings: {payload.get('advisory_warnings', 0)}",
            ]
        )
    if "case_count" in payload and "suite_count" in payload:
        return f"cases: {payload['case_count']}\nsuites: {payload['suite_count']}"
    return json.dumps(payload, indent=2, sort_keys=True)


if __name__ == "__main__":
    raise SystemExit(main())
