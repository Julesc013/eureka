#!/usr/bin/env python3
"""Validate DEV-TO-MAIN-MERGE-R0 promotion evidence."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[2]
TASK_ID = "DEV-TO-MAIN-MERGE-R0"
F0_TASK = "F0-BUNDLE-01 \u2014 Deep extraction source-family and extraction-boundary policy packs"

INVENTORIES = {
    "control/inventory/dev_to_main_r0_git_state.json": "dev_to_main_r0_git_state.v0",
    "control/inventory/dev_to_main_r0_validation_result.json": "dev_to_main_r0_validation_result.v0",
    "control/inventory/dev_to_main_r0_merge_result.json": "dev_to_main_r0_merge_result.v0",
    "control/inventory/dev_to_main_r0_next_task_decision.json": "dev_to_main_r0_next_task_decision.v0",
}

AUDIT_PACK = Path("control/audits/dev-to-main-merge-r0-v0")
AUDIT_FILES = (
    "README.md",
    "merge_report.json",
    "git_state.md",
    "validation.md",
    "promotion_result.md",
    "f0_start_decision.md",
    "generated/sample_merge_result.json",
    "generated/sample_git_state.json",
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
    "secrets/",
    ".aide.local/",
    ".local/",
    ".cache/",
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--skip-git", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    result = validate(Path(args.repo_root).resolve(), check_git=not args.skip_git)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print("DEV-TO-MAIN-MERGE-R0 validation", file=stdout)
        print(f"status: {result['status']}", file=stdout)
        for error in result["errors"]:
            print(f"ERROR: {error}", file=stdout)
        for warning in result["warnings"]:
            print(f"WARN: {warning}", file=stdout)
    return 0 if result["status"] == "pass" else 1


def validate(root: Path = REPO_ROOT, *, check_git: bool = True) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    inventories = validate_inventories(root, errors)
    validate_audit_pack(root, inventories, errors)
    validate_decisions(inventories, errors)
    validate_boundaries(inventories, errors)
    if check_git:
        validate_git_state(root, inventories, errors)
    return {
        "schema_version": "dev_to_main_r0_merge_validation.v0",
        "task": TASK_ID,
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "warnings": warnings,
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
        if payload.get("task") != TASK_ID:
            errors.append(f"unexpected task for {rel}")
    return loaded


def validate_audit_pack(root: Path, inventories: Mapping[str, Any], errors: list[str]) -> None:
    for rel in AUDIT_FILES:
        if not (root / AUDIT_PACK / rel).exists():
            errors.append(f"missing audit pack file: {(AUDIT_PACK / rel).as_posix()}")
    report = read_json(root / AUDIT_PACK / "merge_report.json") or {}
    if report.get("schema_version") != "dev_to_main_r0_merge_report.v0":
        errors.append("merge_report schema mismatch")
    merge = inventories.get("dev_to_main_r0_merge_result", {})
    for key in (
        "status",
        "merge_performed",
        "merge_method",
        "push_main_performed",
        "force_push_performed",
        "history_rewrite_performed",
        "deployment_performed",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
        "recommended_next_task",
    ):
        if report.get(key) != merge.get(key):
            errors.append(f"merge_report mismatch: {key}")


def validate_decisions(inventories: Mapping[str, Any], errors: list[str]) -> None:
    git_state = inventories.get("dev_to_main_r0_git_state", {})
    validation = inventories.get("dev_to_main_r0_validation_result", {})
    merge = inventories.get("dev_to_main_r0_merge_result", {})
    next_task = inventories.get("dev_to_main_r0_next_task_decision", {})
    if merge.get("status") not in {"pass", "pass_with_warnings"}:
        errors.append("merge status is not passing")
    if merge.get("merge_performed") is not True:
        errors.append("merge_performed must be true")
    if merge.get("merge_method") != "fast_forward":
        errors.append("merge_method must be fast_forward")
    if merge.get("push_main_performed") is not True:
        errors.append("push_main_performed must be true")
    if git_state.get("origin_main_equals_origin_dev_after") is not True:
        errors.append("origin main/dev equality is not recorded")
    if git_state.get("working_tree_clean_after") is not True:
        errors.append("working tree clean after merge is not recorded")
    for key in (
        "full_unittest_discovery_pass",
        "generated_artifact_cleanliness_pass",
        "architecture_boundary_checks_pass",
        "r0_validators_pass",
    ):
        if validation.get(key) is not True:
            errors.append(f"validation gate failed: {key}")
    if validation.get("blockers"):
        errors.append("validation blockers remain")
    if next_task.get("recommended_next_task") != F0_TASK:
        errors.append("F0 next task is not explicit")
    if next_task.get("recommended_start_branch") != "main":
        errors.append("recommended_start_branch must be main")
    if next_task.get("f0_can_resume") is not True:
        errors.append("f0_can_resume must be true")


def validate_boundaries(inventories: Mapping[str, Any], errors: list[str]) -> None:
    merge = inventories.get("dev_to_main_r0_merge_result", {})
    next_task = inventories.get("dev_to_main_r0_next_task_decision", {})
    report = inventories.get("dev_to_main_r0_validation_result", {})
    if merge.get("force_push_performed") is not False:
        errors.append("force_push_performed must be false")
    if merge.get("history_rewrite_performed") is not False:
        errors.append("history_rewrite_performed must be false")
    if merge.get("deployment_performed") is not False:
        errors.append("deployment_performed must be false")
    for payload_name, payload in (("merge_result", merge), ("next_task", next_task), ("validation_result", report)):
        if payload.get("production_readiness_claimed") is True:
            errors.append(f"{payload_name} claims production readiness")
        if payload.get("public_launch_readiness_claimed") is True:
            errors.append(f"{payload_name} claims public launch readiness")


def validate_git_state(root: Path, inventories: Mapping[str, Any], errors: list[str]) -> None:
    status_lines = git_lines(root, "status", "--porcelain=v1")
    for path in parse_status_paths(status_lines):
        if path == ".env" or path.startswith(FORBIDDEN_CHANGED_ROOTS):
            errors.append(f"forbidden path changed: {path}")
        if path.startswith("site/dist/"):
            errors.append(f"site/dist path changed: {path}")
    if status_lines:
        errors.append("working tree is not clean")
    merge = inventories.get("dev_to_main_r0_merge_result", {})
    if merge.get("merge_performed") is True:
        origin_main = git_value(root, "rev-parse", "origin/main")
        origin_dev = git_value(root, "rev-parse", "origin/dev")
        if not origin_main or origin_main != origin_dev:
            errors.append("origin/main and origin/dev are not equal after merge")


def read_json(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def git_value(root: Path, *args: str) -> str:
    completed = subprocess.run(["git", *args], cwd=root, text=True, capture_output=True, check=False)
    return completed.stdout.strip() if completed.returncode == 0 else ""


def git_lines(root: Path, *args: str) -> list[str]:
    value = git_value(root, *args)
    return [line for line in value.splitlines() if line]


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
