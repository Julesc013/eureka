#!/usr/bin/env python3
"""Build a combined clean-machine bootstrap proof summary."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence, TextIO


TASK_ID = "LOCAL-13"


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bootstrap-result", required=True)
    parser.add_argument("--smoke-result", required=True)
    parser.add_argument("--output")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    try:
        bootstrap = load_json(Path(args.bootstrap_result))
        smoke = load_json(Path(args.smoke_result))
        result = build_report(bootstrap, smoke)
    except Exception as exc:  # pragma: no cover - defensive CLI boundary
        result = fail_result(str(exc))
        print(f"ERROR: {exc}", file=stderr)
    if args.output:
        write_output(Path(args.output), result)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print(f"status: {result['status']}", file=stdout)
    return 0 if result.get("status") in {"pass", "pass_with_warnings"} else 1


def build_report(bootstrap: dict[str, Any], smoke: dict[str, Any]) -> dict[str, Any]:
    bootstrap_ok = bootstrap.get("status") in {"pass", "pass_with_warnings"}
    smoke_ok = smoke.get("status") in {"pass", "pass_with_warnings"}
    external_status = "not_performed"
    warnings = ["actual second-machine proof was not performed"]
    return {
        "schema_version": "local_clean_machine_validation_result.v0",
        "task": TASK_ID,
        "status": "pass_with_warnings" if bootstrap_ok and smoke_ok else "fail",
        "temp_checkout_created": bootstrap.get("temp_checkout_created") is True,
        "instance_initialized": bootstrap.get("instance_initialized") is True,
        "instance_validated": bootstrap.get("instance_validated") is True,
        "runtime_status_passed": bootstrap.get("runtime_status_passed") is True and smoke.get("runtime_status_passed") is True,
        "localhost_server_started": smoke.get("localhost_server_started") is True,
        "service_smoke_passed": smoke.get("service_smoke_passed") is True,
        "workbench_smoke_passed": smoke.get("workbench_smoke_passed") is True,
        "auto_test_passed": smoke.get("auto_test_passed") is True,
        "auto_search_passed": smoke.get("auto_search_passed") is True,
        "server_shutdown_clean": smoke.get("server_shutdown_clean") is True,
        "instance_valid_after_shutdown": smoke.get("instance_valid_after_shutdown") is True,
        "actual_second_machine_proof_performed": False,
        "actual_second_machine_proof_status": external_status,
        "hidden_state_copied": bootstrap.get("hidden_state_copied") is True,
        "committed_instance_state_found": bool(bootstrap.get("committed_instance_state_found") or smoke.get("committed_instance_state_found")),
        "master_index_mutated": smoke.get("master_index_mutated") is True,
        "site_dist_mutated": smoke.get("site_dist_mutated") is True,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
        "warnings": warnings,
        "limitations": [
            "clean-machine proof is local reproducibility evidence",
            "actual second-machine proof is optional and not claimed",
        ],
    }


def build_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# LOCAL-13 Clean-Machine Bootstrap Summary",
        "",
        f"Status: {report.get('status')}",
        "",
        "- Temp checkout created: " + str(report.get("temp_checkout_created")).lower(),
        "- Instance initialized: " + str(report.get("instance_initialized")).lower(),
        "- Instance validated: " + str(report.get("instance_validated")).lower(),
        "- Runtime status passed: " + str(report.get("runtime_status_passed")).lower(),
        "- Service smoke passed: " + str(report.get("service_smoke_passed")).lower(),
        "- Workbench smoke passed: " + str(report.get("workbench_smoke_passed")).lower(),
        "- Auto-test passed: " + str(report.get("auto_test_passed")).lower(),
        "- Auto-search passed: " + str(report.get("auto_search_passed")).lower(),
        "- Server shutdown clean: " + str(report.get("server_shutdown_clean")).lower(),
        "- Actual second-machine proof performed: false",
        "",
        "This is local reproducibility evidence only. It is not deployment, production readiness, or public launch readiness.",
        "",
    ]
    return "\n".join(lines)


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"JSON file must contain an object: {path}")
    return payload


def write_output(path: Path, result: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix.lower() == ".json":
        path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    else:
        path.write_text(build_markdown(result), encoding="utf-8")


def fail_result(message: str) -> dict[str, Any]:
    return {
        "schema_version": "local_clean_machine_validation_result.v0",
        "task": TASK_ID,
        "status": "fail",
        "message": message,
        "actual_second_machine_proof_performed": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


if __name__ == "__main__":
    raise SystemExit(main())
