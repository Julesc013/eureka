#!/usr/bin/env python3
"""Validate the HUNT-10 deterministic hunt replay harness."""

from __future__ import annotations

import argparse
import ast
import json
import sys
import tempfile
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.hunt_queue_progress import hunt_queue_current_or_advanced
from runtime.local_appliance import close_local_appliance, open_local_appliance
from runtime.local_operator import write_operator_token_record
from runtime.local_operator.auth import build_cli_operator_auth_state
from runtime.local_service import LocalServiceApp
from runtime.search_hunt import (
    BLOCKED_REPLAY_STEP_KINDS,
    ENABLED_REPLAY_STEP_KINDS,
    build_replay_fixture_from_hunt,
    run_hunt_replay,
    verify_existing_hunt_against_replay,
)
from scripts.eureka_hunt_workflow_smoke import run_workflow_smoke
from scripts.eureka_init_instance import initialize_instance


TASK_ID = "HUNT-10"
NEXT_TASK = "HUNT-11"
POLICIES = {
    "control/policies/hunt_replay_policy.json": "hunt_replay_policy.v0",
    "control/policies/hunt_replay_step_policy.json": "hunt_replay_step_policy.v0",
    "control/policies/hunt_replay_side_effect_policy.json": "hunt_replay_side_effect_policy.v0",
    "control/policies/hunt_replay_auth_policy.json": "hunt_replay_auth_policy.v0",
    "control/policies/hunt_replay_non_claim_policy.json": "hunt_replay_non_claim_policy.v0",
    "control/policies/hunt_replay_output_policy.json": "hunt_replay_output_policy.v0",
}
INVENTORIES = {
    "control/inventory/hunt_replay_inventory.json": "hunt_replay_inventory.v0",
    "control/inventory/hunt_replay_step_matrix.json": "hunt_replay_step_matrix.v0",
    "control/inventory/hunt_replay_blocked_step_matrix.json": "hunt_replay_blocked_step_matrix.v0",
    "control/inventory/hunt_replay_result.json": "hunt_replay_result.v0",
    "control/inventory/hunt_replay_demo_result.json": "hunt_replay_demo_result.v0",
    "control/inventory/hunt_replay_gap_register.json": "hunt_replay_gap_register.v0",
    "control/inventory/hunt_10_next_task_decision.json": "hunt_10_next_task_decision.v0",
}
RUNTIME_FILES = (
    "runtime/search_hunt/replay.py",
    "runtime/search_hunt/replay_records.py",
    "runtime/search_hunt/replay_fixtures.py",
    "runtime/search_hunt/replay_diff.py",
    "runtime/search_hunt/replay_validation.py",
    "runtime/search_hunt/schema.py",
    "runtime/search_hunt/store.py",
    "runtime/search_hunt/validation.py",
    "runtime/local_service/routes.py",
    "surfaces/web/workbench/local_html/pages.py",
    "surfaces/web/workbench/local_html/view_models.py",
)
REPLAY_RUNTIME_FILES = (
    "runtime/search_hunt/replay.py",
    "runtime/search_hunt/replay_records.py",
    "runtime/search_hunt/replay_fixtures.py",
    "runtime/search_hunt/replay_diff.py",
    "runtime/search_hunt/replay_validation.py",
)
SCRIPTS = (
    "scripts/eureka_hunt_replay.py",
    "scripts/demo_hunt_replay.py",
    "scripts/validate_hunt_replay.py",
)
DOCS = (
    "docs/architecture/HUNT_REPLAY_HARNESS.md",
    "docs/reference/HUNT_REPLAY_RECORD.md",
    "docs/reference/HUNT_REPLAY_API.md",
    "docs/reference/HUNT_REPLAY_STEP_MATRIX.md",
    "docs/operations/HUNT_REPLAY_RUNBOOK.md",
    "docs/operations/HUNT_REPLAY_BOUNDARIES.md",
)
TESTS = (
    "tests/runtime/test_hunt_replay_records.py",
    "tests/runtime/test_hunt_replay_plan.py",
    "tests/runtime/test_hunt_replay_execution.py",
    "tests/runtime/test_hunt_replay_diff.py",
    "tests/runtime/test_hunt_replay_routes.py",
    "tests/runtime/test_hunt_replay_ui.py",
    "tests/runtime/test_hunt_replay_policy.py",
    "tests/operations/test_hunt_replay_scripts.py",
)
AUDIT_ROOT = Path("control/audits/hunt-10-deterministic-replay-v0")
AUDIT_FILES = (
    "README.md",
    "hunt_10_report.json",
    "replay_harness_summary.md",
    "step_matrix.md",
    "blocked_step_matrix.md",
    "auth_boundary.md",
    "side_effect_boundary.md",
    "replay_diff_summary.md",
    "ui_summary.md",
    "demo_result.md",
    "validation.md",
    "generated/sample_hunt_replay_record.json",
    "generated/sample_hunt_replay_plan.json",
    "generated/sample_hunt_replay_result.json",
    "generated/sample_hunt_replay_diff.json",
    "generated/sample_hunt_replay_page.html",
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
        print("HUNT-10 hunt replay validation", file=stdout)
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
    report = load_json(root / AUDIT_ROOT / "hunt_10_report.json", "hunt_10_report.v0", errors)
    validate_files(root, errors)
    validate_policy_payloads(payloads, errors)
    validate_inventory_payloads(payloads, errors)
    validate_report_payload(report, errors)
    validate_runtime_imports(root, errors)
    validate_runtime_vocabulary(root, errors)
    behavior = validate_behavior(root, errors)
    validate_queue(root, errors)
    status = "fail" if errors else ("pass_with_warnings" if warnings else "pass")
    return {
        "schema_version": "hunt_replay_validation.v0",
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
        "master_index_mutated": False,
        "site_dist_mutated": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def validate_files(root: Path, errors: list[str]) -> None:
    for rel in (*RUNTIME_FILES, *SCRIPTS, *DOCS, *TESTS):
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
    policy = payloads.get("control/policies/hunt_replay_policy.json", {})
    for key in (
        "replay_enabled",
        "deterministic_local_replay_only",
        "plan_only_enabled",
        "replay_local_enabled",
        "verify_existing_enabled",
        "operator_token_required_for_replay_run",
        "localhost_only_replay_run",
    ):
        if policy.get(key) is not True:
            errors.append(f"replay policy {key} must be true")
    for key in (
        "lan_replay_run_enabled",
        "source_probe_execution_enabled",
        "extraction_execution_enabled",
        "ai_model_execution_enabled",
        "agent_research_execution_enabled",
        "external_network_enabled",
        "download_install_execute_enabled",
        "deployment_enabled",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    ):
        if policy.get(key) is not False:
            errors.append(f"replay policy {key} must be false")
    step_policy = payloads.get("control/policies/hunt_replay_step_policy.json", {})
    if set(step_policy.get("enabled_step_kinds", ())) != {item.value for item in ENABLED_REPLAY_STEP_KINDS}:
        errors.append("step policy enabled_step_kinds mismatch")
    if set(step_policy.get("blocked_step_kinds", ())) != {item.value for item in BLOCKED_REPLAY_STEP_KINDS}:
        errors.append("step policy blocked_step_kinds mismatch")
    side = payloads.get("control/policies/hunt_replay_side_effect_policy.json", {})
    for key in ("replay_store_mutation_allowed", "temp_instance_mutation_allowed", "existing_instance_mutation_allowed_only_with_operator_token", "workunit_state_mutation_allowed_for_safe_worker_replay"):
        if side.get(key) is not True:
            errors.append(f"side-effect policy {key} must be true")
    for key in ("source_probe_allowed", "extraction_allowed", "external_network_allowed", "model_provider_allowed", "download_allowed", "install_execution_allowed", "source_sync_allowed", "lan_operations_allowed", "deployment_allowed", "site_dist_writes_allowed", "master_index_mutation_allowed"):
        if side.get(key) is not False:
            errors.append(f"side-effect policy {key} must be false")
    auth = payloads.get("control/policies/hunt_replay_auth_policy.json", {})
    if auth.get("replay_run_requires_operator_token") is not True or auth.get("localhost_only_run") is not True:
        errors.append("auth policy must require token and localhost run")
    if auth.get("plan_requires_token") is not False or auth.get("lan_run_forbidden") is not True:
        errors.append("auth policy plan/LAN boundary mismatch")


def validate_inventory_payloads(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    result = payloads.get("control/inventory/hunt_replay_result.json", {})
    for key in (
        "replay_runtime_added",
        "replay_store_added",
        "cli_added",
        "demo_added",
        "validator_added",
        "plan_only_passed",
        "replay_local_passed",
        "verify_existing_passed",
        "replay_diff_present",
        "blocked_source_probe_remained_blocked",
        "blocked_extraction_remained_blocked",
        "blocked_ai_model_remained_blocked",
        "missing_token_rejected",
        "invalid_token_rejected",
        "lan_replay_run_blocked",
        "ui_routes_added",
        "api_routes_added",
    ):
        if result.get(key) is not True:
            errors.append(f"result inventory {key} must be true")
    for key in (
        "source_probe_executed",
        "extraction_executed",
        "external_network_used",
        "model_provider_used",
        "download_install_execute_performed",
        "master_index_mutated",
        "site_dist_mutated",
        "deployment_performed",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    ):
        if result.get(key) is not False:
            errors.append(f"result inventory {key} must be false")
    next_task = payloads.get("control/inventory/hunt_10_next_task_decision.json", {})
    if "HUNT-11" not in str(next_task.get("recommended_next_task", "")):
        errors.append("next task decision must recommend HUNT-11")


def validate_report_payload(report: Mapping[str, Any], errors: list[str]) -> None:
    if report.get("status") != "pass":
        errors.append("hunt_10_report status must be pass")
    for key in ("replay_runtime_added", "replay_store_added", "cli_added", "demo_added", "validator_added", "plan_only_passed", "replay_local_passed", "verify_existing_passed"):
        if report.get(key) is not True:
            errors.append(f"hunt_10_report {key} must be true")
    for key in ("source_probe_executed", "extraction_executed", "external_network_used", "model_provider_used", "master_index_mutated", "site_dist_mutated", "deployment_performed"):
        if report.get(key) is not False:
            errors.append(f"hunt_10_report {key} must be false")


def validate_runtime_imports(root: Path, errors: list[str]) -> None:
    for rel in REPLAY_RUNTIME_FILES:
        path = root / rel
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except SyntaxError as exc:
            errors.append(f"syntax error in {rel}: {exc}")
            continue
        for node in ast.walk(tree):
            imported: list[str] = []
            if isinstance(node, ast.Import):
                imported.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.append(node.module)
            for module in imported:
                if any(module == prefix or module.startswith(prefix + ".") for prefix in FORBIDDEN_IMPORT_PREFIXES):
                    errors.append(f"forbidden import in {rel}: {module}")


def validate_runtime_vocabulary(root: Path, errors: list[str]) -> None:
    for rel in REPLAY_RUNTIME_FILES:
        text = (root / rel).read_text(encoding="utf-8")
        for token in FORBIDDEN_RUNTIME_VOCABULARY:
            if token in text:
                errors.append(f"runtime replay file contains forbidden task vocabulary {token}: {rel}")


def validate_behavior(root: Path, errors: list[str]) -> dict[str, Any]:
    result = {
        "plan_only_passed": False,
        "replay_local_passed": False,
        "verify_existing_passed": False,
        "replay_diff_present": False,
        "blocked_source_probe_remained_blocked": False,
        "blocked_extraction_remained_blocked": False,
        "blocked_ai_model_remained_blocked": False,
        "missing_token_rejected": False,
        "invalid_token_rejected": False,
        "lan_replay_run_blocked": False,
        "ui_routes_added": False,
        "api_routes_added": False,
    }
    with tempfile.TemporaryDirectory() as tmp:
        instance = Path(tmp) / "eureka-instance"
        initialize_instance(instance)
        write_operator_token_record(instance, "validator-token")
        runtime = open_local_appliance(instance)
        try:
            workflow = run_workflow_smoke(runtime, query="sampleproject", missing_query="definitely-not-present-hunt-10")
            hunt_id = str(workflow["hunt_id"])
            runtime.agent_research.draft_task_from_hunt(runtime, hunt_id, operator_label="validator")
            fixture = build_replay_fixture_from_hunt(runtime, hunt_id)
            plan = run_hunt_replay(runtime, fixture, mode="plan_only")
            replay = run_hunt_replay(runtime, fixture, operator_context={"authorized": True, "operator_label": "validator"}, mode="replay_local")
            verify = verify_existing_hunt_against_replay(runtime, hunt_id, fixture)
            stored = runtime.search_hunt.get_replay_result(replay.record.replay_id)
            result["plan_only_passed"] = plan.mode.value == "plan_only" and plan.record.status in {"planned", "pass"}
            result["replay_local_passed"] = replay.mode.value == "replay_local" and replay.record.status == "pass" and stored is not None
            result["verify_existing_passed"] = verify.mode.value == "verify_existing" and verify.record.status == "pass"
            result["replay_diff_present"] = bool(replay.record.diff_summary.to_dict())
            blocked = {item.kind.value for item in fixture.blocked_steps}
            result["blocked_source_probe_remained_blocked"] = "run_source_probe" in blocked
            result["blocked_extraction_remained_blocked"] = "run_extraction" in blocked
            result["blocked_ai_model_remained_blocked"] = "run_ai_model" in blocked
            if replay.to_dict()["source_probe_executed"] or replay.to_dict()["extraction_executed"] or replay.to_dict()["model_provider_used"]:
                errors.append("replay result reported forbidden execution")
            app = LocalServiceApp(runtime, operator_auth_state=build_cli_operator_auth_state("validator-token"))
            api_get = app.handle("GET", f"/api/v1/hunt/{hunt_id}/replay")
            html_get = app.handle("GET", f"/hunt/{hunt_id}/replay")
            plan_route = app.handle("POST", f"/api/v1/hunt/{hunt_id}/replay/plan")
            missing = app.handle("POST", f"/api/v1/hunt/{hunt_id}/replay/run")
            invalid = app.handle("POST", f"/api/v1/hunt/{hunt_id}/replay/run", body="operator_token=bad")
            lan = app.handle("POST", f"/api/v1/hunt/{hunt_id}/replay/run", client_host="192.168.1.20", body="operator_token=validator-token")
            run = app.handle("POST", f"/api/v1/hunt/{hunt_id}/replay/run", body="operator_token=validator-token")
            result["api_routes_added"] = api_get.status_code == 200 and plan_route.status_code == 200 and run.status_code == 200
            result["ui_routes_added"] = html_get.status_code == 200 and "Deterministic hunt replay" in html_get.body
            result["missing_token_rejected"] = missing.status_code == 401
            result["invalid_token_rejected"] = invalid.status_code == 401
            result["lan_replay_run_blocked"] = lan.status_code == 403
            if "download artifact" in html_get.body.lower() or "install or execute artifact" in html_get.body.lower():
                errors.append("replay UI exposed forbidden future-action wording")
        finally:
            close_local_appliance(runtime)
    for key, value in result.items():
        if value is not True:
            errors.append(f"behavior check failed: {key}")
    return result


def validate_queue(root: Path, errors: list[str]) -> None:
    index = root / ".aide/queue/index.yaml"
    text = index.read_text(encoding="utf-8") if index.is_file() else ""
    if not hunt_queue_current_or_advanced(root, TASK_ID, NEXT_TASK):
        errors.append("queue index must point to HUNT-11")
    if not (root / ".aide/queue/HUNT-11/task.yaml").is_file():
        errors.append("missing HUNT-11 queue task")


def load_json(path: Path, schema_version: str, errors: list[str]) -> Mapping[str, Any]:
    if not path.is_file():
        errors.append(f"missing json file: {path.as_posix()}")
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"invalid json in {path.as_posix()}: {exc}")
        return {}
    if payload.get("schema_version") != schema_version:
        errors.append(f"{path.as_posix()} schema_version must be {schema_version}")
    return payload


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
