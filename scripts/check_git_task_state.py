#!/usr/bin/env python3
"""Check local Git task state before Codex/AIDE sync workflows."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Sequence


SCHEMA_VERSION = "git_task_state_guard.v0"
MODES = ("start-task", "finish-task", "merge-task", "rescue")
TASK_PREFIXES = ("task/", "obs/", "track-b/", "sync/", "hotfix/")
SECRET_LIKE_PATTERNS = (
    ".env",
    ".aide.local",
    ".local/eureka",
    ".cache/eureka",
    "secrets",
    "credentials",
    "credential",
    "token",
    "private_key",
    "private-key",
    "id_rsa",
    "api_key",
    "apikey",
)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Non-mutating Git task-state guard for Eureka Codex/AIDE workflows."
    )
    parser.add_argument("--mode", choices=MODES, default="start-task")
    parser.add_argument("--task-id", default="", help="Expected task identifier.")
    parser.add_argument("--json", action="store_true", help="Emit deterministic JSON.")
    parser.add_argument("--fail-on-warn", action="store_true")
    parser.add_argument("--allow-main", action="store_true")
    parser.add_argument("--allow-no-upstream", action="store_true")
    parser.add_argument("--expected-origin-main", default="")
    args = parser.parse_args(argv)

    report = build_report(
        cwd=Path.cwd(),
        mode=args.mode,
        task_id=args.task_id,
        allow_main=args.allow_main,
        allow_no_upstream=args.allow_no_upstream,
        expected_origin_main=args.expected_origin_main,
    )

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(format_report(report))

    if report["status"] == "FAIL":
        return 1
    if args.fail_on_warn and report["status"] == "WARN":
        return 1
    return 0


def build_report(
    *,
    cwd: Path,
    mode: str,
    task_id: str,
    allow_main: bool,
    allow_no_upstream: bool,
    expected_origin_main: str,
) -> dict[str, Any]:
    checks: list[dict[str, str]] = []
    git_root = _git_output(cwd, "rev-parse", "--show-toplevel")
    if git_root.returncode != 0:
        checks.append(_check("git_repository", "FAIL", "current directory is not a Git repository"))
        return _final_report(cwd, mode, task_id, "", "", None, None, checks)

    root = Path(git_root.stdout.strip())
    branch = _git_value(root, "branch", "--show-current")
    head = _git_value(root, "rev-parse", "HEAD")
    status_lines = _git_lines(root, "status", "--porcelain=v1")
    status_paths = _status_paths(status_lines)
    untracked_paths = _untracked_paths(status_lines)

    merge_state = _git_path_exists(root, "MERGE_HEAD")
    rebase_state = _git_path_exists(root, "rebase-merge") or _git_path_exists(root, "rebase-apply")
    cherry_pick_state = _git_path_exists(root, "CHERRY_PICK_HEAD")
    revert_state = _git_path_exists(root, "REVERT_HEAD")

    checks.append(_clean_working_tree_check(mode, status_lines))
    checks.append(_state_check("no_merge_state", merge_state, mode, "active merge metadata exists"))
    checks.append(_state_check("no_rebase_state", rebase_state, mode, "active rebase metadata exists"))
    checks.append(
        _state_check(
            "no_cherry_pick_state",
            cherry_pick_state,
            mode,
            "active cherry-pick metadata exists",
        )
    )
    checks.append(_state_check("no_revert_state", revert_state, mode, "active revert metadata exists"))
    checks.append(_branch_not_main_check(branch, mode, allow_main))

    origin_main = _optional_ref(root, "origin/main")
    main_ref = _optional_ref(root, "main")
    checks.extend(_local_main_checks(root, mode, main_ref, origin_main))
    checks.append(_expected_origin_main_check(origin_main, expected_origin_main))

    upstream = _upstream(root)
    upstream_counts = _ahead_behind(root, "HEAD", "@{upstream}") if upstream else None
    checks.extend(
        _upstream_checks(
            branch=branch,
            mode=mode,
            upstream=upstream,
            upstream_counts=upstream_counts,
            allow_no_upstream=allow_no_upstream,
        )
    )

    checks.append(_branch_task_id_check(branch, task_id))
    checks.extend(_private_path_checks(status_paths, untracked_paths))

    return _final_report(
        root,
        mode,
        task_id,
        branch,
        head,
        origin_main,
        upstream,
        checks,
        upstream_counts=upstream_counts,
    )


def format_report(report: dict[str, Any]) -> str:
    lines = [
        "Git Task State Guard",
        f"status: {report['status']}",
        f"mode: {report['mode']}",
        f"task_id: {report['task_id'] or '<none>'}",
        f"branch: {report['branch'] or '<detached-or-unknown>'}",
        f"head: {report['head'] or '<unknown>'}",
        f"origin_main: {report['origin_main'] or '<unavailable>'}",
        f"upstream: {report['upstream'] or '<none>'}",
        "checks:",
    ]
    for check in report["checks"]:
        lines.append(f"- {check['status']}: {check['check']} - {check['message']}")
    return "\n".join(lines)


def _final_report(
    root: Path,
    mode: str,
    task_id: str,
    branch: str,
    head: str,
    origin_main: str | None,
    upstream: str | None,
    checks: list[dict[str, str]],
    *,
    upstream_counts: dict[str, int] | None = None,
) -> dict[str, Any]:
    status = "PASS"
    if any(check["status"] == "FAIL" for check in checks):
        status = "FAIL"
    elif any(check["status"] == "WARN" for check in checks):
        status = "WARN"
    return {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "mode": mode,
        "task_id": task_id,
        "repo_root": str(root),
        "branch": branch,
        "head": head,
        "origin_main": origin_main,
        "upstream": upstream,
        "upstream_ahead_behind": upstream_counts,
        "checks": sorted(checks, key=lambda item: item["check"]),
        "mutated_repo": False,
    }


def _clean_working_tree_check(mode: str, status_lines: list[str]) -> dict[str, str]:
    if not status_lines:
        return _check("clean_working_tree", "PASS", "working tree is clean")
    message = f"working tree has {len(status_lines)} changed path(s)"
    return _check("clean_working_tree", "WARN" if mode == "rescue" else "FAIL", message)


def _state_check(check_id: str, present: bool, mode: str, message: str) -> dict[str, str]:
    if not present:
        return _check(check_id, "PASS", "not present")
    return _check(check_id, "WARN" if mode == "rescue" else "FAIL", message)


def _branch_not_main_check(branch: str, mode: str, allow_main: bool) -> dict[str, str]:
    if branch != "main":
        return _check("current_branch_not_main_for_task_work", "PASS", "current branch is not main")
    if mode in ("merge-task", "rescue"):
        return _check(
            "current_branch_not_main_for_task_work",
            "PASS",
            f"main is allowed for {mode} mode",
        )
    if allow_main:
        return _check(
            "current_branch_not_main_for_task_work",
            "WARN",
            "main allowed by explicit override",
        )
    return _check(
        "current_branch_not_main_for_task_work",
        "FAIL",
        "normal task work must not run directly on main",
    )


def _local_main_checks(
    root: Path,
    mode: str,
    main_ref: str | None,
    origin_main: str | None,
) -> list[dict[str, str]]:
    if not main_ref or not origin_main:
        return [
            _check(
                "local_main_fast_forwardable_or_current_with_origin_main",
                "WARN",
                "main or origin/main is unavailable",
            ),
            _check("no_unpushed_main_work", "WARN", "main or origin/main is unavailable"),
        ]
    counts = _ahead_behind(root, "main", "origin/main")
    if counts is None:
        return [
            _check(
                "local_main_fast_forwardable_or_current_with_origin_main",
                "WARN",
                "could not compare main and origin/main",
            ),
            _check("no_unpushed_main_work", "WARN", "could not compare main and origin/main"),
        ]
    ahead = counts["left"]
    behind = counts["right"]
    checks: list[dict[str, str]] = []
    if behind:
        checks.append(
            _check(
                "local_main_fast_forwardable_or_current_with_origin_main",
                "WARN" if mode == "rescue" else "FAIL",
                f"local main is behind origin/main by {behind} commit(s)",
            )
        )
    else:
        checks.append(
            _check(
                "local_main_fast_forwardable_or_current_with_origin_main",
                "PASS",
                "local main is current with origin/main",
            )
        )
    if ahead:
        status = "WARN" if mode == "rescue" else "FAIL"
        checks.append(
            _check(
                "no_unpushed_main_work",
                status,
                f"main has {ahead} local-only commit(s); push origin main before continuing",
            )
        )
    else:
        checks.append(_check("no_unpushed_main_work", "PASS", "main has no local-only commits"))
    return checks


def _expected_origin_main_check(origin_main: str | None, expected: str) -> dict[str, str]:
    if not expected:
        return _check("origin_main_not_unexpectedly_advanced", "PASS", "no expected origin/main provided")
    if origin_main == expected:
        return _check("origin_main_not_unexpectedly_advanced", "PASS", "origin/main matches expected SHA")
    return _check(
        "origin_main_not_unexpectedly_advanced",
        "WARN",
        f"origin/main is {origin_main or '<unavailable>'}, expected {expected}",
    )


def _upstream_checks(
    *,
    branch: str,
    mode: str,
    upstream: str | None,
    upstream_counts: dict[str, int] | None,
    allow_no_upstream: bool,
) -> list[dict[str, str]]:
    if not branch:
        return [_check("task_branch_upstream_status", "WARN", "detached or unknown branch")]
    if branch == "main":
        return [_check("task_branch_upstream_status", "PASS", "main branch upstream is not a task-branch gate")]
    if not upstream:
        status = "PASS" if allow_no_upstream else "WARN"
        return [
            _check(
                "task_branch_upstream_status",
                status,
                "branch has no upstream; first push should set one",
            ),
            _check("task_branch_not_behind_upstream", "PASS", "no upstream to be behind"),
        ]
    if upstream_counts is None:
        return [
            _check("task_branch_upstream_status", "WARN", f"upstream is {upstream}"),
            _check("task_branch_not_behind_upstream", "WARN", "could not compare upstream"),
        ]
    ahead = upstream_counts["left"]
    behind = upstream_counts["right"]
    checks = [_check("task_branch_upstream_status", "PASS", f"upstream is {upstream}")]
    if behind:
        checks.append(
            _check("task_branch_not_behind_upstream", "FAIL", f"branch is behind upstream by {behind} commit(s)")
        )
    else:
        checks.append(_check("task_branch_not_behind_upstream", "PASS", "branch is not behind upstream"))
    if ahead and mode in ("finish-task", "start-task"):
        checks.append(_check("unpushed_task_branch_work", "WARN", f"branch is ahead of upstream by {ahead} commit(s)"))
    elif ahead:
        checks.append(_check("unpushed_task_branch_work", "PASS", f"branch is ahead of upstream by {ahead} commit(s)"))
    else:
        checks.append(_check("unpushed_task_branch_work", "PASS", "branch has no local-only upstream commits"))
    return checks


def _branch_task_id_check(branch: str, task_id: str) -> dict[str, str]:
    if not task_id or branch == "main":
        return _check("task_id_branch_name_match", "PASS", "task ID branch match not required")
    normalized = _normalize_task_id(task_id)
    lowered = branch.lower()
    if lowered.startswith(TASK_PREFIXES) and normalized in lowered:
        return _check("task_id_branch_name_match", "PASS", "branch name includes task ID")
    return _check("task_id_branch_name_match", "WARN", "branch name does not include task ID")


def _private_path_checks(paths: list[str], untracked_paths: list[str]) -> list[dict[str, str]]:
    risky = sorted({path for path in paths if _is_secret_like(path)})
    untracked_risky = sorted({path for path in untracked_paths if _is_secret_like(path)})
    return [
        _check(
            "no_forbidden_private_paths",
            "FAIL" if risky else "PASS",
            "secret-like/private paths detected: " + ", ".join(risky) if risky else "no secret-like/private changed paths",
        ),
        _check(
            "no_untracked_secret_like_paths",
            "FAIL" if untracked_risky else "PASS",
            "untracked secret-like paths detected: " + ", ".join(untracked_risky) if untracked_risky else "no untracked secret-like paths",
        ),
    ]


def _is_secret_like(path: str) -> bool:
    normalized = path.replace("\\", "/").lower()
    return any(pattern in normalized for pattern in SECRET_LIKE_PATTERNS)


def _normalize_task_id(task_id: str) -> str:
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", task_id.lower())).strip("-")


def _status_paths(status_lines: list[str]) -> list[str]:
    paths: list[str] = []
    for line in status_lines:
        if len(line) < 4:
            continue
        path = line[3:]
        if " -> " in path:
            paths.extend(path.split(" -> ", 1))
        else:
            paths.append(path)
    return [path.strip('"') for path in paths]


def _untracked_paths(status_lines: list[str]) -> list[str]:
    return [line[3:].strip('"') for line in status_lines if line.startswith("?? ")]


def _upstream(root: Path) -> str | None:
    completed = _git_output(root, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}")
    if completed.returncode != 0:
        return None
    return completed.stdout.strip() or None


def _optional_ref(root: Path, ref: str) -> str | None:
    completed = _git_output(root, "rev-parse", "--verify", ref)
    if completed.returncode != 0:
        return None
    return completed.stdout.strip()


def _ahead_behind(root: Path, left: str, right: str) -> dict[str, int] | None:
    completed = _git_output(root, "rev-list", "--left-right", "--count", f"{left}...{right}")
    if completed.returncode != 0:
        return None
    parts = completed.stdout.strip().split()
    if len(parts) != 2:
        return None
    return {"left": int(parts[0]), "right": int(parts[1])}


def _git_path_exists(root: Path, name: str) -> bool:
    completed = _git_output(root, "rev-parse", "--git-path", name)
    if completed.returncode != 0:
        return False
    return (root / completed.stdout.strip()).exists()


def _git_value(root: Path, *args: str) -> str:
    completed = _git_output(root, *args)
    return completed.stdout.strip() if completed.returncode == 0 else ""


def _git_lines(root: Path, *args: str) -> list[str]:
    completed = _git_output(root, *args)
    if completed.returncode != 0:
        return []
    return [line for line in completed.stdout.splitlines() if line]


def _git_output(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )


def _check(check_id: str, status: str, message: str) -> dict[str, str]:
    return {"check": check_id, "status": status, "message": message}


if __name__ == "__main__":
    sys.exit(main())
