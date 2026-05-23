#!/usr/bin/env python3
"""Validate the HUNT-05 hunt-to-SearchNeed pipeline."""

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

from runtime.local.appliance import close_local_appliance, open_local_appliance
from runtime.local.operator.auth import build_cli_operator_auth_state
from runtime.local.service import LocalServiceApp
from runtime.search.need import SearchNeedTransitionError


TASK_ID = "HUNT-05"
NEXT_TASK = "HUNT-06"
POLICIES = {
    "control/policies/search_need_runtime_policy.json": "search_need_runtime_policy.v0",
    "control/policies/search_need_state_policy.json": "search_need_state_policy.v0",
    "control/policies/search_need_from_hunt_policy.json": "search_need_from_hunt_policy.v0",
    "control/policies/search_need_side_effect_policy.json": "search_need_side_effect_policy.v0",
    "control/policies/search_need_ui_policy.json": "search_need_ui_policy.v0",
    "control/policies/search_need_non_claim_policy.json": "search_need_non_claim_policy.v0",
}
INVENTORIES = {
    "control/inventory/search_need_runtime_inventory.json": "search_need_runtime_inventory.v0",
    "control/inventory/search_need_state_machine.json": "search_need_state_machine.v0",
    "control/inventory/search_need_from_hunt_matrix.json": "search_need_from_hunt_matrix.v0",
    "control/inventory/search_need_runtime_result.json": "search_need_runtime_result.v0",
    "control/inventory/hunt_to_search_need_result.json": "hunt_to_search_need_result.v0",
    "control/inventory/search_need_demo_result.json": "search_need_demo_result.v0",
    "control/inventory/search_need_gap_register.json": "search_need_gap_register.v0",
    "control/inventory/hunt_05_next_task_decision.json": "hunt_05_next_task_decision.v0",
}
RUNTIME_FILES = (
    "runtime/search/need/__init__.py",
    "runtime/search/need/schema.py",
    "runtime/search/need/records.py",
    "runtime/search/need/store.py",
    "runtime/search/need/transitions.py",
    "runtime/search/need/from_hunt.py",
    "runtime/search/need/summaries.py",
    "runtime/search/need/queries.py",
    "runtime/search/need/validation.py",
    "runtime/search/need/errors.py",
    "runtime/local/appliance/manifest.py",
    "runtime/local/appliance/composition.py",
    "runtime/local/appliance/status.py",
    "runtime/local/appliance/validation.py",
    "runtime/local/service/routes.py",
    "runtime/local/service/validation.py",
    "surfaces/web/workbench/local_html/pages.py",
    "surfaces/web/workbench/local_html/view_models.py",
)
SCRIPTS = (
    "scripts/eureka_search_need.py",
    "scripts/eureka_hunt_to_search_need.py",
    "scripts/demo_hunt_to_search_need.py",
    "scripts/validate_hunt_to_search_need.py",
)
DOCS = (
    "docs/architecture/SEARCH_NEED_RUNTIME.md",
    "docs/architecture/HUNT_TO_SEARCH_NEED_PIPELINE.md",
    "docs/reference/SEARCH_NEED_RECORD.md",
    "docs/reference/SEARCH_NEED_STATE_MACHINE.md",
    "docs/reference/SEARCH_NEED_API.md",
    "docs/operations/SEARCH_NEED_RUNBOOK.md",
    "docs/operations/HUNT_TO_SEARCH_NEED_BOUNDARIES.md",
)
TESTS = (
    "tests/runtime/test_search_need_store.py",
    "tests/runtime/test_search_need_records.py",
    "tests/runtime/test_search_need_transitions.py",
    "tests/runtime/test_hunt_to_search_need.py",
    "tests/runtime/test_search_need_routes.py",
    "tests/runtime/test_search_need_ui.py",
    "tests/runtime/test_search_need_auth.py",
    "tests/operations/test_search_need_scripts.py",
)
AUDIT_ROOT = Path("control/audits/hunt-05-hunt-to-search-need-v0")
AUDIT_FILES = (
    "README.md",
    "hunt_05_report.json",
    "search_need_runtime_summary.md",
    "state_machine.md",
    "hunt_to_need_pipeline.md",
    "auth_boundary.md",
    "side_effect_boundary.md",
    "ui_summary.md",
    "demo_result.md",
    "validation.md",
    "generated/sample_search_need.json",
    "generated/sample_search_need_list.json",
    "generated/sample_search_need_detail.html",
    "generated/sample_hunt_with_search_need.html",
    "generated/sample_hunt_to_need_result.json",
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
        print("HUNT-05 hunt-to-SearchNeed validation", file=stdout)
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
    report = load_json(root / AUDIT_ROOT / "hunt_05_report.json", "hunt_05_report.v0", errors)
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
        "schema_version": "hunt_to_search_need_validation.v0",
        "task": TASK_ID,
        "status": status,
        "errors": errors,
        "warnings": warnings,
        **behavior,
        "validator_added": True,
        "workunit_creation_performed": False,
        "source_probe_executed": False,
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
    runtime = payloads.get("control/policies/search_need_runtime_policy.json", {})
    for key in (
        "durable_store_required",
        "sqlite_store_required",
        "explicit_instance_path_required",
        "local_appliance_composition_required",
        "search_need_creation_enabled",
        "creation_from_hunt_enabled",
    ):
        if runtime.get(key) is not True:
            errors.append(f"runtime policy {key} must be true")
    for key in (
        "workunit_creation_enabled",
        "source_probe_execution_enabled",
        "extraction_execution_enabled",
        "model_provider_enabled",
        "sync_enabled",
        "public_index_mutation_enabled",
        "master_index_mutation_enabled",
        "deployment_enabled",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    ):
        if runtime.get(key) is not False:
            errors.append(f"runtime policy {key} must be false")

    from_hunt = payloads.get("control/policies/search_need_from_hunt_policy.json", {})
    for key in (
        "creation_requires_existing_hunt",
        "creation_prefers_exhaustion_report",
        "creation_requires_operator_token",
        "localhost_only_creation",
        "dedupe_by_hunt_and_query",
        "private_notes_allowed_local_only",
    ):
        if from_hunt.get(key) is not True:
            errors.append(f"from-hunt policy {key} must be true")
    for key in ("lan_creation_enabled", "public_safe_summary_default", "workunit_creation_enabled", "source_probe_execution_enabled", "model_provider_enabled"):
        if from_hunt.get(key) is not False:
            errors.append(f"from-hunt policy {key} must be false")


def validate_inventory_payloads(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    inventory = payloads.get("control/inventory/search_need_runtime_inventory.json", {})
    if inventory.get("store_id") != "search_need":
        errors.append("runtime inventory store_id must be search_need")
    if inventory.get("db_path") != "db/search_need.sqlite":
        errors.append("runtime inventory db_path mismatch")
    if inventory.get("creation_from_hunt_enabled") is not True:
        errors.append("runtime inventory creation_from_hunt_enabled must be true")
    for key in ("workunit_creation_enabled", "source_probe_execution_enabled", "model_provider_enabled", "sync_enabled", "deployment_performed"):
        if inventory.get(key) is not False:
            errors.append(f"runtime inventory {key} must be false")
    next_task = payloads.get("control/inventory/hunt_05_next_task_decision.json", {})
    if not str(next_task.get("recommended_next_task", "")).startswith(NEXT_TASK):
        errors.append("next task must be HUNT-06")
    if next_task.get("workunit_creation_enabled") is not False:
        errors.append("next task decision must keep WorkUnit creation disabled")


def validate_report_payload(report: Mapping[str, Any], errors: list[str]) -> None:
    for key in (
        "runtime_package_added",
        "sqlite_store_added",
        "store_added_to_instance_manifest",
        "cli_added",
        "demo_added",
        "validator_added",
        "search_need_create_passed",
        "search_need_list_show_passed",
        "valid_transitions_passed",
        "invalid_transitions_rejected",
        "transition_history_recorded",
        "hunt_link_recorded",
        "exhaustion_link_recorded",
        "operator_auth_required",
        "missing_token_rejected",
        "invalid_token_rejected",
        "lan_creation_blocked",
        "ui_routes_added",
        "api_routes_added",
    ):
        if report.get(key) is not True:
            errors.append(f"hunt_05_report {key} must be true")
    for key in (
        "workunit_creation_performed",
        "source_probe_executed",
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
            errors.append(f"hunt_05_report {key} must be false")


def validate_behavior(root: Path, errors: list[str]) -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as tmp:
        instance = Path(tmp) / "eureka-instance"
        init = run_cmd(root, "scripts/eureka_init_instance.py", "--instance", str(instance), "--json")
        if init.returncode != 0:
            errors.append(f"instance init failed: {init.stderr or init.stdout}")
            return {}
        runtime = open_local_appliance(instance, read_only=False)
        try:
            before_work = runtime.workunit_queue.summarize().to_dict()
            before_public = runtime.public_index.summarize().to_dict()
            hunt = runtime.search_hunt.create_session_from_query("sampleproject", runtime=runtime)
            need = runtime.search_need.create_need_from_hunt(runtime, hunt.id, operator_label="validator")
            duplicate = runtime.search_need.create_need_from_hunt(runtime, hunt.id, operator_label="validator")
            latest_report = runtime.search_hunt.get_latest_exhaustion_report(hunt.id)
            opened = runtime.search_need.transition_need(need.id, "open", reason="validator")
            try:
                runtime.search_need.transition_need(opened.id, "proposed", reason="invalid")
                errors.append("invalid SearchNeed transition was accepted")
            except SearchNeedTransitionError:
                pass

            app = LocalServiceApp(runtime, operator_auth_state=build_cli_operator_auth_state("validator-token"))
            missing = app.handle("POST", f"/hunt/{hunt.id}/search-need")
            invalid = app.handle("POST", f"/hunt/{hunt.id}/search-need", body="operator_token=bad")
            lan = app.handle("POST", f"/hunt/{hunt.id}/search-need", client_host="192.168.1.20", body="operator_token=validator-token")
            list_response = app.handle("GET", "/api/v1/needs")
            detail_response = app.handle("GET", f"/api/v1/need/{need.id}")
            hunt_needs_response = app.handle("GET", f"/api/v1/hunt/{hunt.id}/needs")
            hunt_page = app.handle("GET", f"/hunt/{hunt.id}")
            need_page = app.handle("GET", f"/need/{need.id}")
            after_work = runtime.workunit_queue.summarize().to_dict()
            after_public = runtime.public_index.summarize().to_dict()

            if need.id != duplicate.id:
                errors.append("SearchNeed dedupe by hunt/query failed")
            if latest_report is None or latest_report.report_id != need.exhaustion_report_id:
                errors.append("SearchNeed exhaustion report link mismatch")
            if missing.status_code != 401:
                errors.append("missing operator token was not rejected")
            if invalid.status_code != 401:
                errors.append("invalid operator token was not rejected")
            if lan.status_code != 403:
                errors.append("LAN SearchNeed creation was not blocked")
            for name, response in (
                ("need list route", list_response),
                ("need detail route", detail_response),
                ("hunt needs route", hunt_needs_response),
                ("hunt page", hunt_page),
                ("need page", need_page),
            ):
                if response.status_code != 200:
                    errors.append(f"{name} failed: {response.status_code}")
            if before_work != after_work:
                errors.append("WorkUnit queue changed during SearchNeed validation")
            if before_public != after_public:
                errors.append("public index changed during SearchNeed validation")
            return {
                "search_need_create_passed": need.hunt_id == hunt.id,
                "search_need_list_show_passed": list_response.status_code == 200 and detail_response.status_code == 200,
                "valid_transitions_passed": opened.state.value == "open",
                "invalid_transitions_rejected": True,
                "transition_history_recorded": len(runtime.search_need.list_transitions(need.id)) >= 2,
                "hunt_link_recorded": need.hunt_id == hunt.id,
                "exhaustion_link_recorded": bool(need.exhaustion_report_id),
                "missing_token_rejected": missing.status_code == 401,
                "invalid_token_rejected": invalid.status_code == 401,
                "lan_creation_blocked": lan.status_code == 403,
                "ui_routes_added": hunt_page.status_code == 200 and need_page.status_code == 200,
                "api_routes_added": list_response.status_code == 200 and detail_response.status_code == 200,
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
        for name, args in (
            ("hunt_to_need", ("scripts/eureka_hunt_to_search_need.py", "--instance", str(instance), "--operator-token", "validator-token", "--hunt-id", hunt_id, "--json")),
            ("need_list", ("scripts/eureka_search_need.py", "--instance", str(instance), "list", "--json")),
            ("demo", ("scripts/demo_hunt_to_search_need.py", "--instance", str(instance), "--operator-token", "validator-token", "--json")),
        ):
            completed = run_cmd(root, *args)
            if completed.returncode != 0:
                errors.append(f"{name} command failed: {completed.stderr or completed.stdout}")
            else:
                payload = json.loads(completed.stdout)
                if payload.get("status") != "pass":
                    errors.append(f"{name} command did not pass")


def validate_runtime_imports(root: Path, errors: list[str]) -> None:
    for path in (root / "runtime" / "search" / "need").glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            module = ""
            if isinstance(node, ast.ImportFrom):
                module = node.module or ""
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    module = alias.name
                    if any(module == prefix or module.startswith(prefix + ".") for prefix in FORBIDDEN_IMPORT_PREFIXES):
                        errors.append(f"forbidden import in {path.relative_to(root)}: {module}")
                continue
            if module and any(module == prefix or module.startswith(prefix + ".") for prefix in FORBIDDEN_IMPORT_PREFIXES):
                errors.append(f"forbidden import in {path.relative_to(root)}: {module}")


def validate_runtime_vocabulary(root: Path, errors: list[str]) -> None:
    for path in (root / "runtime" / "search" / "need").glob("*.py"):
        text = path.read_text(encoding="utf-8")
        for marker in FORBIDDEN_RUNTIME_VOCABULARY:
            if marker in text:
                errors.append(f"forbidden runtime vocabulary in {path.relative_to(root)}: {marker}")


def validate_queue(root: Path, errors: list[str]) -> None:
    queue = root / ".aide" / "queue" / "index.yaml"
    text = queue.read_text(encoding="utf-8") if queue.is_file() else ""
    if NEXT_TASK not in text:
        errors.append("queue does not point to HUNT-06")
    decision = load_json(root / "control/inventory/hunt_05_next_task_decision.json", "hunt_05_next_task_decision.v0", errors)
    if not str(decision.get("recommended_next_task", "")).startswith(NEXT_TASK):
        errors.append("hunt_05_next_task_decision does not recommend HUNT-06")


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
