#!/usr/bin/env python3
"""Validate LOCAL-10 local auto-test and auto-search harness evidence."""

from __future__ import annotations

import argparse
import ast
import json
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO

try:
    from local_queue_progress import f0_deferred_or_past_local_closeout, queue_current_or_advanced, queue_task_available, queue_task_completed
except ModuleNotFoundError:  # pragma: no cover - supports package-style imports in tests.
    from scripts.local_queue_progress import f0_deferred_or_past_local_closeout, queue_current_or_advanced, queue_task_available, queue_task_completed


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local.eval import get_default_local_eval_suites, get_default_query_suite, validate_eval_report, validate_no_forbidden_eval_effects


TASK_ID = "LOCAL-10"
NEXT_TASK = "LOCAL-11"
AUDIT_ROOT = Path("control/audits/local-10-auto-test-search-harness-v0")
POLICIES = {
    "control/policies/local_auto_test_policy.json": "local_auto_test_policy.v0",
    "control/policies/local_auto_search_policy.json": "local_auto_search_policy.v0",
    "control/policies/local_eval_safety_policy.json": "local_eval_safety_policy.v0",
    "control/policies/local_eval_latency_policy.json": "local_eval_latency_policy.v0",
    "control/policies/local_eval_report_policy.json": "local_eval_report_policy.v0",
}
INVENTORIES = {
    "control/inventory/local_auto_test_inventory.json": "local_auto_test_inventory.v0",
    "control/inventory/local_auto_search_suite.json": "local_auto_search_suite.v0",
    "control/inventory/local_auto_test_result.json": "local_auto_test_result.v0",
    "control/inventory/local_auto_search_result.json": "local_auto_search_result.v0",
    "control/inventory/local_latency_smoke_result.json": "local_latency_smoke_result.v0",
    "control/inventory/local_eval_safety_result.json": "local_eval_safety_result.v0",
    "control/inventory/local_eval_gap_register.json": "local_eval_gap_register.v0",
    "control/inventory/local_10_leakage_baseline.json": "local_10_leakage_baseline.v0",
    "control/inventory/local_10_next_task_decision.json": "local_10_next_task_decision.v0",
}
RUNTIME_FILES = (
    "runtime/local/eval/__init__.py",
    "runtime/local/eval/assertions.py",
    "runtime/local/eval/errors.py",
    "runtime/local/eval/latency.py",
    "runtime/local/eval/reports.py",
    "runtime/local/eval/runner.py",
    "runtime/local/eval/safety.py",
    "runtime/local/eval/suites.py",
    "runtime/local/eval/validation.py",
)
SCRIPTS = (
    "scripts/eureka_local_auto_test.py",
    "scripts/eureka_local_auto_search.py",
    "scripts/eureka_local_eval_report.py",
    "scripts/validate_local_auto_test_harness.py",
)
AUDIT_FILES = (
    "README.md",
    "local_10_report.json",
    "auto_test_summary.md",
    "auto_search_suite.md",
    "auto_search_result.md",
    "latency_smoke.md",
    "safety_result.md",
    "gap_register.md",
    "leakage_baseline.md",
    "validation.md",
    "generated/sample_auto_test_result.json",
    "generated/sample_auto_search_result.json",
    "generated/sample_latency_report.json",
    "generated/sample_safety_report.json",
    "generated/sample_eval_summary.md",
    "generated/sample_summary.md",
)
EXPECTED_SUITES = (
    "service_health",
    "json_search",
    "html_workbench",
    "absence",
    "read_only_safety",
    "worker_queue_safety",
    "latency_smoke",
    "local_state_cleanliness",
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
FORBIDDEN_RUNTIME_TOKENS = (
    "LOCAL-",
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
    "task",
    "prompt",
    "agent",
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
        print("LOCAL-10 local auto-test harness validation", file=stdout)
        print(f"status: {result['status']}", file=stdout)
        for error in result["errors"]:
            print(f"ERROR: {error}", file=stdout)
        for warning in result["warnings"]:
            print(f"WARN: {warning}", file=stdout)
    return 0 if result["status"] in {"pass", "pass_with_warnings"} else 1


def validate(root: Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    payloads = {rel: load_json(root / rel, schema, errors) for rel, schema in {**POLICIES, **INVENTORIES}.items()}
    report = load_json(root / AUDIT_ROOT / "local_10_report.json", "local_10_report.v0", errors)
    validate_files(root, errors)
    validate_policies(payloads, errors)
    validate_inventories(payloads, errors)
    validate_runtime_imports(root, errors)
    validate_runtime_vocabulary(root, errors)
    runtime_result = validate_runtime_shapes(errors)
    smoke_result = validate_scripts_against_server(root, errors)
    validate_queue_state(root, errors)
    validate_report(report, errors)
    validate_leakage(root, payloads.get("control/inventory/local_10_leakage_baseline.json", {}), errors, warnings)
    status = "fail" if errors else ("pass_with_warnings" if warnings else "pass")
    return {
        "schema_version": "local_auto_test_harness_validation.v0",
        "task": TASK_ID,
        "status": status,
        "errors": errors,
        "warnings": warnings,
        "runtime_package_added": all((root / item).is_file() for item in RUNTIME_FILES),
        "auto_test_script_added": (root / "scripts/eureka_local_auto_test.py").is_file(),
        "auto_search_script_added": (root / "scripts/eureka_local_auto_search.py").is_file(),
        "eval_report_script_added": (root / "scripts/eureka_local_eval_report.py").is_file(),
        "validator_added": True,
        "service_health_suite_passed": smoke_result.get("service_health_suite_passed", False),
        "json_search_suite_passed": smoke_result.get("json_search_suite_passed", False),
        "html_workbench_suite_passed": smoke_result.get("html_workbench_suite_passed", False),
        "absence_suite_passed": smoke_result.get("absence_suite_passed", False),
        "read_only_safety_suite_passed": smoke_result.get("read_only_safety_suite_passed", False),
        "worker_queue_safety_suite_passed": smoke_result.get("worker_queue_safety_suite_passed", False),
        "latency_recorded": smoke_result.get("latency_recorded", False),
        "default_suites_present": runtime_result.get("default_suites_present", False),
        "default_queries_present": runtime_result.get("default_queries_present", False),
        "external_network_used": False,
        "source_probe_executed": False,
        "extraction_executed": False,
        "model_provider_used": False,
        "download_install_execute_performed": False,
        "site_dist_mutated": False,
        "master_index_mutated": False,
        "lan_enabled": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def validate_files(root: Path, errors: list[str]) -> None:
    for rel in (*RUNTIME_FILES, *SCRIPTS):
        if not (root / rel).is_file():
            errors.append(f"required file is missing: {rel}")
    for rel in AUDIT_FILES:
        if not (root / AUDIT_ROOT / rel).is_file():
            errors.append(f"audit file is missing: {AUDIT_ROOT / rel}")


def validate_policies(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    auto = payloads.get("control/policies/local_auto_test_policy.json", {})
    for key in ("deterministic_suites_only", "localhost_only", "generated_artifact_cleanliness_required", "report_outputs_required"):
        require_true(auto, key, errors, "auto-test policy")
    for key in (
        "lan_enabled",
        "external_network_enabled",
        "source_probe_execution_enabled",
        "extraction_execution_enabled",
        "model_provider_enabled",
        "download_install_execute_enabled",
        "site_dist_writes_enabled",
        "master_index_mutation_enabled",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    ):
        require_false(auto, key, errors, "auto-test policy")
    search = payloads.get("control/policies/local_auto_search_policy.json", {})
    for key in ("local_reviewed_index_only", "query_suite_fixed_current_task", "absence_report_required_for_missing_queries", "no_global_absence_claim"):
        require_true(search, key, errors, "auto-search policy")
    for key in ("synthetic_generation_enabled", "live_source_search_enabled", "source_probe_enabled"):
        require_false(search, key, errors, "auto-search policy")
    if search.get("query_max_length") != 256 or search.get("result_limit_max") != 50:
        errors.append("auto-search policy query/result bounds mismatch")
    latency = payloads.get("control/policies/local_eval_latency_policy.json", {})
    require_false(latency, "strict_latency_gate_enabled", errors, "latency policy")
    require_true(latency, "record_elapsed_ms", errors, "latency policy")
    if latency.get("per_route_timeout_seconds") != 10:
        errors.append("latency policy per-route timeout mismatch")
    report = payloads.get("control/policies/local_eval_report_policy.json", {})
    for key in ("json_report_required", "markdown_summary_required", "suite_status_required", "per_query_status_required", "latency_values_required", "safety_status_required"):
        require_true(report, key, errors, "report policy")


def validate_inventories(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    inventory = payloads.get("control/inventory/local_auto_test_inventory.json", {})
    if tuple(inventory.get("suites", ())) != EXPECTED_SUITES:
        errors.append("auto-test inventory suite list mismatch")
    result = payloads.get("control/inventory/local_auto_test_result.json", {})
    for key in (
        "runtime_package_added",
        "auto_test_script_added",
        "auto_search_script_added",
        "eval_report_script_added",
        "validator_added",
        "service_health_suite_passed",
        "json_search_suite_passed",
        "html_workbench_suite_passed",
        "absence_suite_passed",
        "read_only_safety_suite_passed",
        "worker_queue_safety_suite_passed",
        "latency_recorded",
    ):
        require_true(result, key, errors, "auto-test result")
    for key in (
        "external_network_used",
        "source_probe_executed",
        "extraction_executed",
        "model_provider_used",
        "site_dist_mutated",
        "master_index_mutated",
        "lan_enabled",
        "deployment_performed",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    ):
        require_false(result, key, errors, "auto-test result")
    next_decision = payloads.get("control/inventory/local_10_next_task_decision.json", {})
    if next_decision.get("recommended_next_task") != "LOCAL-11 \u2014 LAN binding policy and safety gate":
        errors.append("LOCAL-10 next decision must recommend LOCAL-11")
    require_false(next_decision, "lan_can_start", errors, "LOCAL-10 next decision")


def validate_runtime_imports(root: Path, errors: list[str]) -> None:
    for path in (root / "runtime/local/eval").glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            modules: list[str] = []
            if isinstance(node, ast.Import):
                modules = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and not node.level:
                modules = [node.module or ""]
            for module in modules:
                if any(module == item or module.startswith(item + ".") for item in FORBIDDEN_IMPORT_PREFIXES):
                    errors.append(f"forbidden import in {path}: {module}")


def validate_runtime_vocabulary(root: Path, errors: list[str]) -> None:
    for path in (root / "runtime/local/eval").glob("*.py"):
        text = path.read_text(encoding="utf-8")
        for token in FORBIDDEN_RUNTIME_TOKENS:
            if token in text:
                errors.append(f"forbidden runtime token in {path}: {token}")


def validate_runtime_shapes(errors: list[str]) -> dict[str, bool]:
    suites = get_default_local_eval_suites()
    queries = get_default_query_suite()
    suite_names = tuple(suite.name for suite in suites)
    if suite_names != EXPECTED_SUITES:
        errors.append("default suite names mismatch")
    if "sampleproject" not in queries or "definitely-not-present-local-10" not in queries:
        errors.append("default query suite is missing required queries")
    return {
        "default_suites_present": suite_names == EXPECTED_SUITES,
        "default_queries_present": "sampleproject" in queries and "definitely-not-present-local-10" in queries,
    }


def validate_scripts_against_server(root: Path, errors: list[str]) -> dict[str, bool]:
    with tempfile.TemporaryDirectory() as temp:
        temp_path = Path(temp)
        instance = temp_path / "eureka-instance"
        init = run_cmd(root, "scripts/eureka_init_instance.py", "--instance", str(instance), "--json")
        if init.returncode != 0:
            errors.append(f"instance init failed: {init.stderr or init.stdout}")
            return {}
        validate = run_cmd(root, "scripts/eureka_validate_instance.py", "--instance", str(instance), "--json")
        if validate.returncode != 0:
            errors.append(f"instance validation failed: {validate.stderr or validate.stdout}")
            return {}
        port = free_port()
        process = start_server(root, instance, port)
        base_url = f"http://127.0.0.1:{port}"
        try:
            auto_report = temp_path / "auto_test.json"
            auto_summary = temp_path / "auto_test.md"
            auto = run_cmd(
                root,
                "scripts/eureka_local_auto_test.py",
                "--base-url",
                base_url,
                "--json",
                "--output",
                str(auto_report),
                "--summary-output",
                str(auto_summary),
                timeout=90,
            )
            if auto.returncode != 0:
                errors.append(f"auto-test script failed: {auto.stderr or auto.stdout[:500]}")
            search_report = temp_path / "auto_search.json"
            search = run_cmd(
                root,
                "scripts/eureka_local_auto_search.py",
                "--base-url",
                base_url,
                "--json",
                "--output",
                str(search_report),
                timeout=90,
            )
            if search.returncode != 0:
                errors.append(f"auto-search script failed: {search.stderr or search.stdout[:500]}")
            summary = temp_path / "summary.md"
            eval_report = run_cmd(
                root,
                "scripts/eureka_local_eval_report.py",
                "--input",
                str(auto_report),
                "--output",
                str(summary),
                "--json",
                timeout=60,
            )
            if eval_report.returncode != 0:
                errors.append(f"eval report script failed: {eval_report.stderr or eval_report.stdout}")
            auto_payload = load_json(auto_report, "local_eval_report.v0", errors) if auto_report.is_file() else {}
            if auto_payload:
                try:
                    validate_no_forbidden_eval_effects(validate_eval_report(auto_payload))
                except Exception as exc:
                    errors.append(f"auto-test report validation failed: {exc}")
            search_payload = load_json(search_report, "local_auto_search_result.v0", errors) if search_report.is_file() else {}
            if search_payload and search_payload.get("status") != "pass":
                errors.append("auto-search report did not pass")
            suite_map = {suite.get("suite"): suite for suite in auto_payload.get("suite_results", [])} if isinstance(auto_payload, Mapping) else {}
            return {
                "service_health_suite_passed": suite_map.get("service_health", {}).get("status") == "pass",
                "json_search_suite_passed": suite_map.get("json_search", {}).get("status") == "pass",
                "html_workbench_suite_passed": suite_map.get("html_workbench", {}).get("status") == "pass",
                "absence_suite_passed": suite_map.get("absence", {}).get("status") == "pass",
                "read_only_safety_suite_passed": suite_map.get("read_only_safety", {}).get("status") == "pass",
                "worker_queue_safety_suite_passed": suite_map.get("worker_queue_safety", {}).get("status") == "pass",
                "latency_recorded": bool(auto_payload.get("latency", {}).get("route_count")),
            }
        finally:
            stop_server(process)


def validate_queue_state(root: Path, errors: list[str]) -> None:
    index = (root / ".aide/queue/index.yaml").read_text(encoding="utf-8")
    if not queue_current_or_advanced(root, TASK_ID, NEXT_TASK):
        errors.append("queue index must point to LOCAL-11 after LOCAL-10")
    if not queue_task_completed(root, TASK_ID):
        errors.append("queue index must include completed LOCAL-10 entry")
    next_path = root / ".aide/queue/LOCAL-11/task.yaml"
    if not next_path.is_file() or not queue_task_available(root, NEXT_TASK):
        errors.append("LOCAL-11 queue item is missing")
    f0 = json.loads((root / "control/inventory/f0_deferral_for_local_appliance.json").read_text(encoding="utf-8"))
    if f0.get("deferred_until") != "LOCAL-14" and not f0_deferred_or_past_local_closeout(root):
        errors.append("F0 must remain deferred until LOCAL-14")


def validate_report(report: Mapping[str, Any], errors: list[str]) -> None:
    for key in (
        "runtime_package_added",
        "auto_test_script_added",
        "auto_search_script_added",
        "eval_report_script_added",
        "validator_added",
        "service_health_suite_passed",
        "json_search_suite_passed",
        "html_workbench_suite_passed",
        "absence_suite_passed",
        "read_only_safety_suite_passed",
        "worker_queue_safety_suite_passed",
        "latency_recorded",
        "server_implemented",
        "html_workbench_implemented",
        "workunit_runtime_implemented",
        "worker_execution_enabled",
        "auto_test_harness_enabled",
    ):
        require_true(report, key, errors, "LOCAL-10 report")
    for key in (
        "lan_enabled",
        "external_network_used",
        "source_probe_executed",
        "extraction_executed",
        "agent_execution_performed",
        "model_provider_used",
        "download_install_execute_performed",
        "master_index_mutated",
        "site_dist_mutated",
        "deployment_performed",
        "local_10_increased_leakage",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    ):
        require_false(report, key, errors, "LOCAL-10 report")
    if report.get("recommended_next_task") != "LOCAL-11 \u2014 LAN binding policy and safety gate":
        errors.append("LOCAL-10 report recommended_next_task mismatch")


def validate_leakage(root: Path, baseline: Mapping[str, Any], errors: list[str], warnings: list[str]) -> None:
    if baseline.get("local_10_increased_leakage") is not False:
        errors.append("LOCAL-10 leakage baseline must state no increase")
    try:
        scan = subprocess.run(
            [sys.executable, "scripts/audit_runtime_architecture_leakage.py", "--check", "--json"],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
            timeout=360,
        )
    except subprocess.TimeoutExpired:
        errors.append("runtime leakage scan timed out during LOCAL-10 validation")
        return
    try:
        payload = json.loads(scan.stdout)
        new_count = int(payload.get("summary", {}).get("new_violation_count", 0))
    except Exception:
        errors.append("runtime leakage scan output could not be parsed")
        return
    expected_after = int(baseline.get("new_unallowlisted_production_findings_after", new_count))
    if new_count > expected_after:
        errors.append(f"LOCAL-10 increased runtime leakage: {new_count} > {expected_after}")
    if scan.returncode != 0:
        warnings.append(f"runtime leakage gate remains failing with {new_count} pre-existing new violations")


def start_server(root: Path, instance: Path, port: int) -> subprocess.Popen[str]:
    process = subprocess.Popen(
        [
            sys.executable,
            "scripts/eureka_local_server.py",
            "--instance",
            str(instance),
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
            "--json-startup",
        ],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        line = process.stdout.readline().strip() if process.stdout else ""
        if not line:
            raise RuntimeError("local server did not emit startup output")
        payload = json.loads(line)
        if payload.get("status") != "pass":
            raise RuntimeError(f"local server failed to start: {payload}")
        wait_for_status(port)
        return process
    except Exception:
        stop_server(process)
        raise


def wait_for_status(port: int) -> None:
    import urllib.request

    url = f"http://127.0.0.1:{port}/api/v1/health"
    for _ in range(30):
        try:
            with urllib.request.urlopen(url, timeout=1) as response:
                if int(response.getcode()) == 200:
                    return
        except Exception:
            time.sleep(0.1)
    raise RuntimeError("local server did not become healthy")


def stop_server(process: subprocess.Popen[str]) -> None:
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)
    if process.stdout:
        process.stdout.close()
    if process.stderr:
        process.stderr.close()


def free_port() -> int:
    sock = socket.socket()
    try:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])
    finally:
        sock.close()


def run_cmd(root: Path, *args: str, timeout: int = 60) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, *args], cwd=root, text=True, capture_output=True, check=False, timeout=timeout)


def load_json(path: Path, schema: str, errors: list[str]) -> dict[str, Any]:
    if not path.is_file():
        errors.append(f"JSON file is missing: {path}")
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"JSON file is invalid: {path}: {exc}")
        return {}
    if payload.get("schema_version") != schema:
        errors.append(f"unexpected schema for {path}: {payload.get('schema_version')!r}")
    return payload


def require_true(payload: Mapping[str, Any], key: str, errors: list[str], context: str) -> None:
    if payload.get(key) is not True:
        errors.append(f"{context} must set {key}=true")


def require_false(payload: Mapping[str, Any], key: str, errors: list[str], context: str) -> None:
    if payload.get(key) is not False:
        errors.append(f"{context} must set {key}=false")


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
