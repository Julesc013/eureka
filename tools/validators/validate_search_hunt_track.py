#!/usr/bin/env python3
"""Validate HUNT-00 Search Hunt track planning evidence."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
import re
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.hunt_queue_progress import (
    hunt_latest_packet_current_or_advanced,
    hunt_queue_current_or_advanced,
    post_hunt_current_allowed,
)

TASK_ID = "HUNT-00"
NEXT_TASK = "HUNT-01"

POLICIES = {
    "control/policies/search_hunt_policy.json": "search_hunt_policy.v0",
    "control/policies/search_hunt_workunit_policy.json": "search_hunt_workunit_policy.v0",
    "control/policies/search_hunt_ui_policy.json": "search_hunt_ui_policy.v0",
    "control/policies/search_hunt_sync_policy.json": "search_hunt_sync_policy.v0",
    "control/policies/search_hunt_ai_boundary_policy.json": "search_hunt_ai_boundary_policy.v0",
    "control/policies/search_hunt_completion_policy.json": "search_hunt_completion_policy.v0",
}

INVENTORIES = {
    "control/inventory/search_hunt_track_plan.json": "search_hunt_track_plan.v0",
    "control/inventory/search_hunt_readiness_matrix.json": "search_hunt_readiness_matrix.v0",
    "control/inventory/search_hunt_dependency_matrix.json": "search_hunt_dependency_matrix.v0",
    "control/inventory/search_hunt_local_appliance_dependency.json": "search_hunt_local_appliance_dependency.v0",
    "control/inventory/search_hunt_future_track_gate.json": "search_hunt_future_track_gate.v0",
    "control/inventory/search_hunt_next_task_decision.json": "search_hunt_next_task_decision.v0",
    "control/inventory/hunt_00_final_state_alignment.json": "hunt_00_final_state_alignment.v0",
}

DOCS = (
    "docs/architecture/SEARCH_HUNT_MODEL.md",
    "docs/architecture/SEARCH_HUNT_LOCAL_APPLIANCE_INTEGRATION.md",
    "docs/architecture/SEARCH_HUNT_WORKUNIT_FLOW.md",
    "docs/operations/SEARCH_HUNT_TRACK.md",
    "docs/operations/SEARCH_HUNT_POLICY.md",
    "docs/operations/SEARCH_HUNT_AI_BOUNDARY.md",
    "docs/operations/SEARCH_HUNT_COMPLETION_STANDARD.md",
    "docs/operations/HUNT_TO_SYN_F0_HANDOFF.md",
)

AUDIT_ROOT = Path("control/audits/hunt-00-search-hunt-track-v0")
AUDIT_FILES = (
    "README.md",
    "hunt_00_report.json",
    "track_plan.md",
    "readiness_matrix.md",
    "dependency_matrix.md",
    "local_appliance_integration.md",
    "policy_summary.md",
    "future_track_gate.md",
    "validation.md",
    "generated/sample_search_hunt_track_plan.json",
    "generated/sample_readiness_matrix.json",
    "generated/sample_dependency_matrix.json",
    "generated/sample_summary.md",
)

HUNT_SEQUENCE = [f"HUNT-{index:02d}" for index in range(13)]
READINESS_CAPABILITIES = {
    "final_local_appliance_baseline",
    "explicit_instance_root",
    "local_runtime_composition",
    "local_http_service",
    "html_workbench",
    "workunit_queue",
    "deterministic_worker_runner",
    "review_rebuild_loop",
    "auto_test_harness",
    "search_hunt_session_runtime",
    "hunt_ui_state",
    "steering_commands",
    "exhaustion_report",
    "hunt_to_search_need",
    "hunt_to_workunit",
    "background_hunt_runner",
    "deterministic_replay",
    "ai_escalation_gate_disabled_by_default",
}
DEPENDENCIES = {
    "Local Appliance",
    "WorkUnit queue",
    "local worker runner",
    "reviewed public index",
    "evidence ledger",
    "review queue",
    "auto-test harness",
    "SYN",
    "F0",
    "G",
    "H source expansion",
    "K AI assist",
}
FORBIDDEN_CHANGED_ROOTS = (
    "runtime/",
    "contracts/",
    "surfaces/",
    "site/",
    "site/dist/",
    "native/",
    "crates/",
    "examples/",
    "archive/prototypes/",
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    result = validate(Path(args.repo_root).resolve())
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print("HUNT-00 Search Hunt track validation", file=stdout)
        print(f"status: {result['status']}", file=stdout)
        for error in result["errors"]:
            print(f"ERROR: {error}", file=stdout)
        for warning in result["warnings"]:
            print(f"WARN: {warning}", file=stdout)
    return 0 if result["status"] in {"pass", "pass_with_warnings"} else 1


def validate(root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    payloads = {rel: load_json(root / rel, schema, errors) for rel, schema in {**POLICIES, **INVENTORIES}.items()}
    report = load_json(root / AUDIT_ROOT / "hunt_00_report.json", "hunt_00_report.v0", errors)
    validate_required_files(root, errors)
    validate_plan(payloads.get("control/inventory/search_hunt_track_plan.json", {}), errors)
    validate_readiness(payloads.get("control/inventory/search_hunt_readiness_matrix.json", {}), errors)
    validate_dependencies(payloads.get("control/inventory/search_hunt_dependency_matrix.json", {}), errors)
    validate_local_appliance_dependency(payloads.get("control/inventory/search_hunt_local_appliance_dependency.json", {}), errors)
    validate_future_gate(payloads.get("control/inventory/search_hunt_future_track_gate.json", {}), errors)
    validate_policies(payloads, errors)
    validate_report(root, report, errors, warnings)
    validate_queue(root, errors)
    validate_scope(root, errors)
    status = "fail" if errors else ("pass_with_warnings" if warnings else "pass")
    return {
        "schema_version": "search_hunt_track_validation.v0",
        "task": TASK_ID,
        "status": status,
        "errors": errors,
        "warnings": warnings,
        "next_task": NEXT_TASK,
        "runtime_modified": False,
        "contracts_modified": False,
        "source_probe_executed": False,
        "model_provider_used": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def validate_required_files(root: Path, errors: list[str]) -> None:
    for rel in (*DOCS, "scripts/validate_search_hunt_track.py", "tests/operations/test_search_hunt_track.py"):
        path = root / rel
        if not path.is_file():
            errors.append(f"required file missing: {rel}")
        elif path.stat().st_size == 0:
            errors.append(f"required file empty: {rel}")
    for rel in AUDIT_FILES:
        path = root / AUDIT_ROOT / rel
        if not path.is_file():
            errors.append(f"audit file missing: {(AUDIT_ROOT / rel).as_posix()}")
        elif path.stat().st_size == 0:
            errors.append(f"audit file empty: {(AUDIT_ROOT / rel).as_posix()}")


def validate_plan(plan: Mapping[str, Any], errors: list[str]) -> None:
    rows = plan.get("track")
    if not isinstance(rows, list):
        errors.append("track plan must contain track list")
        return
    ids = [row.get("task_id") for row in rows if isinstance(row, Mapping)]
    if ids != HUNT_SEQUENCE:
        errors.append(f"HUNT task sequence must be exact: {ids}")
    for row in rows:
        if not isinstance(row, Mapping):
            errors.append("track row must be an object")
            continue
        for key in (
            "task_id",
            "purpose",
            "proof_level_required",
            "required_local_appliance_capabilities",
            "required_runtime_behavior",
            "required_tests",
            "forbidden_side_effects",
            "next_task",
        ):
            if key not in row:
                errors.append(f"track row {row.get('task_id')} missing {key}")
    if plan.get("search_hunt_runtime_implemented_current_task") is not False:
        errors.append("HUNT-00 must not implement Search Hunt runtime")


def validate_readiness(matrix: Mapping[str, Any], errors: list[str]) -> None:
    rows = matrix.get("capabilities")
    if not isinstance(rows, list):
        errors.append("readiness matrix must contain capabilities list")
        return
    seen = {row.get("capability") for row in rows if isinstance(row, Mapping)}
    missing = READINESS_CAPABILITIES - seen
    if missing:
        errors.append(f"readiness matrix missing capabilities: {sorted(missing)}")
    statuses = {"missing", "planned", "implemented", "tested", "blocked"}
    for row in rows:
        if not isinstance(row, Mapping):
            errors.append("readiness row must be an object")
            continue
        if row.get("status") not in statuses:
            errors.append(f"invalid readiness status for {row.get('capability')}")
        for key in ("required_before_hunt_01", "required_before_hunt_closeout"):
            if not isinstance(row.get(key), bool):
                errors.append(f"readiness row {row.get('capability')} missing boolean {key}")


def validate_dependencies(matrix: Mapping[str, Any], errors: list[str]) -> None:
    rows = matrix.get("dependencies")
    if not isinstance(rows, list):
        errors.append("dependency matrix must contain dependencies list")
        return
    seen = {row.get("dependency") for row in rows if isinstance(row, Mapping)}
    missing = DEPENDENCIES - seen
    if missing:
        errors.append(f"dependency matrix missing dependencies: {sorted(missing)}")
    for row in rows:
        if not isinstance(row, Mapping):
            errors.append("dependency row must be an object")
            continue
        for key in ("dependency_kind", "required_before_task", "direction", "notes"):
            if not row.get(key):
                errors.append(f"dependency row {row.get('dependency')} missing {key}")


def validate_local_appliance_dependency(payload: Mapping[str, Any], errors: list[str]) -> None:
    required_true = (
        "must_use_explicit_local_instance",
        "must_use_runtime_local_appliance_composition",
        "must_use_runtime_workunit_queue_for_background_tasks",
        "must_use_local_workers_for_deterministic_execution",
        "must_use_review_evidence_index_path_for_promoted_records",
        "must_use_local_auto_test_harness",
        "must_be_visible_in_local_workbench_when_ui_tasks_begin",
        "direct_master_index_mutation_forbidden",
    )
    for key in required_true:
        if payload.get(key) is not True:
            errors.append(f"local appliance dependency must set {key}=true")


def validate_future_gate(payload: Mapping[str, Any], errors: list[str]) -> None:
    for key, value in payload.items():
        if key.endswith("_claimed"):
            continue
        if key not in {"schema_version", "task", "status"} and value is not True:
            errors.append(f"future track gate must set {key}=true")


def validate_policies(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    hunt = payloads.get("control/policies/search_hunt_policy.json", {})
    workunit = payloads.get("control/policies/search_hunt_workunit_policy.json", {})
    ui = payloads.get("control/policies/search_hunt_ui_policy.json", {})
    sync = payloads.get("control/policies/search_hunt_sync_policy.json", {})
    ai = payloads.get("control/policies/search_hunt_ai_boundary_policy.json", {})
    completion = payloads.get("control/policies/search_hunt_completion_policy.json", {})
    required_true = {
        "local_appliance_required": hunt,
        "reviewed_index_first": hunt,
        "absence_may_create_hunt_future": hunt,
        "weak_result_may_create_hunt_future": hunt,
        "direct_truth_acceptance_forbidden": hunt,
        "direct_master_index_mutation_forbidden": hunt,
        "hunts_create_workunits_only_through_workunit_queue": workunit,
        "workunits_must_have_policy_state": workunit,
        "workunits_must_have_transition_history": workunit,
        "public_safe_need_summaries_require_policy_gate": sync,
        "future_ai_output_candidate_material_only": ai,
        "ai_must_consume_exhaustion_report_not_only_raw_query": ai,
    }
    for key, payload in required_true.items():
        if payload.get(key) is not True:
            errors.append(f"policy flag must be true: {key}")
    required_false = {
        "search_hunt_sessions_enabled_current_task": hunt,
        "source_probe_execution_enabled": hunt,
        "model_provider_enabled": hunt,
        "deployment_enabled": hunt,
        "production_readiness_claimed": hunt,
        "public_launch_readiness_claimed": hunt,
        "workunits_equal_truth": workunit,
        "hunt_00_executes_workunits": workunit,
        "source_probe_workunits_enabled_current_task": workunit,
        "hunt_00_adds_ui_routes": ui,
        "sync_enabled_current_task": sync,
        "ai_model_provider_calls_enabled_current_task": ai,
        "ai_can_accept_truth": ai,
        "ai_can_mutate_reviewed_index": ai,
        "ai_can_mutate_master_index": ai,
        "ai_can_clear_rights_or_safety": ai,
        "scaffold_only_completion_allowed": completion,
    }
    for key, payload in required_false.items():
        if payload.get(key) is not False:
            errors.append(f"policy flag must be false: {key}")
    if hunt.get("implementation_deferred_to") != NEXT_TASK:
        errors.append("Search Hunt implementation must be deferred to HUNT-01")
    proof_levels = completion.get("proof_levels", {})
    if set(proof_levels) != set(HUNT_SEQUENCE):
        errors.append("completion policy must define proof levels for HUNT-00 through HUNT-12")


def validate_report(root: Path, report: Mapping[str, Any], errors: list[str], warnings: list[str]) -> None:
    expected_true = (
        "main_dev_aligned_before",
        "local_appliance_baseline_verified",
        "hunt_track_plan_created",
        "readiness_matrix_created",
        "dependency_matrix_created",
        "local_appliance_dependency_recorded",
        "future_track_gate_created",
        "policies_created",
        "docs_created",
        "validator_added",
        "tests_added",
    )
    for key in expected_true:
        if report.get(key) is not True:
            errors.append(f"HUNT-00 report must set {key}=true")
    expected_false = (
        "runtime_modified",
        "contracts_modified",
        "search_hunt_runtime_implemented",
        "source_probe_executed",
        "model_provider_used",
        "deployment_performed",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    )
    for key in expected_false:
        if report.get(key) is not False:
            errors.append(f"HUNT-00 report must set {key}=false")
    if report.get("recommended_next_task") != "HUNT-01 — Search Hunt Session runtime":
        errors.append("HUNT-00 report must recommend HUNT-01")
    if report.get("status") == "pass_with_warnings" and not post_hunt_current_allowed(root):
        warnings.append("HUNT-00 carries final baseline warning disposition forward")


def validate_queue(root: Path, errors: list[str]) -> None:
    queue = read_text(root / ".aide/queue/index.yaml", errors)
    packet = read_text(root / ".aide/context/latest-task-packet.md", errors)
    if not hunt_queue_current_or_advanced(root, TASK_ID, NEXT_TASK):
        errors.append("queue must point to HUNT-01 or a later HUNT task")
    if "id: HUNT-00" not in queue or "status: completed" not in queue:
        errors.append("queue must mark HUNT-00 completed")
    if "id: HUNT-01" not in queue:
        errors.append("queue must include HUNT-01")
    if not hunt_latest_packet_current_or_advanced(root, TASK_ID, NEXT_TASK):
        errors.append("latest task packet must point to HUNT-01 or a later HUNT task")
    if "F0-00" in queue and "current_recommended_task: F0-00" in queue and not post_hunt_current_allowed(root):
        errors.append("F0 must not be current")


def validate_scope(root: Path, errors: list[str]) -> None:
    queue = read_text(root / ".aide/queue/index.yaml", errors)
    if re.search(r"current_recommended_task: HUNT-(0[2-9]|1[0-2])\b", queue) or post_hunt_current_allowed(root):
        return
    status = git(root, "status", "--porcelain=v1")
    for path in parse_status_paths(status.splitlines() if status else []):
        if any(path == prefix.rstrip("/") or path.startswith(prefix) for prefix in FORBIDDEN_CHANGED_ROOTS):
            errors.append(f"forbidden product path changed: {path}")


def load_json(path: Path, schema: str, errors: list[str]) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"missing JSON file: {relpath(path)}")
        return {}
    except json.JSONDecodeError as exc:
        errors.append(f"invalid JSON {relpath(path)}: {exc}")
        return {}
    if not isinstance(payload, dict):
        errors.append(f"JSON file must contain an object: {relpath(path)}")
        return {}
    if payload.get("schema_version") != schema:
        errors.append(f"schema_version mismatch for {relpath(path)}")
    return payload


def read_text(path: Path, errors: list[str]) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        errors.append(f"missing text file: {relpath(path)}")
        return ""


def git(root: Path, *args: str) -> str:
    completed = subprocess.run(["git", *args], cwd=root, text=True, capture_output=True, check=False)
    if completed.returncode != 0:
        return ""
    return completed.stdout.strip()


def parse_status_paths(lines: Sequence[str]) -> list[str]:
    paths: list[str] = []
    for line in lines:
        if len(line) < 4:
            continue
        raw = line[3:].replace("\\", "/").strip('"')
        if " -> " in raw:
            paths.extend(part.strip('"') for part in raw.split(" -> "))
        else:
            paths.append(raw)
    return paths


def relpath(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
