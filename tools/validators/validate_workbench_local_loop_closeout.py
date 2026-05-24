#!/usr/bin/env python3
"""Validate WORKBENCH-LOCAL-LOOP-CLOSEOUT-01 evidence, CLI proof, and boundaries."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
TASK = "AIDE-BATCH-WORKBENCH-LOCAL-LOOP-CLOSEOUT-01"

CONTRACTS = {
    "contracts/local_loop/README.md",
    "contracts/local_loop/local_loop_plan.v0.json",
    "contracts/local_loop/local_loop_step.v0.json",
    "contracts/local_loop/local_loop_result.v0.json",
    "contracts/local_loop/local_loop_apply_proof.v0.json",
    "contracts/local_loop/local_loop_rollback_proof.v0.json",
    "contracts/local_loop/local_loop_search_after_apply_proof.v0.json",
    "contracts/local_loop/local_loop_boundary_report.v0.json",
}
POLICIES = {
    "control/policies/workbench_local_loop_policy.json",
    "control/policies/workbench_local_loop_non_claim_policy.json",
    "control/policies/workbench_local_loop_boundary_policy.json",
    "control/policies/workbench_local_loop_operator_policy.json",
}
MATRICES = {
    "control/inventory/workbench_local_loop_policy_matrix.json",
    "control/inventory/workbench_local_loop_route_matrix.json",
    "control/inventory/workbench_local_loop_api_matrix.json",
    "control/inventory/workbench_local_loop_state_matrix.json",
    "control/inventory/workbench_local_loop_event_matrix.json",
    "control/inventory/workbench_local_loop_step_matrix.json",
    "control/inventory/workbench_local_loop_boundary_report.json",
    "control/inventory/workbench_local_loop_smoke_result.json",
    "control/inventory/workbench_local_loop_apply_proof.json",
    "control/inventory/workbench_local_loop_rollback_proof.json",
    "control/inventory/workbench_local_loop_search_after_apply_proof.json",
    "control/inventory/workbench_local_loop_validation_matrix.json",
    "control/inventory/workbench_local_loop_result.json",
    "control/inventory/workbench_local_loop_next_task_decision.json",
}
EXAMPLES = {
    "examples/local_loop/sample_local_loop_plan.json",
    "examples/local_loop/sample_local_loop_result.json",
    "examples/local_loop/sample_apply_proof.json",
    "examples/local_loop/sample_rollback_proof.json",
    "examples/local_loop/sample_search_after_apply_proof.json",
    "examples/local_loop/sample_boundary_report.json",
    "examples/local_loop/sample_public_blocked_projection.json",
    "examples/local_loop/sample_native_blocked_projection.json",
}
DOCS = {
    "docs/architecture/WORKBENCH_LOCAL_LOOP.md",
    "docs/architecture/LOCAL_PRODUCT_LOOP.md",
    "docs/operations/WORKBENCH_LOCAL_LOOP_RUNBOOK.md",
    "docs/operations/POST_WORKBENCH_LOCAL_LOOP_PLAN.md",
    "docs/reference/WORKBENCH_LOCAL_LOOP_STEPS.md",
    "docs/reference/WORKBENCH_LOCAL_LOOP_PROOFS.md",
}
AUDIT_ROOT = Path("control/audits/workbench-local-loop-closeout-01-v0")
AUDIT_FILES = {
    "README.md",
    "workbench_local_loop_report.json",
    "step_matrix.md",
    "apply_proof.md",
    "rollback_proof.md",
    "search_after_apply_proof.md",
    "boundary_report.md",
    "smoke_result.md",
    "validation_matrix.md",
    "validation.md",
    "generated/sample_local_loop_plan.json",
    "generated/sample_local_loop_result.json",
    "generated/sample_apply_proof.json",
    "generated/sample_rollback_proof.json",
    "generated/sample_search_after_apply_proof.json",
    "generated/sample_boundary_report.json",
    "generated/sample_summary.md",
}
BOUNDARY_FALSES = (
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
        print(f"workbench local loop validation: {result['status']}", file=stdout)
        for error in result["errors"]:
            print(f"ERROR: {error}", file=stdout)
        for warning in result["warnings"]:
            print(f"WARN: {warning}", file=stdout)
    return 0 if result["status"] == "pass" else 1


def validate(root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    for rel in sorted(CONTRACTS | POLICIES | MATRICES | EXAMPLES | DOCS):
        require_file(root, rel, errors)
    for rel in sorted(AUDIT_FILES):
        require_file(root, (AUDIT_ROOT / rel).as_posix(), errors)
    payloads = {rel: load_json(root / rel, errors) for rel in sorted(POLICIES | MATRICES | EXAMPLES)}
    result_payload = load_json(root / "control/inventory/workbench_local_loop_result.json", errors)
    boundary = load_json(root / "control/inventory/workbench_local_loop_boundary_report.json", errors)
    apply_proof = load_json(root / "control/inventory/workbench_local_loop_apply_proof.json", errors)
    rollback_proof = load_json(root / "control/inventory/workbench_local_loop_rollback_proof.json", errors)
    search_proof = load_json(root / "control/inventory/workbench_local_loop_search_after_apply_proof.json", errors)
    local_apply_result = load_json(root / "control/inventory/local_apply_gate_result.json", errors)

    validate_prior_local_apply(local_apply_result, errors)
    validate_policies(payloads, errors)
    validate_matrix_content(payloads, errors)
    validate_examples(payloads, errors)
    validate_result(result_payload, errors)
    validate_proofs(apply_proof, rollback_proof, search_proof, errors)
    validate_boundary(boundary, errors)
    script_checks = validate_script_commands(root, errors)
    errors.extend(validate_git_boundaries(root))

    return {
        "schema_version": "workbench_local_loop_validation.v0",
        "task": TASK,
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "warnings": warnings,
        "script_checks": script_checks,
        "contracts_added": all((root / rel).is_file() for rel in CONTRACTS),
        "policies_added": all((root / rel).is_file() for rel in POLICIES),
        "step_matrix_added": (root / "control/inventory/workbench_local_loop_step_matrix.json").is_file(),
        "runtime_local_loop_added": (root / "runtime/local_loop/closeout.py").is_file(),
        "cli_added": (root / "scripts/eureka_local_loop_closeout.py").is_file(),
        "examples_added": all((root / rel).is_file() for rel in EXAMPLES),
        "docs_added": all((root / rel).is_file() for rel in DOCS),
        "validator_added": True,
        "tests_added": True,
        "dry_run_loop_passed": result_payload.get("dry_run_loop_passed") is True,
        "temp_apply_loop_passed": result_payload.get("temp_apply_loop_passed") is True,
        "search_after_apply_passed": result_payload.get("search_after_apply_passed") is True,
        "rollback_passed": result_payload.get("rollback_passed") is True,
        "search_after_rollback_passed": result_payload.get("search_after_rollback_passed") is True,
        "public_projection_blocked": result_payload.get("public_projection_blocked") is True,
        "native_read_only_projection_blocked": result_payload.get("native_read_only_projection_blocked") is True,
    }


def validate_prior_local_apply(payload: Mapping[str, Any], errors: list[str]) -> None:
    if payload.get("status") not in {"pass", "pass_with_warnings"}:
        errors.append("LOCAL-APPLY-GATE-01 result must be pass or pass_with_warnings")
    for field in (
        "dry_run_preview_passed",
        "apply_without_token_blocked",
        "apply_without_confirmation_blocked",
        "repo_path_target_blocked",
        "temp_instance_apply_passed",
        "backup_created_before_apply",
        "mutation_manifest_created",
        "audit_log_created",
        "rollback_plan_created",
        "rollback_passed",
        "post_apply_validation_passed",
        "post_rollback_validation_passed",
        "public_projection_blocked",
        "native_read_only_projection_blocked",
    ):
        if payload.get(field) is not True:
            errors.append(f"local apply result requires {field}=true")
    for field in BOUNDARY_FALSES:
        if payload.get(field) is not False:
            errors.append(f"local apply result requires {field}=false")


def validate_policies(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    combined: dict[str, Any] = {}
    for rel in POLICIES:
        combined.update(payloads.get(rel, {}))
    for field in (
        "local_loop_requires_apply_gate",
        "local_loop_uses_temp_instance_for_automated_tests",
        "operator_token_required_for_apply",
        "explicit_confirmation_required_for_apply",
        "backup_required_before_apply",
        "rollback_required",
        "audit_log_required",
        "mutation_manifest_required",
        "fake_evidence_forbidden",
        "fake_verified_records_forbidden",
    ):
        if combined.get(field) is not True:
            errors.append(f"policy requires {field}=true")
    for field in (
        "operator_instance_mutation_default",
        "public_loop_mutation_enabled",
        "native_loop_mutation_enabled",
        "master_index_mutation_enabled",
        "committed_data_public_index_mutation_enabled",
        "downloads_enabled",
        "extraction_enabled",
        "model_provider_enabled",
        "deployment_enabled",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    ):
        if combined.get(field) is not False:
            errors.append(f"policy requires {field}=false")


def validate_matrix_content(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    route_text = json.dumps(payloads.get("control/inventory/workbench_local_loop_route_matrix.json", {}))
    for token in ("/local-loop", "/api/v1/local-loop/plan", "/api/v1/local-loop/apply-temp", "/api/v1/local-loop/{loop_id}/proofs"):
        if token not in route_text:
            errors.append(f"route matrix missing {token}")
    step_text = json.dumps(payloads.get("control/inventory/workbench_local_loop_step_matrix.json", {}))
    for token in ("create_resolution_run", "apply_to_temp_instance", "search_after_apply", "rollback_temp_instance", "search_after_rollback"):
        if token not in step_text:
            errors.append(f"step matrix missing {token}")
    event_text = json.dumps(payloads.get("control/inventory/workbench_local_loop_event_matrix.json", {}))
    for token in ("local_loop.run_created", "local_loop.apply_completed_temp", "local_loop.rollback_completed", "local_loop.search_after_rollback_passed"):
        if token not in event_text:
            errors.append(f"event matrix missing {token}")


def validate_examples(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    loop = payloads.get("examples/local_loop/sample_local_loop_result.json", {})
    if loop.get("status") != "pass":
        errors.append("sample local loop result must pass")
    for rel in (
        "examples/local_loop/sample_public_blocked_projection.json",
        "examples/local_loop/sample_native_blocked_projection.json",
    ):
        payload = payloads.get(rel, {})
        if payload.get("read_only") is not True or payload.get("mutation_allowed") is not False:
            errors.append(f"{rel} must be read-only and mutation-blocked")


def validate_result(payload: Mapping[str, Any], errors: list[str]) -> None:
    required_true = (
        "contracts_added",
        "policies_added",
        "step_matrix_added",
        "runtime_local_loop_added",
        "cli_added",
        "examples_added",
        "docs_added",
        "validator_added",
        "tests_added",
        "dry_run_loop_passed",
        "temp_apply_loop_passed",
        "search_after_apply_passed",
        "rollback_passed",
        "search_after_rollback_passed",
        "public_projection_blocked",
        "native_read_only_projection_blocked",
    )
    for field in required_true:
        if payload.get(field) is not True:
            errors.append(f"result requires {field}=true")
    for field in BOUNDARY_FALSES:
        if payload.get(field) is not False:
            errors.append(f"result requires {field}=false")


def validate_proofs(
    apply_proof: Mapping[str, Any],
    rollback_proof: Mapping[str, Any],
    search_proof: Mapping[str, Any],
    errors: list[str],
) -> None:
    for field in ("backup_created_before_apply", "mutation_manifest_created", "audit_log_created", "post_apply_validation_passed", "search_after_apply_passed"):
        if apply_proof.get(field) is not True:
            errors.append(f"apply proof requires {field}=true")
    for field in ("rollback_passed", "post_rollback_validation_passed", "search_after_rollback_passed"):
        if rollback_proof.get(field) is not True:
            errors.append(f"rollback proof requires {field}=true")
    if search_proof.get("search_after_apply_passed") is not True:
        errors.append("search proof requires search_after_apply_passed=true")
    if search_proof.get("search_after_rollback_passed") is not True:
        errors.append("search proof requires search_after_rollback_passed=true")


def validate_boundary(payload: Mapping[str, Any], errors: list[str]) -> None:
    for field in BOUNDARY_FALSES:
        if payload.get(field) is not False:
            errors.append(f"boundary requires {field}=false")


def validate_script_commands(root: Path, errors: list[str]) -> dict[str, bool]:
    checks: dict[str, bool] = {}
    commands = {
        "help": [sys.executable, "scripts/eureka_local_loop_closeout.py", "--help"],
        "dry_run": [sys.executable, "scripts/eureka_local_loop_closeout.py", "--query", "sampleproject", "--projection", "operator_workbench", "--dry-run", "--json"],
        "temp_apply": [sys.executable, "scripts/eureka_local_loop_closeout.py", "--query", "sampleproject", "--projection", "operator_workbench", "--use-temp-instance", "--apply-to-temp", "--operator-token", "local-dev-token", "--confirm", "APPLY_TO_LOCAL_INSTANCE", "--json"],
        "public_blocked": [sys.executable, "scripts/eureka_local_loop_closeout.py", "--query", "sampleproject", "--projection", "public_web", "--use-temp-instance", "--apply-to-temp", "--operator-token", "local-dev-token", "--confirm", "APPLY_TO_LOCAL_INSTANCE", "--json"],
        "native_blocked": [sys.executable, "scripts/eureka_local_loop_closeout.py", "--query", "sampleproject", "--projection", "native_desktop_read_only", "--use-temp-instance", "--apply-to-temp", "--operator-token", "local-dev-token", "--confirm", "APPLY_TO_LOCAL_INSTANCE", "--json"],
    }
    for label, command in commands.items():
        completed = subprocess.run(command, cwd=root, text=True, capture_output=True, check=False)
        if label == "help":
            checks[label] = completed.returncode == 0
            if completed.returncode != 0:
                errors.append(f"CLI help failed: {completed.stderr or completed.stdout}")
            continue
        payload = json_from_stdout(completed)
        if not payload:
            checks[label] = False
            errors.append(f"{label} did not emit JSON: {completed.stderr or completed.stdout}")
            continue
        if label in {"public_blocked", "native_blocked"}:
            checks[label] = payload.get("status") == "blocked" and completed.returncode != 0
        else:
            checks[label] = completed.returncode == 0
        if label == "dry_run" and payload.get("status") != "dry_run":
            errors.append("dry-run command did not return dry_run")
        if label == "temp_apply":
            for field in ("temp_apply_loop_passed", "search_after_apply_passed", "rollback_passed", "search_after_rollback_passed"):
                if payload.get(field) is not True:
                    errors.append(f"temp apply command missing {field}=true")
        if label == "public_blocked" and payload.get("public_projection_blocked") is not True:
            errors.append("public projection apply was not blocked")
        if label == "native_blocked" and payload.get("native_read_only_projection_blocked") is not True:
            errors.append("native projection apply was not blocked")
        for field in BOUNDARY_FALSES:
            if payload.get(field) is not False:
                errors.append(f"{label} must keep {field}=false")
    return checks


def validate_git_boundaries(root: Path) -> list[str]:
    errors: list[str] = []
    tracked_instances = run(["git", "ls-files", "instances", "eureka-instance"], root).stdout.strip()
    if tracked_instances:
        errors.append("committed instance state is tracked")
    changed = run(["git", "status", "--short", "--", "instances", "eureka-instance", "site/dist", "data/public_index"], root).stdout.strip()
    if changed:
        errors.append(f"forbidden output/instance paths changed: {changed}")
    return errors


def require_file(root: Path, rel: str, errors: list[str]) -> None:
    path = root / rel
    if not path.is_file():
        errors.append(f"missing file: {rel}")
    elif path.stat().st_size == 0:
        errors.append(f"empty file: {rel}")


def load_json(path: Path, errors: list[str]) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"missing JSON file: {path.relative_to(REPO_ROOT).as_posix() if path.is_absolute() else path.as_posix()}")
        return {}
    except json.JSONDecodeError as exc:
        errors.append(f"invalid JSON {path}: {exc}")
        return {}
    if not isinstance(payload, dict):
        errors.append(f"JSON file must contain object: {path}")
        return {}
    return payload


def json_from_stdout(completed: subprocess.CompletedProcess[str]) -> dict[str, Any]:
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def run(command: Sequence[str], root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=root, text=True, capture_output=True, check=False)


if __name__ == "__main__":
    raise SystemExit(main())
