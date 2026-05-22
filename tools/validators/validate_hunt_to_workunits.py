#!/usr/bin/env python3
"""Validate the HUNT-06 SearchNeed-to-WorkUnit pipeline."""

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
from runtime.local_appliance import close_local_appliance, open_local_appliance
from runtime.local_operator.auth import build_cli_operator_auth_state
from runtime.local_service import LocalServiceApp
from runtime.search_need import (
    SearchNeedKind,
    build_workunit_plan_for_need,
    create_workunits_from_need,
    list_workunits_for_hunt,
    list_workunits_for_need,
)


TASK_ID = "HUNT-06"
NEXT_TASK = "HUNT-07"
POLICIES = {
    "control/policies/hunt_to_workunit_policy.json": "hunt_to_workunit_policy.v0",
    "control/policies/search_need_workunit_policy.json": "search_need_workunit_policy.v0",
    "control/policies/search_need_workunit_side_effect_policy.json": "search_need_workunit_side_effect_policy.v0",
    "control/policies/search_need_workunit_auth_policy.json": "search_need_workunit_auth_policy.v0",
    "control/policies/search_need_workunit_ui_policy.json": "search_need_workunit_ui_policy.v0",
    "control/policies/search_need_workunit_non_claim_policy.json": "search_need_workunit_non_claim_policy.v0",
}
INVENTORIES = {
    "control/inventory/hunt_to_workunit_inventory.json": "hunt_to_workunit_inventory.v0",
    "control/inventory/hunt_to_workunit_kind_matrix.json": "hunt_to_workunit_kind_matrix.v0",
    "control/inventory/hunt_to_workunit_policy_matrix.json": "hunt_to_workunit_policy_matrix.v0",
    "control/inventory/hunt_to_workunit_result.json": "hunt_to_workunit_result.v0",
    "control/inventory/search_need_workunit_link_result.json": "search_need_workunit_link_result.v0",
    "control/inventory/hunt_to_workunit_demo_result.json": "hunt_to_workunit_demo_result.v0",
    "control/inventory/hunt_to_workunit_gap_register.json": "hunt_to_workunit_gap_register.v0",
    "control/inventory/hunt_06_next_task_decision.json": "hunt_06_next_task_decision.v0",
}
REQUIRED_FILES = (
    "runtime/search_need/workunit_plan.py",
    "runtime/search_need/workunits.py",
    "scripts/eureka_need_to_workunits.py",
    "scripts/demo_hunt_to_workunits.py",
    "scripts/validate_hunt_to_workunits.py",
    "tests/runtime/test_need_to_workunit_plan.py",
    "tests/runtime/test_need_to_workunit_creation.py",
    "tests/runtime/test_need_workunit_links.py",
    "tests/runtime/test_need_workunit_routes.py",
    "tests/runtime/test_need_workunit_ui.py",
    "tests/runtime/test_need_workunit_auth.py",
    "tests/operations/test_need_to_workunit_scripts.py",
    "docs/architecture/HUNT_TO_WORKUNIT_PIPELINE.md",
    "docs/reference/HUNT_TO_WORKUNIT_PLAN.md",
    "docs/reference/SEARCH_NEED_WORKUNIT_LINKS.md",
    "docs/reference/HUNT_WORKUNIT_API.md",
    "docs/operations/HUNT_TO_WORKUNIT_RUNBOOK.md",
    "docs/operations/HUNT_TO_WORKUNIT_BOUNDARIES.md",
)
AUDIT_ROOT = Path("control/audits/hunt-06-hunt-to-workunit-v0")
AUDIT_FILES = (
    "README.md",
    "hunt_06_report.json",
    "workunit_plan_summary.md",
    "kind_matrix.md",
    "policy_matrix.md",
    "auth_boundary.md",
    "side_effect_boundary.md",
    "ui_summary.md",
    "demo_result.md",
    "validation.md",
    "generated/sample_workunit_plan.json",
    "generated/sample_created_workunits.json",
    "generated/sample_search_need_with_workunits.html",
    "generated/sample_hunt_with_workunits.html",
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
        print("HUNT-06 Hunt-to-WorkUnit validation", file=stdout)
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
    report = load_json(root / AUDIT_ROOT / "hunt_06_report.json", "hunt_06_report.v0", errors)
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
        "schema_version": "hunt_to_workunit_validation.v0",
        "task": TASK_ID,
        "status": status,
        "errors": errors,
        "warnings": warnings,
        **behavior,
        "validator_added": True,
        "workunit_execution_performed": False,
        "source_probe_executed": False,
        "extraction_executed": False,
        "external_network_used": False,
        "model_provider_used": False,
        "review_mutation_performed": False,
        "public_index_mutated": False,
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
    policy = payloads.get("control/policies/hunt_to_workunit_policy.json", {})
    if policy.get("workunit_creation_from_search_need_enabled") is not True:
        errors.append("hunt_to_workunit policy must enable creation from SearchNeed")
    for key in (
        "workunit_execution_enabled",
        "source_probe_execution_enabled",
        "extraction_execution_enabled",
        "model_provider_enabled",
        "public_index_mutation_enabled",
        "master_index_mutation_enabled",
        "deployment_enabled",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    ):
        if policy.get(key) is not False:
            errors.append(f"hunt_to_workunit policy {key} must be false")
    auth = payloads.get("control/policies/search_need_workunit_auth_policy.json", {})
    for key in ("generation_requires_operator_token", "persist_requires_token", "localhost_only_mutation", "lan_mutation_forbidden", "missing_token_rejected", "invalid_token_rejected"):
        if auth.get(key) is not True:
            errors.append(f"auth policy {key} must be true")


def validate_inventory_payloads(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    inventory = payloads.get("control/inventory/hunt_to_workunit_inventory.json", {})
    if inventory.get("workunit_creation_from_search_need_enabled") is not True:
        errors.append("inventory must enable workunit creation from SearchNeed")
    for key in ("workunit_execution_enabled", "source_probe_execution_enabled", "extraction_execution_enabled", "model_provider_enabled", "deployment_performed"):
        if inventory.get(key) is not False:
            errors.append(f"inventory {key} must be false")
    matrix = payloads.get("control/inventory/hunt_to_workunit_kind_matrix.json", {})
    rows = matrix.get("rows", [])
    if len(rows) != len(SearchNeedKind):
        errors.append("kind matrix must cover every SearchNeed kind")
    next_task = payloads.get("control/inventory/hunt_06_next_task_decision.json", {})
    if not str(next_task.get("recommended_next_task", "")).startswith(NEXT_TASK):
        errors.append("next task must be HUNT-07")
    if next_task.get("workunit_execution_enabled") is not False:
        errors.append("next task decision must keep WorkUnit execution disabled")


def validate_report_payload(report: Mapping[str, Any], errors: list[str]) -> None:
    for key in (
        "workunit_plan_added",
        "workunit_creation_added",
        "cli_added",
        "demo_added",
        "validator_added",
        "plan_preview_passed",
        "workunit_creation_passed",
        "workunits_linked_to_need",
        "workunits_linked_to_hunt",
        "workunits_linked_to_exhaustion",
        "blocked_policy_workunits_created_as_blocked",
        "missing_token_rejected",
        "invalid_token_rejected",
        "lan_creation_blocked",
        "ui_routes_added",
        "api_routes_added",
    ):
        if report.get(key) is not True:
            errors.append(f"hunt_06_report {key} must be true")
    for key in (
        "workunit_execution_performed",
        "source_probe_executed",
        "extraction_executed",
        "external_network_used",
        "model_provider_used",
        "review_mutation_performed",
        "public_index_mutated",
        "master_index_mutated",
        "deployment_performed",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    ):
        if report.get(key) is not False:
            errors.append(f"hunt_06_report {key} must be false")


def validate_behavior(root: Path, errors: list[str]) -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as tmp:
        instance = Path(tmp) / "eureka-instance"
        init = run_cmd(root, "scripts/eureka_init_instance.py", "--instance", str(instance), "--json")
        if init.returncode != 0:
            errors.append(f"instance init failed: {init.stderr or init.stdout}")
            return {}
        runtime = open_local_appliance(instance, read_only=False)
        try:
            before_public = runtime.public_index.summarize().to_dict()
            hunt = runtime.search_hunt.create_session_from_query("sampleproject", runtime=runtime)
            need = runtime.search_need.create_need_from_hunt(runtime, hunt.id, operator_label="validator")
            before_work_count = runtime.workunit_queue.summarize().total
            plan = build_workunit_plan_for_need(runtime, need.id, operator_label="validator")
            after_plan_count = runtime.workunit_queue.summarize().total
            result = create_workunits_from_need(runtime, need.id, operator_label="validator")
            duplicate = create_workunits_from_need(runtime, need.id, operator_label="validator")
            by_need = list_workunits_for_need(runtime, need.id)
            by_hunt = list_workunits_for_hunt(runtime, hunt.id)
            after_public = runtime.public_index.summarize().to_dict()

            app = LocalServiceApp(runtime, operator_auth_state=build_cli_operator_auth_state("validator-token"))
            missing = app.handle("POST", f"/need/{need.id}/workunits")
            invalid = app.handle("POST", f"/need/{need.id}/workunits", body="operator_token=bad")
            lan = app.handle("POST", f"/need/{need.id}/workunits", client_host="192.168.1.20", body="operator_token=validator-token")
            route_plan = app.handle("POST", f"/api/v1/need/{need.id}/workunits/plan", body="operator_token=validator-token")
            route_create = app.handle("POST", f"/api/v1/need/{need.id}/workunits", body="operator_token=validator-token")
            route_list = app.handle("GET", f"/api/v1/need/{need.id}/workunits")
            route_hunt = app.handle("GET", f"/api/v1/hunt/{hunt.id}/workunits")
            need_page = app.handle("GET", f"/need/{need.id}")
            hunt_page = app.handle("GET", f"/hunt/{hunt.id}")

            if after_plan_count != before_work_count:
                errors.append("plan preview persisted WorkUnits")
            if len(result.workunits) != len(plan.items):
                errors.append("created WorkUnit count did not match plan")
            if len(duplicate.workunits) != len(result.workunits):
                errors.append("duplicate WorkUnit persistence changed result count")
            if len(by_need) != len(by_hunt):
                errors.append("WorkUnits linked to need and hunt differ")
            if not any(item.get("state") == "blocked" for item in by_need):
                errors.append("blocked policy WorkUnits were not created as blocked")
            if any(item.get("state") in {"running", "complete", "failed"} for item in by_need):
                errors.append("WorkUnits were run during validation")
            if before_public != after_public:
                errors.append("public index changed during HUNT-06 validation")
            for name, response in (
                ("route plan", route_plan),
                ("route create", route_create),
                ("route list", route_list),
                ("route hunt", route_hunt),
                ("need page", need_page),
                ("hunt page", hunt_page),
            ):
                if response.status_code != 200:
                    errors.append(f"{name} failed: {response.status_code} {response.payload}")
            if missing.status_code != 401:
                errors.append("missing operator token was not rejected")
            if invalid.status_code != 401:
                errors.append("invalid operator token was not rejected")
            if lan.status_code != 403:
                errors.append("LAN WorkUnit creation was not blocked")

            return {
                "workunit_plan_added": bool(plan.items),
                "workunit_creation_added": len(result.workunits) == len(plan.items),
                "plan_preview_passed": after_plan_count == before_work_count,
                "workunit_creation_passed": len(by_need) == len(plan.items),
                "workunits_linked_to_need": all(item.get("search_need_id") == need.id for item in by_need),
                "workunits_linked_to_hunt": all(item.get("search_hunt_id") == hunt.id for item in by_need),
                "workunits_linked_to_exhaustion": all(item.get("exhaustion_report_id") == need.exhaustion_report_id for item in by_need),
                "blocked_policy_workunits_created_as_blocked": any(item.get("state") == "blocked" for item in by_need),
                "missing_token_rejected": missing.status_code == 401,
                "invalid_token_rejected": invalid.status_code == 401,
                "lan_creation_blocked": lan.status_code == 403,
                "ui_routes_added": need_page.status_code == 200 and hunt_page.status_code == 200,
                "api_routes_added": route_list.status_code == 200 and route_hunt.status_code == 200,
            }
        finally:
            close_local_appliance(runtime)


def validate_cli_and_demo(root: Path, errors: list[str]) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        instance = Path(tmp) / "eureka-instance"
        commands = [
            ("init", ("scripts/eureka_init_instance.py", "--instance", str(instance), "--json")),
            ("token", ("scripts/eureka_set_operator_token.py", "--instance", str(instance), "--token", "validator-token", "--json")),
            ("hunt", ("scripts/eureka_search_hunt.py", "--instance", str(instance), "create", "--query", "sampleproject", "--json")),
        ]
        outputs: dict[str, dict[str, Any]] = {}
        for name, args in commands:
            completed = run_cmd(root, *args)
            if completed.returncode != 0:
                errors.append(f"{name} command failed: {completed.stderr or completed.stdout}")
                return
            outputs[name] = json.loads(completed.stdout)
        hunt_id = outputs["hunt"]["session"]["id"]
        need_cmd = run_cmd(root, "scripts/eureka_hunt_to_search_need.py", "--instance", str(instance), "--operator-token", "validator-token", "--hunt-id", hunt_id, "--json")
        if need_cmd.returncode != 0:
            errors.append(f"hunt_to_need command failed: {need_cmd.stderr or need_cmd.stdout}")
            return
        need_id = json.loads(need_cmd.stdout)["need"]["id"]
        for name, args in (
            ("plan", ("scripts/eureka_need_to_workunits.py", "--instance", str(instance), "--need-id", need_id, "--plan-only", "--json")),
            ("create", ("scripts/eureka_need_to_workunits.py", "--instance", str(instance), "--need-id", need_id, "--operator-token", "validator-token", "--create", "--json")),
            ("list", ("scripts/eureka_search_need.py", "--instance", str(instance), "workunits", "--id", need_id, "--json")),
            ("demo", ("scripts/demo_hunt_to_workunits.py", "--instance", str(instance), "--operator-token", "validator-token", "--json")),
        ):
            completed = run_cmd(root, *args)
            if completed.returncode != 0:
                errors.append(f"{name} command failed: {completed.stderr or completed.stdout}")
            else:
                payload = json.loads(completed.stdout)
                if payload.get("status") != "pass":
                    errors.append(f"{name} command did not pass")


def validate_runtime_imports(root: Path, errors: list[str]) -> None:
    for rel in ("runtime/search_need/workunit_plan.py", "runtime/search_need/workunits.py"):
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
    for rel in ("runtime/search_need/workunit_plan.py", "runtime/search_need/workunits.py"):
        text = (root / rel).read_text(encoding="utf-8")
        for marker in FORBIDDEN_RUNTIME_VOCABULARY:
            if marker in text:
                errors.append(f"forbidden runtime vocabulary in {rel}: {marker}")


def validate_queue(root: Path, errors: list[str]) -> None:
    queue = root / ".aide" / "queue" / "index.yaml"
    text = queue.read_text(encoding="utf-8") if queue.is_file() else ""
    if not hunt_queue_current_or_advanced(root, TASK_ID, NEXT_TASK):
        errors.append("queue does not point to HUNT-07")
    decision = load_json(root / "control/inventory/hunt_06_next_task_decision.json", "hunt_06_next_task_decision.v0", errors)
    if not str(decision.get("recommended_next_task", "")).startswith(NEXT_TASK):
        errors.append("hunt_06_next_task_decision does not recommend HUNT-07")


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
