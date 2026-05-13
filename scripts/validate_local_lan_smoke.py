#!/usr/bin/env python3
"""Validate LOCAL-12 read-only LAN smoke evidence."""

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
SCRIPTS_ROOT = Path(__file__).resolve().parent
for item in (REPO_ROOT, SCRIPTS_ROOT):
    if str(item) not in sys.path:
        sys.path.insert(0, str(item))

from eureka_lan_read_only_probe import run_probe
from eureka_lan_smoke import start_server_process, stop_server_process


TASK_ID = "LOCAL-12"
NEXT_TASK = "LOCAL-13"
AUDIT_ROOT = Path("control/audits/local-12-lan-read-only-smoke-v0")
POLICIES = {
    "control/policies/local_lan_smoke_policy.json": "local_lan_smoke_policy.v0",
    "control/policies/local_lan_read_only_smoke_policy.json": "local_lan_read_only_smoke_policy.v0",
    "control/policies/local_lan_shutdown_policy.json": "local_lan_shutdown_policy.v0",
    "control/policies/local_lan_external_client_evidence_policy.json": "local_lan_external_client_evidence_policy.v0",
}
INVENTORIES = {
    "control/inventory/local_lan_smoke_inventory.json": "local_lan_smoke_inventory.v0",
    "control/inventory/local_lan_smoke_result.json": "local_lan_smoke_result.v0",
    "control/inventory/local_lan_read_only_route_result.json": "local_lan_read_only_route_result.v0",
    "control/inventory/local_lan_mutation_block_result.json": "local_lan_mutation_block_result.v0",
    "control/inventory/local_lan_external_client_evidence.json": "local_lan_external_client_evidence.v0",
    "control/inventory/local_lan_shutdown_result.json": "local_lan_shutdown_result.v0",
    "control/inventory/local_lan_gap_register.json": "local_lan_gap_register.v0",
    "control/inventory/local_12_leakage_baseline.json": "local_12_leakage_baseline.v0",
    "control/inventory/local_12_next_task_decision.json": "local_12_next_task_decision.v0",
}
SCRIPTS = (
    "scripts/eureka_lan_smoke.py",
    "scripts/eureka_lan_read_only_probe.py",
    "scripts/eureka_lan_shutdown_check.py",
    "scripts/validate_local_lan_smoke.py",
)
AUDIT_FILES = (
    "README.md",
    "local_12_report.json",
    "lan_smoke_summary.md",
    "read_only_route_result.md",
    "mutation_block_result.md",
    "external_client_evidence.md",
    "shutdown_result.md",
    "leakage_baseline.md",
    "validation.md",
    "generated/sample_lan_smoke_result.json",
    "generated/sample_read_only_route_result.json",
    "generated/sample_mutation_block_result.json",
    "generated/sample_external_client_checklist.md",
    "generated/sample_shutdown_result.json",
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
        print("LOCAL-12 LAN smoke validation", file=stdout)
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
    report = load_json(root / AUDIT_ROOT / "local_12_report.json", "local_12_report.v0", errors)
    validate_files(root, errors)
    validate_policies(payloads, errors)
    validate_inventories(payloads, errors)
    validate_script_imports(root, errors)
    validate_queue_state(root, errors)
    smoke = run_smoke_command(root, errors)
    probe = run_probe_against_temp_server(root, errors)
    validate_smoke_result(smoke, errors)
    validate_probe_result(probe, errors)
    validate_report(report, errors)
    validate_external_client_evidence(payloads.get("control/inventory/local_lan_external_client_evidence.json", {}), errors)
    validate_leakage(root, payloads.get("control/inventory/local_12_leakage_baseline.json", {}), errors, warnings)
    status = "fail" if errors else ("pass_with_warnings" if warnings else "pass")
    return {
        "schema_version": "local_lan_smoke_validation.v0",
        "task": TASK_ID,
        "status": status,
        "errors": errors,
        "warnings": warnings,
        "lan_smoke_script_added": (root / "scripts/eureka_lan_smoke.py").is_file(),
        "lan_read_only_probe_added": (root / "scripts/eureka_lan_read_only_probe.py").is_file(),
        "lan_shutdown_check_added": (root / "scripts/eureka_lan_shutdown_check.py").is_file(),
        "validator_added": True,
        "bind_lan_used": smoke.get("bind_lan_used") is True,
        "read_only_mode": smoke.get("read_only_mode") is True,
        "same_machine_lan_bind_smoke_passed": smoke.get("same_machine_lan_bind_smoke_passed") is True,
        "external_client_smoke_performed": False,
        "external_client_smoke_status": "not_performed",
        "read_only_routes_passed": smoke.get("read_only_routes_passed") is True and probe.get("read_only_routes_passed") is True,
        "mutation_routes_blocked": smoke.get("mutation_routes_blocked") is True and probe.get("mutation_routes_blocked") is True,
        "operator_mutations_localhost_only": smoke.get("operator_mutations_localhost_only") is True,
        "source_probe_executed": False,
        "workunit_execution_from_lan": False,
        "review_mutation_from_lan": False,
        "rebuild_mutation_from_lan": False,
        "external_internet_used": False,
        "master_index_mutated": False,
        "site_dist_mutated": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def validate_files(root: Path, errors: list[str]) -> None:
    for rel in SCRIPTS:
        if not (root / rel).is_file():
            errors.append(f"required script is missing: {rel}")
    for rel in AUDIT_FILES:
        if not (root / AUDIT_ROOT / rel).is_file():
            errors.append(f"audit file is missing: {AUDIT_ROOT / rel}")


def validate_policies(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    smoke = payloads.get("control/policies/local_lan_smoke_policy.json", {})
    for key in (
        "bind_lan_required",
        "read_only_required",
        "external_client_smoke_preferred",
        "same_machine_lan_bind_smoke_allowed",
        "false_cross_device_claim_forbidden",
        "operator_firewall_warning_required",
        "shutdown_check_required",
        "no_deployment",
        "no_public_hosting_claim",
        "no_production_readiness_claim",
        "no_public_launch_readiness_claim",
    ):
        require_true(smoke, key, errors, "LAN smoke policy")
    shutdown = payloads.get("control/policies/local_lan_shutdown_policy.json", {})
    for key in (
        "graceful_shutdown_required",
        "instance_left_valid_after_shutdown",
        "working_tree_clean_after_shutdown",
        "server_process_cleanup_required",
        "port_reuse_or_cleanup_checked",
        "logs_may_be_written_only_under_instance",
        "committed_local_state_forbidden",
    ):
        require_true(shutdown, key, errors, "LAN shutdown policy")
    evidence = payloads.get("control/policies/local_lan_external_client_evidence_policy.json", {})
    require_true(evidence, "external_client_optional_for_pass_with_warnings", errors, "external client evidence policy")
    require_true(evidence, "external_client_required_for_full_lan_operational_claim", errors, "external client evidence policy")


def validate_inventories(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    result = payloads.get("control/inventory/local_lan_smoke_result.json", {})
    for key in (
        "bind_lan_used",
        "read_only_mode",
        "same_machine_lan_bind_smoke_passed",
        "read_only_routes_passed",
        "mutation_routes_blocked",
        "operator_mutations_localhost_only",
    ):
        require_true(result, key, errors, "LAN smoke result")
    for key in (
        "external_client_smoke_performed",
        "source_probe_executed",
        "workunit_execution_from_lan",
        "review_mutation_from_lan",
        "rebuild_mutation_from_lan",
        "site_dist_mutated",
        "master_index_mutated",
        "deployment_performed",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    ):
        require_false(result, key, errors, "LAN smoke result")
    if result.get("external_client_smoke_status") != "not_performed":
        errors.append("LAN smoke result must record external client smoke as not_performed")
    next_decision = payloads.get("control/inventory/local_12_next_task_decision.json", {})
    if next_decision.get("recommended_next_task") != "LOCAL-13 \u2014 Clean-machine bootstrap proof":
        errors.append("LOCAL-12 next decision must recommend LOCAL-13")
    require_true(next_decision, "lan_read_only_smoke_passed", errors, "LOCAL-12 next decision")
    if next_decision.get("f0_can_resume_after") != "LOCAL-14":
        errors.append("F0 must remain deferred until LOCAL-14")


def validate_script_imports(root: Path, errors: list[str]) -> None:
    for rel in SCRIPTS:
        path = root / rel
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            modules: list[str] = []
            if isinstance(node, ast.Import):
                modules = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and not node.level:
                modules = [node.module or ""]
            for module in modules:
                if any(module == item or module.startswith(item + ".") for item in FORBIDDEN_IMPORT_PREFIXES):
                    errors.append(f"forbidden import in {rel}: {module}")


def validate_queue_state(root: Path, errors: list[str]) -> None:
    index = (root / ".aide/queue/index.yaml").read_text(encoding="utf-8")
    if f"current_recommended_task: {NEXT_TASK}" not in index:
        errors.append("queue index must point to LOCAL-13 after LOCAL-12")
    if "id: LOCAL-12" not in index or "status: completed" not in index:
        errors.append("queue index must mark LOCAL-12 completed")
    if "id: LOCAL-13" not in index or "status: queued" not in index:
        errors.append("queue index must include queued LOCAL-13")


def run_smoke_command(root: Path, errors: list[str]) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="eureka-lan-smoke-validator-") as temp:
        instance = Path(temp) / "eureka-instance"
        completed = subprocess.run(
            [
                sys.executable,
                "scripts/eureka_lan_smoke.py",
                "--instance",
                str(instance),
                "--host",
                "0.0.0.0",
                "--port",
                "0",
                "--bind-lan",
                "--read-only",
                "--json",
            ],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
            timeout=180,
        )
    if completed.returncode != 0:
        errors.append(f"LAN smoke script failed: {completed.stderr or completed.stdout}")
        return {}
    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        errors.append(f"LAN smoke script emitted invalid JSON: {exc}")
        return {}


def run_probe_against_temp_server(root: Path, errors: list[str]) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="eureka-lan-probe-validator-") as temp:
        instance = Path(temp) / "eureka-instance"
        init = subprocess.run([sys.executable, "scripts/eureka_init_instance.py", "--instance", str(instance), "--json"], cwd=root, text=True, capture_output=True, check=False)
        if init.returncode != 0:
            errors.append(f"instance init failed for probe: {init.stderr or init.stdout}")
            return {}
        process, startup = start_server_process(instance, "0.0.0.0", 0, True)
        try:
            return run_probe(f"http://127.0.0.1:{startup['port']}")
        finally:
            stop_server_process(process)


def validate_smoke_result(smoke: Mapping[str, Any], errors: list[str]) -> None:
    for key in (
        "bind_lan_used",
        "read_only_mode",
        "same_machine_lan_bind_smoke_passed",
        "read_only_routes_passed",
        "mutation_routes_blocked",
        "operator_mutations_localhost_only",
    ):
        require_true(smoke, key, errors, "LAN smoke script result")
    for key in (
        "external_client_smoke_performed",
        "external_internet_used",
        "source_probe_executed",
        "workunit_execution_from_lan",
        "review_mutation_from_lan",
        "rebuild_mutation_from_lan",
        "master_index_mutated",
        "site_dist_mutated",
        "deployment_performed",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    ):
        require_false(smoke, key, errors, "LAN smoke script result")


def validate_probe_result(probe: Mapping[str, Any], errors: list[str]) -> None:
    require_true(probe, "read_only_routes_passed", errors, "LAN read-only probe")
    require_true(probe, "mutation_routes_blocked", errors, "LAN read-only probe")
    require_true(probe, "operator_mutations_localhost_only", errors, "LAN read-only probe")


def validate_report(report: Mapping[str, Any], errors: list[str]) -> None:
    for key in (
        "lan_smoke_script_added",
        "lan_read_only_probe_added",
        "lan_shutdown_check_added",
        "validator_added",
        "bind_lan_used",
        "read_only_mode",
        "same_machine_lan_bind_smoke_passed",
        "read_only_routes_passed",
        "mutation_routes_blocked",
        "operator_mutations_localhost_only",
        "server_implemented",
        "html_workbench_implemented",
        "workunit_runtime_implemented",
        "worker_execution_enabled",
        "auto_test_harness_enabled",
        "lan_can_start_with_explicit_flag",
    ):
        require_true(report, key, errors, "LOCAL-12 report")
    for key in (
        "external_client_smoke_performed",
        "lan_enabled_by_default",
        "source_probe_executed",
        "workunit_execution_from_lan",
        "review_mutation_from_lan",
        "rebuild_mutation_from_lan",
        "external_internet_used",
        "master_index_mutated",
        "site_dist_mutated",
        "deployment_performed",
        "local_12_increased_leakage",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    ):
        require_false(report, key, errors, "LOCAL-12 report")


def validate_external_client_evidence(payload: Mapping[str, Any], errors: list[str]) -> None:
    if payload.get("external_client_smoke_performed") is not False:
        errors.append("automated LOCAL-12 evidence must not claim external client smoke")
    if payload.get("status") != "not_performed":
        errors.append("external client evidence status must be not_performed")
    if not payload.get("reason"):
        errors.append("external client evidence must include a reason")


def validate_leakage(root: Path, baseline: Mapping[str, Any], errors: list[str], warnings: list[str]) -> None:
    if baseline.get("local_12_increased_leakage") is not False:
        errors.append("LOCAL-12 leakage baseline must state no increase")
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
        errors.append(f"LOCAL-12 increased runtime leakage: {new_count} > {expected_after}")
    if scan.returncode != 0:
        warnings.append(f"runtime leakage gate remains failing with {new_count} pre-existing new violations")


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
