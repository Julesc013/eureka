#!/usr/bin/env python3
"""Run deterministic local auto-test suites against a loopback service."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local.eval import LocalEvalRunner, build_markdown_summary, validate_localhost_base_url
from runtime.local.eval.reports import dumps_report


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output")
    parser.add_argument("--summary-output")
    args = parser.parse_args(argv)
    try:
        base_url = validate_localhost_base_url(args.base_url)
        report = LocalEvalRunner().run_all(base_url)
    except Exception as exc:
        report = fail_report("auto_test_failed", str(exc), args.base_url)
        emit_report(report, args.json, args.output, args.summary_output, stdout)
        print(f"ERROR: {exc}", file=stderr)
        return 2
    emit_report(report, args.json, args.output, args.summary_output, stdout)
    return 0 if report.get("status") == "pass" else 1


def fail_report(code: str, message: str, base_url: str) -> dict[str, Any]:
    return {
        "schema_version": "local_eval_report.v0",
        "status": "fail",
        "error": code,
        "message": message,
        "base_url": base_url,
        "suite_count": 0,
        "case_count": 0,
        "passed_case_count": 0,
        "failed_case_count": 0,
        "suite_results": [],
        "latency": {"schema_version": "local_eval_latency_summary.v0", "status": "fail", "route_count": 0},
        "external_network_used": False,
        "source_probe_executed": False,
        "extraction_executed": False,
        "model_provider_used": False,
        "download_install_execute_performed": False,
        "site_dist_mutated": False,
        "master_index_mutated": False,
        "lan_enabled": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
        "warnings": [],
        "limitations": ["auto-test failed before completing suites"],
    }


def emit_report(
    report: dict[str, Any],
    as_json: bool,
    output: str | None,
    summary_output: str | None,
    stdout: TextIO,
) -> None:
    if output:
        write_text(Path(output), dumps_report(report))
    if summary_output:
        write_text(Path(summary_output), build_markdown_summary(report))
    if as_json:
        print(json.dumps(report, indent=2, sort_keys=True), file=stdout)
        return
    print(f"status: {report.get('status')}", file=stdout)
    print(f"cases: {report.get('passed_case_count')}/{report.get('case_count')} passed", file=stdout)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
