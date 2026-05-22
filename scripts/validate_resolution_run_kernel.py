#!/usr/bin/env python3
"""Validate the headless resolution-run kernel foundation."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from runtime.resolution_run import BLOCKED_ACTIONS, run_resolution_dry_run


REQUIRED_FILES = (
    "contracts/resolution_run/README.md",
    "contracts/resolution_run/resolution_run.v0.json",
    "contracts/resolution_run/run_event.v0.json",
    "contracts/resolution_run/run_command.v0.json",
    "contracts/resolution_run/run_lane_snapshot.v0.json",
    "contracts/resolution_run/run_coverage_report.v0.json",
    "control/policies/resolution_run_policy.json",
    "control/policies/resolution_run_non_claim_policy.json",
    "control/inventory/resolution_run_contract_matrix.json",
    "control/inventory/resolution_run_port_matrix.json",
    "control/inventory/resolution_run_result.json",
    "runtime/resolution_run/run_kernel.py",
    "scripts/eureka_resolution_run.py",
    "docs/architecture/RESOLUTION_RUN_KERNEL.md",
    "docs/operations/RESOLUTION_RUN_KERNEL_RUNBOOK.md",
    "examples/resolution_run/sample_resolution_run.json",
)
BOUNDARY_KEYS = (
    "source_probe_executed",
    "live_ia_call_performed",
    "download_performed",
    "upload_performed",
    "extraction_executed",
    "model_provider_used",
    "source_cache_write_performed",
    "evidence_write_performed",
    "candidate_index_mutated",
    "review_queue_mutated",
    "reviewed_index_mutated",
    "operator_instance_mutated",
    "master_index_mutated",
    "deployment_performed",
    "production_readiness_claimed",
    "public_launch_readiness_claimed",
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    result = validate_repo(Path(args.repo_root).resolve())
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print("Resolution run kernel validation", file=stdout)
        print(f"status: {result['status']}", file=stdout)
        print(f"error_count: {len(result['errors'])}", file=stdout)
        for error in result["errors"]:
            print(f"ERROR: {error}", file=stdout)
    return 0 if result["status"] == "valid" else 1


def validate_repo(root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    for rel in REQUIRED_FILES:
        path = root / rel
        if not path.is_file():
            errors.append(f"missing required file: {rel}")
        elif not path.read_text(encoding="utf-8").strip():
            errors.append(f"empty required file: {rel}")
    policy = load_json(root / "control/policies/resolution_run_policy.json", errors)
    for key in (
        "live_source_calls_enabled",
        "live_ia_calls_enabled",
        "source_probe_enabled",
        "downloads_enabled",
        "uploads_enabled",
        "extraction_enabled",
        "execution_enabled",
        "model_provider_enabled",
        "reviewed_record_creation_enabled",
        "source_cache_write_enabled",
        "evidence_write_enabled",
        "candidate_index_write_enabled",
        "review_queue_write_enabled",
        "reviewed_index_write_enabled",
        "master_index_mutation_enabled",
        "operator_instance_mutation_enabled",
        "public_fanout_enabled",
        "deployment_enabled",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    ):
        if policy.get(key) is not False:
            errors.append(f"policy must set {key}=false")
    result = run_resolution_dry_run("sampleproject", projection_profile="operator_workbench")
    validate_kernel_result(result, errors)
    validate_cli(root, errors)
    inventory = load_json(root / "control/inventory/resolution_run_result.json", errors)
    for key in (
        "contracts_added",
        "runtime_kernel_added",
        "event_log_added",
        "command_bus_added",
        "lane_projector_added",
        "workunit_scheduler_added",
        "validator_added",
        "tests_added",
        "docs_added",
        "dry_run_passed",
        "ia_hunt_dry_run_workunits_planned",
        "lane_snapshot_passed",
    ):
        if inventory.get(key) is not True:
            errors.append(f"resolution run result must set {key}=true")
    return {
        "schema_version": "resolution_run_kernel_validation.v0",
        "task": "AIDE-BATCH-RUN-KERNEL-01",
        "status": "valid" if not errors else "invalid",
        "errors": errors,
        "dry_run_passed": not errors,
        "workunit_count": result.get("workunit_schedule", {}).get("workunit_count", 0),
        "lane_count": result.get("lane_snapshot", {}).get("lane_count", 0),
        "blocked_actions": list(BLOCKED_ACTIONS),
        "source_probe_executed": False,
        "live_ia_call_performed": False,
        "model_provider_used": False,
        "deployment_performed": False,
    }


def validate_kernel_result(result: Mapping[str, Any], errors: list[str]) -> None:
    if result.get("schema_version") != "resolution_run_kernel_result.v0":
        errors.append("kernel result schema mismatch")
    if result.get("run", {}).get("state") != "completed":
        errors.append("dry-run run must complete")
    if result.get("workunit_schedule", {}).get("workunit_count", 0) < 1:
        errors.append("dry-run must plan IA-Hunt WorkUnits")
    if result.get("lane_snapshot", {}).get("lane_count", 0) < 1:
        errors.append("dry-run must produce lane snapshot")
    boundaries = result.get("boundaries", {})
    for key in BOUNDARY_KEYS:
        if boundaries.get(key) is not False:
            errors.append(f"boundary {key} must be false")


def validate_cli(root: Path, errors: list[str]) -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/eureka_resolution_run.py",
            "--query",
            "sampleproject",
            "--projection",
            "operator_workbench",
            "--json",
        ],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        errors.append(f"resolution run CLI failed: {completed.stderr or completed.stdout}")
        return
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        errors.append(f"resolution run CLI emitted invalid JSON: {exc}")
        return
    if payload.get("run", {}).get("state") != "completed":
        errors.append("resolution run CLI must complete dry-run")


def load_json(path: Path, errors: list[str]) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"missing JSON file: {path.relative_to(REPO_ROOT).as_posix()}")
        return {}
    except json.JSONDecodeError as exc:
        errors.append(f"invalid JSON {path.relative_to(REPO_ROOT).as_posix()}: {exc}")
        return {}
    return payload if isinstance(payload, dict) else {}


if __name__ == "__main__":
    raise SystemExit(main())
