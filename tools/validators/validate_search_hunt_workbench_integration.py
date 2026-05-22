#!/usr/bin/env python3
"""Validate HUNT-08 Search Hunt workbench integration smoke evidence."""

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


TASK_ID = "HUNT-08"
NEXT_TASK = "HUNT-09"
POLICIES = {
    "control/policies/search_hunt_workbench_integration_policy.json": "search_hunt_workbench_integration_policy.v0",
    "control/policies/search_hunt_workflow_smoke_policy.json": "search_hunt_workflow_smoke_policy.v0",
    "control/policies/search_hunt_integration_safety_policy.json": "search_hunt_integration_safety_policy.v0",
    "control/policies/search_hunt_workbench_navigation_policy.json": "search_hunt_workbench_navigation_policy.v0",
    "control/policies/search_hunt_integration_non_claim_policy.json": "search_hunt_integration_non_claim_policy.v0",
}
INVENTORIES = {
    "control/inventory/search_hunt_workbench_integration_inventory.json": "search_hunt_workbench_integration_inventory.v0",
    "control/inventory/search_hunt_workflow_smoke_matrix.json": "search_hunt_workflow_smoke_matrix.v0",
    "control/inventory/search_hunt_workbench_integration_result.json": "search_hunt_workbench_integration_result.v0",
    "control/inventory/search_hunt_workflow_smoke_result.json": "search_hunt_workflow_smoke_result.v0",
    "control/inventory/search_hunt_api_smoke_result.json": "search_hunt_api_smoke_result.v0",
    "control/inventory/search_hunt_integration_safety_result.json": "search_hunt_integration_safety_result.v0",
    "control/inventory/search_hunt_integration_gap_register.json": "search_hunt_integration_gap_register.v0",
    "control/inventory/hunt_08_next_task_decision.json": "hunt_08_next_task_decision.v0",
}
REQUIRED_FILES = (
    "scripts/eureka_hunt_workflow_smoke.py",
    "scripts/eureka_hunt_workbench_smoke.py",
    "scripts/eureka_hunt_api_smoke.py",
    "scripts/demo_search_hunt_workflow.py",
    "scripts/validate_search_hunt_workbench_integration.py",
    "tests/runtime/test_search_hunt_workflow_integration.py",
    "tests/runtime/test_search_hunt_workbench_integration.py",
    "tests/runtime/test_search_hunt_api_integration.py",
    "tests/runtime/test_search_hunt_safety_integration.py",
    "tests/operations/test_search_hunt_workflow_smoke_scripts.py",
    "tests/operations/test_search_hunt_workbench_smoke_scripts.py",
    "docs/architecture/SEARCH_HUNT_WORKBENCH_INTEGRATION.md",
    "docs/reference/SEARCH_HUNT_WORKFLOW_SMOKE.md",
    "docs/reference/SEARCH_HUNT_INTEGRATION_API.md",
    "docs/operations/SEARCH_HUNT_WORKFLOW_RUNBOOK.md",
    "docs/operations/SEARCH_HUNT_INTEGRATION_SAFETY.md",
    "docs/operations/HUNT_08_TO_AGENT_CONTRACT_HANDOFF.md",
)
AUDIT_ROOT = Path("control/audits/hunt-08-workbench-integration-smoke-v0")
AUDIT_FILES = (
    "README.md",
    "hunt_08_report.json",
    "workflow_smoke_summary.md",
    "workbench_integration_summary.md",
    "api_smoke_summary.md",
    "safety_result.md",
    "navigation_summary.md",
    "non_claim_matrix.md",
    "demo_result.md",
    "validation.md",
    "generated/sample_hunt_workflow_smoke.json",
    "generated/sample_hunt_api_smoke.json",
    "generated/sample_hunt_workbench_smoke.json",
    "generated/sample_integrated_hunt_page.html",
    "generated/sample_integrated_need_page.html",
    "generated/sample_demo_result.json",
    "generated/sample_summary.md",
)
WORKFLOW_STAGES = (
    "create_hunt",
    "apply_command",
    "add_steering",
    "generate_exhaustion",
    "create_search_need",
    "plan_workunits",
    "create_workunits",
    "run_safe_background_worker",
    "inspect_workbench",
    "inspect_api",
    "verify_safety_boundaries",
)
FORBIDDEN_IMPORT_PREFIXES = (
    "runtime.connectors",
    "runtime.local_foundry",
    "runtime.extraction",
    "runtime.search_quality",
    "requests",
    "httpx",
    "aiohttp",
)
RUNTIME_FILES_TO_SCAN = (
    "surfaces/web/workbench/local_html/html.py",
    "surfaces/web/workbench/local_html/pages.py",
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
        print("HUNT-08 workbench integration validation", file=stdout)
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
    report = load_json(root / AUDIT_ROOT / "hunt_08_report.json", "hunt_08_report.v0", errors)
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
        "schema_version": "search_hunt_workbench_integration_validation.v0",
        "task": TASK_ID,
        "status": status,
        "errors": errors,
        "warnings": warnings,
        **behavior,
        "workflow_smoke_script_added": True,
        "workbench_smoke_script_added": True,
        "api_smoke_script_added": True,
        "demo_added": True,
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
    integration = payloads.get("control/policies/search_hunt_workbench_integration_policy.json", {})
    for key in ("integrated_workflow_smoke_required", "local_appliance_required", "localhost_only_mutations", "operator_token_required_for_mutations"):
        if integration.get(key) is not True:
            errors.append(f"integration policy {key} must be true")
    for key in ("source_probe_execution_enabled", "extraction_execution_enabled", "model_provider_enabled", "external_network_enabled", "deployment_enabled", "production_readiness_claimed", "public_launch_readiness_claimed"):
        if integration.get(key) is not False:
            errors.append(f"integration policy {key} must be false")
    workflow = payloads.get("control/policies/search_hunt_workflow_smoke_policy.json", {})
    stages = [str(item) for item in workflow.get("required_workflow_stages", [])]
    for stage in WORKFLOW_STAGES:
        if stage not in stages:
            errors.append(f"workflow smoke policy missing stage {stage}")
    safety = payloads.get("control/policies/search_hunt_integration_safety_policy.json", {})
    for key in ("source_probe_execution_forbidden", "extraction_execution_forbidden", "ai_model_execution_forbidden", "external_network_forbidden", "download_install_execute_forbidden", "master_index_mutation_forbidden", "site_dist_writes_forbidden", "deployment_forbidden", "public_launch_claim_forbidden", "production_readiness_claim_forbidden"):
        if safety.get(key) is not True:
            errors.append(f"integration safety policy {key} must be true")


def validate_inventory_payloads(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    inventory = payloads.get("control/inventory/search_hunt_workbench_integration_inventory.json", {})
    for key in ("integrated_workflow_smoke_enabled", "workbench_smoke_enabled", "api_smoke_enabled", "local_appliance_required"):
        if inventory.get(key) is not True:
            errors.append(f"integration inventory {key} must be true")
    for key in ("source_probe_execution_enabled", "extraction_execution_enabled", "model_provider_enabled", "deployment_performed"):
        if inventory.get(key) is not False:
            errors.append(f"integration inventory {key} must be false")
    result = payloads.get("control/inventory/search_hunt_workbench_integration_result.json", {})
    for key in (
        "workflow_smoke_script_added",
        "workbench_smoke_script_added",
        "api_smoke_script_added",
        "demo_added",
        "validator_added",
        "create_hunt_stage_passed",
        "command_steering_stage_passed",
        "exhaustion_stage_passed",
        "search_need_stage_passed",
        "workunit_creation_stage_passed",
        "safe_worker_stage_passed",
        "workbench_pages_passed",
        "api_routes_passed",
        "navigation_links_passed",
        "policy_blocked_workunits_remained_blocked",
    ):
        if result.get(key) is not True:
            errors.append(f"integration result {key} must be true")
    for key in ("source_probe_executed", "extraction_executed", "external_network_used", "model_provider_used", "download_install_execute_performed", "master_index_mutated", "site_dist_mutated", "deployment_performed", "production_readiness_claimed", "public_launch_readiness_claimed"):
        if result.get(key) is not False:
            errors.append(f"integration result {key} must be false")


def validate_report_payload(report: Mapping[str, Any], errors: list[str]) -> None:
    for key in (
        "workflow_smoke_script_added",
        "workbench_smoke_script_added",
        "api_smoke_script_added",
        "demo_added",
        "validator_added",
        "create_hunt_stage_passed",
        "command_steering_stage_passed",
        "exhaustion_stage_passed",
        "search_need_stage_passed",
        "workunit_creation_stage_passed",
        "safe_worker_stage_passed",
        "workbench_pages_passed",
        "api_routes_passed",
        "navigation_links_passed",
        "policy_blocked_workunits_remained_blocked",
    ):
        if report.get(key) is not True:
            errors.append(f"hunt_08_report {key} must be true")
    for key in ("source_probe_executed", "extraction_executed", "external_network_used", "model_provider_used", "download_install_execute_performed", "master_index_mutated", "site_dist_mutated", "deployment_performed", "production_readiness_claimed", "public_launch_readiness_claimed"):
        if report.get(key) is not False:
            errors.append(f"hunt_08_report {key} must be false")


def validate_behavior(root: Path, errors: list[str]) -> dict[str, Any]:
    site_before = tree_digest(root / "site" / "dist")
    with tempfile.TemporaryDirectory(prefix="eureka-hunt-08-") as tmp:
        instance = Path(tmp) / "eureka-instance"
        for name, args in (
            ("init", ("scripts/eureka_init_instance.py", "--instance", str(instance), "--json")),
            ("token", ("scripts/eureka_set_operator_token.py", "--instance", str(instance), "--token", "validator-token", "--json")),
        ):
            completed = run_cmd(root, *args)
            if completed.returncode != 0:
                errors.append(f"{name} failed: {completed.stderr or completed.stdout}")
                return {}
        workflow = run_cmd(root, "scripts/eureka_hunt_workflow_smoke.py", "--instance", str(instance), "--operator-token", "validator-token", "--json")
        if workflow.returncode != 0:
            errors.append(f"workflow smoke failed: {workflow.stderr or workflow.stdout}")
            return {}
        workflow_payload = json.loads(workflow.stdout)
        hunt_id = str(workflow_payload.get("hunt_id") or "")
        need_id = str(workflow_payload.get("search_need_id") or "")

        auth = validate_auth_and_lan(root, instance, hunt_id, errors)
        server_payloads = validate_server_smokes(root, instance, errors)
        auto_test = server_payloads.get("auto_test", {})
        auto_search = server_payloads.get("auto_search", {})
        workbench = server_payloads.get("workbench", {})
        api = server_payloads.get("api", {})
        site_after = tree_digest(root / "site" / "dist")
        if site_after != site_before:
            errors.append("site/dist changed during integration validation")
        return {
            "create_hunt_stage_passed": bool(workflow_payload.get("create_hunt_stage_passed")),
            "command_steering_stage_passed": bool(workflow_payload.get("command_steering_stage_passed")),
            "exhaustion_stage_passed": bool(workflow_payload.get("exhaustion_stage_passed")),
            "search_need_stage_passed": bool(workflow_payload.get("search_need_stage_passed")),
            "workunit_creation_stage_passed": bool(workflow_payload.get("workunit_creation_stage_passed")),
            "safe_worker_stage_passed": bool(workflow_payload.get("safe_worker_stage_passed")),
            "policy_blocked_workunits_remained_blocked": bool(workflow_payload.get("policy_blocked_workunits_remained_blocked")),
            "workbench_pages_passed": bool(workbench.get("workbench_pages_passed")),
            "api_routes_passed": bool(api.get("api_routes_passed")),
            "navigation_links_passed": bool(workbench.get("navigation_links_passed")),
            "auto_test_passed": auto_test.get("status") in {"pass", "pass_with_warnings"},
            "auto_search_passed": auto_search.get("status") in {"pass", "pass_with_warnings", None},
            "missing_token_rejected": auth["missing_token_rejected"],
            "invalid_token_rejected": auth["invalid_token_rejected"],
            "lan_mutation_blocked": auth["lan_mutation_blocked"],
            "hunt_id": hunt_id,
            "search_need_id": need_id,
        }


def validate_auth_and_lan(root: Path, instance: Path, hunt_id: str, errors: list[str]) -> dict[str, bool]:
    runtime = open_local_appliance(instance, read_only=False)
    try:
        app = LocalServiceApp(runtime, operator_auth_state=build_cli_operator_auth_state("validator-token"))
        missing = app.handle("POST", f"/hunt/{hunt_id}/exhaustion")
        invalid = app.handle("POST", f"/hunt/{hunt_id}/exhaustion", body="operator_token=bad")
        lan = app.handle("POST", f"/hunt/{hunt_id}/pause", client_host="192.168.1.20", body="operator_token=validator-token")
        result = {
            "missing_token_rejected": missing.status_code == 401,
            "invalid_token_rejected": invalid.status_code == 401,
            "lan_mutation_blocked": lan.status_code == 403,
        }
        for key, passed in result.items():
            if not passed:
                errors.append(f"{key} did not pass")
        return result
    finally:
        close_local_appliance(runtime)


def validate_server_smokes(root: Path, instance: Path, errors: list[str]) -> dict[str, Any]:
    process: subprocess.Popen[str] | None = None
    payloads: dict[str, Any] = {}
    try:
        process = subprocess.Popen(
            [
                sys.executable,
                "scripts/eureka_local_server.py",
                "--instance",
                str(instance),
                "--host",
                "127.0.0.1",
                "--port",
                "0",
                "--operator-token",
                "validator-token",
                "--json-startup",
            ],
            cwd=root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        startup_line = process.stdout.readline() if process.stdout is not None else ""
        if not startup_line:
            stderr = process.stderr.read() if process.stderr is not None else ""
            errors.append(f"local server did not start: {stderr}")
            return payloads
        startup = json.loads(startup_line)
        if startup.get("status") != "pass":
            errors.append(f"local server startup failed: {startup}")
            return payloads
        base_url = str(startup["base_url"])
        commands = {
            "workbench": ("scripts/eureka_hunt_workbench_smoke.py", "--base-url", base_url, "--instance", str(instance), "--operator-token", "validator-token", "--json"),
            "api": ("scripts/eureka_hunt_api_smoke.py", "--base-url", base_url, "--json"),
            "auto_test": ("scripts/eureka_local_auto_test.py", "--base-url", base_url, "--json"),
        }
        if (root / "scripts/eureka_local_auto_search.py").is_file():
            commands["auto_search"] = ("scripts/eureka_local_auto_search.py", "--base-url", base_url, "--json")
        for name, args in commands.items():
            completed = run_cmd(root, *args, timeout=90)
            if completed.returncode != 0:
                errors.append(f"{name} smoke failed: {completed.stderr or completed.stdout}")
                payloads[name] = {}
            else:
                payloads[name] = json.loads(completed.stdout)
    finally:
        if process is not None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
            if process.stdout is not None:
                process.stdout.close()
            if process.stderr is not None:
                process.stderr.close()
    return payloads


def validate_cli_and_demo(root: Path, errors: list[str]) -> None:
    with tempfile.TemporaryDirectory(prefix="eureka-hunt-08-cli-") as tmp:
        instance = Path(tmp) / "eureka-instance"
        for name, args in (
            ("init", ("scripts/eureka_init_instance.py", "--instance", str(instance), "--json")),
            ("token", ("scripts/eureka_set_operator_token.py", "--instance", str(instance), "--token", "validator-token", "--json")),
            ("workflow", ("scripts/eureka_hunt_workflow_smoke.py", "--instance", str(instance), "--operator-token", "validator-token", "--json")),
            ("demo", ("scripts/demo_search_hunt_workflow.py", "--instance", str(instance), "--operator-token", "validator-token", "--json")),
        ):
            completed = run_cmd(root, *args, timeout=90)
            if completed.returncode != 0:
                errors.append(f"{name} command failed: {completed.stderr or completed.stdout}")
                return
            payload = json.loads(completed.stdout)
            if payload.get("status") != "pass":
                errors.append(f"{name} command did not pass")


def validate_runtime_imports(root: Path, errors: list[str]) -> None:
    for rel in RUNTIME_FILES_TO_SCAN:
        path = root / rel
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=rel)
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
    for rel in RUNTIME_FILES_TO_SCAN:
        text = (root / rel).read_text(encoding="utf-8")
        for marker in FORBIDDEN_RUNTIME_VOCABULARY:
            if marker in text:
                errors.append(f"forbidden runtime vocabulary in {rel}: {marker}")


def validate_queue(root: Path, errors: list[str]) -> None:
    queue = (root / ".aide/queue/index.yaml").read_text(encoding="utf-8")
    if not hunt_queue_current_or_advanced(root, TASK_ID, NEXT_TASK):
        errors.append("queue does not point to HUNT-09")
    if "id: HUNT-08" not in queue or "status: completed" not in queue:
        errors.append("queue does not mark HUNT-08 completed")
    if "id: HUNT-09" not in queue or "status: queued" not in queue:
        errors.append("queue does not include queued HUNT-09")
    decision = load_json(root / "control/inventory/hunt_08_next_task_decision.json", "hunt_08_next_task_decision.v0", errors)
    if not str(decision.get("recommended_next_task", "")).startswith(NEXT_TASK):
        errors.append("hunt_08_next_task_decision must recommend HUNT-09")


def load_json(path: Path, schema_version: str, errors: list[str]) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"missing json file: {path.as_posix()}")
        return {}
    except json.JSONDecodeError as exc:
        errors.append(f"invalid json file {path.as_posix()}: {exc}")
        return {}
    if payload.get("schema_version") != schema_version:
        errors.append(f"{path.as_posix()} schema_version mismatch")
    return payload


def run_cmd(root: Path, *args: str, timeout: int = 60) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=root,
        text=True,
        capture_output=True,
        timeout=timeout,
    )


def tree_digest(path: Path) -> str:
    if not path.exists():
        return "missing"
    rows = []
    for item in sorted(path.rglob("*")):
        if item.is_file():
            stat = item.stat()
            rows.append(f"{item.relative_to(path).as_posix()}:{stat.st_size}:{int(stat.st_mtime)}")
    return "|".join(rows)


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
