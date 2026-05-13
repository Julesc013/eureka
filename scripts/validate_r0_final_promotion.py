#!/usr/bin/env python3
"""Validate R0 final promotion review inventories and audit pack."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.audit_r0_final_promotion import find_forbidden_claims

TASK_ID = "R0-FINAL-PROMOTION-REVIEW"

INVENTORIES = {
    "control/inventory/r0_final_promotion_review_result.json": "r0_final_promotion_review_result.v0",
    "control/inventory/r0_final_promotion_readiness_matrix.json": "r0_final_promotion_readiness_matrix.v0",
    "control/inventory/r0_final_promotion_blockers.json": "r0_final_promotion_blockers.v0",
    "control/inventory/r0_final_promotion_warning_disposition.json": "r0_final_promotion_warning_disposition.v0",
    "control/inventory/r0_final_promotion_git_state.json": "r0_final_promotion_git_state.v0",
    "control/inventory/r0_final_promotion_next_task_decision.json": "r0_final_promotion_next_task_decision.v0",
}

AUDIT_PACK = Path("control/audits/r0-final-promotion-review-v0")
AUDIT_FILES = (
    "README.md",
    "promotion_review_report.json",
    "git_state.md",
    "readiness_matrix.md",
    "blocker_report.md",
    "warning_disposition.md",
    "merge_plan.md",
    "f0_start_policy.md",
    "validation.md",
    "generated/sample_promotion_review_result.json",
    "generated/sample_git_state.json",
    "generated/sample_merge_plan.json",
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
    "secrets/",
    ".aide.local/",
    ".local/",
    ".cache/",
)

DECISIONS = {"promote_ready", "promotion_plan_only", "remain_blocked", "already_on_main"}
F0_DECISIONS = {"resume_f0", "remain_blocked", "remediation_required"}
WARNING_CLASSIFICATIONS = {"harmless_for_promotion", "blocks_promotion", "blocks_f0", "child_task_created", "deferred_with_expiry"}


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    result = validate(Path(args.repo_root).resolve())
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print("R0 final promotion validation", file=stdout)
        print(f"status: {result['status']}", file=stdout)
        for error in result["errors"]:
            print(f"ERROR: {error}", file=stdout)
        for warning in result["warnings"]:
            print(f"WARN: {warning}", file=stdout)
    return 0 if result["status"] == "pass" else 1


def validate(root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    inventories = validate_inventories(root, errors)
    validate_audit_pack(root, inventories, errors)
    validate_decisions(inventories, errors)
    validate_branch_mutation(inventories, root, errors)
    validate_scope(root, errors)
    validate_claims(root, inventories, errors)
    validate_f0_next_task(inventories, errors)
    return {
        "schema_version": "r0_final_promotion_validation.v0",
        "task": TASK_ID,
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "warnings": warnings,
        "product_paths_changed": any(error.startswith("forbidden path changed") for error in errors),
        "site_dist_mutated": any("site/dist" in error for error in errors),
        "branch_mutation_performed": inventories.get("r0_final_promotion_review_result", {}).get("branch_mutation_performed"),
        "production_readiness_claimed": inventories.get("r0_final_promotion_review_result", {}).get("production_readiness_claimed"),
        "public_launch_readiness_claimed": inventories.get("r0_final_promotion_review_result", {}).get("public_launch_readiness_claimed"),
    }


def validate_inventories(root: Path, errors: list[str]) -> dict[str, Any]:
    loaded: dict[str, Any] = {}
    for rel, schema in INVENTORIES.items():
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
        if payload.get("schema_version") != schema:
            errors.append(f"unexpected schema_version for {rel}")
    return loaded


def validate_audit_pack(root: Path, inventories: Mapping[str, Any], errors: list[str]) -> None:
    for rel in AUDIT_FILES:
        if not (root / AUDIT_PACK / rel).exists():
            errors.append(f"missing audit pack file: {(AUDIT_PACK / rel).as_posix()}")
    report = read_json(root / AUDIT_PACK / "promotion_review_report.json") or {}
    if report.get("schema_version") != "r0_final_promotion_review_report.v0":
        errors.append("promotion review report schema mismatch")
    result = inventories.get("r0_final_promotion_review_result", {})
    for key in (
        "status",
        "current_branch",
        "dev_to_main_decision",
        "f0_decision",
        "branch_mutation_performed",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    ):
        if report.get(key) != result.get(key):
            errors.append(f"promotion review report mismatch: {key}")


def validate_decisions(inventories: Mapping[str, Any], errors: list[str]) -> None:
    result = inventories.get("r0_final_promotion_review_result", {})
    matrix = inventories.get("r0_final_promotion_readiness_matrix", {})
    blockers = inventories.get("r0_final_promotion_blockers", {})
    warning_disposition = inventories.get("r0_final_promotion_warning_disposition", {})
    if result.get("dev_to_main_decision") not in DECISIONS:
        errors.append("dev-to-main decision is not explicit")
    if result.get("f0_decision") not in F0_DECISIONS:
        errors.append("F0 decision is not explicit")
    if result.get("hard_blockers_remaining") != blockers.get("hard_blocker_count"):
        errors.append("hard blocker count mismatch")
    if result.get("warnings_fully_disposed") is not True:
        errors.append("warnings are not fully disposed")
    for warning in warning_disposition.get("warnings", []):
        if warning.get("classification") not in WARNING_CLASSIFICATIONS:
            errors.append(f"invalid warning classification: {warning.get('warning_id')}")
        if warning.get("classification") == "deferred_with_expiry" and not warning.get("expiry"):
            errors.append(f"deferred warning missing expiry: {warning.get('warning_id')}")
    if result.get("dev_to_main_decision") == "promotion_plan_only" and matrix.get("promotion_ready") is not True:
        errors.append("promotion_plan_only requires promotion_ready true")
    for key in (
        "full_unittest_discovery_pass",
        "generated_artifact_cleanliness_pass",
        "architecture_boundary_checks_pass",
        "r0_validators_pass",
    ):
        if result.get(key) is not True:
            errors.append(f"required gate did not pass: {key}")


def validate_branch_mutation(inventories: Mapping[str, Any], root: Path, errors: list[str]) -> None:
    result = inventories.get("r0_final_promotion_review_result", {})
    git_state = inventories.get("r0_final_promotion_git_state", {})
    report = read_json(root / AUDIT_PACK / "promotion_review_report.json") or {}
    apply_evidence = root / "control/inventory/r0_final_promotion_apply_evidence.json"
    if result.get("branch_mutation_performed") is not False or git_state.get("branch_mutation_performed") is not False or report.get("branch_mutation_performed") is not False:
        if not apply_evidence.exists():
            errors.append("branch_mutation_performed is true without apply evidence")
    if result.get("merge_performed") is not False:
        errors.append("merge_performed must be false for review-only output")
    if result.get("push_main_performed") is not False:
        errors.append("push_main_performed must be false for review-only output")


def validate_scope(root: Path, errors: list[str]) -> None:
    completed = subprocess.run(["git", "status", "--porcelain=v1"], cwd=root, text=True, capture_output=True, check=False)
    if completed.returncode != 0:
        return
    for raw in parse_status_paths(completed.stdout.splitlines()):
        if raw == ".env" or raw.startswith(FORBIDDEN_CHANGED_ROOTS):
            errors.append(f"forbidden path changed: {raw}")
        if raw.startswith("site/dist/"):
            errors.append(f"site/dist path changed: {raw}")


def validate_claims(root: Path, inventories: Mapping[str, Any], errors: list[str]) -> None:
    result = inventories.get("r0_final_promotion_review_result", {})
    decision = inventories.get("r0_final_promotion_next_task_decision", {})
    for key in ("production_readiness_claimed", "public_launch_readiness_claimed"):
        if result.get(key) is not False:
            errors.append(f"promotion result overclaims {key}")
        if decision.get(key) is not False:
            errors.append(f"next-task decision overclaims {key}")
    claims = find_forbidden_claims(root)
    if claims:
        errors.extend(f"forbidden claim detected: {item['claim']} in {item['path']}:{item.get('line', 0)}" for item in claims)


def validate_f0_next_task(inventories: Mapping[str, Any], errors: list[str]) -> None:
    decision = inventories.get("r0_final_promotion_next_task_decision", {})
    if decision.get("f0_decision") not in F0_DECISIONS:
        errors.append("next-task F0 decision is not explicit")
    if decision.get("recommended_start_branch") not in {"dev", "main"}:
        errors.append("F0 recommended_start_branch is not explicit")
    if not decision.get("recommended_next_task"):
        errors.append("recommended_next_task is missing")
    if decision.get("f0_must_use_r0_runtime_seams") is not True:
        errors.append("F0 runtime seam requirement is missing")
    if decision.get("f0_must_not_reintroduce_scaffold_only_completion") is not True:
        errors.append("F0 scaffold-only guard is missing")


def read_json(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


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


if __name__ == "__main__":
    raise SystemExit(main())
