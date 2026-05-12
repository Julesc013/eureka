#!/usr/bin/env python3
"""Validate R0-11 final closeout evidence and gates."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[1]

INVENTORIES = {
    "control/inventory/r0_final_closeout_result.json": "r0_final_closeout_result.v0",
    "control/inventory/r0_final_blocker_register.json": "r0_final_blocker_register.v0",
    "control/inventory/r0_final_warning_disposition.json": "r0_final_warning_disposition.v0",
    "control/inventory/r0_final_runtime_readiness_matrix.json": "r0_final_runtime_readiness_matrix.v0",
    "control/inventory/r0_final_branch_state.json": "r0_final_branch_state.v0",
    "control/inventory/r0_final_queue_state.json": "r0_final_queue_state.v0",
    "control/inventory/r0_final_next_task_decision.json": "r0_final_next_task_decision.v0",
    "control/inventory/r0_deferred_paths_register.json": "r0_deferred_paths_register.v0",
    "control/inventory/r0_superseded_paths_register.json": "r0_superseded_paths_register.v0",
    "control/inventory/r0_child_remediation_tasks.json": "r0_child_remediation_tasks.v0",
}

AUDIT_PACK = Path("control/audits/r0-11-final-closeout-v0")
AUDIT_FILES = (
    "README.md",
    "r0_11_report.json",
    "final_closeout.md",
    "final_runtime_readiness_matrix.md",
    "final_blocker_register.md",
    "final_warning_disposition.md",
    "final_branch_state.md",
    "final_queue_state.md",
    "deferred_paths.md",
    "superseded_paths.md",
    "child_remediation_tasks.md",
    "f0_resumption_decision.md",
    "dev_main_promotion_decision.md",
    "future_task_completion_standard.md",
    "validation.md",
    "generated/sample_final_closeout_result.json",
    "generated/sample_runtime_readiness_matrix.json",
    "generated/sample_next_task_decision.json",
    "generated/sample_summary.md",
)

R0_VALIDATORS = (
    "scripts/validate_runtime_architecture_leakage.py",
    "scripts/validate_contract_taxonomy_plan.py",
    "scripts/validate_contract_taxonomy_migration.py",
    "scripts/validate_product_contract_tree.py",
    "scripts/validate_source_observation_seam.py",
    "scripts/validate_source_cache_store.py",
    "scripts/validate_evidence_ledger_store.py",
    "scripts/validate_review_queue_store.py",
    "scripts/validate_reviewed_public_index.py",
    "scripts/validate_one_source_live_test.py",
    "scripts/validate_r0_production_review.py",
)

FORBIDDEN_CHANGED_ROOTS = ("runtime/connectors/", "runtime/local_foundry/", "runtime/extraction/", "runtime/search_quality/", "surfaces/", "site/", "native/", "crates/", "examples/", ".aide.local/", ".local/", ".cache/", "secrets/")


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--skip-commands", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    result = validate(Path(args.repo_root).resolve(), run_commands=not args.skip_commands)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print("R0 final closeout validation", file=stdout)
        print(f"status: {result['status']}", file=stdout)
        for error in result["errors"]:
            print(f"ERROR: {error}", file=stdout)
        for warning in result["warnings"]:
            print(f"WARN: {warning}", file=stdout)
    return 0 if result["status"] == "pass" else 1


def validate(root: Path = REPO_ROOT, *, run_commands: bool = True) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    inventories = validate_inventories(root, errors)
    validate_audit_pack(root, errors)
    validate_decisions(inventories, errors)
    validate_blockers_and_warnings(inventories, errors)
    validate_future_standard(root, errors)
    validate_no_forbidden_changes(root, errors)
    command_results: list[dict[str, Any]] = []
    if run_commands:
        command_results.extend(run_r0_validators(root, errors, warnings))
        command_results.append(run_command(root, [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-t", "."], "python -m unittest discover -s tests -t .", errors, warnings, allow_warning=False))
        command_results.append(run_command(root, [sys.executable, "scripts/check_architecture_boundaries.py"], "python scripts/check_architecture_boundaries.py", errors, warnings, allow_warning=False))
    return {
        "schema_version": "r0_final_closeout_validation.v0",
        "task": "R0-11",
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "warnings": warnings,
        "command_results": command_results,
        "site_dist_mutated": False,
        "master_index_mutated": False,
        "network_used": False,
        "model_provider_used": False,
    }


def validate_inventories(root: Path, errors: list[str]) -> dict[str, Any]:
    loaded: dict[str, Any] = {}
    for rel, schema in INVENTORIES.items():
        path = root / rel
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            errors.append(f"missing inventory: {rel}")
            continue
        except json.JSONDecodeError as exc:
            errors.append(f"invalid inventory JSON {rel}: {exc}")
            continue
        loaded[path.stem] = payload
        if payload.get("schema_version") != schema:
            errors.append(f"unexpected schema_version for {rel}")
    return loaded


def validate_audit_pack(root: Path, errors: list[str]) -> None:
    for rel in AUDIT_FILES:
        if not (root / AUDIT_PACK / rel).exists():
            errors.append(f"missing audit pack file: {(AUDIT_PACK / rel).as_posix()}")
    report = read_json(root / AUDIT_PACK / "r0_11_report.json") or {}
    if report.get("schema_version") != "r0_11_report.v0":
        errors.append("R0-11 report schema mismatch")
    if report.get("branch_mutation_performed") is not False:
        errors.append("R0-11 report must not record branch mutation")


def validate_decisions(inventories: Mapping[str, Any], errors: list[str]) -> None:
    closeout = inventories.get("r0_final_closeout_result", {})
    decision = inventories.get("r0_final_next_task_decision", {})
    branch = inventories.get("r0_final_branch_state", {})
    if closeout.get("f0_decision") not in {"resume_f0", "remain_blocked", "remediation_required"}:
        errors.append("F0 decision is not explicit")
    if closeout.get("main_promotion_decision") not in {"promote_ready", "promotion_plan_only", "remain_blocked", "already_on_main"}:
        errors.append("branch promotion decision is not explicit")
    if closeout.get("production_readiness_claimed") is not False or decision.get("production_readiness_claimed") is not False:
        errors.append("production readiness must not be claimed")
    if closeout.get("public_launch_readiness_claimed") is not False or decision.get("public_launch_readiness_claimed") is not False:
        errors.append("public launch readiness must not be claimed")
    if closeout.get("branch_mutation_performed") is not False or branch.get("branch_mutation_performed") is not False:
        errors.append("branch mutation must be false")


def validate_blockers_and_warnings(inventories: Mapping[str, Any], errors: list[str]) -> None:
    blockers = inventories.get("r0_final_blocker_register", {}).get("blockers", [])
    child_ids = {item.get("task_id") for item in inventories.get("r0_child_remediation_tasks", {}).get("tasks", [])}
    for blocker in blockers:
        if not blocker.get("fixed_in_r0_11") and not blocker.get("child_task"):
            errors.append(f"blocker is neither fixed nor child-tasked: {blocker.get('blocker_id')}")
        if blocker.get("child_task") and blocker.get("child_task") not in child_ids:
            errors.append(f"blocker child task missing: {blocker.get('blocker_id')}")
    for warning in inventories.get("r0_final_warning_disposition", {}).get("warnings", []):
        if warning.get("disposition") not in {"harmless", "fixed", "child_task_created", "blocks_f0", "blocks_promotion", "not_evaluable"}:
            errors.append(f"warning disposition invalid: {warning.get('warning_id')}")


def validate_future_standard(root: Path, errors: list[str]) -> None:
    path = root / "docs/operations/FUTURE_TASK_COMPLETION_STANDARD.md"
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        errors.append("future task completion standard is missing")
        return
    required = [
        "A task is not complete merely because contracts, policies, examples, validators, or audit reports exist.",
        "runtime code",
        "tests",
        "explicit command output",
        "persistent state where applicable",
        "audit evidence",
        "no forbidden side effects",
    ]
    for phrase in required:
        if phrase not in text:
            errors.append(f"future task completion standard missing phrase: {phrase}")


def validate_no_forbidden_changes(root: Path, errors: list[str]) -> None:
    completed = subprocess.run(["git", "status", "--porcelain=v1"], cwd=root, text=True, capture_output=True, check=False)
    if completed.returncode != 0:
        return
    for line in completed.stdout.splitlines():
        if len(line) < 4:
            continue
        raw = line[3:].replace("\\", "/").strip('"')
        for path in raw.split(" -> "):
            if path.startswith(FORBIDDEN_CHANGED_ROOTS):
                errors.append(f"forbidden path changed: {path}")
            if path.startswith("site/dist/"):
                errors.append(f"site/dist path changed: {path}")


def run_r0_validators(root: Path, errors: list[str], warnings: list[str]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for rel in R0_VALIDATORS:
        results.append(run_command(root, [sys.executable, rel], f"python {rel}", errors, warnings, allow_warning=True))
    return results


def run_command(root: Path, args: list[str], label: str, errors: list[str], warnings: list[str], *, allow_warning: bool) -> dict[str, Any]:
    completed = subprocess.run(args, cwd=root, text=True, capture_output=True, check=False)
    text = completed.stdout + completed.stderr
    status = "pass" if completed.returncode == 0 else "fail"
    if completed.returncode != 0:
        errors.append(f"command failed: {label}")
    elif allow_warning and ("warning" in text.lower() or "valid_with_warnings" in text.lower() or "pass_with_warnings" in text.lower()):
        status = "pass_with_warnings"
        warnings.append(f"command has warnings: {label}")
    return {"command": label, "status": status}


def read_json(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


if __name__ == "__main__":
    raise SystemExit(main())
