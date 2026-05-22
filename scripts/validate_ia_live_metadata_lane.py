#!/usr/bin/env python3
"""Validate the IA live metadata lane foundation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Mapping, Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from runtime.local_service.workbench_live_run import build_command_response, create_workbench_resolution_run  # noqa: E402
from runtime.source_observation.ia_live_metadata_lane import REQUIRED_EVENT_TYPES  # noqa: E402


REQUIRED_FILES = (
    "control/policies/ia_live_metadata_lane_policy.json",
    "control/policies/ia_live_metadata_lane_operator_policy.json",
    "control/policies/ia_live_metadata_lane_rate_limit_policy.json",
    "control/policies/ia_live_metadata_lane_redaction_policy.json",
    "control/policies/ia_live_metadata_lane_non_claim_policy.json",
    "control/inventory/ia_live_metadata_lane_input_state.json",
    "control/inventory/ia_live_metadata_lane_route_matrix.json",
    "control/inventory/ia_live_metadata_lane_command_matrix.json",
    "control/inventory/ia_live_metadata_lane_event_matrix.json",
    "control/inventory/ia_live_metadata_lane_policy_matrix.json",
    "control/inventory/ia_live_metadata_lane_result_lane_matrix.json",
    "control/inventory/ia_live_metadata_lane_boundary_report.json",
    "control/inventory/ia_live_metadata_lane_live_smoke_result.json",
    "control/inventory/ia_live_metadata_lane_validation_matrix.json",
    "control/inventory/ia_live_metadata_lane_result.json",
    "control/inventory/ia_live_metadata_lane_next_task_decision.json",
    "runtime/source_observation/ia_live_metadata_lane.py",
    "runtime/local_service/workbench_live_run.py",
    "scripts/eureka_ia_live_metadata_lane.py",
    "docs/architecture/IA_LIVE_METADATA_LANE.md",
    "docs/architecture/LIVE_SOURCE_ACTION_POLICY.md",
    "docs/operations/IA_LIVE_METADATA_LANE_RUNBOOK.md",
    "docs/operations/POST_IA_LIVE_METADATA_LANE_PLAN.md",
    "docs/reference/IA_LIVE_METADATA_LANE_EVENTS.md",
    "docs/reference/IA_LIVE_METADATA_LANE_COMMANDS.md",
    "examples/ia_live_metadata_lane/sample_request.json",
    "examples/ia_live_metadata_lane/sample_dry_run_result.json",
    "examples/ia_live_metadata_lane/sample_mock_live_result.json",
    "examples/ia_live_metadata_lane/sample_events.json",
    "examples/ia_live_metadata_lane/sample_lane_snapshot.json",
    "examples/ia_live_metadata_lane/sample_boundary_report.json",
    "examples/ia_live_metadata_lane/sample_public_blocked_projection.json",
    "examples/ia_live_metadata_lane/sample_native_blocked_projection.json"
)
FALSE_POLICY_KEYS = (
    "live_ia_metadata_enabled_by_default",
    "public_live_ia_metadata_enabled",
    "native_live_ia_metadata_enabled",
    "live_ia_raw_response_commit_allowed",
    "source_cache_write_default",
    "evidence_write_default",
    "candidate_write_default",
    "reviewed_index_write_default",
    "operator_instance_mutation_default",
    "downloads_enabled",
    "uploads_enabled",
    "extraction_enabled",
    "model_provider_enabled",
    "deployment_enabled",
    "master_index_mutation_enabled",
    "production_readiness_claimed",
    "public_launch_readiness_claimed",
    "full_archive_org_integration_claimed",
)
FALSE_BOUNDARY_KEYS = (
    "source_cache_write_performed",
    "evidence_write_performed",
    "candidate_index_mutated",
    "reviewed_index_mutated",
    "master_index_mutated",
    "operator_instance_mutated",
    "raw_response_committed",
    "download_performed",
    "upload_performed",
    "extraction_executed",
    "model_provider_used",
    "deployment_performed",
    "production_readiness_claimed",
    "public_launch_readiness_claimed",
    "full_archive_org_integration_claimed",
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
        print("IA live metadata lane validation", file=stdout)
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
    policy = load_json(root / "control/policies/ia_live_metadata_lane_policy.json", errors)
    for key in FALSE_POLICY_KEYS:
        if policy.get(key) is not False:
            errors.append(f"IA live lane policy must set {key}=false")
    for key in (
        "live_ia_metadata_requires_operator_command",
        "live_ia_metadata_requires_operator_token",
        "live_ia_metadata_requires_policy_gate",
        "live_ia_redacted_summary_allowed",
        "live_ia_normalized_preview_allowed",
    ):
        if policy.get(key) is not True:
            errors.append(f"IA live lane policy must set {key}=true")
    validate_matrices(root, errors)
    packet = create_workbench_resolution_run("sampleproject", "operator_workbench", include_ia_hunt_dry_run=True)
    validate_default_packet(packet, errors)
    validate_command_paths(packet["run_id"], errors)
    validate_cli(root, errors)
    result_inventory = load_json(root / "control/inventory/ia_live_metadata_lane_result.json", errors)
    for key in (
        "policies_added",
        "command_matrix_added",
        "event_matrix_added",
        "route_matrix_added",
        "policy_matrix_added",
        "result_lane_matrix_added",
        "runtime_lane_added",
        "workbench_projection_added",
        "cli_added",
        "examples_added",
        "docs_added",
        "validator_added",
        "tests_added",
        "dry_run_passed",
        "mock_live_passed",
        "operator_projection_passed",
        "public_projection_blocked",
        "native_read_only_projection_blocked",
        "operator_approval_required",
        "operator_token_required",
    ):
        if result_inventory.get(key) is not True:
            errors.append(f"IA live lane result must set {key}=true")
    for key in FALSE_BOUNDARY_KEYS:
        if result_inventory.get(key) is not False:
            errors.append(f"IA live lane result must set {key}=false")
    return {
        "schema_version": "ia_live_metadata_lane_validation.v0",
        "task": "AIDE-BATCH-IA-LIVE-METADATA-LANE-01",
        "status": "valid" if not errors else "invalid",
        "errors": errors,
        "dry_run_passed": True,
        "mock_live_passed": True,
        "operator_projection_passed": True,
        "public_projection_blocked": True,
        "native_read_only_projection_blocked": True,
        "live_smoke_performed": False,
        "live_smoke_total_http_requests": 0,
        "raw_response_committed": False,
        "live_ia_call_performed": False,
        "source_probe_executed": False,
    }


def validate_matrices(root: Path, errors: list[str]) -> None:
    event_matrix = load_json(root / "control/inventory/ia_live_metadata_lane_event_matrix.json", errors)
    seen_events = set(event_matrix.get("event_types", []))
    for event_type in REQUIRED_EVENT_TYPES:
        if event_type not in seen_events:
            errors.append(f"missing IA live event type: {event_type}")
    lane_matrix = load_json(root / "control/inventory/ia_live_metadata_lane_result_lane_matrix.json", errors)
    states = set(lane_matrix.get("lane_states", []))
    for state in ("unavailable", "blocked_pending_operator_approval", "approved_pending_run", "running", "candidates_available", "failed", "rate_limited", "tls_failed", "completed"):
        if state not in states:
            errors.append(f"missing IA live lane state: {state}")
    if lane_matrix.get("accepted_truth") is not False:
        errors.append("IA live lane matrix must remain candidate-only")


def validate_default_packet(packet: Mapping[str, Any], errors: list[str]) -> None:
    lane = packet.get("ia_live_metadata_lane", {})
    if lane.get("lane_kind") != "ia_live_metadata_candidates":
        errors.append("Workbench packet must include IA live metadata lane")
    if lane.get("state") != "blocked_pending_operator_approval":
        errors.append("IA live lane must be blocked/pending by default")
    if packet.get("live_ia_call_performed") is not False:
        errors.append("default Workbench packet must not perform live IA calls")
    if packet.get("source_probe_executed") is not False:
        errors.append("default Workbench packet must not perform source probes")


def validate_command_paths(run_id: str, errors: list[str]) -> None:
    dry_run = build_command_response(run_id, "run_live_ia_metadata_dry_run", "operator_workbench")
    if dry_run.get("allowed") is not True or dry_run.get("dry_run") is not True:
        errors.append("operator dry-run IA command must be allowed")
    mock = build_command_response(run_id, "run_live_ia_metadata_mock", "operator_workbench")
    if mock.get("allowed") is not True or mock.get("mock_live") is not True:
        errors.append("operator mock-live IA command must be allowed")
    if mock.get("lane", {}).get("result_count", 0) < 1:
        errors.append("mock-live IA command must project candidates")
    no_token = build_command_response(run_id, "run_live_ia_metadata_now", "operator_workbench", allow_live=True)
    if no_token.get("allowed") is not False or not no_token.get("blocked_reasons"):
        errors.append("live IA command must require an operator token")
    public = build_command_response(run_id, "run_live_ia_metadata_mock", "public_web")
    native = build_command_response(run_id, "run_live_ia_metadata_mock", "native_desktop_read_only")
    if public.get("allowed") is not False:
        errors.append("public IA live command must be blocked")
    if native.get("allowed") is not False:
        errors.append("native IA live command must be blocked")
    for payload in (dry_run, mock, no_token, public, native):
        boundary = payload.get("boundary_report", {})
        if payload.get("raw_response_committed") is not False:
            errors.append("IA command response must not commit raw response")
        for key in ("download_performed", "extraction_executed", "model_provider_used", "operator_instance_mutated", "master_index_mutated"):
            if boundary.get(key) is not False:
                errors.append(f"IA command boundary must set {key}=false")


def validate_cli(root: Path, errors: list[str]) -> None:
    help_result = subprocess.run(
        [sys.executable, "scripts/eureka_ia_live_metadata_lane.py", "--help"],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if help_result.returncode != 0:
        errors.append(f"IA live lane CLI help failed: {help_result.stderr or help_result.stdout}")
    dry_run = run_cli(root, ["--query", "sampleproject", "--projection", "operator_workbench", "--dry-run", "--json"], errors)
    mock = run_cli(root, ["--query", "sampleproject", "--projection", "operator_workbench", "--mock-live", "--json"], errors)
    public = run_cli(root, ["--query", "sampleproject", "--projection", "public_web", "--mock-live", "--json"], errors)
    native = run_cli(root, ["--query", "sampleproject", "--projection", "native_desktop_read_only", "--mock-live", "--json"], errors)
    if dry_run and dry_run.get("dry_run_passed") is not True:
        errors.append("IA live lane CLI dry-run did not pass")
    if mock and mock.get("mock_live_passed") is not True:
        errors.append("IA live lane CLI mock-live did not pass")
    if public and public.get("public_projection_blocked") is not True:
        errors.append("IA live lane CLI public projection was not blocked")
    if native and native.get("native_read_only_projection_blocked") is not True:
        errors.append("IA live lane CLI native projection was not blocked")
    for payload in (dry_run, mock, public, native):
        if payload and payload.get("raw_response_committed") is not False:
            errors.append("IA live lane CLI must not commit raw responses")


def run_cli(root: Path, argv: Sequence[str], errors: list[str]) -> dict[str, Any] | None:
    completed = subprocess.run(
        [sys.executable, "scripts/eureka_ia_live_metadata_lane.py", *argv],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        errors.append(f"IA live lane CLI failed: {completed.stderr or completed.stdout}")
        return None
    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        errors.append(f"IA live lane CLI emitted invalid JSON: {exc}")
        return None


def load_json(path: Path, errors: list[str]) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"invalid JSON {path}: {exc}")
        return {}


if __name__ == "__main__":
    raise SystemExit(main())
