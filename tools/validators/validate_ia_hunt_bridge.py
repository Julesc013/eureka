#!/usr/bin/env python3
"""Validate IA-HUNT-BRIDGE-00 artifacts and local bridge behavior."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Mapping, Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.search.hunt.ia_bridge import (  # noqa: E402
    IA_WORKUNIT_STATES,
    IA_WORKUNIT_TYPES,
    build_ia_hunt_boundary_report,
    build_ia_hunt_result_lanes,
    plan_ia_hunt_pipeline,
    run_ia_hunt_pipeline_dry_run,
    run_ia_hunt_pipeline_temp_instance,
)


TASK = "IA-HUNT-BRIDGE-00"
REQUIRED_JSON = {
    "control/policies/ia_hunt_bridge_policy.json": "ia_hunt_bridge_policy.v0",
    "control/policies/ia_workunit_policy.json": "ia_workunit_policy.v0",
    "control/policies/ia_hunt_non_claim_policy.json": "ia_hunt_non_claim_policy.v0",
    "control/inventory/ia_hunt_bridge_input_state.json": "ia_hunt_bridge_input_state.v0",
    "control/inventory/ia_hunt_bridge_policy_matrix.json": "ia_hunt_bridge_policy_matrix.v0",
    "control/inventory/ia_hunt_workunit_schema.json": "ia_hunt_workunit_schema.v0",
    "control/inventory/ia_hunt_pipeline_matrix.json": "ia_hunt_pipeline_matrix.v0",
    "control/inventory/ia_hunt_result_lane_matrix.json": "ia_hunt_result_lane_matrix.v0",
    "control/inventory/ia_hunt_failure_repair_log.json": "ia_hunt_failure_repair_log.v0",
}
OPTIONAL_RESULT_JSON = {
    "control/inventory/ia_hunt_smoke_result.json": "ia_hunt_smoke_result.v0",
    "control/inventory/ia_hunt_validation_matrix.json": "ia_hunt_validation_matrix.v0",
    "control/inventory/ia_hunt_bridge_result.json": "ia_hunt_bridge_result.v0",
    "control/inventory/ia_hunt_bridge_next_task_decision.json": "ia_hunt_bridge_next_task_decision.v0",
    "control/audits/ia-hunt-bridge-00-v0/ia_hunt_bridge_report.json": "ia_hunt_bridge_report.v0",
}
REQUIRED_DOCS = [
    "docs/architecture/IA_HUNT_BRIDGE.md",
    "docs/operations/IA_HUNT_BRIDGE_RUNBOOK.md",
    "docs/operations/POST_IA_HUNT_BRIDGE_PLAN.md",
]
REQUIRED_EXAMPLES = [
    "examples/ia_hunt_bridge/sample_ia_hunt_plan.json",
    "examples/ia_hunt_bridge/sample_ia_workunits.json",
    "examples/ia_hunt_bridge/sample_ia_hunt_result_lanes.json",
    "examples/ia_hunt_bridge/sample_ia_hunt_boundary_report.json",
]
REQUIRED_LANES = {
    "reviewed_local_results",
    "ia_metadata_candidates",
    "source_cache_hits",
    "review_queue_items",
    "known_absence",
    "blocked_actions",
    "running_workunits",
    "deferred_deepening",
    "future_extraction_work",
}
UNSAFE_FALSE_FLAGS = (
    "source_probe_executed",
    "live_ia_call_performed",
    "operator_instance_mutated",
    "master_index_mutated",
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
    report = validate_repo(Path(args.repo_root).resolve())
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True), file=stdout)
    else:
        print("IA Hunt bridge validation", file=stdout)
        print(f"status: {report['status']}", file=stdout)
        print(f"error_count: {len(report['errors'])}", file=stdout)
        for error in report["errors"]:
            print(f"ERROR: {error}", file=stdout)
    return 0 if report["status"] == "valid" else 1


def validate_repo(root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    payloads = {rel: load_json(root / rel, schema, errors) for rel, schema in REQUIRED_JSON.items()}
    for rel, schema in OPTIONAL_RESULT_JSON.items():
        if (root / rel).exists():
            load_json(root / rel, schema, errors)
    for rel in REQUIRED_DOCS:
        if not (root / rel).is_file():
            errors.append(f"missing doc: {rel}")
    for rel in REQUIRED_EXAMPLES:
        if not (root / rel).is_file():
            errors.append(f"missing example: {rel}")
    for rel in ("runtime/search/hunt/ia_bridge.py", "scripts/eureka_ia_hunt_bridge.py"):
        if not (root / rel).is_file():
            errors.append(f"missing implementation file: {rel}")

    bridge_policy = payloads["control/policies/ia_hunt_bridge_policy.json"]
    require_true(bridge_policy, "dry_run_default", errors)
    require_true(bridge_policy, "temp_instance_allowed", errors)
    for key in (
        "operator_instance_mutation_default",
        "live_ia_calls_enabled_by_default",
        "master_index_mutation_enabled",
        "public_fanout_enabled",
        "downloads_enabled",
        "extraction_enabled",
        "model_provider_enabled",
        "deployment_enabled",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
        "full_archive_org_integration_claimed",
    ):
        require_false(bridge_policy, key, errors)

    workunit_schema = payloads["control/inventory/ia_hunt_workunit_schema.json"]
    if set(IA_WORKUNIT_TYPES) - set(workunit_schema.get("workunit_types", [])):
        errors.append("workunit schema missing IA WorkUnit types")
    if set(IA_WORKUNIT_STATES) - set(workunit_schema.get("workunit_states", [])):
        errors.append("workunit schema missing IA WorkUnit states")
    required_fields = set(workunit_schema.get("required_fields", []))
    for field in (
        "workunit_id",
        "hunt_id",
        "source_family",
        "workunit_type",
        "state",
        "input_ref",
        "output_ref",
        "policy_ref",
        "dry_run",
        "writes_instance_state",
        "write_scope",
        "blocked_actions",
        "created_at",
        "completed_at",
        "limitations",
    ):
        if field not in required_fields:
            errors.append(f"workunit schema missing required field: {field}")

    lane_matrix = payloads["control/inventory/ia_hunt_result_lane_matrix.json"]
    lane_kinds = {str(row.get("lane_kind", "")) for row in lane_matrix.get("lanes", [])}
    if REQUIRED_LANES - lane_kinds:
        errors.append(f"result lane matrix missing lanes: {sorted(REQUIRED_LANES - lane_kinds)}")

    _run_cli_help(root, errors)
    dry_outputs = _validate_dry_run(errors)
    temp_outputs = _validate_temp_instance(errors)
    if dry_outputs:
        _validate_runtime_outputs(dry_outputs, "dry_run", errors)
    if temp_outputs:
        _validate_runtime_outputs(temp_outputs, "temp_instance", errors)

    return {
        "schema_version": "ia_hunt_bridge_validation.v0",
        "task": TASK,
        "status": "valid" if not errors else "invalid",
        "errors": errors,
        "policy_added": True,
        "workunit_schema_added": True,
        "pipeline_matrix_added": True,
        "bridge_runtime_added": (root / "runtime/search/hunt/ia_bridge.py").is_file(),
        "bridge_cli_added": (root / "scripts/eureka_ia_hunt_bridge.py").is_file(),
        "result_lane_integration_added": True,
        "examples_added": all((root / rel).is_file() for rel in REQUIRED_EXAMPLES),
        "docs_added": all((root / rel).is_file() for rel in REQUIRED_DOCS),
        "validator_added": True,
        "tests_added": all(
            (root / rel).is_file()
            for rel in (
                "tests/runtime/test_ia_hunt_bridge.py",
                "tests/runtime/test_ia_hunt_workunits.py",
                "tests/runtime/test_ia_hunt_result_lanes.py",
                "tests/operations/test_ia_hunt_bridge_scripts.py",
                "tests/operations/test_ia_hunt_bridge_smoke.py",
                "tests/scripts/test_validate_ia_hunt_bridge.py",
            )
        ),
        "dry_run_plan_passed": bool(dry_outputs),
        "temp_instance_bridge_passed": bool(temp_outputs),
        "source_probe_executed": False,
        "live_ia_call_performed": False,
        "operator_instance_mutated": False,
        "master_index_mutated": False,
        "download_performed": False,
        "upload_performed": False,
        "extraction_executed": False,
        "model_provider_used": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
        "full_archive_org_integration_claimed": False,
    }


def _validate_dry_run(errors: list[str]) -> dict[str, Any]:
    try:
        plan = plan_ia_hunt_pipeline("sampleproject")
        outputs = run_ia_hunt_pipeline_dry_run(plan)
    except Exception as exc:
        errors.append(f"dry-run bridge failed: {exc}")
        return {}
    if not outputs.get("dry_run"):
        errors.append("dry-run outputs must remain dry_run")
    return outputs


def _validate_temp_instance(errors: list[str]) -> dict[str, Any]:
    try:
        plan = plan_ia_hunt_pipeline("sampleproject")
        with TemporaryDirectory(prefix="eureka-ia-hunt-validator-") as tmp:
            outputs = run_ia_hunt_pipeline_temp_instance(plan, tmp, "validator-temp-token")
    except Exception as exc:
        errors.append(f"temp-instance bridge failed: {exc}")
        return {}
    if outputs.get("dry_run") is not False:
        errors.append("temp-instance outputs must not be dry_run")
    return outputs


def _validate_runtime_outputs(outputs: Mapping[str, Any], mode: str, errors: list[str]) -> None:
    boundary = build_ia_hunt_boundary_report(outputs)
    lanes = build_ia_hunt_result_lanes(outputs, "operator_workbench")
    public_lanes = build_ia_hunt_result_lanes(outputs, "public_web")
    native_lanes = build_ia_hunt_result_lanes(outputs, "native_desktop_read_only")
    if boundary.get("mode") != mode:
        errors.append(f"{mode} boundary mode mismatch")
    for key in UNSAFE_FALSE_FLAGS:
        if boundary.get(key) is not False:
            errors.append(f"{mode} boundary {key} must be false")
    if mode == "dry_run":
        for key in ("source_cache_write_performed", "evidence_write_performed", "candidate_index_mutated", "review_queue_mutated", "reviewed_index_mutated"):
            if boundary.get(key) is not False:
                errors.append(f"dry-run boundary {key} must be false")
    if mode == "temp_instance":
        for key in ("source_cache_write_performed", "evidence_write_performed", "candidate_index_mutated", "review_queue_mutated", "reviewed_index_mutated"):
            if boundary.get(key) is not True:
                errors.append(f"temp-instance boundary {key} must be true")
    workunits = [dict(item) for item in outputs.get("workunits", []) or []]
    if len(workunits) != len(IA_WORKUNIT_TYPES):
        errors.append(f"{mode} must emit all IA WorkUnits")
    for item in workunits:
        if item.get("source_family") != "internet_archive_metadata":
            errors.append(f"{mode} WorkUnit source_family mismatch")
        if item.get("workunit_type") not in IA_WORKUNIT_TYPES:
            errors.append(f"{mode} unknown WorkUnit type: {item.get('workunit_type')}")
        if item.get("state") not in IA_WORKUNIT_STATES:
            errors.append(f"{mode} unknown WorkUnit state: {item.get('state')}")
        if not item.get("blocked_actions"):
            errors.append(f"{mode} WorkUnit missing blocked_actions")
    lane_kinds = {str(lane.get("lane_kind", "")) for lane in lanes.get("lanes", [])}
    if REQUIRED_LANES - lane_kinds:
        errors.append(f"{mode} result lanes missing: {sorted(REQUIRED_LANES - lane_kinds)}")
    if not any(lane.get("lane_kind") == "ia_metadata_candidates" and lane.get("result_count", 0) > 0 for lane in lanes.get("lanes", [])):
        errors.append(f"{mode} must emit IA metadata candidate lane items")
    if public_lanes.get("boundary_report", {}).get("operator_fields_hidden") is not True:
        errors.append(f"{mode} public projection must hide operator fields")
    for lane in native_lanes.get("lanes", []):
        posture = dict(lane.get("action_posture", {}) or {})
        if posture.get("can_review") is not False or posture.get("can_rebuild_index") is not False:
            errors.append(f"{mode} native read-only projection cannot mutate or review")


def _run_cli_help(root: Path, errors: list[str]) -> None:
    completed = subprocess.run(
        [sys.executable, "scripts/eureka_ia_hunt_bridge.py", "--help"],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
        timeout=30,
    )
    if completed.returncode != 0:
        errors.append("CLI --help failed")
    if "--apply-to-temp" not in completed.stdout:
        errors.append("CLI help missing --apply-to-temp")


def load_json(path: Path, schema_version: str, errors: list[str]) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"missing JSON file: {path}")
        return {}
    except json.JSONDecodeError as exc:
        errors.append(f"malformed JSON file {path}: {exc}")
        return {}
    if payload.get("schema_version") != schema_version:
        errors.append(f"{path} schema_version must be {schema_version}")
    return payload


def require_true(payload: Mapping[str, Any], key: str, errors: list[str]) -> None:
    if payload.get(key) is not True:
        errors.append(f"{key} must be true")


def require_false(payload: Mapping[str, Any], key: str, errors: list[str]) -> None:
    if payload.get(key) is not False:
        errors.append(f"{key} must be false")


if __name__ == "__main__":
    raise SystemExit(main())
