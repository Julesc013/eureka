#!/usr/bin/env python3
"""Validate LOCAL-02 local instance schema and migration guard evidence."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
TASK_ID = "LOCAL-02"
NEXT_TASK = "LOCAL-03"
F0_CLOSEOUT = "LOCAL-14"

POLICIES = {
    "control/policies/local_instance_schema_policy.json": "local_instance_schema_policy.v0",
    "control/policies/local_instance_migration_policy.json": "local_instance_migration_policy.v0",
}
INVENTORIES = {
    "control/inventory/local_instance_schema_version.json": "local_instance_schema_version.v0",
    "control/inventory/local_instance_config_schema.json": "local_instance_config_schema.v0",
    "control/inventory/local_instance_store_manifest_schema.json": "local_instance_store_manifest_schema.v0",
    "control/inventory/local_instance_migration_state_schema.json": "local_instance_migration_state_schema.v0",
    "control/inventory/local_instance_migration_guard_result.json": "local_instance_migration_guard_result.v0",
    "control/inventory/local_instance_migration_gap_register.json": "local_instance_migration_gap_register.v0",
    "control/inventory/local_02_leakage_baseline.json": "local_02_leakage_baseline.v0",
    "control/inventory/local_02_next_task_decision.json": "local_02_next_task_decision.v0",
}
DOCS = (
    "docs/reference/LOCAL_INSTANCE_CONFIG_SCHEMA.md",
    "docs/reference/LOCAL_INSTANCE_MIGRATION_GUARD.md",
    "docs/operations/LOCAL_INSTANCE_MIGRATION_POLICY.md",
    "docs/architecture/LOCAL_INSTANCE_MODEL.md",
    "docs/reference/LOCAL_INSTANCE_LAYOUT.md",
    "docs/operations/LOCAL_INSTANCE_BOOTSTRAP.md",
)
SCRIPTS = (
    "scripts/eureka_init_instance.py",
    "scripts/eureka_validate_instance.py",
    "scripts/eureka_instance_status.py",
    "scripts/eureka_instance_migration_status.py",
    "scripts/validate_local_instance_migration_guard.py",
)
TESTS = (
    "tests/operations/test_local_instance_migration_guard.py",
    "tests/operations/test_local_instance_schema_version.py",
)
AUDIT_ROOT = Path("control/audits/local-02-instance-configuration-migration-guard-v0")
AUDIT_FILES = (
    "README.md",
    "local_02_report.json",
    "instance_config_schema.md",
    "store_manifest_schema.md",
    "migration_state_schema.md",
    "migration_guard_result.md",
    "leakage_baseline.md",
    "validation.md",
    "generated/sample_instance_config.json",
    "generated/sample_store_manifest.json",
    "generated/sample_migration_state.json",
    "generated/sample_migration_status.json",
    "generated/sample_validation_result.json",
    "generated/sample_summary.md",
)
FORBIDDEN_CHANGED_ROOTS = (
    "runtime/",
    "contracts/",
    "surfaces/",
    "site/",
    "native/",
    "crates/",
    "examples/",
    "control/prototypes/",
    "eureka-instance/",
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    result = validate(Path(args.repo_root).resolve())
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print("LOCAL-02 local instance migration guard validation", file=stdout)
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
    report = load_json(root / AUDIT_ROOT / "local_02_report.json", "local_02_report.v0", errors)

    validate_policies(payloads, errors)
    validate_schema_inventories(payloads, errors)
    validate_next_task(payloads.get("control/inventory/local_02_next_task_decision.json", {}), errors)
    validate_leakage(payloads.get("control/inventory/local_02_leakage_baseline.json", {}), errors, warnings)
    validate_docs_scripts_tests(root, errors)
    validate_audit_pack(root, errors)
    validate_queue_and_context(root, errors)
    validate_scope(root, errors)
    validate_no_committed_instance(root, errors)
    validate_temp_instance_commands(root, errors, warnings)
    validate_report(report, errors)

    status = "fail" if errors else ("pass_with_warnings" if warnings else "pass")
    return {
        "schema_version": "local_instance_migration_guard_validation.v0",
        "task": TASK_ID,
        "status": status,
        "errors": errors,
        "warnings": warnings,
        "next_task": NEXT_TASK,
        "server_enabled": False,
        "lan_enabled": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def validate_policies(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    schema = payloads.get("control/policies/local_instance_schema_policy.json", {})
    migration = payloads.get("control/policies/local_instance_migration_policy.json", {})
    expected_schema = {
        "current_instance_schema_version": 1,
        "minimum_supported_instance_schema_version": 1,
        "unsupported_version_behavior": "fail_closed",
        "silent_upgrade_allowed": False,
        "destructive_migration_allowed": False,
        "backup_before_migration_required": True,
        "migration_history_required": True,
        "store_manifest_required": True,
        "migration_state_required": True,
        "network_access_enabled": False,
        "server_enabled": False,
        "lan_enabled": False,
    }
    for key, value in expected_schema.items():
        if schema.get(key) != value:
            errors.append(f"schema policy {key} mismatch")
    expected_migration = {
        "migration_default_mode": "check_only",
        "apply_requires_explicit_flag": True,
        "destructive_migrations_enabled": False,
        "rollback_metadata_required": True,
        "backup_metadata_required": True,
        "migration_log_required": True,
        "unknown_store_behavior": "fail_closed",
        "missing_store_behavior": "warn_or_block_by_requiredness",
        "committed_instance_state_forbidden": True,
    }
    for key, value in expected_migration.items():
        if migration.get(key) != value:
            errors.append(f"migration policy {key} mismatch")


def validate_schema_inventories(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    version = payloads.get("control/inventory/local_instance_schema_version.json", {})
    if version.get("current_instance_schema_version") != 1 or version.get("minimum_supported_instance_schema_version") != 1:
        errors.append("schema version inventory must define version 1")
    if version.get("unsupported_version_behavior") != "fail_closed":
        errors.append("schema version inventory must fail closed")
    config = payloads.get("control/inventory/local_instance_config_schema.json", {})
    for field in ("schema_version", "instance_id", "instance_schema_version", "stores", "policies", "warnings", "limitations"):
        if field not in config.get("fields", []):
            errors.append(f"config schema missing field: {field}")
    for key in ("server_enabled", "lan_enabled", "production_readiness_claimed", "public_launch_readiness_claimed"):
        if config.get("invariants", {}).get(key) is not False:
            errors.append(f"config invariant must set {key}=false")
    store = payloads.get("control/inventory/local_instance_store_manifest_schema.json", {})
    for name in ("source_cache", "evidence_ledger", "review_queue", "public_index"):
        if name not in store.get("required_store_entries", []):
            errors.append(f"store manifest schema missing {name}")
    migration = payloads.get("control/inventory/local_instance_migration_state_schema.json", {})
    for field in ("migration_needed", "migration_allowed", "destructive_migration_required", "backup_required", "rollback_available"):
        if field not in migration.get("fields", []):
            errors.append(f"migration schema missing field: {field}")
    if migration.get("invariants", {}).get("destructive_migration_required") is not False:
        errors.append("migration schema must forbid destructive migration")


def validate_next_task(decision: Mapping[str, Any], errors: list[str]) -> None:
    if decision.get("recommended_next_task") != "LOCAL-03 \u2014 Local runtime composition boundary":
        errors.append("next task decision must point to LOCAL-03")
    if decision.get("f0_current_status") != "deferred" or decision.get("f0_can_resume_after") != F0_CLOSEOUT:
        errors.append("F0 must remain deferred until LOCAL-14")
    if decision.get("server_can_start") is not False or decision.get("lan_can_start") is not False:
        errors.append("server and LAN cannot start after LOCAL-02")


def validate_leakage(leakage: Mapping[str, Any], errors: list[str], warnings: list[str]) -> None:
    if leakage.get("local_02_increased_leakage") is not False:
        errors.append("LOCAL-02 must not increase runtime leakage")
    before = int(leakage.get("new_unallowlisted_production_findings_before", -1))
    after = int(leakage.get("new_unallowlisted_production_findings_after", -1))
    if after > before:
        errors.append("runtime leakage count increased")
    if leakage.get("runtime_leakage_gate_status_after") == "fail":
        warnings.append("pre-existing runtime leakage gate still fails")


def validate_docs_scripts_tests(root: Path, errors: list[str]) -> None:
    for rel in (*DOCS, *SCRIPTS, *TESTS):
        path = root / rel
        if not path.is_file():
            errors.append(f"missing file: {rel}")
        elif path.stat().st_size == 0:
            errors.append(f"empty file: {rel}")


def validate_audit_pack(root: Path, errors: list[str]) -> None:
    for rel in AUDIT_FILES:
        path = root / AUDIT_ROOT / rel
        if not path.is_file():
            errors.append(f"missing audit file: {(AUDIT_ROOT / rel).as_posix()}")
        elif path.stat().st_size == 0:
            errors.append(f"empty audit file: {(AUDIT_ROOT / rel).as_posix()}")


def validate_queue_and_context(root: Path, errors: list[str]) -> None:
    queue = read_text(root / ".aide/queue/index.yaml", errors)
    task_packet = read_text(root / ".aide/context/latest-task-packet.md", errors)
    if "current_recommended_task: LOCAL-03" not in queue:
        errors.append("queue index must point to LOCAL-03")
    if "id: LOCAL-02" not in queue or "status: completed" not in queue:
        errors.append("queue index must mark LOCAL-02 completed")
    if "id: LOCAL-03" not in queue:
        errors.append("queue index must include LOCAL-03")
    if "deferred_until: LOCAL-14" not in queue:
        errors.append("queue index must keep F0 deferred until LOCAL-14")
    if "LOCAL-03" not in task_packet:
        errors.append("latest task packet must point to LOCAL-03")


def validate_scope(root: Path, errors: list[str]) -> None:
    status = git(root, "status", "--porcelain=v1")
    for path in parse_status_paths(status.splitlines() if status else []):
        if any(path == prefix.rstrip("/") or path.startswith(prefix) for prefix in FORBIDDEN_CHANGED_ROOTS):
            errors.append(f"forbidden path changed: {path}")


def validate_no_committed_instance(root: Path, errors: list[str]) -> None:
    tracked = git(root, "ls-files", "--", "eureka-instance")
    if tracked:
        errors.append("eureka-instance state is tracked by git")
    ignored = git(root, "check-ignore", "eureka-instance/config/instance.json")
    if not ignored:
        errors.append("eureka-instance local state is not ignored")


def validate_temp_instance_commands(root: Path, errors: list[str], warnings: list[str]) -> None:
    with tempfile.TemporaryDirectory(prefix="eureka-local-02-") as tmp:
        instance = Path(tmp) / "eureka-instance"
        init = run(root, "python", "scripts/eureka_init_instance.py", "--instance", str(instance), "--json")
        if init.returncode != 0:
            errors.append("temp instance init command failed")
            return
        init_payload = parse_json_output(init.stdout, errors, "init")
        validate_cmd_false_boundaries(init_payload, "init", errors)
        for rel in ("config/instance.json", "config/store_manifest.json", "config/migration_state.json"):
            if not (instance / rel).is_file():
                errors.append(f"temp instance missing {rel}")
        manifest = load_json(instance / "config" / "instance.json", "temp manifest", errors)
        first_id = manifest.get("instance_id")
        second = run(root, "python", "scripts/eureka_init_instance.py", "--instance", str(instance), "--json")
        if second.returncode != 0:
            errors.append("temp instance idempotent init failed")
        second_manifest = load_json(instance / "config" / "instance.json", "temp manifest rerun", errors)
        if first_id != second_manifest.get("instance_id"):
            errors.append("idempotent init did not preserve instance_id")
        validate = run(root, "python", "scripts/eureka_validate_instance.py", "--instance", str(instance), "--json")
        if validate.returncode != 0:
            errors.append("temp instance validation command failed")
        validate_payload = parse_json_output(validate.stdout, errors, "validate")
        validate_cmd_false_boundaries(validate_payload, "validate", errors)
        migration_status = run(root, "python", "scripts/eureka_instance_migration_status.py", "--instance", str(instance), "--json")
        if migration_status.returncode != 0:
            errors.append("temp migration status command failed")
        migration_payload = parse_json_output(migration_status.stdout, errors, "migration status")
        validate_cmd_false_boundaries(migration_payload, "migration status", errors)
        if migration_payload.get("destructive_migration_required") is not False:
            errors.append("migration status must not require destructive migration")

        unsupported_manifest = second_manifest
        unsupported_manifest["instance_schema_version"] = 999
        write_json(instance / "config" / "instance.json", unsupported_manifest)
        migration_state = load_json(instance / "config" / "migration_state.json", "migration state", errors)
        migration_state["current_instance_schema_version"] = 999
        migration_state["migration_needed"] = True
        migration_state["blockers"] = ["unsupported instance_schema_version 999"]
        write_json(instance / "config" / "migration_state.json", migration_state)
        unsupported_validate = run(root, "python", "scripts/eureka_validate_instance.py", "--instance", str(instance), "--json")
        if unsupported_validate.returncode == 0:
            errors.append("unsupported schema version validation did not fail closed")
        unsupported_status = run(root, "python", "scripts/eureka_instance_migration_status.py", "--instance", str(instance), "--json")
        unsupported_payload = parse_json_output(unsupported_status.stdout, errors, "unsupported migration status")
        if unsupported_payload.get("migration_needed") is not True:
            errors.append("migration status did not detect migration_needed")

        repo_root_attempt = run(root, "python", "scripts/eureka_init_instance.py", "--instance", str(root), "--json")
        if repo_root_attempt.returncode == 0:
            errors.append("init accepted repo root as instance path")
        hidden_attempt = run(root, "python", "scripts/eureka_init_instance.py", "--instance", str(Path(tmp) / ".cache" / "instance"), "--json")
        if hidden_attempt.returncode == 0:
            errors.append("init accepted hidden root instance path")


def validate_cmd_false_boundaries(payload: Mapping[str, Any], label: str, errors: list[str]) -> None:
    for key in ("server_enabled", "lan_enabled", "deployment_performed", "production_readiness_claimed", "public_launch_readiness_claimed"):
        if payload.get(key) is not False:
            errors.append(f"{label} command must set {key}=false")


def validate_report(report: Mapping[str, Any], errors: list[str]) -> None:
    if report.get("recommended_next_task") != "LOCAL-03 \u2014 Local runtime composition boundary":
        errors.append("audit report must recommend LOCAL-03")
    for key in (
        "store_manifest_added",
        "migration_state_added",
        "migration_status_script_added",
        "unsupported_version_fail_closed_passed",
        "idempotency_preserves_instance_id",
        "temp_instance_validation_passed",
        "forbidden_roots_rejected",
    ):
        if report.get(key) is not True:
            errors.append(f"audit report must set {key}=true")
    for key in (
        "destructive_migration_allowed",
        "committed_instance_state_found",
        "server_implemented",
        "html_workbench_implemented",
        "workunit_runtime_implemented",
        "lan_enabled",
        "deployment_performed",
        "runtime_modified",
        "contracts_modified",
        "local_02_increased_leakage",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    ):
        if report.get(key) is not False:
            errors.append(f"audit report must set {key}=false")


def load_json(path: Path, label_or_schema: str, errors: list[str]) -> dict[str, Any]:
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
    if label_or_schema.endswith(".v0") and payload.get("schema_version") != label_or_schema:
        errors.append(f"schema_version mismatch for {relpath(path)}")
    return payload


def read_text(path: Path, errors: list[str]) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        errors.append(f"missing text file: {relpath(path)}")
        return ""


def run(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(list(args), cwd=root, text=True, capture_output=True, check=False)


def git(root: Path, *args: str) -> str:
    completed = run(root, "git", *args)
    return completed.stdout.strip() if completed.returncode == 0 else ""


def parse_json_output(text: str, errors: list[str], label: str) -> dict[str, Any]:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        errors.append(f"{label} command did not emit valid JSON: {exc}")
        return {}
    if not isinstance(payload, dict):
        errors.append(f"{label} command JSON output must be an object")
        return {}
    return payload


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_status_paths(lines: Sequence[str]) -> list[str]:
    paths: list[str] = []
    for line in lines:
        if len(line) < 4:
            continue
        raw = line[3:].replace("\\", "/").strip('"')
        if " -> " in raw:
            paths.extend(part.strip('"') for part in raw.split(" -> "))
        else:
            paths.append(raw)
    return paths


def relpath(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
