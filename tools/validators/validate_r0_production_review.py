#!/usr/bin/env python3
"""Validate R0-10 production review evidence."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.audit_r0_production_review import build_r0_production_review

INVENTORIES = (
    "control/inventory/r0_production_review_result.json",
    "control/inventory/r0_promotion_readiness_matrix.json",
    "control/inventory/r0_remaining_blockers.json",
    "control/inventory/r0_warning_disposition.json",
    "control/inventory/r0_next_phase_decision.json",
    "control/inventory/dev_to_main_promotion_plan.json",
)
AUDIT_PACK = Path("control/audits/r0-10-dev-to-main-production-review-v0")
AUDIT_FILES = (
    "README.md",
    "r0_10_report.json",
    "production_review.md",
    "promotion_readiness_matrix.md",
    "remaining_blockers.md",
    "warning_disposition.md",
    "f0_resumption_decision.md",
    "dev_to_main_promotion_plan.md",
    "validation.md",
    "generated/sample_production_review_result.json",
    "generated/sample_promotion_readiness_matrix.json",
    "generated/sample_next_phase_decision.json",
    "generated/sample_summary.md",
)
PRODUCT_ROOTS = ("runtime/", "contracts/", "surfaces/", "site/", "native/", "crates/", "examples/")
HIDDEN_ROOTS = (".aide.local/", ".local/", ".cache/", "secrets/")
VALIDATORS = (
    "scripts/validate_one_source_live_test.py",
    "scripts/validate_reviewed_public_index.py",
    "scripts/validate_review_queue_store.py",
    "scripts/validate_evidence_ledger_store.py",
    "scripts/validate_source_cache_store.py",
    "scripts/validate_source_observation_seam.py",
    "scripts/validate_runtime_architecture_leakage.py",
    "scripts/validate_product_contract_tree.py",
    "scripts/validate_contract_taxonomy_migration.py",
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--skip-r0-validators", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    result = validate(Path(args.repo_root).resolve(), run_r0_validators=not args.skip_r0_validators)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print("R0 production review validation", file=stdout)
        print(f"status: {result['status']}", file=stdout)
        for error in result["errors"]:
            print(f"ERROR: {error}", file=stdout)
        for warning in result["warnings"]:
            print(f"WARN: {warning}", file=stdout)
    return 0 if result["status"] == "pass" else 1


def validate(root: Path = REPO_ROOT, *, run_r0_validators: bool = True) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    inventories = validate_inventories(root, errors)
    validate_audit_pack(root, errors)
    validate_decisions(inventories, errors)
    validate_no_forbidden_changes(root, errors)
    validate_no_overclaim(inventories, errors)
    validator_results = run_validators(root, warnings, errors) if run_r0_validators else []
    status = "pass" if not errors else "fail"
    return {
        "schema_version": "r0_production_review_validation.v0",
        "task": "R0-10",
        "status": status,
        "errors": errors,
        "warnings": warnings,
        "validator_results": validator_results,
        "product_paths_changed": False if not any(error.startswith("product path changed") for error in errors) else True,
        "site_dist_mutated": False,
        "hidden_local_state_roots_changed": False if not any(error.startswith("hidden/local path changed") for error in errors) else True,
        "network_used": False,
        "model_provider_used": False,
    }


def validate_inventories(root: Path, errors: list[str]) -> dict[str, Any]:
    loaded: dict[str, Any] = {}
    expected_schemas = {
        "r0_production_review_result": "r0_production_review_result.v0",
        "r0_promotion_readiness_matrix": "r0_promotion_readiness_matrix.v0",
        "r0_remaining_blockers": "r0_remaining_blockers.v0",
        "r0_warning_disposition": "r0_warning_disposition.v0",
        "r0_next_phase_decision": "r0_next_phase_decision.v0",
        "dev_to_main_promotion_plan": "dev_to_main_promotion_plan.v0",
    }
    for rel in INVENTORIES:
        path = root / rel
        key = path.stem
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            errors.append(f"missing inventory: {rel}")
            continue
        except json.JSONDecodeError as exc:
            errors.append(f"invalid inventory JSON {rel}: {exc}")
            continue
        loaded[key] = payload
        if payload.get("schema_version") != expected_schemas[key]:
            errors.append(f"unexpected schema_version for {rel}")
    return loaded


def validate_audit_pack(root: Path, errors: list[str]) -> None:
    for rel in AUDIT_FILES:
        path = root / AUDIT_PACK / rel
        if not path.exists():
            errors.append(f"missing audit pack file: {(AUDIT_PACK / rel).as_posix()}")
    report_path = root / AUDIT_PACK / "r0_10_report.json"
    try:
        report = json.loads(report_path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return
    if report.get("schema_version") != "r0_10_report.v0":
        errors.append("R0-10 report schema_version mismatch")
    if report.get("branch_mutation_performed") is not False:
        errors.append("R0-10 report must not record branch mutation")


def validate_decisions(inventories: Mapping[str, Any], errors: list[str]) -> None:
    review = inventories.get("r0_production_review_result", {})
    decision = inventories.get("r0_next_phase_decision", {})
    plan = inventories.get("dev_to_main_promotion_plan", {})
    if review.get("f0_can_resume") not in {True, False}:
        errors.append("F0 decision is not explicit in production review")
    if review.get("dev_can_promote_to_main") not in {True, False}:
        errors.append("dev-to-main decision is not explicit in production review")
    if decision.get("f0_decision") not in {"resume_f0", "remain_blocked", "remediation_required"}:
        errors.append("next phase F0 decision is invalid")
    if decision.get("main_promotion_decision") not in {"promote_ready", "promotion_plan_only", "remain_blocked"}:
        errors.append("main promotion decision is invalid")
    if plan.get("promotion_plan_only") is not True:
        errors.append("promotion plan must be plan-only")
    if plan.get("branch_mutation_performed") is not False:
        errors.append("promotion plan must not mutate branches")
    for warning in inventories.get("r0_warning_disposition", {}).get("warnings", []):
        if warning.get("disposition") not in {"harmless", "assigned_to_next_task", "blocks_promotion", "fixed", "not_evaluable"}:
            errors.append(f"warning has invalid disposition: {warning.get('warning_id')}")


def validate_no_forbidden_changes(root: Path, errors: list[str]) -> None:
    completed = subprocess.run(["git", "status", "--porcelain=v1"], cwd=root, text=True, capture_output=True, check=False)
    if completed.returncode != 0:
        return
    for line in completed.stdout.splitlines():
        if len(line) < 4:
            continue
        path = line[3:].replace("\\", "/")
        if " -> " in path:
            paths = [part.strip('"') for part in path.split(" -> ", 1)]
        else:
            paths = [path.strip('"')]
        for item in paths:
            if item.startswith(PRODUCT_ROOTS):
                errors.append(f"product path changed in R0-10: {item}")
            if item.startswith(HIDDEN_ROOTS):
                errors.append(f"hidden/local path changed in R0-10: {item}")
            if item.startswith("site/dist/"):
                errors.append(f"site/dist path changed in R0-10: {item}")


def validate_no_overclaim(inventories: Mapping[str, Any], errors: list[str]) -> None:
    review = inventories.get("r0_production_review_result", {})
    decision = inventories.get("r0_next_phase_decision", {})
    for key in ("production_readiness_claimed", "public_launch_readiness_claimed"):
        if review.get(key) is not False:
            errors.append(f"production review overclaims {key}")
        if decision.get(key) is not False:
            errors.append(f"next phase decision overclaims {key}")


def run_validators(root: Path, warnings: list[str], errors: list[str]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for rel in VALIDATORS:
        path = root / rel
        if not path.exists():
            warnings.append(f"validator missing: {rel}")
            results.append({"command": f"python {rel}", "status": "missing"})
            continue
        completed = subprocess.run([sys.executable, rel], cwd=root, text=True, capture_output=True, check=False)
        status = "pass" if completed.returncode == 0 else "fail"
        if completed.returncode != 0:
            errors.append(f"validator failed: {rel}")
        elif "warning" in (completed.stdout + completed.stderr).lower() or "valid_with_warnings" in completed.stdout.lower():
            status = "pass_with_warnings"
            warnings.append(f"validator has warnings: {rel}")
        results.append({"command": f"python {rel}", "status": status})
    return results


if __name__ == "__main__":
    raise SystemExit(main())
