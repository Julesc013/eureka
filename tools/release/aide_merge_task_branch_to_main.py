#!/usr/bin/env python3
"""Merge one work branch into an integration target and push the target."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_GUARD = REPO_ROOT / "scripts" / "check_git_task_state.py"


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--branch", help="Task branch to merge. Defaults to current branch.")
    parser.add_argument("--repo", default=".")
    parser.add_argument("--remote", default="origin")
    parser.add_argument("--main", dest="target_branch", default="main", help="Integration target branch. Defaults to main.")
    parser.add_argument("--target-branch", dest="target_branch", help="Alias for --main.")
    parser.add_argument("--guard-script", default=str(DEFAULT_GUARD))
    parser.add_argument("--execute", action="store_true", help="Actually fetch, merge, and push the integration target.")
    parser.add_argument(
        "--publish-branch",
        action="store_true",
        help="Push the task branch before merging when another machine needs it.",
    )
    parser.add_argument(
        "--delete-merged-branch",
        action="store_true",
        help="Safely delete the local task branch after its tip is contained in the pushed integration target.",
    )
    parser.add_argument(
        "--delete-remote-branch",
        action="store_true",
        help="Safely delete the remote task branch after its tip is contained in the pushed integration target. Implies --publish-branch.",
    )
    parser.add_argument("--json", action="store_true")
    parser.add_argument(
        "--validation-command",
        action="append",
        default=[],
        help="Validation command to run after merge and before pushing the integration target. Repeatable.",
    )
    args = parser.parse_args(argv)

    report = run_merge_workflow(
        repo=Path(args.repo),
        task_id=args.task_id,
        branch=args.branch,
        remote=args.remote,
        main_branch=args.target_branch,
        guard_script=Path(args.guard_script),
        execute=args.execute,
        publish_branch=args.publish_branch or args.delete_remote_branch,
        delete_merged_branch=args.delete_merged_branch,
        delete_remote_branch=args.delete_remote_branch,
        validation_commands=args.validation_command or ["git diff --check"],
    )
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True), file=stdout)
    else:
        print(format_report(report), file=stdout)
    return 0 if report["status"] == "pass" else 1


def run_merge_workflow(
    *,
    repo: Path,
    task_id: str,
    branch: str | None,
    remote: str,
    main_branch: str,
    guard_script: Path,
    execute: bool,
    publish_branch: bool,
    delete_merged_branch: bool,
    delete_remote_branch: bool,
    validation_commands: Sequence[str],
) -> dict[str, Any]:
    repo = repo.resolve()
    guard_script = guard_script.resolve()
    steps: list[dict[str, Any]] = []
    errors: list[str] = []

    current_branch = _git_value(repo, "branch", "--show-current")
    task_branch = branch or current_branch
    if not task_branch:
        errors.append("could not determine task branch")
    if task_branch == main_branch:
        errors.append("task branch must not be the integration target")
    if not _is_clean(repo):
        errors.append("working tree must be clean before merge workflow")
    if errors or not execute:
        return _report(
            repo,
            task_id,
            task_branch,
            remote,
            main_branch,
            execute,
            publish_branch,
            delete_merged_branch,
            delete_remote_branch,
            steps,
            errors,
        )

    def finish(label: str) -> dict[str, Any]:
        errors.append(f"{label} failed")
        return _report(
            repo,
            task_id,
            task_branch,
            remote,
            main_branch,
            execute,
            publish_branch,
            delete_merged_branch,
            delete_remote_branch,
            steps,
            errors,
        )

    def run_step(label: str, command: Sequence[str]) -> bool:
        result = _run(repo, command)
        steps.append(
            {
                "label": label,
                "command": list(command),
                "returncode": result.returncode,
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
            }
        )
        return result.returncode == 0

    if not run_step("fetch_origin", ["git", "fetch", remote, "--prune"]):
        return finish("fetch_origin")
    if not run_step(
        "finish_task_guard",
        [
            sys.executable,
            str(guard_script),
            "--mode",
            "finish-task",
            "--task-id",
            task_id,
            "--allow-no-upstream",
        ],
    ):
        return finish("finish_task_guard")

    merge_ref = task_branch
    if publish_branch:
        if not run_step("push_task_branch", ["git", "push", "-u", remote, task_branch]):
            return finish("push_task_branch")
        merge_ref = f"{remote}/{task_branch}"

    if not run_step("switch_integration_target", ["git", "switch", main_branch]):
        return finish("switch_integration_target")
    if not run_step("pull_integration_target_ff_only", ["git", "pull", "--ff-only", remote, main_branch]):
        return finish("pull_integration_target_ff_only")
    if not run_step(
        "pre_merge_guard",
        [
            sys.executable,
            str(guard_script),
            "--mode",
            "merge-task",
            "--task-id",
            task_id,
            "--allow-main",
            "--fail-on-warn",
        ],
    ):
        return finish("pre_merge_guard")
    if not run_step("merge_task_branch", ["git", "merge", "--no-ff", "--no-edit", merge_ref]):
        return finish("merge_task_branch")
    for index, command_text in enumerate(validation_commands, start=1):
        if not run_step(f"validation_{index}", _split_command(command_text)):
            return finish(f"validation_{index}")
    if not run_step("push_integration_target", ["git", "push", remote, main_branch]):
        return finish("push_integration_target")
    if not run_step("fetch_after_push", ["git", "fetch", remote, "--prune"]):
        return finish("fetch_after_push")
    if not run_step(
        "post_push_guard",
        [
            sys.executable,
            str(guard_script),
            "--mode",
            "merge-task",
            "--task-id",
            task_id,
            "--allow-main",
            "--fail-on-warn",
        ],
    ):
        return finish("post_push_guard")

    if delete_remote_branch:
        remote_ref = f"{remote}/{task_branch}"
        if not _is_ancestor(repo, remote_ref, f"{remote}/{main_branch}"):
            errors.append(f"remote task branch is not contained in {remote}/{main_branch}; refusing remote deletion")
            return _report(repo, task_id, task_branch, remote, main_branch, execute, publish_branch, delete_merged_branch, delete_remote_branch, steps, errors)
        if not run_step("delete_remote_task_branch", ["git", "push", remote, "--delete", task_branch]):
            return finish("delete_remote_task_branch")
        run_step("fetch_after_remote_branch_delete", ["git", "fetch", remote, "--prune"])

    if delete_merged_branch:
        if not _is_ancestor(repo, task_branch, f"{remote}/{main_branch}"):
            errors.append(f"local task branch is not contained in {remote}/{main_branch}; refusing local deletion")
            return _report(repo, task_id, task_branch, remote, main_branch, execute, publish_branch, delete_merged_branch, delete_remote_branch, steps, errors)
        if not run_step("delete_local_task_branch", ["git", "branch", "-d", task_branch]):
            return finish("delete_local_task_branch")

    return _report(
        repo,
        task_id,
        task_branch,
        remote,
        main_branch,
        execute,
        publish_branch,
        delete_merged_branch,
        delete_remote_branch,
        steps,
        errors,
    )


def format_report(report: dict[str, Any]) -> str:
    lines = [
        "AIDE merge task branch to integration target",
        f"status: {report['status']}",
        f"task_id: {report['task_id']}",
        f"task_branch: {report['task_branch']}",
        f"target_branch: {report['main_branch']}",
        f"execute: {report['execute']}",
        f"publish_branch: {report['publish_branch']}",
        f"delete_merged_branch: {report['delete_merged_branch']}",
        f"delete_remote_branch: {report['delete_remote_branch']}",
        f"final_target: {report['final_main'] or '<unknown>'}",
        f"origin_target: {report['origin_main'] or '<unknown>'}",
    ]
    for error in report["errors"]:
        lines.append(f"ERROR: {error}")
    for step in report["steps"]:
        lines.append(f"- {step['label']}: rc={step['returncode']} {' '.join(step['command'])}")
    if not report["execute"]:
        lines.append("dry_run: no fetch, push, branch switch, or merge was performed")
    return "\n".join(lines)


def _report(
    repo: Path,
    task_id: str,
    task_branch: str,
    remote: str,
    main_branch: str,
    execute: bool,
    publish_branch: bool,
    delete_merged_branch: bool,
    delete_remote_branch: bool,
    steps: list[dict[str, Any]],
    errors: list[str],
) -> dict[str, Any]:
    return {
        "schema_version": "aide_merge_task_branch_to_main.v0",
        "status": "pass" if not errors else "fail",
        "task_id": task_id,
        "task_branch": task_branch,
        "remote": remote,
        "main_branch": main_branch,
        "target_branch": main_branch,
        "execute": execute,
        "publish_branch": publish_branch,
        "delete_merged_branch": delete_merged_branch,
        "delete_remote_branch": delete_remote_branch,
        "steps": steps,
        "errors": errors,
        "final_branch": _git_value(repo, "branch", "--show-current"),
        "final_main": _optional_ref(repo, main_branch),
        "origin_main": _optional_ref(repo, f"{remote}/{main_branch}"),
        "final_target": _optional_ref(repo, main_branch),
        "origin_target": _optional_ref(repo, f"{remote}/{main_branch}"),
        "mutated_repo": execute,
        "force_push_used": False,
        "history_rewrite_used": False,
    }


def _split_command(command: str) -> list[str]:
    # The workflow only passes simple validation commands without quoting needs.
    return command.split()


def _is_clean(repo: Path) -> bool:
    return _git_value(repo, "status", "--porcelain=v1") == ""


def _optional_ref(repo: Path, ref: str) -> str | None:
    result = _run(repo, ["git", "rev-parse", "--verify", ref])
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def _is_ancestor(repo: Path, ancestor: str, descendant: str) -> bool:
    return _run(repo, ["git", "merge-base", "--is-ancestor", ancestor, descendant]).returncode == 0


def _git_value(repo: Path, *args: str) -> str:
    result = _run(repo, ["git", *args])
    return result.stdout.strip() if result.returncode == 0 else ""


def _run(repo: Path, command: Sequence[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=repo, text=True, capture_output=True, check=False)


if __name__ == "__main__":
    raise SystemExit(main())
