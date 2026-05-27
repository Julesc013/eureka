#!/usr/bin/env python3
"""Validate LOCAL-01 local instance bootstrap evidence."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO

try:
    from local_queue_progress import (
        current_recommended_task,
        f0_deferred_or_past_local_closeout,
        is_later_control_or_handoff,
        latest_packet_current_or_advanced,
        queue_current_or_advanced,
        queue_task_available,
        queue_task_completed,
    )
except ModuleNotFoundError:  # pragma: no cover - supports package-style imports in tests.
    from scripts.local_queue_progress import (
        current_recommended_task,
        f0_deferred_or_past_local_closeout,
        is_later_control_or_handoff,
        latest_packet_current_or_advanced,
        queue_current_or_advanced,
        queue_task_available,
        queue_task_completed,
    )


REPO_ROOT = Path(__file__).resolve().parents[2]
TASK_ID = "LOCAL-01"
NEXT_TASK = "LOCAL-02"
F0_CLOSEOUT = "LOCAL-14"

POLICIES = {
    "control/policies/local_instance_policy.json": "local_instance_policy.v0",
    "control/policies/local_instance_path_policy.json": "local_instance_path_policy.v0",
    "control/policies/local_instance_state_policy.json": "local_instance_state_policy.v0",
}
INVENTORIES = {
    "control/inventory/local_instance_layout.json": "local_instance_layout.v0",
    "control/inventory/local_instance_bootstrap_result.json": "local_instance_bootstrap_result.v0",
    "control/inventory/local_instance_validation_result.json": "local_instance_validation_result.v0",
    "control/inventory/local_instance_gap_register.json": "local_instance_gap_register.v0",
    "control/inventory/local_01_leakage_baseline.json": "local_01_leakage_baseline.v0",
    "control/inventory/local_01_next_task_decision.json": "local_01_next_task_decision.v0",
}
DOCS = (
    "docs/architecture/LOCAL_INSTANCE_MODEL.md",
    "docs/reference/LOCAL_INSTANCE_LAYOUT.md",
    "docs/operations/LOCAL_INSTANCE_BOOTSTRAP.md",
)
SCRIPTS = (
    "scripts/eureka_init_instance.py",
    "scripts/eureka_validate_instance.py",
    "scripts/eureka_instance_status.py",
    "scripts/validate_local_instance_bootstrap.py",
)
TESTS = (
    "tests/operations/test_local_instance_bootstrap.py",
    "tests/operations/test_local_instance_policy.py",
)
AUDIT_ROOT = Path("control/audits/local-01-local-instance-bootstrap-v0")
AUDIT_FILES = (
    "README.md",
    "local_01_report.json",
    "instance_layout.md",
    "bootstrap_result.md",
    "validation_result.md",
    "leakage_baseline.md",
    "validation.md",
    "generated/sample_instance_manifest.json",
    "generated/sample_instance_status.json",
    "generated/sample_bootstrap_result.json",
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
    "archive/prototypes/",
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
        print("LOCAL-01 local instance bootstrap validation", file=stdout)
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

    validate_policy_payloads(payloads, errors)
    validate_layout(payloads.get("control/inventory/local_instance_layout.json", {}), errors)
    validate_decision(payloads.get("control/inventory/local_01_next_task_decision.json", {}), errors)
    validate_leakage(payloads.get("control/inventory/local_01_leakage_baseline.json", {}), errors, warnings)
    validate_docs_scripts_tests(root, errors)
    validate_audit_pack(root, errors)
    validate_queue_and_context(root, errors)
    validate_scope(root, errors)
    validate_no_committed_instance(root, errors)
    validate_temp_instance_commands(root, errors, warnings)
    validate_report(root, errors)

    status = "fail" if errors else ("pass_with_warnings" if warnings else "pass")
    return {
        "schema_version": "local_instance_bootstrap_validation.v0",
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


def validate_policy_payloads(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    instance = payloads.get("control/policies/local_instance_policy.json", {})
    path = payloads.get("control/policies/local_instance_path_policy.json", {})
    state = payloads.get("control/policies/local_instance_state_policy.json", {})
    expected_true = {
        "explicit_instance_path_required": instance,
        "hidden_state_roots_forbidden": instance,
        "committed_instance_state_forbidden": instance,
        "instance_init_idempotent": instance,
        "instance_validation_required": instance,
        "committed_local_state_forbidden": state,
        "sqlite_db_files_forbidden_in_git": state,
        "logs_forbidden_in_git": state,
        "run_locks_forbidden_in_git": state,
        "tmp_files_forbidden_in_git": state,
        "exports_imports_forbidden_by_default": state,
        "generated_instance_state_must_be_explicit": state,
    }
    for key, payload in expected_true.items():
        if payload.get(key) is not True:
            errors.append(f"policy flag must be true: {key}")
    expected_false = ("network_access_enabled", "server_enabled", "lan_enabled", "deployment_enabled")
    for key in expected_false:
        if instance.get(key) is not False:
            errors.append(f"local instance policy must set {key}=false")
    if instance.get("default_instance_name") != "eureka-instance":
        errors.append("default instance name must be eureka-instance")
    allowed_dirs = path.get("allowed_instance_dirs")
    if allowed_dirs != ["config", "db", "logs", "run", "tmp", "exports", "imports"]:
        errors.append("path policy allowed_instance_dirs mismatch")
    forbidden_roots = set(path.get("forbidden_instance_roots", []))
    for required in (".cache", ".local", ".aide.local", "home directory implicit path", "site/dist", "repo root as instance path"):
        if required not in forbidden_roots:
            errors.append(f"path policy missing forbidden root: {required}")


def validate_layout(layout: Mapping[str, Any], errors: list[str]) -> None:
    if layout.get("default_instance_name") != "eureka-instance":
        errors.append("layout default_instance_name mismatch")
    if layout.get("required_directories") != ["config", "db", "logs", "run", "tmp", "exports", "imports"]:
        errors.append("layout required_directories mismatch")
    for rel in ("config/instance.json", "run/status.json"):
        if rel not in layout.get("required_files", []):
            errors.append(f"layout missing required file: {rel}")
    for rel in ("db/source_cache.sqlite", "db/evidence_ledger.sqlite", "db/review_queue.sqlite", "db/public_index.sqlite"):
        if rel not in layout.get("planned_database_files", []):
            errors.append(f"layout missing database: {rel}")
    for key in ("committed_instance_state_allowed", "hidden_state_roots_allowed", "server_enabled", "lan_enabled"):
        if layout.get(key) is not False:
            errors.append(f"layout must set {key}=false")


def validate_decision(decision: Mapping[str, Any], errors: list[str]) -> None:
    if decision.get("recommended_next_task") != "LOCAL-02 \u2014 Instance configuration, schema, and migration guard":
        errors.append("next task decision must point to LOCAL-02")
    if decision.get("f0_current_status") != "deferred" or decision.get("f0_can_resume_after") != F0_CLOSEOUT:
        errors.append("F0 must remain deferred until LOCAL-14")
    for key in ("server_can_start", "lan_can_start"):
        if decision.get(key) is not False:
            errors.append(f"next task decision must set {key}=false")


def validate_leakage(leakage: Mapping[str, Any], errors: list[str], warnings: list[str]) -> None:
    if leakage.get("local_01_increased_leakage") is not False:
        errors.append("LOCAL-01 must not increase runtime leakage")
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
    if not queue_current_or_advanced(root, TASK_ID, NEXT_TASK):
        errors.append("queue index must point to LOCAL-02")
    if not queue_task_completed(root, TASK_ID):
        errors.append("queue index must mark LOCAL-01 completed")
    if not queue_task_available(root, NEXT_TASK):
        errors.append("queue index must include LOCAL-02")
    if not f0_deferred_or_past_local_closeout(root):
        errors.append("queue index must keep F0 deferred until LOCAL-14")
    if not latest_packet_current_or_advanced(root, TASK_ID, NEXT_TASK):
        errors.append("latest task packet must point to LOCAL-02")


def validate_scope(root: Path, errors: list[str]) -> None:
    if queue_task_completed(root, TASK_ID) and is_later_control_or_handoff(current_recommended_task(root)):
        return
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
    with tempfile.TemporaryDirectory(prefix="eureka-local-01-") as tmp:
        instance = Path(tmp) / "eureka-instance"
        init = run(root, "python", "scripts/eureka_init_instance.py", "--instance", str(instance), "--json")
        if init.returncode != 0:
            errors.append("temp instance init command failed")
            return
        init_payload = parse_json_output(init.stdout, errors, "init")
        validate_cmd_false_boundaries(init_payload, "init", errors)
        second = run(root, "python", "scripts/eureka_init_instance.py", "--instance", str(instance), "--json")
        if second.returncode != 0:
            errors.append("temp instance idempotent init failed")
        validate = run(root, "python", "scripts/eureka_validate_instance.py", "--instance", str(instance), "--json")
        if validate.returncode != 0:
            errors.append("temp instance validation command failed")
        validate_payload = parse_json_output(validate.stdout, errors, "validate")
        validate_cmd_false_boundaries(validate_payload, "validate", errors)
        status = run(root, "python", "scripts/eureka_instance_status.py", "--instance", str(instance), "--json")
        if status.returncode != 0:
            errors.append("temp instance status command failed")
        status_payload = parse_json_output(status.stdout, errors, "status")
        validate_cmd_false_boundaries(status_payload, "status", errors)

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


def validate_report(root: Path, errors: list[str]) -> None:
    report = load_json(root / AUDIT_ROOT / "local_01_report.json", "local_01_report.v0", errors)
    if report.get("recommended_next_task") != "LOCAL-02 \u2014 Instance configuration, schema, and migration guard":
        errors.append("audit report must recommend LOCAL-02")
    for key in (
        "init_script_added",
        "validate_script_added",
        "status_script_added",
        "temp_instance_init_passed",
        "temp_instance_validation_passed",
        "idempotency_passed",
        "forbidden_roots_rejected",
    ):
        if report.get(key) is not True:
            errors.append(f"audit report must set {key}=true")
    for key in (
        "committed_instance_state_found",
        "server_implemented",
        "html_workbench_implemented",
        "workunit_runtime_implemented",
        "lan_enabled",
        "deployment_performed",
        "runtime_modified",
        "contracts_modified",
        "local_01_increased_leakage",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    ):
        if report.get(key) is not False:
            errors.append(f"audit report must set {key}=false")


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
