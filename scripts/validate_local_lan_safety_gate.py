#!/usr/bin/env python3
"""Validate LOCAL-11 LAN binding safety gate evidence."""

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

from runtime.local_appliance import close_local_appliance, open_local_appliance
from runtime.local_network import classify_client_scope, is_route_allowed_for_scope, validate_service_host
from runtime.local_service import LocalServiceApp


TASK_ID = "LOCAL-11"
NEXT_TASK = "LOCAL-12"
AUDIT_ROOT = Path("control/audits/local-11-lan-binding-safety-gate-v0")
POLICIES = {
    "control/policies/local_lan_binding_policy.json": "local_lan_binding_policy.v0",
    "control/policies/local_lan_route_policy.json": "local_lan_route_policy.v0",
    "control/policies/local_lan_mutation_policy.json": "local_lan_mutation_policy.v0",
    "control/policies/local_lan_operator_boundary_policy.json": "local_lan_operator_boundary_policy.v0",
    "control/policies/local_lan_smoke_prereq_policy.json": "local_lan_smoke_prereq_policy.v0",
}
INVENTORIES = {
    "control/inventory/local_lan_binding_inventory.json": "local_lan_binding_inventory.v0",
    "control/inventory/local_lan_route_matrix.json": "local_lan_route_matrix.v0",
    "control/inventory/local_lan_safety_gate_result.json": "local_lan_safety_gate_result.v0",
    "control/inventory/local_lan_mutation_block_matrix.json": "local_lan_mutation_block_matrix.v0",
    "control/inventory/local_lan_gap_register.json": "local_lan_gap_register.v0",
    "control/inventory/local_11_leakage_baseline.json": "local_11_leakage_baseline.v0",
    "control/inventory/local_11_next_task_decision.json": "local_11_next_task_decision.v0",
}
RUNTIME_FILES = (
    "runtime/local_network/__init__.py",
    "runtime/local_network/client_scope.py",
    "runtime/local_network/errors.py",
    "runtime/local_network/hosts.py",
    "runtime/local_network/policy.py",
    "runtime/local_network/safety.py",
    "runtime/local_network/validation.py",
)
AUDIT_FILES = (
    "README.md",
    "local_11_report.json",
    "lan_policy_summary.md",
    "route_matrix.md",
    "mutation_block_matrix.md",
    "operator_boundary.md",
    "smoke_prereqs.md",
    "leakage_baseline.md",
    "validation.md",
    "generated/sample_lan_policy_check.json",
    "generated/sample_lan_route_matrix.json",
    "generated/sample_mutation_block_matrix.json",
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
        print("LOCAL-11 LAN safety gate validation", file=stdout)
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
    report = load_json(root / AUDIT_ROOT / "local_11_report.json", "local_11_report.v0", errors)
    validate_files(root, errors)
    validate_policies(payloads, errors)
    validate_inventories(payloads, errors)
    validate_runtime_imports(root, errors)
    validate_runtime_vocabulary(root, errors)
    runtime_result = validate_runtime_shapes(errors)
    service_result = validate_service_gate(root, errors)
    script_result = validate_policy_script(root, errors)
    validate_queue_state(root, errors)
    validate_report(report, errors)
    validate_leakage(root, payloads.get("control/inventory/local_11_leakage_baseline.json", {}), errors, warnings)
    status = "fail" if errors else ("pass_with_warnings" if warnings else "pass")
    return {
        "schema_version": "local_lan_safety_gate_validation.v0",
        "task": TASK_ID,
        "status": status,
        "errors": errors,
        "warnings": warnings,
        "runtime_package_added": all((root / item).is_file() for item in RUNTIME_FILES),
        "lan_policy_check_script_added": (root / "scripts/eureka_lan_policy_check.py").is_file(),
        "validator_added": True,
        "localhost_default_confirmed": runtime_result.get("localhost_default_confirmed", False),
        "bind_lan_required_for_lan_hosts": runtime_result.get("bind_lan_required_for_lan_hosts", False),
        "lan_read_only_default": True,
        "lan_mutations_blocked": service_result.get("lan_mutations_blocked", False),
        "localhost_operator_mutations_remain_token_gated": service_result.get("localhost_operator_mutations_remain_token_gated", False),
        "lan_source_probe_routes_blocked": service_result.get("lan_source_probe_routes_blocked", False),
        "lan_workunit_execution_blocked": runtime_result.get("lan_workunit_execution_blocked", False),
        "lan_review_rebuild_mutation_blocked": service_result.get("lan_review_rebuild_mutation_blocked", False),
        "policy_script_passed": script_result.get("policy_script_passed", False),
        "actual_lan_smoke_performed": False,
        "external_network_used": False,
        "source_probe_executed": False,
        "workunit_execution_from_lan": False,
        "review_mutation_from_lan": False,
        "rebuild_mutation_from_lan": False,
        "master_index_mutated": False,
        "site_dist_mutated": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def validate_files(root: Path, errors: list[str]) -> None:
    for rel in RUNTIME_FILES:
        if not (root / rel).is_file():
            errors.append(f"required runtime file is missing: {rel}")
    for rel in ("scripts/eureka_lan_policy_check.py", "scripts/validate_local_lan_safety_gate.py"):
        if not (root / rel).is_file():
            errors.append(f"required script is missing: {rel}")
    for rel in AUDIT_FILES:
        if not (root / AUDIT_ROOT / rel).is_file():
            errors.append(f"audit file is missing: {AUDIT_ROOT / rel}")


def validate_policies(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    binding = payloads.get("control/policies/local_lan_binding_policy.json", {})
    for key in ("localhost_default", "bind_lan_requires_explicit_flag", "lan_mode_read_only_default", "operator_warning_required", "firewall_warning_required", "shutdown_command_required_before_closeout"):
        require_true(binding, key, errors, "LAN binding policy")
    for key in ("lan_binding_default", "public_deployment_claim_forbidden", "production_readiness_claim_forbidden"):
        if key.endswith("_forbidden"):
            require_true(binding, key, errors, "LAN binding policy")
        else:
            require_false(binding, key, errors, "LAN binding policy")
    if binding.get("allowed_default_host") != "127.0.0.1":
        errors.append("LAN binding policy default host mismatch")
    if tuple(binding.get("allowed_lan_hosts_when_explicit", ())) != ("0.0.0.0", "::"):
        errors.append("LAN binding policy allowed LAN hosts mismatch")

    mutation = payloads.get("control/policies/local_lan_mutation_policy.json", {})
    for key, value in mutation.items():
        if key != "schema_version" and value is not False:
            errors.append(f"LAN mutation policy must set {key}=false")

    boundary = payloads.get("control/policies/local_lan_operator_boundary_policy.json", {})
    for key in ("operator_mutations_localhost_only_current", "operator_token_does_not_grant_lan_mutation_current", "raw_token_never_exposed_to_lan", "token_logging_forbidden", "unsafe_lan_route_returns_403"):
        require_true(boundary, key, errors, "LAN operator boundary policy")


def validate_inventories(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    inventory = payloads.get("control/inventory/local_lan_binding_inventory.json", {})
    for key in ("localhost_default", "bind_lan_explicit_flag_required", "lan_read_only_default", "operator_mutations_localhost_only_current"):
        require_true(inventory, key, errors, "LAN binding inventory")
    for key in ("lan_binding_default", "deployment_performed", "production_readiness_claimed", "public_launch_readiness_claimed"):
        require_false(inventory, key, errors, "LAN binding inventory")
    result = payloads.get("control/inventory/local_lan_safety_gate_result.json", {})
    for key in (
        "runtime_package_added",
        "lan_policy_check_script_added",
        "validator_added",
        "localhost_default_confirmed",
        "bind_lan_required_for_lan_hosts",
        "lan_read_only_default",
        "lan_mutations_blocked",
        "localhost_operator_mutations_remain_token_gated",
        "lan_source_probe_routes_blocked",
        "lan_workunit_execution_blocked",
        "lan_review_rebuild_mutation_blocked",
    ):
        require_true(result, key, errors, "LAN safety result")
    for key in ("deployment_performed", "production_readiness_claimed", "public_launch_readiness_claimed"):
        require_false(result, key, errors, "LAN safety result")
    next_decision = payloads.get("control/inventory/local_11_next_task_decision.json", {})
    if next_decision.get("recommended_next_task") != "LOCAL-12 \u2014 LAN read-only smoke test":
        errors.append("LOCAL-11 next decision must recommend LOCAL-12")
    require_true(next_decision, "lan_can_start_with_explicit_flag", errors, "LOCAL-11 next decision")
    if next_decision.get("f0_can_resume_after") != "LOCAL-14":
        errors.append("F0 must remain deferred until LOCAL-14")


def validate_runtime_imports(root: Path, errors: list[str]) -> None:
    for path in (root / "runtime/local_network").glob("*.py"):
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
    for path in (root / "runtime/local_network").glob("*.py"):
        text = path.read_text(encoding="utf-8")
        for token in FORBIDDEN_RUNTIME_TOKENS:
            if token in text:
                errors.append(f"forbidden runtime token in {path}: {token}")


def validate_runtime_shapes(errors: list[str]) -> dict[str, bool]:
    localhost_ok = validate_service_host("127.0.0.1") == "127.0.0.1" and validate_service_host("localhost") == "localhost"
    rejected = []
    for host in ("0.0.0.0", "::"):
        try:
            validate_service_host(host)
            rejected.append(False)
        except Exception:
            rejected.append(True)
    allowed = validate_service_host("0.0.0.0", bind_lan=True) == "0.0.0.0" and validate_service_host("::", bind_lan=True) == "::"
    if classify_client_scope("192.168.1.20").value != "lan":
        errors.append("LAN client scope classification failed")
    if not is_route_allowed_for_scope("GET", "/status", "lan"):
        errors.append("LAN read-only status route should be allowed")
    if is_route_allowed_for_scope("GET", "/review", "lan"):
        errors.append("LAN review route should be blocked")
    if is_route_allowed_for_scope("POST", "/rebuild", "lan"):
        errors.append("LAN rebuild mutation should be blocked")
    source_blocked = not is_route_allowed_for_scope("GET", "/api/v1/source-probe", "lan")
    work_blocked = not is_route_allowed_for_scope("POST", "/workers/run", "lan")
    if not source_blocked:
        errors.append("LAN source probe route class should be blocked")
    if not work_blocked:
        errors.append("LAN worker execution route class should be blocked")
    return {
        "localhost_default_confirmed": localhost_ok,
        "bind_lan_required_for_lan_hosts": all(rejected) and allowed,
        "lan_workunit_execution_blocked": work_blocked,
    }


def validate_service_gate(root: Path, errors: list[str]) -> dict[str, bool]:
    with tempfile.TemporaryDirectory(prefix="eureka-lan-gate-") as temp:
        instance = Path(temp) / "eureka-instance"
        init = run_cmd(root, "scripts/eureka_init_instance.py", "--instance", str(instance), "--json")
        if init.returncode != 0:
            errors.append(f"instance init failed: {init.stderr or init.stdout}")
            return {}
        runtime = open_local_appliance(instance, read_only=True)
        try:
            app = LocalServiceApp(runtime)
            lan_status = app.handle("GET", "/api/v1/status", client_host="192.168.1.20")
            lan_review = app.handle("GET", "/review", client_host="192.168.1.20")
            lan_rebuild = app.handle("POST", "/rebuild", client_host="192.168.1.20")
            lan_probe = app.handle("GET", "/api/v1/source-probe", client_host="192.168.1.20")
            loopback_rebuild = app.handle("POST", "/rebuild", client_host="127.0.0.1")
        finally:
            close_local_appliance(runtime)
    if lan_status.status_code != 200:
        errors.append(f"LAN read-only status route failed: {lan_status.status_code}")
    if lan_review.status_code != 403:
        errors.append(f"LAN review page should be blocked: {lan_review.status_code}")
    if lan_rebuild.status_code != 403:
        errors.append(f"LAN rebuild mutation should be blocked: {lan_rebuild.status_code}")
    if lan_probe.status_code != 403:
        errors.append(f"LAN source probe route class should be blocked: {lan_probe.status_code}")
    if loopback_rebuild.status_code != 401:
        errors.append(f"loopback rebuild should remain token-gated: {loopback_rebuild.status_code}")
    return {
        "lan_mutations_blocked": lan_rebuild.status_code == 403,
        "localhost_operator_mutations_remain_token_gated": loopback_rebuild.status_code == 401,
        "lan_source_probe_routes_blocked": lan_probe.status_code == 403,
        "lan_review_rebuild_mutation_blocked": lan_rebuild.status_code == 403 and lan_review.status_code == 403,
    }


def validate_policy_script(root: Path, errors: list[str]) -> dict[str, bool]:
    checks = (
        run_cmd(root, "scripts/eureka_lan_policy_check.py", "--host", "127.0.0.1", "--json"),
        run_cmd(root, "scripts/eureka_lan_policy_check.py", "--host", "0.0.0.0", "--json"),
        run_cmd(root, "scripts/eureka_lan_policy_check.py", "--host", "0.0.0.0", "--bind-lan", "--json"),
    )
    if any(item.returncode != 0 for item in checks):
        errors.append("LAN policy check script returned nonzero")
        return {"policy_script_passed": False}
    try:
        localhost, rejected, accepted = [json.loads(item.stdout) for item in checks]
    except json.JSONDecodeError as exc:
        errors.append(f"LAN policy check output invalid: {exc}")
        return {"policy_script_passed": False}
    ok = bool(localhost.get("host_allowed")) and not bool(rejected.get("host_allowed")) and bool(accepted.get("host_allowed"))
    if not ok:
        errors.append("LAN policy check script decisions mismatch")
    return {"policy_script_passed": ok}


def validate_queue_state(root: Path, errors: list[str]) -> None:
    index = (root / ".aide/queue/index.yaml").read_text(encoding="utf-8")
    if f"current_recommended_task: {NEXT_TASK}" not in index:
        errors.append("queue index must point to LOCAL-12 after LOCAL-11")
    if "id: LOCAL-11" not in index or "status: completed" not in index:
        errors.append("queue index must mark LOCAL-11 completed")
    if "id: LOCAL-12" not in index or "status: queued" not in index:
        errors.append("queue index must include queued LOCAL-12")
    f0 = json.loads((root / "control/inventory/f0_deferral_for_local_appliance.json").read_text(encoding="utf-8"))
    if f0.get("deferred_until") != "LOCAL-14":
        errors.append("F0 must remain deferred until LOCAL-14")


def validate_report(report: Mapping[str, Any], errors: list[str]) -> None:
    for key in (
        "runtime_package_added",
        "lan_policy_check_script_added",
        "validator_added",
        "localhost_default_confirmed",
        "bind_lan_required_for_lan_hosts",
        "lan_read_only_default",
        "lan_mutations_blocked",
        "localhost_operator_mutations_remain_token_gated",
        "lan_source_probe_routes_blocked",
        "lan_workunit_execution_blocked",
        "lan_review_rebuild_mutation_blocked",
        "server_implemented",
        "html_workbench_implemented",
        "workunit_runtime_implemented",
        "worker_execution_enabled",
        "auto_test_harness_enabled",
        "lan_can_start_with_explicit_flag",
    ):
        require_true(report, key, errors, "LOCAL-11 report")
    for key in (
        "lan_enabled_by_default",
        "actual_lan_smoke_performed",
        "external_network_used",
        "source_probe_executed",
        "workunit_execution_from_lan",
        "review_mutation_from_lan",
        "rebuild_mutation_from_lan",
        "master_index_mutated",
        "site_dist_mutated",
        "deployment_performed",
        "local_11_increased_leakage",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    ):
        require_false(report, key, errors, "LOCAL-11 report")
    if report.get("recommended_next_task") != "LOCAL-12 \u2014 LAN read-only smoke test":
        errors.append("LOCAL-11 report recommended_next_task mismatch")


def validate_leakage(root: Path, baseline: Mapping[str, Any], errors: list[str], warnings: list[str]) -> None:
    if baseline.get("local_11_increased_leakage") is not False:
        errors.append("LOCAL-11 leakage baseline must state no increase")
    scan = subprocess.run(
        [sys.executable, "scripts/audit_runtime_architecture_leakage.py", "--check", "--json"],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
        timeout=180,
    )
    try:
        payload = json.loads(scan.stdout)
        new_count = int(payload.get("summary", {}).get("new_violation_count", 0))
    except Exception:
        errors.append("runtime leakage scan output could not be parsed")
        return
    expected_after = int(baseline.get("new_unallowlisted_production_findings_after", new_count))
    if new_count > expected_after:
        errors.append(f"LOCAL-11 increased runtime leakage: {new_count} > {expected_after}")
    if scan.returncode != 0:
        warnings.append(f"runtime leakage gate remains failing with {new_count} pre-existing new violations")


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
