#!/usr/bin/env python3
"""Validate the HUNT-09 disabled agent research task contract."""

from __future__ import annotations

import argparse
import ast
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.agent_research import (
    build_agent_research_report_schema,
    validate_agent_research_task,
    validate_candidate_only_report,
)
from runtime.local_appliance import close_local_appliance, open_local_appliance
from runtime.local_operator import write_operator_token_record
from runtime.local_service import LocalServiceApp
from runtime.search_hunt import build_hunt_exhaustion_report


TASK_ID = "HUNT-09"
NEXT_TASK = "HUNT-10"
POLICIES = {
    "control/policies/agent_research_task_policy.json": "agent_research_task_policy.v0",
    "control/policies/agent_research_provider_disabled_policy.json": "agent_research_provider_disabled_policy.v0",
    "control/policies/agent_research_report_policy.json": "agent_research_report_policy.v0",
    "control/policies/agent_research_side_effect_policy.json": "agent_research_side_effect_policy.v0",
    "control/policies/agent_research_ui_policy.json": "agent_research_ui_policy.v0",
    "control/policies/agent_research_non_claim_policy.json": "agent_research_non_claim_policy.v0",
}
INVENTORIES = {
    "control/inventory/agent_research_task_inventory.json": "agent_research_task_inventory.v0",
    "control/inventory/agent_research_task_state_machine.json": "agent_research_task_state_machine.v0",
    "control/inventory/agent_research_report_schema_inventory.json": "agent_research_report_schema_inventory.v0",
    "control/inventory/agent_research_disabled_boundary_result.json": "agent_research_disabled_boundary_result.v0",
    "control/inventory/agent_research_task_result.json": "agent_research_task_result.v0",
    "control/inventory/agent_research_demo_result.json": "agent_research_demo_result.v0",
    "control/inventory/agent_research_gap_register.json": "agent_research_gap_register.v0",
    "control/inventory/hunt_09_next_task_decision.json": "hunt_09_next_task_decision.v0",
}
RUNTIME_FILES = (
    "runtime/agent_research/__init__.py",
    "runtime/agent_research/schema.py",
    "runtime/agent_research/records.py",
    "runtime/agent_research/store.py",
    "runtime/agent_research/task_builder.py",
    "runtime/agent_research/report_schema.py",
    "runtime/agent_research/validation.py",
    "runtime/agent_research/errors.py",
    "runtime/local_appliance/manifest.py",
    "runtime/local_appliance/composition.py",
    "runtime/local_appliance/status.py",
    "runtime/local_service/routes.py",
    "runtime/local_workbench/pages.py",
    "runtime/local_workbench/view_models.py",
)
SCRIPTS = (
    "scripts/eureka_agent_research_task.py",
    "scripts/demo_agent_research_task.py",
    "scripts/validate_agent_research_task_contract.py",
)
DOCS = (
    "docs/architecture/AGENT_RESEARCH_TASK_MODEL.md",
    "docs/reference/AGENT_RESEARCH_TASK_RECORD.md",
    "docs/reference/AGENT_RESEARCH_REPORT_SCHEMA.md",
    "docs/reference/AGENT_RESEARCH_API.md",
    "docs/operations/AGENT_RESEARCH_DISABLED_BOUNDARY.md",
    "docs/operations/AGENT_RESEARCH_NON_CLAIMS.md",
    "docs/operations/HUNT_09_TO_REPLAY_AND_AI_GATE.md",
)
TESTS = (
    "tests/runtime/test_agent_research_records.py",
    "tests/runtime/test_agent_research_store.py",
    "tests/runtime/test_agent_research_task_builder.py",
    "tests/runtime/test_agent_research_report_schema.py",
    "tests/runtime/test_agent_research_routes.py",
    "tests/runtime/test_agent_research_ui.py",
    "tests/runtime/test_agent_research_disabled_boundary.py",
    "tests/operations/test_agent_research_scripts.py",
)
AUDIT_ROOT = Path("control/audits/hunt-09-agent-research-task-contract-v0")
AUDIT_FILES = (
    "README.md",
    "hunt_09_report.json",
    "task_model_summary.md",
    "report_schema_summary.md",
    "provider_disabled_boundary.md",
    "side_effect_boundary.md",
    "ui_summary.md",
    "demo_result.md",
    "validation.md",
    "generated/sample_agent_research_task.json",
    "generated/sample_agent_research_report_schema.json",
    "generated/sample_agent_research_task_page.html",
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
        print("HUNT-09 agent research task contract validation", file=stdout)
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
    report = load_json(root / AUDIT_ROOT / "hunt_09_report.json", "hunt_09_report.v0", errors)
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
        "schema_version": "agent_research_task_contract_validation.v0",
        "task": TASK_ID,
        "status": status,
        "errors": errors,
        "warnings": warnings,
        **behavior,
        "validator_added": True,
        "model_provider_used": False,
        "external_network_used": False,
        "source_probe_executed": False,
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
    task_policy = payloads.get("control/policies/agent_research_task_policy.json", {})
    for key in ("task_records_enabled", "input_requires_exhaustion_report", "input_requires_local_context", "output_candidate_only", "review_required"):
        if task_policy.get(key) is not True:
            errors.append(f"task policy {key} must be true")
    for key in (
        "task_execution_enabled",
        "provider_enabled",
        "browser_enabled",
        "source_probe_enabled",
        "public_index_mutation_enabled",
        "master_index_mutation_enabled",
        "deployment_enabled",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    ):
        if task_policy.get(key) is not False:
            errors.append(f"task policy {key} must be false")
    disabled = payloads.get("control/policies/agent_research_provider_disabled_policy.json", {})
    for key in ("model_provider_calls_enabled", "provider_credentials_allowed", "network_browser_calls_enabled"):
        if disabled.get(key) is not False:
            errors.append(f"provider-disabled policy {key} must be false")
    side = payloads.get("control/policies/agent_research_side_effect_policy.json", {})
    if side.get("task_record_creation_allowed") is not True:
        errors.append("side-effect policy must allow task_record_creation_allowed")
    for key in (
        "task_execution_allowed",
        "provider_call_allowed",
        "browser_call_allowed",
        "source_probe_allowed",
        "extraction_allowed",
        "external_network_allowed",
        "download_allowed",
        "install_execution_allowed",
        "review_decision_allowed",
        "public_index_mutation_allowed",
        "master_index_mutation_allowed",
        "site_dist_writes_allowed",
        "deployment_allowed",
    ):
        if side.get(key) is not False:
            errors.append(f"side-effect policy {key} must be false")


def validate_inventory_payloads(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    inventory = payloads.get("control/inventory/agent_research_task_inventory.json", {})
    expected = {
        "runtime_package": "runtime/agent_research",
        "store_id": "agent_research",
        "db_path": "db/agent_research.sqlite",
    }
    for key, value in expected.items():
        if inventory.get(key) != value:
            errors.append(f"agent research inventory {key} mismatch")
    for key in ("task_records_enabled", "report_schema_enabled", "candidate_only_output"):
        if inventory.get(key) is not True:
            errors.append(f"agent research inventory {key} must be true")
    for key in ("task_execution_enabled", "provider_enabled", "browser_enabled", "source_probe_enabled", "deployment_performed"):
        if inventory.get(key) is not False:
            errors.append(f"agent research inventory {key} must be false")

    result = payloads.get("control/inventory/agent_research_task_result.json", {})
    for key in (
        "runtime_package_added",
        "sqlite_store_added",
        "store_added_to_instance_manifest",
        "cli_added",
        "demo_added",
        "validator_added",
        "draft_from_hunt_passed",
        "draft_from_need_passed",
        "report_schema_added",
        "provider_disabled_boundary_passed",
        "execution_disabled_boundary_passed",
        "missing_token_rejected",
        "invalid_token_rejected",
        "lan_creation_blocked",
        "ui_routes_added",
        "api_routes_added",
    ):
        if result.get(key) is not True:
            errors.append(f"agent research result {key} must be true")
    for key in (
        "model_provider_used",
        "external_network_used",
        "source_probe_executed",
        "review_mutation_performed",
        "public_index_mutated",
        "master_index_mutated",
        "deployment_performed",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    ):
        if result.get(key) is not False:
            errors.append(f"agent research result {key} must be false")


def validate_report_payload(report: Mapping[str, Any], errors: list[str]) -> None:
    if report.get("status") not in {"pass", "pass_with_warnings"}:
        errors.append("hunt_09_report status must be pass or pass_with_warnings")
    for key in (
        "runtime_package_added",
        "sqlite_store_added",
        "store_added_to_instance_manifest",
        "draft_from_hunt_passed",
        "draft_from_need_passed",
        "report_schema_added",
        "provider_disabled_boundary_passed",
        "execution_disabled_boundary_passed",
        "ui_routes_added",
        "api_routes_added",
    ):
        if report.get(key) is not True:
            errors.append(f"hunt_09_report {key} must be true")
    for key in (
        "model_provider_used",
        "external_network_used",
        "source_probe_executed",
        "review_mutation_performed",
        "public_index_mutated",
        "master_index_mutated",
        "deployment_performed",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    ):
        if report.get(key) is not False:
            errors.append(f"hunt_09_report {key} must be false")


def validate_behavior(root: Path, errors: list[str]) -> dict[str, Any]:
    token = "validator-token"
    behavior = {
        "draft_from_hunt_passed": False,
        "draft_from_need_passed": False,
        "report_schema_added": False,
        "provider_disabled_boundary_passed": False,
        "execution_disabled_boundary_passed": False,
        "missing_token_rejected": False,
        "invalid_token_rejected": False,
        "lan_creation_blocked": False,
        "execute_route_exists": False,
        "execute_attempt_rejected": False,
        "ui_routes_added": False,
        "api_routes_added": False,
    }
    with tempfile.TemporaryDirectory(prefix="eureka-agent-research-") as tmp:
        instance = Path(tmp)
        init = run_command([sys.executable, "scripts/eureka_init_instance.py", "--instance", str(instance), "--json"], root)
        if init.returncode != 0:
            errors.append("instance init failed for agent research validation: " + init.stderr.strip())
            return behavior
        write_operator_token_record(instance, token)
        runtime = open_local_appliance(instance)
        try:
            hunt = runtime.search_hunt.create_session_from_query("sampleproject", runtime=runtime)
            report = build_hunt_exhaustion_report(runtime, hunt.id, operator_label="validator")
            runtime.search_hunt.attach_exhaustion_report(hunt.id, report)
            need = runtime.search_need.create_need_from_hunt(runtime, hunt.id, operator_label="validator")
            public_before = runtime.public_index.summarize().to_dict()
            task_from_hunt = runtime.agent_research.draft_task_from_hunt(runtime, hunt.id, operator_label="validator")
            task_from_need = runtime.agent_research.draft_task_from_need(runtime, need.id, operator_label="validator")
            validate_agent_research_task(task_from_hunt)
            validate_agent_research_task(task_from_need)
            schema = build_agent_research_report_schema().to_dict()
            behavior["draft_from_hunt_passed"] = task_from_hunt.search_hunt_id == hunt.id
            behavior["draft_from_need_passed"] = task_from_need.search_need_id == need.id
            behavior["report_schema_added"] = schema.get("candidate_only") is True and schema.get("review_required") is True
            behavior["provider_disabled_boundary_passed"] = task_from_hunt.provider_enabled is False and task_from_need.provider_enabled is False
            behavior["execution_disabled_boundary_passed"] = task_from_hunt.execution_enabled is False and task_from_need.execution_enabled is False
            validate_candidate_only_report(sample_candidate_report(task_from_need.task_id, hunt.id, need.id))
            app = LocalServiceApp(runtime)
            missing = app.handle("POST", f"/hunt/{hunt.id}/agent-task-draft", body="")
            invalid = app.handle("POST", f"/hunt/{hunt.id}/agent-task-draft", body="operator_token=wrong-token")
            lan = app.handle("POST", f"/hunt/{hunt.id}/agent-task-draft", client_host="192.168.1.44", body=f"operator_token={token}")
            good_hunt = app.handle("POST", f"/api/v1/hunt/{hunt.id}/agent-task-draft", body=f"operator_token={token}")
            good_need = app.handle("POST", f"/api/v1/need/{need.id}/agent-task-draft", body=f"operator_token={token}")
            hunt_tasks = app.handle("GET", f"/api/v1/hunt/{hunt.id}/agent-tasks")
            need_tasks = app.handle("GET", f"/api/v1/need/{need.id}/agent-tasks")
            report_schema = app.handle("GET", "/api/v1/agent-research/report-schema")
            hunt_html = app.handle("GET", f"/hunt/{hunt.id}")
            need_html = app.handle("GET", f"/need/{need.id}")
            execute = app.handle("POST", "/api/v1/agent-research/execute", body=f"operator_token={token}")
            behavior["missing_token_rejected"] = missing.status_code == 401
            behavior["invalid_token_rejected"] = invalid.status_code == 401
            behavior["lan_creation_blocked"] = lan.status_code == 403
            behavior["api_routes_added"] = all(
                response.status_code == 200
                for response in (good_hunt, good_need, hunt_tasks, need_tasks, report_schema)
            )
            behavior["ui_routes_added"] = (
                hunt_html.status_code == 200
                and need_html.status_code == 200
                and "Agent research disabled boundary" in str(hunt_html.body)
                and "Agent research disabled boundary" in str(need_html.body)
            )
            behavior["execute_route_exists"] = execute.status_code == 200
            behavior["execute_attempt_rejected"] = execute.status_code != 200
            public_after = runtime.public_index.summarize().to_dict()
            if public_before != public_after:
                errors.append("public index summary changed during agent research validation")
        finally:
            close_local_appliance(runtime)
    for key, value in behavior.items():
        if key == "execute_route_exists":
            if value is not False:
                errors.append("execute route must not exist")
        elif value is not True:
            errors.append(f"behavior check failed: {key}")
    return behavior


def validate_cli_and_demo(root: Path, errors: list[str]) -> None:
    with tempfile.TemporaryDirectory(prefix="eureka-agent-research-cli-") as tmp:
        instance = Path(tmp)
        init = run_command([sys.executable, "scripts/eureka_init_instance.py", "--instance", str(instance), "--json"], root)
        if init.returncode != 0:
            errors.append("CLI validation instance init failed")
            return
        run_command([sys.executable, "scripts/eureka_set_operator_token.py", "--instance", str(instance), "--token", "validator-token", "--json"], root)
        demo = run_command(
            [
                sys.executable,
                "scripts/demo_agent_research_task.py",
                "--instance",
                str(instance),
                "--operator-token",
                "validator-token",
                "--json",
            ],
            root,
        )
        if demo.returncode != 0:
            errors.append("demo_agent_research_task.py failed: " + demo.stderr.strip())
        schema = run_command([sys.executable, "scripts/eureka_agent_research_task.py", "report-schema", "--json"], root)
        if schema.returncode != 0:
            errors.append("eureka_agent_research_task.py report-schema failed")
        execute = run_command([sys.executable, "scripts/eureka_agent_research_task.py", "--instance", str(instance), "execute", "--json"], root)
        if execute.returncode == 0:
            errors.append("agent research execute CLI command must fail closed")


def validate_runtime_imports(root: Path, errors: list[str]) -> None:
    for path in (root / "runtime" / "agent_research").glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            module = ""
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module = alias.name
                    if _forbidden_import(module):
                        errors.append(f"forbidden import in {path.name}: {module}")
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                if _forbidden_import(module):
                    errors.append(f"forbidden import in {path.name}: {module}")


def validate_runtime_vocabulary(root: Path, errors: list[str]) -> None:
    for path in (root / "runtime" / "agent_research").glob("*.py"):
        text = path.read_text(encoding="utf-8")
        for marker in FORBIDDEN_RUNTIME_VOCABULARY:
            if marker in text:
                errors.append(f"forbidden task vocabulary in runtime/agent_research/{path.name}: {marker}")


def validate_queue(root: Path, errors: list[str]) -> None:
    text = (root / ".aide" / "queue" / "index.yaml").read_text(encoding="utf-8")
    if "current_recommended_task: HUNT-10" not in text:
        errors.append("queue current_recommended_task must be HUNT-10")
    if "id: HUNT-09" not in text or "status: completed" not in text:
        errors.append("queue must mark HUNT-09 completed")
    if not (root / ".aide" / "queue" / "HUNT-10" / "task.yaml").is_file():
        errors.append("HUNT-10 task file is required")


def sample_candidate_report(task_id: str, hunt_id: str, need_id: str) -> dict[str, Any]:
    return {
        "report_id": "arr_sample",
        "task_id": task_id,
        "search_hunt_id": hunt_id,
        "search_need_id": need_id,
        "candidate_aliases": [],
        "candidate_source_leads": [],
        "candidate_dead_urls": [],
        "candidate_wayback_paths": [],
        "candidate_extraction_targets": [],
        "candidate_workunits": [],
        "absence_explanation_draft": "",
        "confidence_notes": [],
        "limitations": ["candidate-only"],
        "forbidden_claims_absent": True,
        "review_required": True,
        "public_index_mutation_performed": False,
        "master_index_mutation_performed": False,
    }


def load_json(path: Path, schema_version: str, errors: list[str]) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"missing JSON file: {relative(path)}")
        return {}
    except json.JSONDecodeError as exc:
        errors.append(f"invalid JSON {relative(path)}: {exc}")
        return {}
    if not isinstance(payload, dict):
        errors.append(f"JSON must contain object: {relative(path)}")
        return {}
    if payload.get("schema_version") != schema_version:
        errors.append(f"{relative(path)} schema_version mismatch")
    return payload


def run_command(command: Sequence[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(list(command), cwd=cwd, text=True, capture_output=True, check=False, timeout=120)


def _forbidden_import(module: str) -> bool:
    return any(module == prefix or module.startswith(prefix + ".") for prefix in FORBIDDEN_IMPORT_PREFIXES)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def relative(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
