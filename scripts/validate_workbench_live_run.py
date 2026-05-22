#!/usr/bin/env python3
"""Validate the Workbench live-run projection foundation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Mapping, Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from runtime.local_service.request_context import build_request_context
from runtime.local_service.routes import route_request
from runtime.local_service.workbench_live_run import (
    build_command_response,
    create_workbench_resolution_run,
)


REQUIRED_FILES = (
    "control/policies/workbench_live_run_policy.json",
    "control/policies/workbench_live_run_projection_policy.json",
    "control/policies/workbench_live_run_non_claim_policy.json",
    "control/policies/workbench_live_run_command_policy.json",
    "control/inventory/workbench_live_run_route_matrix.json",
    "control/inventory/workbench_live_run_api_matrix.json",
    "control/inventory/workbench_live_run_projection_matrix.json",
    "control/inventory/workbench_live_run_event_matrix.json",
    "control/inventory/workbench_live_run_command_matrix.json",
    "control/inventory/workbench_live_run_boundary_report.json",
    "control/inventory/workbench_live_run_smoke_result.json",
    "control/inventory/workbench_live_run_validation_matrix.json",
    "control/inventory/workbench_live_run_result.json",
    "runtime/local_service/workbench_live_run.py",
    "scripts/eureka_workbench_live_run.py",
    "docs/architecture/WORKBENCH_LIVE_RUN.md",
    "docs/architecture/WORKBENCH_RUN_PROJECTION.md",
    "docs/operations/WORKBENCH_LIVE_RUN_RUNBOOK.md",
    "docs/operations/POST_WORKBENCH_LIVE_RUN_PLAN.md",
    "docs/reference/WORKBENCH_LIVE_RUN_ROUTES.md",
    "docs/reference/WORKBENCH_LIVE_RUN_API.md",
    "examples/workbench/live_run/sample_workbench_live_run_request.json",
    "examples/workbench/live_run/sample_workbench_live_run_packet.json",
    "examples/workbench/live_run/sample_workbench_live_run_events.json",
    "examples/workbench/live_run/sample_workbench_live_run_lanes.json",
    "examples/workbench/live_run/sample_workbench_live_run_workunits.json",
    "examples/workbench/live_run/sample_workbench_live_run_boundary_report.json",
)
FALSE_POLICY_KEYS = (
    "live_ia_calls_enabled_by_default",
    "source_probes_enabled_by_default",
    "operator_instance_mutation_default",
    "downloads_enabled",
    "extraction_enabled",
    "model_provider_enabled",
    "deployment_enabled",
    "master_index_mutation_enabled",
    "reviewed_index_mutation_enabled_by_live_run",
    "production_readiness_claimed",
    "public_launch_readiness_claimed",
)
FALSE_BOUNDARY_KEYS = (
    "live_ia_call_performed",
    "source_probe_executed",
    "source_cache_write_performed",
    "evidence_write_performed",
    "candidate_index_mutated",
    "reviewed_index_mutated",
    "master_index_mutated",
    "operator_instance_mutated",
    "download_performed",
    "upload_performed",
    "extraction_executed",
    "model_provider_used",
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
        print("Workbench live-run validation", file=stdout)
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
    policy = load_json(root / "control/policies/workbench_live_run_policy.json", errors)
    for key in FALSE_POLICY_KEYS:
        if policy.get(key) is not False:
            errors.append(f"workbench live-run policy must set {key}=false")
    if policy.get("workbench_uses_resolution_run_kernel") is not True:
        errors.append("workbench live-run policy must require the resolution run kernel")
    packet = create_workbench_resolution_run(
        "sampleproject",
        "operator_workbench",
        include_ia_hunt_dry_run=True,
    )
    validate_packet(packet, errors)
    validate_projections(errors)
    validate_cli(root, errors)
    validate_routes(errors)
    result_inventory = load_json(root / "control/inventory/workbench_live_run_result.json", errors)
    for key in (
        "policies_added",
        "route_matrix_added",
        "api_matrix_added",
        "projection_matrix_added",
        "event_matrix_added",
        "command_matrix_added",
        "runtime_projection_added",
        "local_service_projection_added",
        "cli_added",
        "examples_added",
        "docs_added",
        "validator_added",
        "tests_added",
        "run_created_from_query",
        "run_id_emitted",
        "run_events_emitted",
        "lane_snapshot_emitted",
        "workunits_planned",
        "ia_hunt_dry_run_planned",
        "blocked_actions_emitted",
        "operator_projection_passed",
        "public_projection_passed",
        "native_read_only_projection_passed",
    ):
        if result_inventory.get(key) is not True:
            errors.append(f"workbench live-run result must set {key}=true")
    return {
        "schema_version": "workbench_live_run_validation.v0",
        "task": "AIDE-BATCH-WORKBENCH-LIVE-RUN-01",
        "status": "valid" if not errors else "invalid",
        "errors": errors,
        "run_id": packet.get("run_id", ""),
        "lane_count": packet.get("lane_count", 0),
        "workunit_count": packet.get("workunit_count", 0),
        "event_count": packet.get("event_count", 0),
        "live_ia_call_performed": False,
        "source_probe_executed": False,
        "operator_instance_mutated": False,
        "master_index_mutated": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def validate_packet(packet: Mapping[str, Any], errors: list[str]) -> None:
    if packet.get("schema_version") != "workbench_live_run_packet.v0":
        errors.append("workbench live-run packet schema mismatch")
    if not packet.get("run_id"):
        errors.append("workbench live-run packet must emit run_id")
    if packet.get("state") != "completed":
        errors.append("workbench live-run dry-run must complete")
    if packet.get("event_count", 0) < 1:
        errors.append("workbench live-run must emit events")
    if packet.get("lane_count", 0) < 1:
        errors.append("workbench live-run must emit lanes")
    if packet.get("workunit_count", 0) < 1:
        errors.append("workbench live-run must plan IA-HUNT WorkUnits")
    event_types = {str(event.get("event_type", "")) for event in packet.get("events", [])}
    for required in ("run.created", "query.compiled", "lanes.snapshot_created", "workunits.planned", "ia_hunt.dry_run_planned", "action.blocked", "run.completed"):
        if required not in event_types:
            errors.append(f"missing event type: {required}")
    for key in FALSE_BOUNDARY_KEYS:
        if packet.get("boundary_report", {}).get(key) is not False:
            errors.append(f"boundary {key} must be false")
    command = build_command_response(packet["run_id"], "run_live_source", "operator_workbench")
    if command.get("allowed") is not False or command.get("store_mutation_performed") is not False:
        errors.append("blocked command must be denied without mutating state")


def validate_projections(errors: list[str]) -> None:
    public_packet = create_workbench_resolution_run("sampleproject", "public_web", include_ia_hunt_dry_run=True)
    native_packet = create_workbench_resolution_run("sampleproject", "native_desktop_read_only", include_ia_hunt_dry_run=True)
    for label, packet in (("public", public_packet), ("native", native_packet)):
        if packet.get("projection_profile") not in {"public_web", "native_desktop_read_only"}:
            errors.append(f"{label} projection profile mismatch")
        if "compiled_query_id" in packet:
            errors.append(f"{label} projection must hide operator-only compiled_query_id")
        if packet.get("boundary_report", {}).get("operator_instance_mutated") is not False:
            errors.append(f"{label} projection must not mutate operator instance")


def validate_cli(root: Path, errors: list[str]) -> None:
    help_result = subprocess.run(
        [sys.executable, "scripts/eureka_workbench_live_run.py", "--help"],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if help_result.returncode != 0:
        errors.append(f"workbench live-run CLI help failed: {help_result.stderr or help_result.stdout}")
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/eureka_workbench_live_run.py",
            "--query",
            "sampleproject",
            "--projection",
            "operator_workbench",
            "--dry-run",
            "--from-fixtures",
            "--include-ia-hunt-dry-run",
            "--json",
        ],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        errors.append(f"workbench live-run CLI failed: {completed.stderr or completed.stdout}")
        return
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        errors.append(f"workbench live-run CLI emitted invalid JSON: {exc}")
        return
    if payload.get("schema_version") != "workbench_live_run_packet.v0":
        errors.append("workbench live-run CLI packet schema mismatch")


def validate_routes(errors: list[str]) -> None:
    ctx = build_request_context(
        "GET",
        "/api/v1/resolution-runs",
        {"q": "sampleproject", "projection": "operator_workbench"},
        "127.0.0.1",
    )
    response = route_request(object(), ctx)
    if response.status_code != 200 or response.payload.get("data", {}).get("schema_version") != "workbench_live_run_packet.v0":
        errors.append("local service create/list run API route failed")
        return
    run_id = response.payload["run_id"]
    for suffix in ("", "/events", "/lanes", "/workunits", "/commands?command=run_live_source"):
        path, _, query = f"/api/v1/resolution-runs/{run_id}{suffix}".partition("?")
        route_response = route_request(object(), build_request_context("GET", path, query, "127.0.0.1"))
        expected = 403 if suffix.startswith("/commands") else 200
        if route_response.status_code != expected:
            errors.append(f"local service route failed: {path} status={route_response.status_code}")


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
