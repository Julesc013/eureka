#!/usr/bin/env python3
"""Validate LOCAL-04 read-only localhost HTTP service evidence."""

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
from runtime.local_service import LocalServiceApp, validate_host_allowed
from runtime.local_service.errors import LocalServiceHostError


TASK_ID = "LOCAL-04"
NEXT_TASK = "LOCAL-05"
F0_CLOSEOUT = "LOCAL-14"
POLICIES = {
    "control/policies/local_http_service_policy.json": "local_http_service_policy.v0",
    "control/policies/local_http_route_policy.json": "local_http_route_policy.v0",
    "control/policies/local_http_read_only_policy.json": "local_http_read_only_policy.v0",
}
INVENTORIES = {
    "control/inventory/local_http_service_inventory.json": "local_http_service_inventory.v0",
    "control/inventory/local_http_route_matrix.json": "local_http_route_matrix.v0",
    "control/inventory/local_http_service_result.json": "local_http_service_result.v0",
    "control/inventory/local_http_service_smoke_result.json": "local_http_service_smoke_result.v0",
    "control/inventory/local_http_gap_register.json": "local_http_gap_register.v0",
    "control/inventory/local_04_leakage_baseline.json": "local_04_leakage_baseline.v0",
    "control/inventory/local_04_next_task_decision.json": "local_04_next_task_decision.v0",
}
RUNTIME_FILES = (
    "runtime/local_service/__init__.py",
    "runtime/local_service/app.py",
    "runtime/local_service/routes.py",
    "runtime/local_service/responses.py",
    "runtime/local_service/server.py",
    "runtime/local_service/request_context.py",
    "runtime/local_service/validation.py",
    "runtime/local_service/errors.py",
)
SCRIPTS = (
    "scripts/eureka_local_server.py",
    "scripts/eureka_local_service_smoke.py",
    "scripts/validate_local_http_service.py",
)
TESTS = (
    "tests/runtime/test_local_service_routes.py",
    "tests/runtime/test_local_service_read_only.py",
    "tests/runtime/test_local_service_validation.py",
    "tests/operations/test_local_http_service_scripts.py",
)
DOCS = (
    "docs/architecture/LOCAL_HTTP_SERVICE.md",
    "docs/reference/LOCAL_HTTP_API.md",
    "docs/operations/LOCAL_HTTP_SERVICE_RUNBOOK.md",
)
AUDIT_ROOT = Path("control/audits/local-04-read-only-localhost-http-service-v0")
AUDIT_FILES = (
    "README.md",
    "local_04_report.json",
    "service_boundary.md",
    "route_matrix.md",
    "smoke_result.md",
    "read_only_boundary.md",
    "leakage_baseline.md",
    "validation.md",
    "generated/sample_status_response.json",
    "generated/sample_search_response.json",
    "generated/sample_object_response.json",
    "generated/sample_source_response.json",
    "generated/sample_absence_response.json",
    "generated/sample_smoke_result.json",
    "generated/sample_summary.md",
)
ROUTES = (
    "/",
    "/status",
    "/health",
    "/api/v1/status",
    "/api/v1/health",
    "/api/v1/search",
    "/api/v1/object/<record_id>",
    "/api/v1/source/<source_id>",
    "/api/v1/absence",
)
ALLOWED_IMPORTS = {
    "dataclasses",
    "enum",
    "typing",
    "pathlib",
    "json",
    "datetime",
    "contextlib",
    "urllib.parse",
    "http.server",
    "socketserver",
    "runtime.local_appliance",
    "runtime.public_index",
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
FORBIDDEN_VOCABULARY = (
    "LOCAL-",
    "AIDE",
    "H0",
    "H1",
    "H2",
    "H3",
    "H4",
    "H5",
    "H6",
    "H7",
    "H8",
    "H9",
    "H10",
    "H11",
    "H12",
    "H13",
    "H14",
    "BUNDLE",
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output", help="Optional JSON result output path.")
    args = parser.parse_args(argv)
    result = validate(Path(args.repo_root).resolve())
    if args.output:
        write_json(Path(args.output), result)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print("LOCAL-04 local HTTP service validation", file=stdout)
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
    report = load_json(root / AUDIT_ROOT / "local_04_report.json", "local_04_report.v0", errors)

    validate_policies(payloads, errors)
    validate_inventories(payloads, errors, warnings)
    validate_files(root, errors)
    validate_runtime_imports(root, errors)
    validate_runtime_vocabulary(root, errors)
    service_result = validate_temp_service(root, errors)
    validate_queue(root, errors)
    validate_report(report, errors, warnings)
    validate_leakage(root, payloads.get("control/inventory/local_04_leakage_baseline.json", {}), errors, warnings)

    if not service_result.get("localhost_service_started_in_validation"):
        errors.append("localhost service did not start in validation")
    status = "fail" if errors else ("pass_with_warnings" if warnings else "pass")
    return {
        "schema_version": "local_http_service_validation.v0",
        "task": TASK_ID,
        "status": status,
        "errors": errors,
        "warnings": warnings,
        "localhost_service_started_in_validation": bool(service_result.get("localhost_service_started_in_validation")),
        "status_route_passed": bool(service_result.get("status_route_passed")),
        "search_route_passed": bool(service_result.get("search_route_passed")),
        "absence_route_passed": bool(service_result.get("absence_route_passed")),
        "write_methods_rejected": bool(service_result.get("write_methods_rejected")),
        "lan_binding_rejected": bool(service_result.get("lan_binding_rejected")),
        "source_probe_executed": False,
        "review_mutation_performed": False,
        "index_rebuild_performed": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def validate_policies(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    service = payloads.get("control/policies/local_http_service_policy.json", {})
    expected_service = {
        "localhost_default": True,
        "default_host": "127.0.0.1",
        "lan_binding_default": False,
        "read_only_default": True,
        "write_routes_enabled": False,
        "source_probe_execution_enabled": False,
        "workunit_execution_enabled": False,
        "review_decision_mutation_enabled": False,
        "index_rebuild_enabled": False,
        "deployment_enabled": False,
        "site_dist_writes_enabled": False,
        "model_provider_enabled": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }
    for key, value in expected_service.items():
        if service.get(key) != value:
            errors.append(f"service policy {key} mismatch")
    if service.get("allowed_hosts_current") != ["127.0.0.1", "localhost"]:
        errors.append("service policy allowed_hosts_current mismatch")
    if service.get("forbidden_hosts_current") != ["0.0.0.0", "::"]:
        errors.append("service policy forbidden_hosts_current mismatch")

    read_only = payloads.get("control/policies/local_http_read_only_policy.json", {})
    if read_only.get("mutating_methods_forbidden") != ["POST", "PUT", "PATCH", "DELETE"]:
        errors.append("read-only policy mutating methods mismatch")
    for key in (
        "direct_store_mutation_forbidden",
        "review_decision_mutation_forbidden",
        "index_rebuild_forbidden",
        "source_probe_forbidden",
        "workunit_creation_forbidden",
        "lan_binding_forbidden_current_task",
    ):
        if read_only.get(key) is not True:
            errors.append(f"read-only policy {key} must be true")

    route_policy = payloads.get("control/policies/local_http_route_policy.json", {})
    rows = route_policy.get("routes")
    if not isinstance(rows, list):
        errors.append("route policy must contain routes list")
        return
    seen = [str(row.get("path")) for row in rows if isinstance(row, Mapping)]
    if seen != list(ROUTES):
        errors.append("route policy route order mismatch")
    for row in rows:
        if not isinstance(row, Mapping):
            errors.append("route policy row must be object")
            continue
        if row.get("method") != "GET":
            errors.append(f"route policy method must be GET for {row.get('path')}")
        for key, value in {
            "read_only": True,
            "mutates_store": False,
            "requires_operator_token": False,
            "allowed_in_lan_mode": False,
        }.items():
            if row.get(key) is not value:
                errors.append(f"route policy {key} mismatch for {row.get('path')}")


def validate_inventories(payloads: Mapping[str, Mapping[str, Any]], errors: list[str], warnings: list[str]) -> None:
    inventory = payloads.get("control/inventory/local_http_service_inventory.json", {})
    if inventory.get("runtime_package") != "runtime/local_service":
        errors.append("service inventory runtime_package mismatch")
    for key, value in {
        "default_host": "127.0.0.1",
        "lan_enabled": False,
        "read_only": True,
        "write_routes_enabled": False,
        "source_probe_execution_enabled": False,
        "workunit_execution_enabled": False,
        "review_decision_mutation_enabled": False,
        "index_rebuild_enabled": False,
        "deployment_performed": False,
        "network_dependencies_external": 0,
    }.items():
        if inventory.get(key) != value:
            errors.append(f"service inventory {key} mismatch")

    route_matrix = payloads.get("control/inventory/local_http_route_matrix.json", {})
    rows = route_matrix.get("routes")
    if not isinstance(rows, list):
        errors.append("route matrix must contain routes list")
    else:
        seen = [str(row.get("path")) for row in rows if isinstance(row, Mapping)]
        if seen != list(ROUTES):
            errors.append("route matrix route order mismatch")
        for row in rows:
            if isinstance(row, Mapping) and row.get("mutates_store") is not False:
                errors.append(f"route matrix mutation flag must be false for {row.get('path')}")

    result = payloads.get("control/inventory/local_http_service_result.json", {})
    for key in (
        "runtime_package_added",
        "server_script_added",
        "smoke_script_added",
        "validator_added",
        "localhost_service_started_in_validation",
        "status_route_passed",
        "search_route_passed",
        "absence_route_passed",
        "write_methods_rejected",
        "lan_binding_rejected",
    ):
        if result.get(key) is not True:
            errors.append(f"service result {key} must be true")
    for key in (
        "source_probe_executed",
        "review_mutation_performed",
        "index_rebuild_performed",
        "deployment_performed",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    ):
        if result.get(key) is not False:
            errors.append(f"service result {key} must be false")

    smoke = payloads.get("control/inventory/local_http_service_smoke_result.json", {})
    if smoke.get("status") != "pass":
        errors.append("smoke result inventory must pass")

    decision = payloads.get("control/inventory/local_04_next_task_decision.json", {})
    if decision.get("recommended_next_task") != "LOCAL-05 \u2014 HTML workbench v0":
        errors.append("LOCAL-04 next task decision must point to LOCAL-05")
    if decision.get("f0_current_status") != "deferred" or decision.get("f0_can_resume_after") != F0_CLOSEOUT:
        errors.append("F0 must remain deferred until LOCAL-14")
    if decision.get("lan_can_start") is not False or decision.get("html_workbench_can_start") is not True:
        errors.append("LOCAL-04 next task decision flags mismatch")

    leakage = payloads.get("control/inventory/local_04_leakage_baseline.json", {})
    if leakage.get("local_04_increased_leakage") is not False:
        errors.append("LOCAL-04 leakage baseline must not increase leakage")
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
    for rel in RUNTIME_FILES:
        tree = ast.parse((root / rel).read_text(encoding="utf-8"), filename=rel)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    validate_import_name(rel, alias.name, errors)
            elif isinstance(node, ast.ImportFrom):
                if node.level:
                    continue
                validate_import_name(rel, node.module or "", errors)


def validate_import_name(rel: str, module: str, errors: list[str]) -> None:
    if any(module == item or module.startswith(item + ".") for item in FORBIDDEN_IMPORT_PREFIXES):
        errors.append(f"forbidden import in {rel}: {module}")
    if module.startswith("runtime.") and not any(module == item or module.startswith(item + ".") for item in ALLOWED_IMPORTS):
        errors.append(f"unexpected runtime import in {rel}: {module}")
    if not module.startswith("runtime.") and module.split(".")[0] not in {item.split(".")[0] for item in ALLOWED_IMPORTS}:
        errors.append(f"unexpected import in {rel}: {module}")


def validate_runtime_vocabulary(root: Path, errors: list[str]) -> None:
    for rel in RUNTIME_FILES:
        text = (root / rel).read_text(encoding="utf-8")
        for token in FORBIDDEN_VOCABULARY:
            if token in text:
                errors.append(f"forbidden runtime vocabulary in {rel}: {token}")


def validate_temp_service(root: Path, errors: list[str]) -> dict[str, Any]:
    result = {
        "localhost_service_started_in_validation": False,
        "status_route_passed": False,
        "search_route_passed": False,
        "absence_route_passed": False,
        "write_methods_rejected": False,
        "lan_binding_rejected": False,
    }
    with tempfile.TemporaryDirectory(prefix="eureka-local-http-") as tmp:
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
            status = app.handle("GET", "/status")
            api_status = app.handle("GET", "/api/v1/status")
            search = app.handle("GET", "/api/v1/search", "q=sampleproject")
            absence = app.handle("GET", "/api/v1/absence", "q=definitely-not-present-local-04")
            missing_object = app.handle("GET", "/api/v1/object/not-present")
            source = app.handle("GET", "/api/v1/source/not-present")
            post = app.handle("POST", "/api/v1/search", "q=sampleproject")
            result["status_route_passed"] = status.status_code == 200 and api_status.status_code == 200
            result["search_route_passed"] = search.status_code == 200 and search.payload.get("schema_version") == "local_http_search_response.v0"
            result["absence_route_passed"] = absence.status_code == 200 and absence.payload.get("schema_version") == "local_http_absence_response.v0"
            result["write_methods_rejected"] = post.status_code == 405 and missing_object.status_code == 404 and source.status_code == 200
        except Exception as exc:
            errors.append(f"in-process local service failed: {exc}")
        finally:
            if runtime is not None:
                close_local_appliance(runtime)

        try:
            validate_host_allowed("0.0.0.0")
            errors.append("0.0.0.0 host was accepted")
        except LocalServiceHostError:
            result["lan_binding_rejected"] = True
        try:
            validate_host_allowed("192.168.1.10")
            errors.append("non-localhost host was accepted")
        except LocalServiceHostError:
            pass

        smoke_reject = run(root, "python", "scripts/eureka_local_service_smoke.py", "--base-url", "http://192.168.1.10:8765", "--json")
        if smoke_reject.returncode == 0:
            errors.append("smoke script accepted non-localhost URL")

        process: subprocess.Popen[str] | None = None
        try:
            process = subprocess.Popen(
                [
                    "python",
                    "scripts/eureka_local_server.py",
                    "--instance",
                    str(instance),
                    "--host",
                    "127.0.0.1",
                    "--port",
                    "0",
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
                errors.append(f"localhost server did not report startup: {stderr}")
                return result
            startup = json.loads(startup_line)
            if startup.get("status") != "pass":
                errors.append(f"localhost server startup failed: {startup}")
                return result
            result["localhost_service_started_in_validation"] = True
            smoke = run(
                root,
                "python",
                "scripts/eureka_local_service_smoke.py",
                "--base-url",
                str(startup["base_url"]),
                "--json",
            )
            if smoke.returncode != 0:
                errors.append(f"local service smoke failed: {smoke.stdout}{smoke.stderr}")
            else:
                payload = json.loads(smoke.stdout)
                if payload.get("status_route_passed") is not True:
                    errors.append("smoke status route did not pass")
                if payload.get("search_route_passed") is not True:
                    errors.append("smoke search route did not pass")
                if payload.get("absence_route_passed") is not True:
                    errors.append("smoke absence route did not pass")
        except Exception as exc:
            errors.append(f"localhost server validation failed: {exc}")
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

        after = tree_digest(instance)
        if after != before:
            errors.append("local HTTP service mutated initialized instance files")
    return result


def validate_queue(root: Path, errors: list[str]) -> None:
    queue = read_text(root / ".aide/queue/index.yaml", errors)
    task = read_text(root / ".aide/queue/LOCAL-04/task.yaml", errors)
    next_task = read_text(root / ".aide/queue/LOCAL-05/task.yaml", errors)
    if "current_recommended_task: LOCAL-05" not in queue:
        errors.append("queue index must point to LOCAL-05")
    if "id: LOCAL-04" not in queue or "status: completed" not in queue:
        errors.append("queue index must mark LOCAL-04 completed")
    if "id: LOCAL-05" not in queue or "status: queued" not in queue:
        errors.append("queue index must include queued LOCAL-05")
    if "deferred_until: LOCAL-14" not in queue:
        errors.append("queue index must keep F0 deferred until LOCAL-14")
    if "recommended_next: LOCAL-05" not in task:
        errors.append("LOCAL-04 task must recommend LOCAL-05")
    if "HTML workbench v0" not in next_task:
        errors.append("LOCAL-05 task file title mismatch")


def validate_report(report: Mapping[str, Any], errors: list[str], warnings: list[str]) -> None:
    if report.get("recommended_next_task") != "LOCAL-05 \u2014 HTML workbench v0":
        errors.append("LOCAL-04 audit report must recommend LOCAL-05")
    for key in (
        "runtime_package_added",
        "server_script_added",
        "smoke_script_added",
        "validator_added",
        "localhost_service_started_in_validation",
        "status_route_passed",
        "search_route_passed",
        "absence_route_passed",
        "write_methods_rejected",
        "lan_binding_rejected",
        "server_implemented",
    ):
        if report.get(key) is not True:
            errors.append(f"LOCAL-04 report {key} must be true")
    for key in (
        "html_workbench_implemented",
        "workunit_runtime_implemented",
        "lan_enabled",
        "source_probe_executed",
        "review_mutation_performed",
        "index_rebuild_performed",
        "deployment_performed",
        "local_04_increased_leakage",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    ):
        if report.get(key) is not False:
            errors.append(f"LOCAL-04 report {key} must be false")
    validation = report.get("validation", {})
    if isinstance(validation, Mapping) and str(validation.get("runtime_leakage_gate", "")).startswith("fail_pre_existing"):
        warnings.append("audit report records pre-existing runtime leakage gate failure")


def validate_leakage(root: Path, leakage: Mapping[str, Any], errors: list[str], warnings: list[str]) -> None:
    before = int(leakage.get("new_unallowlisted_production_findings_before", -1))
    after = int(leakage.get("new_unallowlisted_production_findings_after", -1))
    if before >= 0 and after > before:
        errors.append("LOCAL-04 increased runtime leakage")
    scan = run_leakage_scan(root)
    if scan:
        scan_count = int(scan.get("summary", {}).get("new_violation_count", -1))
        if scan_count > before and before >= 0:
            errors.append("current leakage scan exceeds recorded LOCAL-04 baseline")
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
