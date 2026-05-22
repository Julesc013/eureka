#!/usr/bin/env python3
"""Validate LOCAL-05 HTML workbench evidence."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local_appliance import close_local_appliance, open_local_appliance
from runtime.local_service import LocalServiceApp
from surfaces.web.workbench.local_html import (
    build_absence_page_view,
    build_home_page_view,
    build_object_page_view,
    build_search_page_view,
    build_source_page_view,
    build_status_page_view,
    render_absence_page,
    render_home_page,
    render_object_page,
    render_search_page,
    render_source_page,
    render_status_page,
    validate_local_workbench_page,
)


TASK_ID = "LOCAL-05"
NEXT_TASK = "LOCAL-06"
F0_CLOSEOUT = "LOCAL-14"
POLICIES = {
    "control/policies/local_html_workbench_policy.json": "local_html_workbench_policy.v0",
    "control/policies/local_html_accessibility_policy.json": "local_html_accessibility_policy.v0",
    "control/policies/local_html_read_only_policy.json": "local_html_read_only_policy.v0",
}
INVENTORIES = {
    "control/inventory/local_html_workbench_inventory.json": "local_html_workbench_inventory.v0",
    "control/inventory/local_html_route_matrix.json": "local_html_route_matrix.v0",
    "control/inventory/local_html_workbench_result.json": "local_html_workbench_result.v0",
    "control/inventory/local_html_smoke_result.json": "local_html_smoke_result.v0",
    "control/inventory/local_html_gap_register.json": "local_html_gap_register.v0",
    "control/inventory/local_05_leakage_baseline.json": "local_05_leakage_baseline.v0",
    "control/inventory/local_05_next_task_decision.json": "local_05_next_task_decision.v0",
}
RUNTIME_FILES = (
    "surfaces/web/workbench/local_html/__init__.py",
    "surfaces/web/workbench/local_html/html.py",
    "surfaces/web/workbench/local_html/pages.py",
    "surfaces/web/workbench/local_html/templates.py",
    "surfaces/web/workbench/local_html/view_models.py",
    "surfaces/web/workbench/local_html/validation.py",
    "surfaces/web/workbench/local_html/errors.py",
)
SCRIPTS = (
    "scripts/eureka_local_workbench_smoke.py",
    "scripts/validate_local_html_workbench.py",
)
TESTS = (
    "tests/runtime/test_local_workbench_pages.py",
    "tests/runtime/test_local_workbench_view_models.py",
    "tests/runtime/test_local_workbench_read_only.py",
    "tests/operations/test_local_workbench_scripts.py",
)
DOCS = (
    "docs/architecture/LOCAL_HTML_WORKBENCH.md",
    "docs/reference/LOCAL_HTML_ROUTES.md",
    "docs/operations/LOCAL_HTML_WORKBENCH_RUNBOOK.md",
)
AUDIT_ROOT = Path("control/audits/local-05-html-workbench-v0")
AUDIT_FILES = (
    "README.md",
    "local_05_report.json",
    "html_workbench_summary.md",
    "route_matrix.md",
    "accessibility_summary.md",
    "smoke_result.md",
    "read_only_boundary.md",
    "leakage_baseline.md",
    "validation.md",
    "generated/sample_home.html",
    "generated/sample_search.html",
    "generated/sample_object.html",
    "generated/sample_source.html",
    "generated/sample_absence.html",
    "generated/sample_status.html",
    "generated/sample_smoke_result.json",
    "generated/sample_summary.md",
)
HTML_ROUTES = ("/", "/status", "/search", "/object/<record_id>", "/source/<source_id>", "/absence")
ALLOWED_IMPORTS = {
    "dataclasses",
    "enum",
    "typing",
    "html",
    "urllib.parse",
    "json",
    "datetime",
    "runtime.local_service",
    "runtime.local_appliance",
}
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
FORBIDDEN_VOCABULARY = ("LOCAL-", "AIDE", "H0", "H1", "H2", "H3", "H4", "H5", "H6", "H7", "H8", "H9", "H10", "H11", "H12", "H13", "H14", "BUNDLE")


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
        print("LOCAL-05 local HTML workbench validation", file=stdout)
        print(f"status: {result['status']}", file=stdout)
        for error in result["errors"]:
            print(f"ERROR: {error}", file=stdout)
        for warning in result["warnings"]:
            print(f"WARN: {warning}", file=stdout)
    return 0 if result["status"] in {"pass", "pass_with_warnings"} else 1


def validate(root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    payloads: dict[str, dict[str, Any]] = {}
    for rel, schema in {**POLICIES, **INVENTORIES}.items():
        payloads[rel] = load_json(root / rel, schema, errors)
    report = load_json(root / AUDIT_ROOT / "local_05_report.json", "local_05_report.v0", errors)
    validate_policies(payloads, errors)
    validate_inventories(payloads, errors, warnings)
    validate_files(root, errors)
    validate_runtime_imports(root, errors)
    validate_runtime_vocabulary(root, errors)
    service = validate_temp_workbench(root, errors)
    validate_queue(root, errors)
    validate_report(report, errors, warnings)
    validate_leakage(root, payloads.get("control/inventory/local_05_leakage_baseline.json", {}), errors, warnings)
    status = "fail" if errors else ("pass_with_warnings" if warnings else "pass")
    return {
        "schema_version": "local_html_workbench_validation.v0",
        "task": TASK_ID,
        "status": status,
        "errors": errors,
        "warnings": warnings,
        "workbench_smoke_passed": bool(service.get("workbench_smoke_passed")),
        "json_api_still_passed": bool(service.get("json_api_still_passed")),
        "mutation_controls_found": False,
        "external_assets_found": False,
        "lan_enabled": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def validate_policies(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    workbench = payloads.get("control/policies/local_html_workbench_policy.json", {})
    expected = {
        "server_rendered": True,
        "frontend_build_required": False,
        "javascript_required": False,
        "localhost_only": True,
        "lan_enabled": False,
        "read_only": True,
        "mutation_routes_enabled": False,
        "review_decision_ui_enabled": False,
        "workunit_ui_enabled": False,
        "search_hunt_ui_enabled": False,
        "source_probe_ui_enabled": False,
        "index_rebuild_ui_enabled": False,
        "deployment_enabled": False,
        "site_dist_writes_enabled": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }
    for key, value in expected.items():
        if workbench.get(key) != value:
            errors.append(f"workbench policy {key} mismatch")
    accessibility = payloads.get("control/policies/local_html_accessibility_policy.json", {})
    for key in ("semantic_html_required", "form_labels_required", "page_title_required", "lang_attribute_required", "keyboard_navigation_required", "no_js_required_for_core_flow", "readable_without_css", "old_browser_friendly"):
        if accessibility.get(key) is not True:
            errors.append(f"accessibility policy {key} must be true")
    if accessibility.get("wcag_target") != "WCAG 2.2 AA where practical for local prototype":
        errors.append("accessibility policy wcag_target mismatch")
    read_only = payloads.get("control/policies/local_html_read_only_policy.json", {})
    if read_only.get("forms_get_only") is not True:
        errors.append("read-only html policy forms_get_only must be true")
    if read_only.get("mutating_methods_forbidden") != ["POST", "PUT", "PATCH", "DELETE"]:
        errors.append("read-only html mutating methods mismatch")
    for key in ("review_decision_controls_forbidden_current_task", "workunit_creation_controls_forbidden_current_task", "source_probe_controls_forbidden_current_task", "index_rebuild_controls_forbidden_current_task", "upload_controls_forbidden", "download_install_execute_controls_forbidden", "lan_controls_forbidden_current_task"):
        if read_only.get(key) is not True:
            errors.append(f"read-only html policy {key} must be true")


def validate_inventories(payloads: Mapping[str, Mapping[str, Any]], errors: list[str], warnings: list[str]) -> None:
    inventory = payloads.get("control/inventory/local_html_workbench_inventory.json", {})
    if inventory.get("runtime_package") != "surfaces/web/workbench/local_html":
        errors.append("html inventory runtime_package mismatch")
    for key, value in {
        "server_rendered": True,
        "frontend_build_required": False,
        "javascript_required": False,
        "read_only": True,
        "lan_enabled": False,
        "review_decision_ui_enabled": False,
        "workunit_ui_enabled": False,
        "source_probe_ui_enabled": False,
        "index_rebuild_ui_enabled": False,
        "deployment_performed": False,
        "external_assets": 0,
    }.items():
        if inventory.get(key) != value:
            errors.append(f"html inventory {key} mismatch")
    matrix = payloads.get("control/inventory/local_html_route_matrix.json", {})
    rows = matrix.get("routes")
    if not isinstance(rows, list):
        errors.append("html route matrix must contain routes list")
    else:
        seen = [str(row.get("route")) for row in rows if isinstance(row, Mapping)]
        if seen != list(HTML_ROUTES):
            errors.append("html route matrix route order mismatch")
        for row in rows:
            if not isinstance(row, Mapping):
                continue
            for key, value in {"method": "GET", "html_enabled": True, "read_only": True, "mutates_store": False, "has_accessible_title": True, "has_navigation": True}.items():
                if row.get(key) != value:
                    errors.append(f"html route matrix {key} mismatch for {row.get('route')}")
    result = payloads.get("control/inventory/local_html_workbench_result.json", {})
    for key in ("runtime_package_added", "home_page_added", "search_page_added", "object_page_added", "source_page_added", "absence_page_added", "status_page_added", "workbench_smoke_passed", "json_api_still_passed"):
        if result.get(key) is not True:
            errors.append(f"html result {key} must be true")
    for key in ("mutation_controls_found", "external_assets_found", "lan_enabled", "deployment_performed", "production_readiness_claimed", "public_launch_readiness_claimed"):
        if result.get(key) is not False:
            errors.append(f"html result {key} must be false")
    smoke = payloads.get("control/inventory/local_html_smoke_result.json", {})
    if smoke.get("status") != "pass":
        errors.append("html smoke inventory must pass")
    decision = payloads.get("control/inventory/local_05_next_task_decision.json", {})
    if decision.get("recommended_next_task") != "LOCAL-06 \u2014 Status, object, source, and absence page hardening":
        errors.append("LOCAL-05 next task decision must point to LOCAL-06")
    if decision.get("f0_current_status") != "deferred" or decision.get("f0_can_resume_after") != F0_CLOSEOUT:
        errors.append("F0 must remain deferred until LOCAL-14")
    if decision.get("lan_can_start") is not False or decision.get("html_workbench_available") is not True:
        errors.append("LOCAL-05 next task decision flags mismatch")
    leakage = payloads.get("control/inventory/local_05_leakage_baseline.json", {})
    if leakage.get("local_05_increased_leakage") is not False:
        errors.append("LOCAL-05 leakage baseline must not increase leakage")
    if leakage.get("runtime_leakage_gate_status_after") == "fail":
        warnings.append("pre-existing runtime leakage gate still fails")


def validate_files(root: Path, errors: list[str]) -> None:
    for rel in (*RUNTIME_FILES, *SCRIPTS, *TESTS, *DOCS):
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


def validate_runtime_imports(root: Path, errors: list[str]) -> None:
    allowed_roots = {item.split(".")[0] for item in ALLOWED_IMPORTS}
    for rel in RUNTIME_FILES:
        tree = ast.parse((root / rel).read_text(encoding="utf-8"), filename=rel)
        for node in ast.walk(tree):
            modules: list[str] = []
            if isinstance(node, ast.Import):
                modules = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and not node.level:
                modules = [node.module or ""]
            for module in modules:
                if any(module == item or module.startswith(item + ".") for item in FORBIDDEN_IMPORT_PREFIXES):
                    errors.append(f"forbidden import in {rel}: {module}")
                if module.startswith("runtime.") and not any(module == item or module.startswith(item + ".") for item in ALLOWED_IMPORTS):
                    errors.append(f"unexpected runtime import in {rel}: {module}")
                if not module.startswith("runtime.") and module.split(".")[0] not in allowed_roots:
                    errors.append(f"unexpected import in {rel}: {module}")


def validate_runtime_vocabulary(root: Path, errors: list[str]) -> None:
    for rel in RUNTIME_FILES:
        text = (root / rel).read_text(encoding="utf-8")
        for token in FORBIDDEN_VOCABULARY:
            if token in text:
                errors.append(f"forbidden runtime vocabulary in {rel}: {token}")


def validate_temp_workbench(root: Path, errors: list[str]) -> dict[str, Any]:
    result = {"workbench_smoke_passed": False, "json_api_still_passed": False}
    validate_page_renderers(errors)
    with tempfile.TemporaryDirectory(prefix="eureka-local-html-") as tmp:
        instance = Path(tmp) / "eureka-instance"
        init = run(root, "python", "scripts/eureka_init_instance.py", "--instance", str(instance), "--json")
        if init.returncode != 0:
            errors.append("temp instance init failed")
            return result
        before = tree_digest(instance)
        runtime = None
        try:
            runtime = open_local_appliance(instance, read_only=True)
            app = LocalServiceApp(runtime)
            for path in ("/", "/status", "/search?q=sampleproject", "/absence?q=missing"):
                response = app.handle("GET", path)
                if response.status_code >= 500 or "text/html" not in response.content_type:
                    errors.append(f"html route failed: {path}")
                validate_local_workbench_page(response.body)
            for path in ("/api/v1/status", "/api/v1/search?q=sampleproject", "/api/v1/absence?q=missing"):
                response = app.handle("GET", path)
                if response.status_code != 200 or "application/json" not in response.content_type:
                    errors.append(f"json route failed: {path}")
            result["json_api_still_passed"] = True
            post = app.handle("POST", "/search", "q=sampleproject")
            if post.status_code != 405:
                errors.append("write method was not rejected")
        except Exception as exc:
            errors.append(f"in-process workbench validation failed: {exc}")
        finally:
            if runtime is not None:
                close_local_appliance(runtime)
        smoke = run_server_smoke(root, instance, errors)
        result["workbench_smoke_passed"] = smoke
        after = tree_digest(instance)
        if after != before:
            errors.append("html workbench mutated initialized instance files")
    return result


def validate_page_renderers(errors: list[str]) -> None:
    status = {
        "status": "pass",
        "runtime": {"instance_id": "sample", "instance_schema_version": 1, "stores": {}, "migration_needed": False},
        "public_index": {"record_count": 0},
        "warnings": [],
        "limitations": [],
    }
    pages = (
        render_home_page(build_home_page_view(status)),
        render_search_page(build_search_page_view("<query>", {"result_count": 0, "results": [], "warnings": [], "limitations": []})),
        render_object_page(build_object_page_view("<id>", None)),
        render_source_page(build_source_page_view("<source>", {"result_count": 0, "records": [], "warnings": [], "limitations": []})),
        render_absence_page(build_absence_page_view("<query>", {"absence": {"result_count": 0, "checked_sources": []}, "warnings": [], "limitations": []})),
        render_status_page(build_status_page_view(status)),
    )
    for page in pages:
        try:
            validate_local_workbench_page(page)
        except Exception as exc:
            errors.append(f"page renderer failed validation: {exc}")
        if "<query>" in page or "<id>" in page or "<source>" in page:
            errors.append("page renderer left unescaped sample marker")


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
        smoke = run(root, "python", "scripts/eureka_local_workbench_smoke.py", "--base-url", str(startup["base_url"]), "--json")
        if smoke.returncode != 0:
            errors.append(f"workbench smoke failed: {smoke.stdout}{smoke.stderr}")
            return False
        payload = json.loads(smoke.stdout)
        if payload.get("mutation_controls_found") is not False or payload.get("external_assets_found") is not False:
            errors.append("workbench smoke found mutation controls or external assets")
            return False
        service_smoke = run(root, "python", "scripts/eureka_local_service_smoke.py", "--base-url", str(startup["base_url"]), "--json")
        if service_smoke.returncode != 0:
            errors.append("LOCAL-04 service smoke failed after HTML integration")
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
            if process.stdout is not None:
                process.stdout.close()
            if process.stderr is not None:
                process.stderr.close()


def validate_queue(root: Path, errors: list[str]) -> None:
    queue = read_text(root / ".aide/queue/index.yaml", errors)
    task = read_text(root / ".aide/queue/LOCAL-05/task.yaml", errors)
    next_task = read_text(root / ".aide/queue/LOCAL-06/task.yaml", errors)
    if "current_recommended_task: LOCAL-06" not in queue:
        errors.append("queue index must point to LOCAL-06")
    if "id: LOCAL-05" not in queue or "status: completed" not in queue:
        errors.append("queue index must mark LOCAL-05 completed")
    if "id: LOCAL-06" not in queue or "status: queued" not in queue:
        errors.append("queue index must include queued LOCAL-06")
    if "deferred_until: LOCAL-14" not in queue:
        errors.append("queue index must keep F0 deferred until LOCAL-14")
    if "recommended_next: LOCAL-06" not in task:
        errors.append("LOCAL-05 task must recommend LOCAL-06")
    if "Status, object, source, and absence page hardening" not in next_task:
        errors.append("LOCAL-06 task title mismatch")


def validate_report(report: Mapping[str, Any], errors: list[str], warnings: list[str]) -> None:
    if report.get("recommended_next_task") != "LOCAL-06 \u2014 Status, object, source, and absence page hardening":
        errors.append("LOCAL-05 audit report must recommend LOCAL-06")
    for key in ("runtime_package_added", "home_page_added", "search_page_added", "object_page_added", "source_page_added", "absence_page_added", "status_page_added", "workbench_smoke_passed", "json_api_still_passed", "server_implemented", "html_workbench_implemented"):
        if report.get(key) is not True:
            errors.append(f"LOCAL-05 report {key} must be true")
    for key in ("mutation_controls_found", "external_assets_found", "workunit_runtime_implemented", "lan_enabled", "source_probe_executed", "review_mutation_performed", "index_rebuild_performed", "deployment_performed", "local_05_increased_leakage", "production_readiness_claimed", "public_launch_readiness_claimed"):
        if report.get(key) is not False:
            errors.append(f"LOCAL-05 report {key} must be false")
    validation = report.get("validation", {})
    if isinstance(validation, Mapping) and str(validation.get("runtime_leakage_gate", "")).startswith("fail_pre_existing"):
        warnings.append("audit report records pre-existing runtime leakage gate failure")


def validate_leakage(root: Path, leakage: Mapping[str, Any], errors: list[str], warnings: list[str]) -> None:
    before = int(leakage.get("new_unallowlisted_production_findings_before", -1))
    after = int(leakage.get("new_unallowlisted_production_findings_after", -1))
    if before >= 0 and after > before:
        errors.append("LOCAL-05 increased runtime leakage")
    scan = run_leakage_scan(root)
    if scan:
        scan_count = int(scan.get("summary", {}).get("new_violation_count", -1))
        if scan_count > before and before >= 0:
            errors.append("current leakage scan exceeds recorded LOCAL-05 baseline")
        if scan.get("gate_report", {}).get("status") == "fail":
            warnings.append("runtime leakage gate fails with pre-existing findings")


def run_leakage_scan(root: Path) -> Mapping[str, Any]:
    import audit_runtime_architecture_leakage as leakage

    policy = leakage.load_json(root / leakage.DEFAULT_POLICY)
    allowlist = leakage.load_json(root / leakage.DEFAULT_ALLOWLIST)
    return leakage.build_leakage_audit(root, policy, allowlist, policy_errors=[])


def tree_digest(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        if path.name.endswith("-journal") or path.name.endswith("-wal") or path.name.endswith("-shm"):
            continue
        digest.update(path.relative_to(root).as_posix().encode("utf-8"))
        digest.update(path.read_bytes())
    return digest.hexdigest()


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
