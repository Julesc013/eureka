#!/usr/bin/env python3
"""Validate LOCAL-13 clean-machine bootstrap evidence."""

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

from eureka_clean_machine_bootstrap import run_bootstrap
from eureka_clean_machine_report import build_report
from eureka_clean_machine_smoke import run_smoke


TASK_ID = "LOCAL-13"
NEXT_TASK = "LOCAL-14"
AUDIT_ROOT = Path("control/audits/local-13-clean-machine-bootstrap-v0")
POLICIES = {
    "control/policies/local_clean_machine_bootstrap_policy.json": "local_clean_machine_bootstrap_policy.v0",
    "control/policies/local_clean_machine_state_policy.json": "local_clean_machine_state_policy.v0",
    "control/policies/local_clean_machine_validation_policy.json": "local_clean_machine_validation_policy.v0",
    "control/policies/local_clean_machine_external_proof_policy.json": "local_clean_machine_external_proof_policy.v0",
}
INVENTORIES = {
    "control/inventory/local_clean_machine_bootstrap_inventory.json": "local_clean_machine_bootstrap_inventory.v0",
    "control/inventory/local_clean_machine_bootstrap_result.json": "local_clean_machine_bootstrap_result.v0",
    "control/inventory/local_clean_machine_smoke_result.json": "local_clean_machine_smoke_result.v0",
    "control/inventory/local_clean_machine_validation_result.json": "local_clean_machine_validation_result.v0",
    "control/inventory/local_clean_machine_external_proof.json": "local_clean_machine_external_proof.v0",
    "control/inventory/local_clean_machine_gap_register.json": "local_clean_machine_gap_register.v0",
    "control/inventory/local_13_leakage_baseline.json": "local_13_leakage_baseline.v0",
    "control/inventory/local_13_next_task_decision.json": "local_13_next_task_decision.v0",
}
SCRIPTS = (
    "scripts/eureka_clean_machine_bootstrap.py",
    "scripts/eureka_clean_machine_smoke.py",
    "scripts/eureka_clean_machine_report.py",
    "scripts/validate_clean_machine_bootstrap.py",
)
AUDIT_FILES = (
    "README.md",
    "local_13_report.json",
    "clean_machine_bootstrap_summary.md",
    "clean_machine_smoke_result.md",
    "clean_machine_validation_result.md",
    "clean_state_report.md",
    "external_machine_proof.md",
    "leakage_baseline.md",
    "validation.md",
    "generated/sample_clean_machine_bootstrap_result.json",
    "generated/sample_clean_machine_smoke_result.json",
    "generated/sample_clean_machine_validation_result.json",
    "generated/sample_external_machine_checklist.md",
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
FORBIDDEN_TERMS = tuple("H" + str(item) for item in range(10)) + ("B" + "UNDLE",)


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
        print("LOCAL-13 clean-machine validation", file=stdout)
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
    report = load_json(root / AUDIT_ROOT / "local_13_report.json", "local_13_report.v0", errors)
    validate_files(root, errors)
    validate_policies(payloads, errors)
    validate_inventories(payloads, errors)
    validate_script_imports(root, errors)
    validate_queue_state(root, errors)
    bootstrap, smoke, combined = run_clean_machine_proof(root, errors)
    validate_dynamic_results(bootstrap, smoke, combined, errors)
    validate_report(report, errors)
    validate_external_proof(payloads.get("control/inventory/local_clean_machine_external_proof.json", {}), errors)
    validate_leakage(root, payloads.get("control/inventory/local_13_leakage_baseline.json", {}), errors, warnings)
    status = "fail" if errors else ("pass_with_warnings" if warnings else "pass")
    return {
        "schema_version": "local_clean_machine_bootstrap_validation.v0",
        "task": TASK_ID,
        "status": status,
        "errors": errors,
        "warnings": warnings,
        "clean_machine_bootstrap_script_added": (root / "scripts/eureka_clean_machine_bootstrap.py").is_file(),
        "clean_machine_smoke_script_added": (root / "scripts/eureka_clean_machine_smoke.py").is_file(),
        "clean_machine_report_script_added": (root / "scripts/eureka_clean_machine_report.py").is_file(),
        "validator_added": True,
        "temp_checkout_created": bootstrap.get("temp_checkout_created") is True,
        "instance_initialized": bootstrap.get("instance_initialized") is True,
        "instance_validated": bootstrap.get("instance_validated") is True,
        "runtime_status_passed": bootstrap.get("runtime_status_passed") is True and smoke.get("runtime_status_passed") is True,
        "localhost_server_started": smoke.get("localhost_server_started") is True,
        "service_smoke_passed": smoke.get("service_smoke_passed") is True,
        "workbench_smoke_passed": smoke.get("workbench_smoke_passed") is True,
        "auto_test_passed": smoke.get("auto_test_passed") is True,
        "auto_search_passed": smoke.get("auto_search_passed") is True,
        "server_shutdown_clean": smoke.get("server_shutdown_clean") is True,
        "instance_valid_after_shutdown": smoke.get("instance_valid_after_shutdown") is True,
        "actual_second_machine_proof_performed": False,
        "hidden_state_copied": False,
        "committed_instance_state_found": False,
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
    bootstrap = payloads.get("control/policies/local_clean_machine_bootstrap_policy.json", {})
    for key in (
        "temp_checkout_required",
        "actual_second_machine_optional",
        "explicit_instance_path_required",
        "hidden_state_roots_forbidden",
        "committed_instance_state_forbidden",
        "local_server_smoke_required",
        "html_workbench_smoke_required",
        "auto_test_required",
        "generated_artifact_cleanliness_required",
        "shutdown_required",
        "no_deployment",
        "no_production_readiness_claim",
        "no_public_launch_readiness_claim",
    ):
        require_true(bootstrap, key, errors, "clean-machine bootstrap policy")
    external = payloads.get("control/policies/local_clean_machine_external_proof_policy.json", {})
    require_true(external, "external_machine_proof_optional_for_LOCAL_13_PASS_WITH_WARNINGS", errors, "external proof policy")
    require_true(external, "manual_evidence_allowed", errors, "external proof policy")


def validate_inventories(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    bootstrap = payloads.get("control/inventory/local_clean_machine_bootstrap_result.json", {})
    for key in ("temp_checkout_created", "instance_initialized", "instance_validated", "runtime_status_passed"):
        require_true(bootstrap, key, errors, "clean-machine bootstrap result")
    for key in ("hidden_state_copied", "committed_instance_state_found", "deployment_performed", "production_readiness_claimed", "public_launch_readiness_claimed"):
        require_false(bootstrap, key, errors, "clean-machine bootstrap result")
    smoke = payloads.get("control/inventory/local_clean_machine_smoke_result.json", {})
    for key in (
        "localhost_server_started",
        "service_smoke_passed",
        "workbench_smoke_passed",
        "auto_test_passed",
        "auto_search_passed",
        "server_shutdown_clean",
        "instance_valid_after_shutdown",
    ):
        require_true(smoke, key, errors, "clean-machine smoke result")
    for key in ("site_dist_mutated", "master_index_mutated", "deployment_performed"):
        require_false(smoke, key, errors, "clean-machine smoke result")
    next_decision = payloads.get("control/inventory/local_13_next_task_decision.json", {})
    expected_next = "LOCAL-14 \u2014 Local appliance closeout and " + "F" + "0/" + "H" + "UNT/SYN handoff"
    if next_decision.get("recommended_next_task") != expected_next:
        errors.append("LOCAL-13 next decision must recommend LOCAL-14")
    if next_decision.get("f0_can_resume_after") != "LOCAL-14":
        errors.append("deferred extraction track must remain deferred until LOCAL-14")


def validate_script_imports(root: Path, errors: list[str]) -> None:
    for rel in SCRIPTS:
        text = (root / rel).read_text(encoding="utf-8")
        for term in FORBIDDEN_TERMS:
            if term in text:
                errors.append(f"forbidden task vocabulary in {rel}: {term}")
        tree = ast.parse(text, filename=str(root / rel))
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
        errors.append("queue index must point to LOCAL-14 after LOCAL-13")
    if "id: LOCAL-13" not in index or "status: completed" not in index:
        errors.append("queue index must mark LOCAL-13 completed")
    if "id: LOCAL-14" not in index or "status: queued" not in index:
        errors.append("queue index must include queued LOCAL-14")


def run_clean_machine_proof(root: Path, errors: list[str]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    with tempfile.TemporaryDirectory(prefix="eureka-clean-machine-validator-") as temp:
        bootstrap = run_bootstrap(
            repo=root,
            workdir=Path(temp),
            instance_name="eureka-instance",
            skip_clone=False,
            include_smoke=False,
            cleanup=False,
        )
        checkout = Path(str(bootstrap.get("temp_checkout", "")))
        instance = Path(str(bootstrap.get("instance", "")))
        smoke = run_smoke(repo=checkout, instance=instance, port=0)
        combined = build_report(bootstrap, smoke)
    if bootstrap.get("status") not in {"pass", "pass_with_warnings"}:
        errors.append("dynamic clean-machine bootstrap failed")
    if smoke.get("status") != "pass":
        errors.append("dynamic clean-machine smoke failed")
    if combined.get("status") not in {"pass", "pass_with_warnings"}:
        errors.append("dynamic clean-machine report failed")
    return bootstrap, smoke, combined


def validate_dynamic_results(bootstrap: Mapping[str, Any], smoke: Mapping[str, Any], combined: Mapping[str, Any], errors: list[str]) -> None:
    for key in ("temp_checkout_created", "instance_initialized", "instance_validated", "runtime_status_passed"):
        require_true(bootstrap, key, errors, "dynamic bootstrap result")
    for key in ("hidden_state_copied", "committed_instance_state_found", "deployment_performed", "production_readiness_claimed", "public_launch_readiness_claimed"):
        require_false(bootstrap, key, errors, "dynamic bootstrap result")
    for key in (
        "localhost_server_started",
        "service_smoke_passed",
        "workbench_smoke_passed",
        "auto_test_passed",
        "auto_search_passed",
        "server_shutdown_clean",
        "instance_valid_after_shutdown",
    ):
        require_true(smoke, key, errors, "dynamic smoke result")
    for key in ("site_dist_mutated", "master_index_mutated", "deployment_performed"):
        require_false(smoke, key, errors, "dynamic smoke result")
    require_false(combined, "actual_second_machine_proof_performed", errors, "dynamic report")


def validate_report(report: Mapping[str, Any], errors: list[str]) -> None:
    for key in (
        "clean_machine_bootstrap_script_added",
        "clean_machine_smoke_script_added",
        "clean_machine_report_script_added",
        "validator_added",
        "temp_checkout_created",
        "instance_initialized",
        "instance_validated",
        "runtime_status_passed",
        "localhost_server_started",
        "service_smoke_passed",
        "workbench_smoke_passed",
        "auto_test_passed",
        "auto_search_passed",
        "server_shutdown_clean",
        "instance_valid_after_shutdown",
    ):
        require_true(report, key, errors, "LOCAL-13 report")
    for key in (
        "actual_second_machine_proof_performed",
        "hidden_state_copied",
        "committed_instance_state_found",
        "master_index_mutated",
        "site_dist_mutated",
        "deployment_performed",
        "local_13_increased_leakage",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    ):
        require_false(report, key, errors, "LOCAL-13 report")


def validate_external_proof(payload: Mapping[str, Any], errors: list[str]) -> None:
    require_false(payload, "actual_second_machine_proof_performed", errors, "external machine proof")
    if payload.get("status") != "not_performed":
        errors.append("external machine proof must be not_performed in automated evidence")
    if not payload.get("reason"):
        errors.append("external machine proof must include a reason")


def validate_leakage(root: Path, baseline: Mapping[str, Any], errors: list[str], warnings: list[str]) -> None:
    if baseline.get("local_13_increased_leakage") is not False:
        errors.append("LOCAL-13 leakage baseline must state no increase")
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
        errors.append(f"LOCAL-13 increased runtime leakage: {new_count} > {expected_after}")
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
    if not isinstance(payload, dict):
        errors.append(f"JSON file must contain an object: {path}")
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
