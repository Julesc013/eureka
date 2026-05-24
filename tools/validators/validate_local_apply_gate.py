#!/usr/bin/env python3
"""Validate LOCAL-APPLY-GATE-01 contracts, policies, CLI, smoke, and boundaries."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
TASK = "AIDE-BATCH-LOCAL-APPLY-GATE-01"
APPLY_CONFIRMATION = "APPLY_TO_LOCAL_INSTANCE"
ROLLBACK_CONFIRMATION = "ROLLBACK_LOCAL_INSTANCE"

REQUIRED_FILES = [
    "contracts/local_apply/README.md",
    "contracts/local_apply/local_apply_plan.v0.json",
    "contracts/local_apply/local_apply_command.v0.json",
    "contracts/local_apply/local_apply_preview.v0.json",
    "contracts/local_apply/local_apply_backup_manifest.v0.json",
    "contracts/local_apply/local_apply_mutation_manifest.v0.json",
    "contracts/local_apply/local_apply_audit_log.v0.json",
    "contracts/local_apply/local_apply_result.v0.json",
    "contracts/local_apply/local_apply_rollback_plan.v0.json",
    "contracts/local_apply/local_apply_rollback_result.v0.json",
    "contracts/local_apply/local_apply_boundary_report.v0.json",
    "contracts/instances/README.md",
    "contracts/instances/instance_descriptor.v0.json",
    "contracts/instances/instance_snapshot.v0.json",
    "contracts/instances/instance_mutation_scope.v0.json",
    "control/policies/local_apply_gate_policy.json",
    "control/policies/local_apply_backup_policy.json",
    "control/policies/local_apply_rollback_policy.json",
    "control/policies/local_apply_audit_policy.json",
    "control/policies/local_apply_non_claim_policy.json",
    "control/policies/operator_instance_mutation_policy.json",
    "control/inventory/local_apply_gate_policy_matrix.json",
    "control/inventory/local_apply_gate_route_matrix.json",
    "control/inventory/local_apply_gate_api_matrix.json",
    "control/inventory/local_apply_gate_command_matrix.json",
    "control/inventory/local_apply_gate_permission_matrix.json",
    "control/inventory/local_apply_gate_state_matrix.json",
    "control/inventory/local_apply_gate_event_matrix.json",
    "control/inventory/local_apply_backup_matrix.json",
    "control/inventory/local_apply_rollback_matrix.json",
    "control/inventory/local_apply_mutation_manifest_matrix.json",
    "control/inventory/local_apply_audit_log_matrix.json",
    "control/inventory/local_apply_reviewed_index_refresh_matrix.json",
    "runtime/local/apply/__init__.py",
    "runtime/local/apply/gate.py",
    "scripts/eureka_local_apply.py",
    "scripts/eureka_local_apply_backup.py",
    "scripts/eureka_local_apply_rollback.py",
    "examples/local_apply/sample_local_apply_preview.json",
    "examples/local_apply/sample_local_apply_plan.json",
    "examples/local_apply/sample_backup_manifest.json",
    "examples/local_apply/sample_mutation_manifest.json",
    "examples/local_apply/sample_audit_log.json",
    "examples/local_apply/sample_apply_result.json",
    "examples/local_apply/sample_rollback_plan.json",
    "examples/local_apply/sample_rollback_result.json",
    "examples/local_apply/sample_boundary_report.json",
    "examples/local_apply/sample_public_blocked_projection.json",
    "examples/local_apply/sample_native_blocked_projection.json",
    "docs/architecture/LOCAL_APPLY_GATE.md",
    "docs/architecture/OPERATOR_INSTANCE_MUTATION_MODEL.md",
    "docs/architecture/LOCAL_APPLY_BACKUP_AND_ROLLBACK.md",
    "docs/operations/LOCAL_APPLY_GATE_RUNBOOK.md",
    "docs/operations/POST_LOCAL_APPLY_GATE_PLAN.md",
    "docs/reference/LOCAL_APPLY_COMMANDS.md",
    "docs/reference/LOCAL_APPLY_AUDIT_LOG.md",
    "docs/reference/LOCAL_APPLY_MUTATION_MANIFEST.md",
    "docs/reference/LOCAL_APPLY_ROLLBACK_PLAN.md",
    "control/audits/local-apply-gate-01-v0/README.md",
    "control/audits/local-apply-gate-01-v0/local_apply_gate_report.json",
]
POLICY_FILES = [
    "control/policies/local_apply_gate_policy.json",
    "control/policies/local_apply_backup_policy.json",
    "control/policies/local_apply_rollback_policy.json",
    "control/policies/local_apply_audit_policy.json",
    "control/policies/local_apply_non_claim_policy.json",
    "control/policies/operator_instance_mutation_policy.json",
]
TRUE_POLICY_FIELDS = [
    "dry_run_default",
    "operator_token_required",
    "explicit_apply_flag_required",
    "explicit_confirmation_required",
    "target_instance_path_required",
    "target_instance_must_be_outside_repo",
    "repository_path_mutation_forbidden",
    "backup_required_before_apply",
    "rollback_plan_required_before_apply",
    "audit_log_required",
    "mutation_manifest_required",
    "post_apply_validation_required",
]
FALSE_POLICY_FIELDS = [
    "local_apply_enabled_by_default",
    "automatic_candidate_acceptance_enabled",
    "master_index_mutation_enabled",
    "committed_data_public_index_mutation_enabled",
    "public_apply_enabled",
    "native_apply_enabled",
    "downloads_enabled",
    "uploads_enabled",
    "extraction_enabled",
    "model_provider_enabled",
    "deployment_enabled",
    "production_readiness_claimed",
    "public_launch_readiness_claimed",
]
BOUNDARY_FALSES = [
    "operator_instance_mutated",
    "operator_instance_mutation_enabled_by_default",
    "committed_instance_state",
    "master_index_mutated",
    "committed_data_public_index_mutated",
    "download_performed",
    "upload_performed",
    "extraction_executed",
    "model_provider_used",
    "deployment_performed",
    "production_readiness_claimed",
    "public_launch_readiness_claimed",
]


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    result = validate()
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print(f"local apply gate validation: {result['status']}", file=stdout)
        for error in result["errors"]:
            print(f"ERROR: {error}", file=stdout)
        for warning in result["warnings"]:
            print(f"WARN: {warning}", file=stdout)
    return 0 if result["status"] == "pass" else 1


def validate() -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    smoke: dict[str, Any] = {}
    for rel in REQUIRED_FILES:
        if not (REPO_ROOT / rel).exists():
            errors.append(f"missing required file: {rel}")
    errors.extend(validate_json_files(REQUIRED_FILES))
    errors.extend(validate_policies())
    errors.extend(validate_matrices())
    errors.extend(validate_projection_examples())
    errors.extend(validate_cli_help())
    try:
        smoke = run_smoke()
        errors.extend(smoke.get("errors", []))
    except Exception as exc:
        errors.append(f"smoke failed: {exc}")
    errors.extend(validate_git_boundaries())
    return {
        "schema_version": "local_apply_gate_validation_result.v0",
        "task": TASK,
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "warnings": warnings,
        "smoke": smoke,
        "contracts_added": True,
        "policies_added": True,
        "runtime_apply_gate_added": True,
        "cli_added": True,
        "examples_added": True,
        "docs_added": True,
        "validator_added": True,
        "tests_added": True,
        "operator_instance_mutated": False,
        "committed_instance_state": False,
        "master_index_mutated": False,
        "committed_data_public_index_mutated": False,
        "download_performed": False,
        "upload_performed": False,
        "extraction_executed": False,
        "model_provider_used": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def validate_json_files(paths: Sequence[str]) -> list[str]:
    errors: list[str] = []
    for rel in paths:
        if not rel.endswith(".json"):
            continue
        try:
            payload = json.loads((REPO_ROOT / rel).read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"{rel} is not valid JSON: {exc}")
            continue
        if not isinstance(payload, Mapping):
            errors.append(f"{rel} must be a JSON object")
    return errors


def validate_policies() -> list[str]:
    errors: list[str] = []
    for rel in POLICY_FILES:
        payload = read_json(rel)
        for field in TRUE_POLICY_FIELDS:
            if payload.get(field) is not True:
                errors.append(f"{rel} requires {field}=true")
        for field in FALSE_POLICY_FIELDS:
            if payload.get(field) is not False:
                errors.append(f"{rel} requires {field}=false")
    return errors


def validate_matrices() -> list[str]:
    errors: list[str] = []
    command_matrix = read_json("control/inventory/local_apply_gate_command_matrix.json")
    for command in (
        "preview_local_apply",
        "create_local_apply_plan",
        "validate_local_apply_plan",
        "create_pre_apply_backup",
        "apply_local_change",
        "validate_post_apply",
        "create_rollback_plan",
        "run_rollback",
        "validate_post_rollback",
        "inspect_apply_audit_log",
    ):
        if command not in command_matrix.get("commands", []):
            errors.append(f"command matrix missing {command}")
    event_matrix = read_json("control/inventory/local_apply_gate_event_matrix.json")
    for event_type in ("local_apply.preview_created", "local_apply.apply_completed", "local_apply.rollback_completed", "local_apply.audit_written"):
        if event_type not in event_matrix.get("event_types", []):
            errors.append(f"event matrix missing {event_type}")
    return errors


def validate_projection_examples() -> list[str]:
    errors: list[str] = []
    for rel in (
        "examples/local_apply/sample_public_blocked_projection.json",
        "examples/local_apply/sample_native_blocked_projection.json",
    ):
        payload = read_json(rel)
        if payload.get("status") != "blocked" or payload.get("apply_enabled") is not False:
            errors.append(f"{rel} must be blocked/read-only")
    return errors


def validate_cli_help() -> list[str]:
    errors: list[str] = []
    for script in ("eureka_local_apply.py", "eureka_local_apply_backup.py", "eureka_local_apply_rollback.py"):
        completed = run([sys.executable, f"scripts/{script}", "--help"])
        if completed.returncode != 0:
            errors.append(f"CLI help failed for {script}: {completed.stderr.strip()}")
    return errors


def run_smoke() -> dict[str, Any]:
    errors: list[str] = []
    with tempfile.TemporaryDirectory(prefix="eureka-local-apply-validator-") as tmp:
        instance = Path(tmp) / "instance"
        init = run_json([sys.executable, "scripts/eureka_init_instance.py", "--instance", str(instance), "--json"])
        if init.get("status") not in {"pass", "pass_with_warnings"}:
            errors.append("temp instance init failed")

        dry = run_json([sys.executable, "scripts/eureka_local_apply.py", "--instance", str(instance), "--from-review-promote-fixture", "--dry-run", "--json"])
        if dry.get("status") != "dry_run" or not dry.get("dry_run_preview_passed"):
            errors.append("dry-run preview did not pass")

        no_token = run([sys.executable, "scripts/eureka_local_apply.py", "--instance", str(instance), "--from-review-promote-fixture", "--apply", "--confirm", APPLY_CONFIRMATION, "--json"])
        if no_token.returncode == 0 or json_from_stdout(no_token).get("status") != "blocked":
            errors.append("apply without token was not blocked")

        no_confirm = run([sys.executable, "scripts/eureka_local_apply.py", "--instance", str(instance), "--from-review-promote-fixture", "--apply", "--operator-token", "local-dev-token", "--json"])
        if no_confirm.returncode == 0 or json_from_stdout(no_confirm).get("status") != "blocked":
            errors.append("apply without confirmation was not blocked")

        repo_path = run([sys.executable, "scripts/eureka_local_apply.py", "--instance", str(REPO_ROOT), "--from-review-promote-fixture", "--apply", "--operator-token", "local-dev-token", "--confirm", APPLY_CONFIRMATION, "--json"])
        if repo_path.returncode == 0 or json_from_stdout(repo_path).get("status") != "blocked":
            errors.append("repo path target was not blocked")

        apply_result = run_json([
            sys.executable,
            "scripts/eureka_local_apply.py",
            "--instance",
            str(instance),
            "--from-review-promote-fixture",
            "--apply",
            "--operator-token",
            "local-dev-token",
            "--confirm",
            APPLY_CONFIRMATION,
            "--json",
        ])
        for field in (
            "backup_created_before_apply",
            "mutation_manifest_created",
            "audit_log_created",
            "rollback_plan_created",
            "post_apply_validation_passed",
        ):
            if apply_result.get(field) is not True:
                errors.append(f"apply result missing {field}=true")
        for field in BOUNDARY_FALSES:
            if apply_result.get(field) is not False:
                errors.append(f"apply result must keep {field}=false")
        rollback_file = Path(apply_result["rollback_plan"]["backup_manifest"]["backup_root"]) / "rollback_plan.json"
        rollback_result = run_json([
            sys.executable,
            "scripts/eureka_local_apply_rollback.py",
            "--instance",
            str(instance),
            "--rollback-plan",
            str(rollback_file),
            "--apply",
            "--operator-token",
            "local-dev-token",
            "--confirm",
            ROLLBACK_CONFIRMATION,
            "--json",
        ])
        if rollback_result.get("status") != "pass" or rollback_result.get("post_rollback_validation_passed") is not True:
            errors.append("rollback did not pass")
        for field in BOUNDARY_FALSES:
            if rollback_result.get(field) is not False:
                errors.append(f"rollback result must keep {field}=false")
        return {
            "schema_version": "local_apply_gate_smoke_result.v0",
            "status": "pass" if not errors else "fail",
            "dry_run_preview_passed": dry.get("dry_run_preview_passed") is True,
            "apply_without_token_blocked": json_from_stdout(no_token).get("status") == "blocked",
            "apply_without_confirmation_blocked": json_from_stdout(no_confirm).get("status") == "blocked",
            "repo_path_target_blocked": json_from_stdout(repo_path).get("status") == "blocked",
            "temp_instance_apply_passed": apply_result.get("status") == "pass",
            "backup_created_before_apply": apply_result.get("backup_created_before_apply") is True,
            "mutation_manifest_created": apply_result.get("mutation_manifest_created") is True,
            "audit_log_created": apply_result.get("audit_log_created") is True,
            "rollback_plan_created": apply_result.get("rollback_plan_created") is True,
            "rollback_passed": rollback_result.get("status") == "pass",
            "post_apply_validation_passed": apply_result.get("post_apply_validation_passed") is True,
            "post_rollback_validation_passed": rollback_result.get("post_rollback_validation_passed") is True,
            "errors": errors,
        }


def validate_git_boundaries() -> list[str]:
    errors: list[str] = []
    tracked_instances = run(["git", "ls-files", "instances", "eureka-instance"]).stdout.strip()
    if tracked_instances:
        errors.append("committed instance state is tracked")
    changed = run(["git", "status", "--short", "--", "instances", "eureka-instance", "site/dist", "data/public_index"]).stdout.strip()
    if changed:
        errors.append(f"forbidden output/instance paths changed: {changed}")
    return errors


def read_json(rel: str) -> dict[str, Any]:
    return json.loads((REPO_ROOT / rel).read_text(encoding="utf-8"))


def run_json(command: Sequence[str]) -> dict[str, Any]:
    completed = run(command)
    payload = json_from_stdout(completed)
    if completed.returncode != 0:
        raise AssertionError(f"{' '.join(command)} failed: {completed.stderr.strip() or completed.stdout.strip()}")
    return payload


def json_from_stdout(completed: subprocess.CompletedProcess[str]) -> dict[str, Any]:
    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError:
        return {}


def run(command: Sequence[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=REPO_ROOT, text=True, capture_output=True, check=False)


if __name__ == "__main__":
    raise SystemExit(main())
