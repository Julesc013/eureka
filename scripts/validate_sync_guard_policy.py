#!/usr/bin/env python3
"""Validate SYNC-GUARD-01 policy, docs, prompts, and guard script."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]

POLICY_FILES = [
    "control/inventory/git/sync_guard_policy.json",
    "control/inventory/git/task_branch_policy.json",
    "control/inventory/git/sync_workflow_commands.json",
]

DOC_FILES = [
    "docs/operations/MULTI_MACHINE_GIT_WORKFLOW.md",
    "docs/operations/AIDE_SYNC_GUARD.md",
    "docs/operations/AIDE_SYNC_RECOVERY_COMMANDS.md",
]

PROMPT_FILES = [
    ".aide/prompts/AIDE-SYNC-01.md",
    ".aide/prompts/AIDE-MERGE-01.md",
    ".aide/prompts/AIDE-RESCUE-01.md",
]

AUDIT_FILES = [
    "control/audits/sync-guard-01-multi-machine-git-guard-v0/README.md",
    "control/audits/sync-guard-01-multi-machine-git-guard-v0/sync_guard_01_report.json",
    "control/audits/sync-guard-01-multi-machine-git-guard-v0/validation.md",
    "control/audits/sync-guard-01-multi-machine-git-guard-v0/workflow_summary.md",
]

REQUIRED_CHECKS = [
    "clean_working_tree",
    "no_merge_state",
    "no_rebase_state",
    "no_cherry_pick_state",
    "no_revert_state",
    "current_branch_not_main_for_task_work",
    "local_main_fast_forwardable_or_current_with_origin_main",
    "task_branch_upstream_status",
    "task_branch_not_behind_upstream",
    "no_unpushed_main_work",
    "origin_main_not_unexpectedly_advanced",
    "no_forbidden_private_paths",
    "no_untracked_secret_like_paths",
]

REQUIRED_FAIL_SNIPPETS = [
    "dirty working tree",
    "active merge",
    "active rebase",
    "active cherry-pick",
    "active revert",
    "local main behind origin/main when starting task work",
    "current branch is main for normal task work",
    "unpushed commits on main",
    "secret-like paths staged or untracked",
    "branch behind upstream",
]

REQUIRED_WARN_SNIPPETS = [
    "task branch has no upstream before first push",
    "branch name does not include the task ID",
    "AIDE queue stale relative to git log",
    "origin/main advanced since task packet generation",
]

REQUIRED_FORBIDDEN = [
    "git push --force",
    "git reset --hard",
    "git clean -fd",
    "git stash pop",
    "git branch -D",
    "git rebase shared branches",
]

DESTRUCTIVE_DOC_COMMANDS = [
    "git push --force",
    "git reset --hard",
    "git clean -fd",
    "git clean -fdx",
    "git stash pop",
    "git branch -D",
]


def main() -> int:
    errors: list[str] = []
    errors.extend(_validate_required_files(POLICY_FILES + DOC_FILES + PROMPT_FILES + AUDIT_FILES))
    errors.extend(_validate_json_files(POLICY_FILES + ["control/audits/sync-guard-01-multi-machine-git-guard-v0/sync_guard_01_report.json"]))
    if not errors:
        errors.extend(_validate_policy_contents())
    errors.extend(_validate_script_exists())
    errors.extend(_validate_docs_do_not_advise_destructive_commands())

    if errors:
        for error in sorted(dict.fromkeys(errors)):
            print(f"FAIL: {error}")
        return 1
    print("PASS: sync guard policy artifacts validate")
    return 0


def _validate_required_files(paths: list[str]) -> list[str]:
    return [f"missing required file: {path}" for path in paths if not (REPO_ROOT / path).is_file()]


def _validate_json_files(paths: list[str]) -> list[str]:
    errors: list[str] = []
    for path in paths:
        file_path = REPO_ROOT / path
        if not file_path.is_file():
            continue
        try:
            json.loads(file_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"invalid JSON {path}: {exc}")
    return errors


def _validate_policy_contents() -> list[str]:
    errors: list[str] = []
    sync_policy = _load_json("control/inventory/git/sync_guard_policy.json")
    branch_policy = _load_json("control/inventory/git/task_branch_policy.json")
    workflow = _load_json("control/inventory/git/sync_workflow_commands.json")

    for required in REQUIRED_CHECKS:
        if required not in sync_policy.get("checks", []):
            errors.append(f"sync guard policy missing check: {required}")
    for required in REQUIRED_FAIL_SNIPPETS:
        if required not in sync_policy.get("fail_conditions", []):
            errors.append(f"sync guard policy missing fail condition: {required}")
    for required in REQUIRED_WARN_SNIPPETS:
        if required not in sync_policy.get("warn_conditions", []):
            errors.append(f"sync guard policy missing warn condition: {required}")
    for required in REQUIRED_FORBIDDEN:
        if required not in sync_policy.get("forbidden_operations", []):
            errors.append(f"sync guard policy missing forbidden operation: {required}")

    product_boundary = sync_policy.get("product_boundary", {})
    for field, value in product_boundary.items():
        if value is not False:
            errors.append(f"product_boundary.{field} must be false")

    if branch_policy.get("normal_task_work_on_main_allowed") is not False:
        errors.append("task branch policy must forbid normal task work on main")
    for workflow_name in ("start_task", "finish_task", "push_task_branch", "merge_task_branch", "rescue_dirty_tree"):
        if workflow_name not in branch_policy.get("required_standard_workflows", []):
            errors.append(f"task branch policy missing workflow: {workflow_name}")

    command_ids = [command.get("command_id") for command in workflow.get("commands", [])]
    for command_id in ("AIDE-SYNC-01", "AIDE-MERGE-01", "AIDE-RESCUE-01"):
        if command_id not in command_ids:
            errors.append(f"workflow command inventory missing: {command_id}")
    for command in workflow.get("commands", []):
        forbidden = command.get("forbidden_commands", [])
        for required in ("git push --force", "git reset --hard", "git clean -fd", "git stash pop"):
            if required not in forbidden:
                errors.append(f"{command.get('command_id')} missing forbidden command: {required}")
    return errors


def _validate_script_exists() -> list[str]:
    script = REPO_ROOT / "scripts" / "check_git_task_state.py"
    validator = REPO_ROOT / "scripts" / "validate_sync_guard_policy.py"
    errors: list[str] = []
    if not script.is_file():
        errors.append("missing guard script: scripts/check_git_task_state.py")
    if not validator.is_file():
        errors.append("missing validator script: scripts/validate_sync_guard_policy.py")
    return errors


def _validate_docs_do_not_advise_destructive_commands() -> list[str]:
    errors: list[str] = []
    for path in DOC_FILES + PROMPT_FILES:
        file_path = REPO_ROOT / path
        if not file_path.is_file():
            continue
        text = file_path.read_text(encoding="utf-8")
        for command in DESTRUCTIVE_DOC_COMMANDS:
            if command in text:
                errors.append(f"{path} contains destructive command literal: {command}")
    return errors


def _load_json(path: str) -> dict[str, Any]:
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


if __name__ == "__main__":
    sys.exit(main())
