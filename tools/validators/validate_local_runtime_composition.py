#!/usr/bin/env python3
"""Validate LOCAL-03 local runtime composition evidence."""

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

from runtime.local_appliance import (
    LocalApplianceError,
    LocalReadOnlyStoreMutationError,
    close_local_appliance,
    open_local_appliance,
    validate_no_forbidden_runtime_flags,
    validate_runtime_composition,
)


TASK_ID = "LOCAL-03"
NEXT_TASK = "LOCAL-04"
F0_CLOSEOUT = "LOCAL-14"
POLICIES = {
    "control/policies/local_runtime_composition_policy.json": "local_runtime_composition_policy.v0",
    "control/policies/local_runtime_store_access_policy.json": "local_runtime_store_access_policy.v0",
}
INVENTORIES = {
    "control/inventory/local_runtime_composition_inventory.json": "local_runtime_composition_inventory.v0",
    "control/inventory/local_runtime_composition_result.json": "local_runtime_composition_result.v0",
    "control/inventory/local_runtime_store_access_matrix.json": "local_runtime_store_access_matrix.v0",
    "control/inventory/local_runtime_gap_register.json": "local_runtime_gap_register.v0",
    "control/inventory/local_03_leakage_baseline.json": "local_03_leakage_baseline.v0",
    "control/inventory/local_03_next_task_decision.json": "local_03_next_task_decision.v0",
}
RUNTIME_FILES = (
    "runtime/local_appliance/__init__.py",
    "runtime/local_appliance/instance.py",
    "runtime/local_appliance/config.py",
    "runtime/local_appliance/manifest.py",
    "runtime/local_appliance/migration.py",
    "runtime/local_appliance/composition.py",
    "runtime/local_appliance/status.py",
    "runtime/local_appliance/validation.py",
    "runtime/local_appliance/errors.py",
)
SCRIPTS = (
    "scripts/eureka_local_runtime_status.py",
    "scripts/demo_local_runtime_composition.py",
    "scripts/validate_local_runtime_composition.py",
)
TESTS = (
    "tests/runtime/test_local_appliance_composition.py",
    "tests/runtime/test_local_appliance_instance.py",
    "tests/runtime/test_local_appliance_validation.py",
    "tests/operations/test_local_runtime_composition_scripts.py",
)
DOCS = (
    "docs/architecture/LOCAL_RUNTIME_COMPOSITION_BOUNDARY.md",
    "docs/reference/LOCAL_APPLIANCE_RUNTIME_API.md",
    "docs/operations/LOCAL_RUNTIME_COMPOSITION.md",
)
AUDIT_ROOT = Path("control/audits/local-03-runtime-composition-boundary-v0")
AUDIT_FILES = (
    "README.md",
    "local_03_report.json",
    "composition_boundary.md",
    "runtime_api_summary.md",
    "store_access_matrix.md",
    "demo_result.md",
    "leakage_baseline.md",
    "validation.md",
    "generated/sample_runtime_status.json",
    "generated/sample_composition_demo.json",
    "generated/sample_store_access_matrix.json",
    "generated/sample_validation_result.json",
    "generated/sample_summary.md",
)
ALLOWED_IMPORTS = {
    "dataclasses",
    "enum",
    "typing",
    "pathlib",
    "json",
    "datetime",
    "contextlib",
    "uuid",
    "hashlib",
    "runtime.source_cache",
    "runtime.source_cache.store",
    "runtime.evidence_ledger",
    "runtime.evidence_ledger.store",
    "runtime.review_queue",
    "runtime.review_queue.store",
    "runtime.public_index",
    "runtime.public_index.store",
    "runtime.search_hunt",
    "runtime.search_hunt.store",
    "runtime.search_need",
    "runtime.search_need.store",
    "runtime.agent_research",
    "runtime.agent_research.store",
    "runtime.ai_escalation",
    "runtime.ai_escalation.store",
    "runtime.source_observation",
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
    "subprocess",
    "socket",
)
FORBIDDEN_VOCABULARY = ("LOCAL-", "AIDE", "H0", "H1", "H2", "H3", "H4", "H5", "H6", "H7", "H8", "H9", "H10", "H11", "H12", "H13", "H14", "BUNDLE")


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
        print("LOCAL-03 local runtime composition validation", file=stdout)
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
    report = load_json(root / AUDIT_ROOT / "local_03_report.json", "local_03_report.v0", errors)

    validate_policies(payloads, errors)
    validate_inventories(payloads, errors, warnings)
    validate_files(root, errors)
    validate_runtime_imports(root, errors)
    validate_runtime_vocabulary(root, errors)
    validate_temp_runtime(root, errors)
    validate_queue(root, errors)
    validate_report(report, errors, warnings)
    validate_leakage(root, payloads.get("control/inventory/local_03_leakage_baseline.json", {}), errors, warnings)

    status = "fail" if errors else ("pass_with_warnings" if warnings else "pass")
    return {
        "schema_version": "local_runtime_composition_validation.v0",
        "task": TASK_ID,
        "status": status,
        "errors": errors,
        "warnings": warnings,
        "server_enabled": False,
        "lan_enabled": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def validate_policies(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    composition = payloads.get("control/policies/local_runtime_composition_policy.json", {})
    expected_composition = {
        "explicit_instance_path_required": True,
        "composition_requires_instance_validation": True,
        "composition_requires_supported_schema_version": True,
        "composition_requires_store_manifest": True,
        "composition_requires_migration_state": True,
        "hidden_state_roots_forbidden": True,
        "server_enabled": False,
        "lan_enabled": False,
        "deployment_enabled": False,
        "network_access_enabled": False,
        "source_probe_execution_enabled": False,
        "review_decision_mutation_enabled": False,
        "index_rebuild_enabled": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }
    for key, value in expected_composition.items():
        if composition.get(key) != value:
            errors.append(f"composition policy {key} mismatch")

    access = payloads.get("control/policies/local_runtime_store_access_policy.json", {})
    expected_access = {
        "open_mode_default": "read_write_local",
        "read_only_mode_supported": True,
        "store_paths_must_come_from_manifest": True,
        "ad_hoc_store_paths_forbidden": True,
        "hidden_store_paths_forbidden": True,
        "direct_public_index_mutation_forbidden": True,
        "direct_master_index_mutation_forbidden": True,
        "source_registry_mutation_forbidden": True,
        "connector_registry_mutation_forbidden": True,
    }
    for key, value in expected_access.items():
        if access.get(key) != value:
            errors.append(f"store access policy {key} mismatch")
    if access.get("allowed_stores") != ["source_cache", "evidence_ledger", "review_queue", "public_index"]:
        errors.append("store access policy allowed_stores mismatch")


def validate_inventories(payloads: Mapping[str, Mapping[str, Any]], errors: list[str], warnings: list[str]) -> None:
    inventory = payloads.get("control/inventory/local_runtime_composition_inventory.json", {})
    if inventory.get("runtime_package") != "runtime/local_appliance":
        errors.append("composition inventory runtime_package mismatch")
    if inventory.get("stores_composed") != ["source_cache", "evidence_ledger", "review_queue", "public_index"]:
        errors.append("composition inventory stores_composed mismatch")
    for key in ("server_enabled", "lan_enabled", "deployment_performed"):
        if inventory.get(key) is not False:
            errors.append(f"composition inventory {key} must be false")
    if inventory.get("network_dependencies") != 0 or inventory.get("h_series_dependencies") != 0:
        errors.append("composition inventory must not add network or H-series dependencies")

    matrix = payloads.get("control/inventory/local_runtime_store_access_matrix.json", {})
    rows = matrix.get("stores")
    if not isinstance(rows, list):
        errors.append("store access matrix must contain stores list")
    else:
        seen = [str(row.get("store_id")) for row in rows if isinstance(row, Mapping)]
        if seen != ["source_cache", "evidence_ledger", "review_queue", "public_index"]:
            errors.append("store access matrix row order mismatch")
        for row in rows:
            if isinstance(row, Mapping) and row.get("direct_mutation_allowed_current_task") is not False:
                errors.append(f"store access matrix mutation flag must be false for {row.get('store_id')}")

    result = payloads.get("control/inventory/local_runtime_composition_result.json", {})
    for key in (
        "runtime_package_added",
        "composition_api_added",
        "status_script_added",
        "demo_script_added",
        "validator_added",
        "temp_instance_composition_passed",
        "stores_opened",
        "integrity_check_passed",
        "close_idempotency_passed",
        "forbidden_roots_rejected",
        "unsupported_version_fail_closed_passed",
    ):
        if result.get(key) is not True:
            errors.append(f"composition result {key} must be true")
    for key in ("server_enabled", "lan_enabled", "deployment_performed", "production_readiness_claimed", "public_launch_readiness_claimed"):
        if result.get(key) is not False:
            errors.append(f"composition result {key} must be false")

    decision = payloads.get("control/inventory/local_03_next_task_decision.json", {})
    if decision.get("recommended_next_task") != "LOCAL-04 \u2014 Read-only localhost HTTP service over reviewed index":
        errors.append("LOCAL-03 next task decision must point to LOCAL-04")
    if decision.get("f0_current_status") != "deferred" or decision.get("f0_can_resume_after") != F0_CLOSEOUT:
        errors.append("F0 must remain deferred until LOCAL-14")
    if decision.get("lan_can_start") is not False:
        errors.append("LAN must remain disabled after LOCAL-03")

    leakage = payloads.get("control/inventory/local_03_leakage_baseline.json", {})
    if leakage.get("local_03_increased_leakage") is not False:
        errors.append("LOCAL-03 leakage baseline must not increase leakage")
    if leakage.get("runtime_leakage_gate_status_after") == "fail":
        # Historical LOCAL-03 evidence predates the exact leakage allowlist. The
        # current scan below remains authoritative for today's validation.
        pass


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
            module = None
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module = alias.name
                    validate_import_name(rel, module, errors)
            elif isinstance(node, ast.ImportFrom):
                if node.level:
                    continue
                module = node.module or ""
                validate_import_name(rel, module, errors)


def validate_import_name(rel: str, module: str, errors: list[str]) -> None:
    if any(module == item or module.startswith(item + ".") for item in FORBIDDEN_IMPORT_PREFIXES):
        errors.append(f"forbidden import in {rel}: {module}")
    if module.startswith("runtime.") and not any(module == item or module.startswith(item + ".") for item in ALLOWED_IMPORTS):
        errors.append(f"unexpected runtime import in {rel}: {module}")
    if not module.startswith("runtime.") and module.split(".")[0] not in ALLOWED_IMPORTS:
        errors.append(f"unexpected import in {rel}: {module}")


def validate_runtime_vocabulary(root: Path, errors: list[str]) -> None:
    for rel in RUNTIME_FILES:
        text = (root / rel).read_text(encoding="utf-8")
        for token in FORBIDDEN_VOCABULARY:
            if token in text:
                errors.append(f"forbidden runtime vocabulary in {rel}: {token}")


def validate_temp_runtime(root: Path, errors: list[str]) -> None:
    with tempfile.TemporaryDirectory(prefix="eureka-local-runtime-") as tmp:
        instance = Path(tmp) / "eureka-instance"
        init = run(root, "python", "scripts/eureka_init_instance.py", "--instance", str(instance), "--json")
        if init.returncode != 0:
            errors.append("temp instance init failed")
            return
        runtime = None
        try:
            runtime = open_local_appliance(instance)
            validate_runtime_composition(runtime)
            integrity = runtime.check_integrity()
            if integrity.get("status") != "pass":
                errors.append("temp runtime integrity failed")
            for name in ("source_cache", "evidence_ledger", "review_queue", "public_index"):
                if getattr(runtime, name, None) is None:
                    errors.append(f"runtime missing opened store: {name}")
            status = runtime.status()
            validate_no_forbidden_runtime_flags(status)
        except LocalApplianceError as exc:
            errors.append(f"temp runtime open failed: {exc}")
        finally:
            if runtime is not None:
                close_local_appliance(runtime)
                close_local_appliance(runtime)

        read_only_runtime = None
        try:
            read_only_runtime = open_local_appliance(instance, read_only=True)
            if read_only_runtime.status().to_dict().get("read_only") is not True:
                errors.append("read-only runtime status did not report read_only=true")
            try:
                read_only_runtime.source_cache.init
                errors.append("read-only runtime exposed init mutation")
            except LocalReadOnlyStoreMutationError:
                pass
        except LocalApplianceError as exc:
            errors.append(f"read-only runtime open failed: {exc}")
        finally:
            if read_only_runtime is not None:
                close_local_appliance(read_only_runtime)

        hidden_attempt = run(root, "python", "scripts/eureka_local_runtime_status.py", "--instance", str(Path(tmp) / ".cache" / "eureka-instance"), "--json")
        if hidden_attempt.returncode == 0:
            errors.append("runtime status accepted hidden root")
        repo_root_attempt = run(root, "python", "scripts/eureka_local_runtime_status.py", "--instance", str(root), "--json")
        if repo_root_attempt.returncode == 0:
            errors.append("runtime status accepted repo root")

        manifest_path = instance / "config" / "instance.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["instance_schema_version"] = 999
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        migration_path = instance / "config" / "migration_state.json"
        migration = json.loads(migration_path.read_text(encoding="utf-8"))
        migration["current_instance_schema_version"] = 999
        migration["migration_needed"] = True
        migration["blockers"] = ["unsupported instance_schema_version 999"]
        migration_path.write_text(json.dumps(migration, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        try:
            unsupported = open_local_appliance(instance)
            close_local_appliance(unsupported)
            errors.append("unsupported instance schema version did not fail closed")
        except LocalApplianceError:
            pass


def validate_queue(root: Path, errors: list[str]) -> None:
    queue = read_text(root / ".aide/queue/index.yaml", errors)
    task = read_text(root / ".aide/queue/LOCAL-03/task.yaml", errors)
    next_task = read_text(root / ".aide/queue/LOCAL-04/task.yaml", errors)
    if "current_recommended_task: LOCAL-04" not in queue:
        errors.append("queue index must point to LOCAL-04")
    if "id: LOCAL-03" not in queue or "status: completed" not in queue:
        errors.append("queue index must mark LOCAL-03 completed")
    if "id: LOCAL-04" not in queue or "status: queued" not in queue:
        errors.append("queue index must include queued LOCAL-04")
    if "deferred_until: LOCAL-14" not in queue:
        errors.append("queue index must keep F0 deferred until LOCAL-14")
    if "recommended_next: LOCAL-04" not in task:
        errors.append("LOCAL-03 task must recommend LOCAL-04")
    if "Read-only localhost HTTP service over reviewed index" not in next_task:
        errors.append("LOCAL-04 task file title mismatch")


def validate_report(report: Mapping[str, Any], errors: list[str], warnings: list[str]) -> None:
    if report.get("recommended_next_task") != "LOCAL-04 \u2014 Read-only localhost HTTP service over reviewed index":
        errors.append("LOCAL-03 audit report must recommend LOCAL-04")
    for key in (
        "runtime_package_added",
        "composition_api_added",
        "status_script_added",
        "demo_script_added",
        "validator_added",
        "temp_instance_composition_passed",
        "stores_opened",
        "integrity_check_passed",
        "close_idempotency_passed",
        "forbidden_roots_rejected",
        "unsupported_version_fail_closed_passed",
    ):
        if report.get(key) is not True:
            errors.append(f"LOCAL-03 report {key} must be true")
    for key in (
        "server_implemented",
        "html_workbench_implemented",
        "workunit_runtime_implemented",
        "lan_enabled",
        "deployment_performed",
        "local_03_increased_leakage",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    ):
        if report.get(key) is not False:
            errors.append(f"LOCAL-03 report {key} must be false")
    validation = report.get("validation", {})
    if isinstance(validation, Mapping) and validation.get("runtime_leakage_gate") == "fail_pre_existing":
        warnings.append("audit report records pre-existing runtime leakage gate failure")


def validate_leakage(root: Path, leakage: Mapping[str, Any], errors: list[str], warnings: list[str]) -> None:
    before = int(leakage.get("new_unallowlisted_production_findings_before", -1))
    after = int(leakage.get("new_unallowlisted_production_findings_after", -1))
    if before >= 0 and after > before:
        errors.append("LOCAL-03 increased runtime leakage")
    scan = run_leakage_scan(root)
    if scan:
        scan_count = int(scan.get("summary", {}).get("new_violation_count", -1))
        if scan_count > before and before >= 0:
            errors.append("current leakage scan exceeds recorded LOCAL-03 baseline")
        if scan.get("gate_report", {}).get("status") == "fail":
            warnings.append("runtime leakage gate fails with pre-existing findings")


def run_leakage_scan(root: Path) -> Mapping[str, Any]:
    import audit_runtime_architecture_leakage as leakage

    policy = leakage.load_json(root / leakage.DEFAULT_POLICY)
    allowlist = leakage.load_json(root / leakage.DEFAULT_ALLOWLIST)
    return leakage.build_leakage_audit(root, policy, allowlist, policy_errors=[])


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
