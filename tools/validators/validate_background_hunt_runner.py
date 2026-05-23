#!/usr/bin/env python3
"""Validate the HUNT-07 background hunt runner."""

from __future__ import annotations

import argparse
import ast
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.hunt_queue_progress import hunt_queue_current_or_advanced
from runtime.local.appliance import close_local_appliance, open_local_appliance
from runtime.local.operator.auth import build_cli_operator_auth_state
from runtime.local.service import LocalServiceApp
from runtime.search.hunt import build_background_hunt_plan, run_background_hunt_batch, run_next_hunt_workunit
from runtime.search.need import create_workunits_from_need
from runtime.worker.workunit_queue.records import WorkUnit, WorkUnitState, WorkUnitType


TASK_ID = "HUNT-07"
NEXT_TASK = "HUNT-08"
POLICIES = {
    "control/policies/background_hunt_runner_policy.json": "background_hunt_runner_policy.v0",
    "control/policies/background_hunt_worker_policy.json": "background_hunt_worker_policy.v0",
    "control/policies/background_hunt_side_effect_policy.json": "background_hunt_side_effect_policy.v0",
    "control/policies/background_hunt_auth_policy.json": "background_hunt_auth_policy.v0",
    "control/policies/background_hunt_ui_policy.json": "background_hunt_ui_policy.v0",
    "control/policies/background_hunt_non_claim_policy.json": "background_hunt_non_claim_policy.v0",
}
INVENTORIES = {
    "control/inventory/background_hunt_runner_inventory.json": "background_hunt_runner_inventory.v0",
    "control/inventory/background_hunt_worker_matrix.json": "background_hunt_worker_matrix.v0",
    "control/inventory/background_hunt_policy_matrix.json": "background_hunt_policy_matrix.v0",
    "control/inventory/background_hunt_runner_result.json": "background_hunt_runner_result.v0",
    "control/inventory/background_hunt_demo_result.json": "background_hunt_demo_result.v0",
    "control/inventory/background_hunt_gap_register.json": "background_hunt_gap_register.v0",
    "control/inventory/hunt_07_next_task_decision.json": "hunt_07_next_task_decision.v0",
}
REQUIRED_FILES = (
    "runtime/search/hunt/runner.py",
    "runtime/search/hunt/run_records.py",
    "runtime/search/hunt/workunit_runner.py",
    "scripts/eureka_hunt_runner.py",
    "scripts/demo_background_hunt_runner.py",
    "scripts/validate_background_hunt_runner.py",
    "tests/runtime/test_background_hunt_runner_plan.py",
    "tests/runtime/test_background_hunt_runner_execution.py",
    "tests/runtime/test_background_hunt_runner_policy.py",
    "tests/runtime/test_background_hunt_runner_routes.py",
    "tests/runtime/test_background_hunt_runner_ui.py",
    "tests/runtime/test_background_hunt_runner_auth.py",
    "tests/operations/test_background_hunt_runner_scripts.py",
    "docs/architecture/BACKGROUND_HUNT_RUNNER.md",
    "docs/reference/BACKGROUND_HUNT_RUN_RECORD.md",
    "docs/reference/BACKGROUND_HUNT_API.md",
    "docs/operations/BACKGROUND_HUNT_RUNNER_RUNBOOK.md",
    "docs/operations/BACKGROUND_HUNT_BOUNDARIES.md",
)
AUDIT_ROOT = Path("control/audits/hunt-07-background-hunt-runner-v0")
AUDIT_FILES = (
    "README.md",
    "hunt_07_report.json",
    "runner_summary.md",
    "worker_matrix.md",
    "policy_matrix.md",
    "auth_boundary.md",
    "side_effect_boundary.md",
    "ui_summary.md",
    "demo_result.md",
    "validation.md",
    "generated/sample_runner_plan.json",
    "generated/sample_background_hunt_run.json",
    "generated/sample_worker_results.json",
    "generated/sample_hunt_with_runner.html",
    "generated/sample_demo_result.json",
    "generated/sample_summary.md",
)
FORBIDDEN_IMPORT_PREFIXES = (
    "runtime.connectors",
    "runtime.local_foundry",
    "runtime.extraction",
    "runtime.search_quality",
    "requests",
    "httpx",
    "aiohttp",
    "urllib.request",
)
FORBIDDEN_RUNTIME_VOCABULARY = ("HUNT-", "LOCAL-", "AIDE", "BUNDLE")


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output")
    args = parser.parse_args(argv)
    result = validate(Path(args.repo_root).resolve())
    if args.output:
        write_json(Path(args.output), result)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print("HUNT-07 background hunt runner validation", file=stdout)
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
    report = load_json(root / AUDIT_ROOT / "hunt_07_report.json", "hunt_07_report.v0", errors)
    validate_files(root, errors)
    validate_policy_payloads(payloads, errors)
    validate_inventory_payloads(payloads, errors)
    validate_report_payload(report, errors)
    validate_runtime_imports(root, errors)
    validate_runtime_vocabulary(root, errors)
    behavior = validate_behavior(root, errors)
    validate_cli_and_demo(root, errors)
    validate_queue(root, errors)
    status = "fail" if errors else ("pass_with_warnings" if warnings else "pass")
    return {
        "schema_version": "background_hunt_runner_validation.v0",
        "task": TASK_ID,
        "status": status,
        "errors": errors,
        "warnings": warnings,
        **behavior,
        "validator_added": True,
        "source_probe_executed": False,
        "extraction_executed": False,
        "external_network_used": False,
        "model_provider_used": False,
        "download_install_execute_performed": False,
        "review_mutation_performed": False,
        "master_index_mutated": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def validate_files(root: Path, errors: list[str]) -> None:
    for rel in REQUIRED_FILES:
        path = root / rel
        if not path.is_file():
            errors.append(f"missing file: {rel}")
        elif path.stat().st_size == 0:
            errors.append(f"empty file: {rel}")
    for rel in AUDIT_FILES:
        path = root / AUDIT_ROOT / rel
        if not path.is_file():
            errors.append(f"missing audit file: {(AUDIT_ROOT / rel).as_posix()}")
        elif path.stat().st_size == 0:
            errors.append(f"empty audit file: {(AUDIT_ROOT / rel).as_posix()}")


def validate_policy_payloads(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    runner = payloads.get("control/policies/background_hunt_runner_policy.json", {})
    for key in (
        "background_hunt_runner_enabled",
        "deterministic_local_workers_only",
        "workunit_execution_enabled_for_safe_workers",
        "operator_token_required_for_execution",
    ):
        if runner.get(key) is not True:
            errors.append(f"runner policy {key} must be true")
    for key in (
        "source_probe_execution_enabled",
        "extraction_execution_enabled",
        "ai_model_execution_enabled",
        "agent_research_execution_enabled",
        "external_network_enabled",
        "download_install_execute_enabled",
        "source_sync_enabled",
        "lan_worker_execution_enabled",
        "deployment_enabled",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    ):
        if runner.get(key) is not False:
            errors.append(f"runner policy {key} must be false")
    if int(runner.get("max_workunits_per_batch", 0)) != 10:
        errors.append("runner policy max_workunits_per_batch must be 10")
    auth = payloads.get("control/policies/background_hunt_auth_policy.json", {})
    for key in ("run_next_requires_operator_token", "run_batch_requires_operator_token", "localhost_only_execution", "lan_execution_forbidden", "missing_token_rejected", "invalid_token_rejected"):
        if auth.get(key) is not True:
            errors.append(f"auth policy {key} must be true")


def validate_inventory_payloads(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    inventory = payloads.get("control/inventory/background_hunt_runner_inventory.json", {})
    if inventory.get("runner_enabled") is not True:
        errors.append("runner inventory must enable runner")
    for key in ("source_probe_execution_enabled", "extraction_execution_enabled", "model_provider_enabled", "external_network_enabled", "deployment_performed"):
        if inventory.get(key) is not False:
            errors.append(f"runner inventory {key} must be false")
    workers = payloads.get("control/inventory/background_hunt_worker_matrix.json", {}).get("rows", [])
    worker_names = {str(row.get("worker_kind")) for row in workers}
    for required in ("noop_worker", "review_queue_checker", "absence_report_worker", "local_status_snapshot_worker", "reviewed_index_rebuild_worker", "source_probe_worker", "extraction_worker", "ai_model_worker"):
        if required not in worker_names:
            errors.append(f"worker matrix missing {required}")
    next_task = payloads.get("control/inventory/hunt_07_next_task_decision.json", {})
    if not str(next_task.get("recommended_next_task", "")).startswith(NEXT_TASK):
        errors.append("next task must be HUNT-08")


def validate_report_payload(report: Mapping[str, Any], errors: list[str]) -> None:
    for key in (
        "runner_added",
        "cli_added",
        "demo_added",
        "validator_added",
        "plan_preview_passed",
        "safe_workunit_execution_passed",
        "transition_history_recorded",
        "worker_audit_recorded",
        "blocked_source_probe_remained_blocked",
        "blocked_extraction_remained_blocked",
        "blocked_ai_model_remained_blocked",
        "missing_token_rejected",
        "invalid_token_rejected",
        "lan_execution_blocked",
        "ui_routes_added",
        "api_routes_added",
    ):
        if report.get(key) is not True:
            errors.append(f"hunt_07_report {key} must be true")
    for key in (
        "source_probe_executed",
        "extraction_executed",
        "external_network_used",
        "model_provider_used",
        "download_install_execute_performed",
        "review_mutation_performed",
        "public_index_mutated_except_allowed_rebuild_worker",
        "master_index_mutated",
        "deployment_performed",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    ):
        if report.get(key) is not False:
            errors.append(f"hunt_07_report {key} must be false")


def validate_behavior(root: Path, errors: list[str]) -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as tmp:
        instance = Path(tmp) / "eureka-instance"
        init = run_cmd(root, "scripts/eureka_init_instance.py", "--instance", str(instance), "--json")
        if init.returncode != 0:
            errors.append(f"instance init failed: {init.stderr or init.stdout}")
            return {}
        runtime = open_local_appliance(instance, read_only=False)
        try:
            fixture = create_fixture(runtime)
            hunt = fixture["hunt"]
            source_id = fixture["source_probe_id"]
            extraction_id = fixture["extraction_id"]
            ai_id = fixture["ai_id"]
            before_public = runtime.public_index.summarize().to_dict()
            plan = build_background_hunt_plan(runtime, hunt.id)
            result = run_next_hunt_workunit(runtime, hunt.id, operator_context={"authorized": True, "operator_label": "validator"})
            batch = run_background_hunt_batch(runtime, hunt.id, limit=50, operator_context={"authorized": True, "operator_label": "validator"})
            transitions = runtime.workunit_queue.list_transitions(limit=500)
            refs = runtime.workunit_queue.list_payload_refs(limit=500)
            runs = runtime.search_hunt.list_background_hunt_runs(hunt_id=hunt.id, limit=20)
            after_public = runtime.public_index.summarize().to_dict()

            app = LocalServiceApp(runtime, operator_auth_state=build_cli_operator_auth_state("validator-token"))
            missing = app.handle("POST", f"/hunt/{hunt.id}/runner/run-next")
            invalid = app.handle("POST", f"/hunt/{hunt.id}/runner/run-next", body="operator_token=bad")
            lan = app.handle("POST", f"/hunt/{hunt.id}/runner/run-next", client_host="192.168.1.20", body="operator_token=validator-token")
            route_plan = app.handle("POST", f"/api/v1/hunt/{hunt.id}/runner/plan")
            route_run = app.handle("POST", f"/api/v1/hunt/{hunt.id}/runner/run-batch", body="operator_token=validator-token&limit=1")
            route_get = app.handle("GET", f"/api/v1/hunt/{hunt.id}/runner")
            hunt_page = app.handle("GET", f"/hunt/{hunt.id}")

            blocked_states = {
                "source": runtime.workunit_queue.get_workunit(source_id).state.value,
                "extraction": runtime.workunit_queue.get_workunit(extraction_id).state.value,
                "ai": runtime.workunit_queue.get_workunit(ai_id).state.value,
            }
            if plan.runnable_count < 1:
                errors.append("runner plan did not list runnable WorkUnits")
            if plan.blocked_count < 3:
                errors.append("runner plan did not list expected blocked WorkUnits")
            if result.run.status.value != "complete":
                errors.append("run-next did not complete one safe WorkUnit")
            if len(batch.run.workunit_ids) > 10:
                errors.append("run-batch exceeded max limit")
            if not any(item.to_state.value == "complete" for item in transitions):
                errors.append("worker transition history was not recorded")
            if not any(ref.ref_kind == "worker_result" for ref in refs):
                errors.append("worker result audit ref was not recorded")
            if not runs:
                errors.append("background hunt run history was not recorded")
            if blocked_states != {"source": "blocked", "extraction": "blocked", "ai": "blocked"}:
                errors.append(f"blocked WorkUnits changed state: {blocked_states}")
            if before_public != after_public:
                errors.append("public index changed during background hunt validation")
            for name, response in (("route plan", route_plan), ("route run", route_run), ("route get", route_get), ("hunt page", hunt_page)):
                if response.status_code != 200:
                    errors.append(f"{name} failed: {response.status_code} {response.payload}")
            if missing.status_code != 401:
                errors.append("missing operator token was not rejected")
            if invalid.status_code != 401:
                errors.append("invalid operator token was not rejected")
            if lan.status_code != 403:
                errors.append("LAN background run was not blocked")

            return {
                "runner_added": True,
                "plan_preview_passed": plan.runnable_count >= 1 and route_plan.status_code == 200,
                "safe_workunit_execution_passed": result.run.status.value == "complete",
                "transition_history_recorded": any(item.to_state.value == "complete" for item in transitions),
                "worker_audit_recorded": any(ref.ref_kind == "worker_result" for ref in refs),
                "blocked_source_probe_remained_blocked": blocked_states["source"] == "blocked",
                "blocked_extraction_remained_blocked": blocked_states["extraction"] == "blocked",
                "blocked_ai_model_remained_blocked": blocked_states["ai"] == "blocked",
                "missing_token_rejected": missing.status_code == 401,
                "invalid_token_rejected": invalid.status_code == 401,
                "lan_execution_blocked": lan.status_code == 403,
                "ui_routes_added": hunt_page.status_code == 200,
                "api_routes_added": route_get.status_code == 200 and route_run.status_code == 200,
                "public_index_mutated_except_allowed_rebuild_worker": False,
            }
        finally:
            close_local_appliance(runtime)


def create_fixture(runtime: Any) -> dict[str, Any]:
    hunt = runtime.search_hunt.create_session_from_query("sampleproject", runtime=runtime)
    need = runtime.search_need.create_need_from_hunt(runtime, hunt.id, operator_label="validator")
    create_workunits_from_need(runtime, need.id, operator_label="validator")
    source_probe = _find_workunit(runtime, hunt.id, "source_probe")
    extraction = _blocked_fixture_workunit(runtime, need, WorkUnitType.EXTRACTION_TASK, "extraction_worker", "blocked extraction worker fixture")
    ai_model = _blocked_fixture_workunit(runtime, need, WorkUnitType.REGRESSION_TEST, "ai_model_worker", "blocked model worker fixture")
    return {
        "hunt": hunt,
        "need": need,
        "source_probe_id": source_probe.id,
        "extraction_id": extraction.id,
        "ai_id": ai_model.id,
    }


def _find_workunit(runtime: Any, hunt_id: str, kind: str) -> Any:
    for workunit in runtime.workunit_queue.list_workunits(limit=200):
        payload = dict(workunit.payload)
        if payload.get("search_hunt_id") == hunt_id and getattr(workunit.kind, "value", "") == kind:
            return workunit
    raise AssertionError(f"missing linked workunit kind {kind}")


def _blocked_fixture_workunit(runtime: Any, need: Any, kind: WorkUnitType, worker_kind: str, title: str) -> Any:
    payload = {
        "search_need_id": need.id,
        "search_hunt_id": need.hunt_id,
        "exhaustion_report_id": need.exhaustion_report_id,
        "generated_from": "validator_fixture",
        "policy_state": "blocked_by_policy",
        "worker_kind": worker_kind,
        "execution_enabled": False,
        "source_probe_enabled": False,
        "extraction_enabled": False,
        "model_provider_enabled": False,
    }
    workunit = runtime.workunit_queue.create_workunit(WorkUnit.new(kind, title, payload=payload, parent_id=need.id))
    runtime.workunit_queue.block_workunit(workunit.id, "blocked by background hunt validator policy fixture")
    runtime.workunit_queue.record_payload_ref(workunit.id, "search_need", need.id)
    runtime.workunit_queue.record_payload_ref(workunit.id, "search_hunt", need.hunt_id)
    runtime.workunit_queue.record_payload_ref(workunit.id, "exhaustion_report", need.exhaustion_report_id)
    return runtime.workunit_queue.get_workunit(workunit.id)


def validate_cli_and_demo(root: Path, errors: list[str]) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        instance = Path(tmp) / "eureka-instance"
        for name, args in (
            ("init", ("scripts/eureka_init_instance.py", "--instance", str(instance), "--json")),
            ("token", ("scripts/eureka_set_operator_token.py", "--instance", str(instance), "--token", "validator-token", "--json")),
            ("workunits-demo", ("scripts/demo_hunt_to_workunits.py", "--instance", str(instance), "--operator-token", "validator-token", "--json")),
        ):
            completed = run_cmd(root, *args)
            if completed.returncode != 0:
                errors.append(f"{name} command failed: {completed.stderr or completed.stdout}")
                return
        payload = json.loads(completed.stdout)
        hunt_id = payload.get("hunt_id") or payload.get("hunt", {}).get("id")
        for name, args in (
            ("plan", ("scripts/eureka_hunt_runner.py", "--instance", str(instance), "--hunt-id", str(hunt_id), "plan", "--json")),
            ("missing", ("scripts/eureka_hunt_runner.py", "--instance", str(instance), "--hunt-id", str(hunt_id), "run-next", "--json")),
            ("run-next", ("scripts/eureka_hunt_runner.py", "--instance", str(instance), "--hunt-id", str(hunt_id), "--operator-token", "validator-token", "run-next", "--json")),
            ("runs", ("scripts/eureka_hunt_runner.py", "--instance", str(instance), "--hunt-id", str(hunt_id), "runs", "--json")),
            ("summary", ("scripts/eureka_hunt_runner.py", "--instance", str(instance), "--hunt-id", str(hunt_id), "summary", "--json")),
            ("demo", ("scripts/demo_background_hunt_runner.py", "--instance", str(instance), "--operator-token", "validator-token", "--json")),
        ):
            completed = run_cmd(root, *args)
            if name == "missing":
                if completed.returncode == 0:
                    errors.append("runner CLI did not reject missing token")
                continue
            if completed.returncode != 0:
                errors.append(f"{name} command failed: {completed.stderr or completed.stdout}")
            else:
                payload = json.loads(completed.stdout)
                if payload.get("status") != "pass":
                    errors.append(f"{name} command did not pass")


def validate_runtime_imports(root: Path, errors: list[str]) -> None:
    for rel in ("runtime/search/hunt/run_records.py", "runtime/search/hunt/runner.py", "runtime/search/hunt/workunit_runner.py"):
        path = root / rel
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            modules = []
            if isinstance(node, ast.ImportFrom):
                modules.append(node.module or "")
            elif isinstance(node, ast.Import):
                modules.extend(alias.name for alias in node.names)
            for module in modules:
                if any(module == prefix or module.startswith(prefix + ".") for prefix in FORBIDDEN_IMPORT_PREFIXES):
                    errors.append(f"forbidden import in {rel}: {module}")


def validate_runtime_vocabulary(root: Path, errors: list[str]) -> None:
    for rel in ("runtime/search/hunt/run_records.py", "runtime/search/hunt/runner.py", "runtime/search/hunt/workunit_runner.py"):
        text = (root / rel).read_text(encoding="utf-8")
        for marker in FORBIDDEN_RUNTIME_VOCABULARY:
            if marker in text:
                errors.append(f"forbidden runtime vocabulary in {rel}: {marker}")


def validate_queue(root: Path, errors: list[str]) -> None:
    queue = root / ".aide" / "queue" / "index.yaml"
    text = queue.read_text(encoding="utf-8") if queue.is_file() else ""
    if not hunt_queue_current_or_advanced(root, TASK_ID, NEXT_TASK):
        errors.append("queue does not point to HUNT-08")
    decision = load_json(root / "control/inventory/hunt_07_next_task_decision.json", "hunt_07_next_task_decision.v0", errors)
    if not str(decision.get("recommended_next_task", "")).startswith(NEXT_TASK):
        errors.append("hunt_07_next_task_decision does not recommend HUNT-08")


def load_json(path: Path, schema_version: str, errors: list[str]) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"missing json: {path.relative_to(REPO_ROOT) if path.is_absolute() else path}")
        return {}
    except json.JSONDecodeError as exc:
        errors.append(f"invalid json: {path}: {exc}")
        return {}
    if payload.get("schema_version") != schema_version:
        errors.append(f"schema mismatch for {path}: expected {schema_version}")
    return payload


def run_cmd(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["python", *args], cwd=root, text=True, capture_output=True, check=False)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
