#!/usr/bin/env python3
"""Validate HUNT-02 read-only Search Hunt UI state."""

from __future__ import annotations

import argparse
import ast
import json
import subprocess
import sys
import tempfile
from pathlib import Path
import re
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local_appliance import close_local_appliance, open_local_appliance
from runtime.local_service import LocalServiceApp


TASK_ID = "HUNT-02"
NEXT_TASK = "HUNT-03"
POLICIES = {
    "control/policies/search_hunt_ui_state_policy.json": "search_hunt_ui_state_policy.v0",
    "control/policies/search_hunt_ui_read_only_policy.json": "search_hunt_ui_read_only_policy.v0",
    "control/policies/search_hunt_non_claim_policy.json": "search_hunt_non_claim_policy.v0",
    "control/policies/search_hunt_unavailable_actions_policy.json": "search_hunt_unavailable_actions_policy.v0",
}
INVENTORIES = {
    "control/inventory/search_hunt_ui_inventory.json": "search_hunt_ui_inventory.v0",
    "control/inventory/search_hunt_ui_route_matrix.json": "search_hunt_ui_route_matrix.v0",
    "control/inventory/search_hunt_ui_result.json": "search_hunt_ui_result.v0",
    "control/inventory/search_hunt_ui_smoke_result.json": "search_hunt_ui_smoke_result.v0",
    "control/inventory/search_hunt_ui_gap_register.json": "search_hunt_ui_gap_register.v0",
    "control/inventory/hunt_02_next_task_decision.json": "hunt_02_next_task_decision.v0",
}
DOCS = (
    "docs/architecture/SEARCH_HUNT_UI_STATE.md",
    "docs/reference/SEARCH_HUNT_UI_ROUTES.md",
    "docs/reference/SEARCH_HUNT_UI_VIEW_MODELS.md",
    "docs/operations/SEARCH_HUNT_UI_RUNBOOK.md",
    "docs/operations/SEARCH_HUNT_UI_NON_CLAIMS.md",
)
RUNTIME_FILES = (
    "runtime/local_workbench/html.py",
    "runtime/local_workbench/pages.py",
    "runtime/local_workbench/templates.py",
    "runtime/local_workbench/view_models.py",
    "runtime/local_workbench/validation.py",
    "runtime/local_service/routes.py",
    "runtime/local_service/responses.py",
    "runtime/local_service/app.py",
    "runtime/local_service/validation.py",
)
TESTS = (
    "tests/runtime/test_search_hunt_ui_view_models.py",
    "tests/runtime/test_search_hunt_ui_pages.py",
    "tests/runtime/test_search_hunt_ui_routes.py",
    "tests/runtime/test_search_hunt_ui_read_only.py",
    "tests/operations/test_search_hunt_ui_scripts.py",
)
AUDIT_ROOT = Path("control/audits/hunt-02-search-hunt-ui-state-v0")
AUDIT_FILES = (
    "README.md",
    "hunt_02_report.json",
    "ui_state_summary.md",
    "route_matrix.md",
    "read_only_boundary.md",
    "non_claim_matrix.md",
    "smoke_result.md",
    "validation.md",
    "generated/sample_hunt_list.html",
    "generated/sample_hunt_detail.html",
    "generated/sample_hunt_not_found.html",
    "generated/sample_hunt_list_response.json",
    "generated/sample_hunt_detail_response.json",
    "generated/sample_smoke_result.json",
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
FORBIDDEN_RUNTIME_VOCABULARY = (
    "HUNT-02",
    "HUNT-03",
    "HUNT-04",
    "HUNT-05",
    "HUNT-06",
    "HUNT-07",
    "HUNT-08",
    "HUNT-09",
    "HUNT-10",
    "HUNT-11",
    "HUNT-12",
    "LOCAL-",
    "AIDE",
    "BUNDLE",
)


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
        print("HUNT-02 Search Hunt UI validation", file=stdout)
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
    report = load_json(root / AUDIT_ROOT / "hunt_02_report.json", "hunt_02_report.v0", errors)
    validate_files(root, errors)
    validate_policies(payloads, errors)
    validate_inventories(payloads, errors)
    validate_report(report, errors)
    validate_runtime_imports(root, errors)
    validate_runtime_vocabulary(root, errors)
    route_result = validate_temp_routes(root, errors)
    validate_queue(root, errors)
    status = "fail" if errors else ("pass_with_warnings" if warnings else "pass")
    return {
        "schema_version": "search_hunt_ui_validation.v0",
        "task": TASK_ID,
        "status": status,
        "errors": errors,
        "warnings": warnings,
        "hunt_ui_smoke_passed": bool(route_result.get("hunt_ui_smoke_passed")),
        "hunt_creation_performed": False,
        "hunt_transition_performed": False,
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
    for rel in (*DOCS, *RUNTIME_FILES, *TESTS, "scripts/eureka_search_hunt_ui_smoke.py", "scripts/validate_search_hunt_ui.py"):
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


def validate_policies(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    state = payloads.get("control/policies/search_hunt_ui_state_policy.json", {})
    expected_true = ("hunt_ui_enabled", "hunt_list_page_enabled", "hunt_detail_page_enabled", "hunt_json_api_enabled", "read_only_current_task", "local_appliance_required")
    expected_false = (
        "create_hunt_ui_enabled",
        "transition_controls_enabled",
        "steering_controls_enabled",
        "workunit_creation_enabled",
        "source_probe_controls_enabled",
        "ai_escalation_controls_enabled",
        "deployment_enabled",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    )
    for key in expected_true:
        if state.get(key) is not True:
            errors.append(f"UI state policy {key} must be true")
    for key in expected_false:
        if state.get(key) is not False:
            errors.append(f"UI state policy {key} must be false")
    read_only = payloads.get("control/policies/search_hunt_ui_read_only_policy.json", {})
    for key, value in read_only.items():
        if key != "schema_version" and value is not True:
            errors.append(f"UI read-only policy {key} must be true")
    non_claim = payloads.get("control/policies/search_hunt_non_claim_policy.json", {})
    forbidden = non_claim.get("forbidden_claims", {})
    if not isinstance(forbidden, Mapping) or not all(value is True for value in forbidden.values()):
        errors.append("non-claim policy must forbid all listed claims")
    unavailable = payloads.get("control/policies/search_hunt_unavailable_actions_policy.json", {}).get("unavailable_actions", {})
    for key in ("pause_resume_steer", "workunit_pipeline", "source_probes", "ai_escalation"):
        if key not in unavailable:
            errors.append(f"unavailable actions policy missing {key}")


def validate_inventories(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    inventory = payloads.get("control/inventory/search_hunt_ui_inventory.json", {})
    for key in ("hunt_list_page_enabled", "hunt_detail_page_enabled", "hunt_json_api_enabled"):
        if inventory.get(key) is not True:
            errors.append(f"UI inventory {key} must be true")
    for key in ("create_hunt_ui_enabled", "transition_controls_enabled", "steering_controls_enabled", "workunit_creation_enabled", "source_probe_controls_enabled", "ai_escalation_controls_enabled", "deployment_performed"):
        if inventory.get(key) is not False:
            errors.append(f"UI inventory {key} must be false")
    matrix = payloads.get("control/inventory/search_hunt_ui_route_matrix.json", {})
    routes = matrix.get("routes")
    expected_routes = ["/hunts", "/hunt/<hunt_id>", "/api/v1/hunts", "/api/v1/hunt/<hunt_id>"]
    if not isinstance(routes, list) or [row.get("route") for row in routes if isinstance(row, Mapping)] != expected_routes:
        errors.append("UI route matrix routes mismatch")
    else:
        for row in routes:
            if row.get("method") != "GET" or row.get("read_only") is not True:
                errors.append(f"route matrix row not read-only GET: {row.get('route')}")
            for key in ("mutates_store", "creates_hunt", "transitions_hunt", "creates_workunit"):
                if row.get(key) is not False:
                    errors.append(f"route matrix {key} must be false for {row.get('route')}")
    result = payloads.get("control/inventory/search_hunt_ui_result.json", {})
    for key in ("hunt_list_page_added", "hunt_detail_page_added", "hunt_json_routes_added", "hunt_not_found_state_added", "transition_history_visible", "checked_layers_visible", "unchecked_layers_visible", "unavailable_actions_visible", "non_claim_banner_present", "smoke_script_added", "validator_added", "hunt_ui_smoke_passed"):
        if result.get(key) is not True:
            errors.append(f"UI result {key} must be true")
    for key in ("mutation_controls_found", "external_assets_found", "forbidden_claims_found", "hunt_creation_performed", "hunt_transition_performed", "workunit_creation_performed", "source_probe_executed", "model_provider_used", "review_mutation_performed", "public_index_mutated", "master_index_mutated", "deployment_performed", "production_readiness_claimed", "public_launch_readiness_claimed"):
        if result.get(key) is not False:
            errors.append(f"UI result {key} must be false")
    decision = payloads.get("control/inventory/hunt_02_next_task_decision.json", {})
    if decision.get("recommended_next_task") != "HUNT-03 \u2014 Pause, resume, cancel, and steer commands":
        errors.append("HUNT-02 next task must be HUNT-03")
    if decision.get("f0_current_status") != "deferred":
        errors.append("F0 must remain deferred")


def validate_report(report: Mapping[str, Any], errors: list[str]) -> None:
    if report.get("recommended_next_task") != "HUNT-03 \u2014 Pause, resume, cancel, and steer commands":
        errors.append("HUNT-02 report must recommend HUNT-03")
    for key in ("hunt_list_page_added", "hunt_detail_page_added", "hunt_json_routes_added", "hunt_not_found_state_added", "transition_history_visible", "checked_layers_visible", "unchecked_layers_visible", "unavailable_actions_visible", "non_claim_banner_present", "smoke_script_added", "validator_added", "hunt_ui_smoke_passed"):
        if report.get(key) is not True:
            errors.append(f"HUNT-02 report {key} must be true")
    for key in ("hunt_creation_performed", "hunt_transition_performed", "workunit_creation_performed", "source_probe_executed", "external_network_used", "model_provider_used", "review_mutation_performed", "public_index_mutated", "master_index_mutated", "deployment_performed", "production_readiness_claimed", "public_launch_readiness_claimed"):
        if report.get(key) is not False:
            errors.append(f"HUNT-02 report {key} must be false")


def validate_temp_routes(root: Path, errors: list[str]) -> dict[str, bool]:
    result = {"hunt_ui_smoke_passed": False}
    with tempfile.TemporaryDirectory(prefix="eureka-hunt-ui-") as tmp:
        instance = Path(tmp) / "eureka-instance"
        init = run(root, "python", "scripts/eureka_init_instance.py", "--instance", str(instance), "--json")
        if init.returncode != 0:
            errors.append("temp instance init failed")
            return result
        runtime = open_local_appliance(instance, read_only=False)
        try:
            session = runtime.search_hunt.create_session_from_query("sampleproject", runtime=runtime, idempotency_key="hunt-ui-validator")
            before_hunts = runtime.search_hunt.summarize()["total"]
            before_workunits = runtime.workunit_queue.summarize().total
        finally:
            close_local_appliance(runtime)
        runtime = open_local_appliance(instance, read_only=True)
        try:
            app = LocalServiceApp(runtime)
            for path in ("/hunts", f"/hunt/{session.id}", "/api/v1/hunts", f"/api/v1/hunt/{session.id}"):
                response = app.handle("GET", path)
                if response.status_code != 200:
                    errors.append(f"hunt UI route failed: {path}")
            missing_html = app.handle("GET", "/hunt/not-present")
            missing_json = app.handle("GET", "/api/v1/hunt/not-present")
            if missing_html.status_code != 404 or "text/html" not in missing_html.content_type:
                errors.append("missing hunt HTML route did not return not-found page")
            if missing_json.status_code != 404 or missing_json.payload.get("hunt") is not None:
                errors.append("missing hunt JSON route did not return not-found payload")
            for method in ("POST", "PUT", "DELETE"):
                blocked = app.handle(method, f"/hunt/{session.id}")
                if blocked.status_code == 200:
                    errors.append(f"{method} hunt route was allowed")
            if runtime.search_hunt.summarize()["total"] != before_hunts:
                errors.append("hunt UI route mutated hunt count")
            if runtime.workunit_queue.summarize().total != before_workunits:
                errors.append("hunt UI route created WorkUnits")
        finally:
            close_local_appliance(runtime)
        result["hunt_ui_smoke_passed"] = run_server_smoke(root, instance, errors)
    return result


def run_server_smoke(root: Path, instance: Path, errors: list[str]) -> bool:
    process: subprocess.Popen[str] | None = None
    try:
        process = subprocess.Popen(
            ["python", "scripts/eureka_local_server.py", "--instance", str(instance), "--host", "127.0.0.1", "--port", "0", "--json-startup"],
            cwd=root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        startup_line = process.stdout.readline() if process.stdout is not None else ""
        if not startup_line:
            errors.append("local server did not report startup")
            return False
        startup = json.loads(startup_line)
        smoke = run(root, "python", "scripts/eureka_search_hunt_ui_smoke.py", "--base-url", str(startup["base_url"]), "--json")
        if smoke.returncode != 0:
            errors.append(f"hunt UI smoke failed: {smoke.stdout}{smoke.stderr}")
            return False
        payload = json.loads(smoke.stdout)
        if payload.get("status") != "pass":
            errors.append("hunt UI smoke did not pass")
            return False
        for key in ("mutation_controls_found", "external_assets_found", "forbidden_claims_found", "source_probe_executed", "model_provider_used"):
            if payload.get(key) is not False:
                errors.append(f"hunt UI smoke boundary flag not false: {key}")
                return False
        return True
    finally:
        if process is not None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)


def validate_runtime_imports(root: Path, errors: list[str]) -> None:
    for rel in RUNTIME_FILES:
        tree = ast.parse((root / rel).read_text(encoding="utf-8"), filename=rel)
        for node in ast.walk(tree):
            modules: list[str] = []
            if isinstance(node, ast.Import):
                modules = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and not node.level:
                modules = [node.module or ""]
            for module in modules:
                if any(module == prefix or module.startswith(prefix + ".") for prefix in FORBIDDEN_IMPORT_PREFIXES):
                    errors.append(f"forbidden import in {rel}: {module}")


def validate_runtime_vocabulary(root: Path, errors: list[str]) -> None:
    for rel in RUNTIME_FILES:
        text = (root / rel).read_text(encoding="utf-8")
        for token in FORBIDDEN_RUNTIME_VOCABULARY:
            if token in text:
                errors.append(f"forbidden runtime vocabulary in {rel}: {token}")


def validate_queue(root: Path, errors: list[str]) -> None:
    queue = read_text(root / ".aide/queue/index.yaml", errors)
    task = read_text(root / ".aide/queue/HUNT-02/task.yaml", errors)
    next_task = read_text(root / ".aide/queue/HUNT-03/task.yaml", errors)
    packet = read_text(root / ".aide/context/latest-task-packet.md", errors)
    if not re.search(r"current_recommended_task: HUNT-(0[3-9]|1[0-2])\b", queue):
        errors.append("queue index must point to HUNT-03 or a later HUNT task")
    if "id: HUNT-02" not in queue or "status: completed" not in queue:
        errors.append("queue index must mark HUNT-02 completed")
    if "id: HUNT-03" not in queue:
        errors.append("queue index must include HUNT-03")
    if "recommended_next: HUNT-03" not in task:
        errors.append("HUNT-02 task must recommend HUNT-03")
    if "Pause, resume, cancel, and steer commands" not in next_task:
        errors.append("HUNT-03 task title mismatch")
    if not re.search(r"HUNT-(0[3-9]|1[0-2])\b", packet):
        errors.append("latest task packet must point to HUNT-03 or a later HUNT task")
    if "current_recommended_task: F0-00" in queue or "current_recommended_task: SYN-00" in queue:
        errors.append("F0/SYN must not be current")


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


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(list(args), cwd=root, text=True, capture_output=True, check=False)


def relpath(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
