#!/usr/bin/env python3
"""Prepare a read-only dev-to-main promotion plan for R0-10."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[2]
FORBIDDEN_OUTPUT_ROOTS = {
    ".git",
    ".env",
    "runtime",
    "contracts",
    "surfaces",
    "site",
    "native",
    "crates",
    "examples",
    "secrets",
    ".aide.local",
    ".local",
    ".cache",
}
REVIEW_RESULT = Path("control/inventory/r0_production_review_result.json")


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--output")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    root = Path(args.repo_root).resolve()
    plan = build_promotion_plan(root)
    if args.apply:
        plan["required_checks"].append(
            {
                "check_id": "apply_disabled",
                "status": "blocked",
                "evidence": [],
                "notes": ["R0-10 is plan-only; branch mutation requires a later explicit operator action."],
            }
        )
        plan["ready"] = False
        plan["branch_mutation_performed"] = False
    if args.output:
        write_json(root, Path(args.output), plan)
    if args.json:
        print(json.dumps(plan, indent=2, sort_keys=True), file=stdout)
    else:
        print("Dev-to-main promotion plan", file=stdout)
        print(f"ready: {str(plan['ready']).lower()}", file=stdout)
        print("branch_mutation_performed: false", file=stdout)
    return 1 if args.apply else 0


def build_promotion_plan(root: Path = REPO_ROOT) -> dict[str, Any]:
    branch = git_value(root, "branch", "--show-current") or ""
    status_lines = git_lines(root, "status", "--porcelain=v1")
    source_branch = "dev"
    target_branch = "main"
    current_is_dev = branch == source_branch
    clean = not status_lines
    main_ref = bool(git_value(root, "rev-parse", "--verify", target_branch))
    dev_contains_main = _contains(root, source_branch, target_branch) if main_ref else False
    upstream = git_value(root, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}") or ""
    upstream_counts = _ahead_behind(root, "HEAD", "@{upstream}") if upstream else None
    review = read_review_result(root)
    review_ready = bool(review and review.get("dev_can_promote_to_main") is True)

    checks = [
        check("current_branch_dev", current_is_dev, [f"branch={branch or '<unknown>'}"]),
        check("working_tree_clean", clean, status_lines),
        check("main_ref_available", main_ref, [target_branch]),
        check("dev_contains_main", dev_contains_main, [f"{source_branch} contains {target_branch}"]),
        check("r0_review_promotes", review_ready, [str(REVIEW_RESULT)]),
        {
            "check_id": "branch_mutation_default",
            "status": "pass",
            "evidence": [],
            "notes": ["Default mode is promotion-plan-only and performs no merge."],
        },
    ]
    if upstream_counts and upstream_counts["left"]:
        checks.append(
            {
                "check_id": "unpushed_dev_commits",
                "status": "warn",
                "evidence": [f"ahead={upstream_counts['left']}", f"upstream={upstream}"],
                "notes": ["Operator must push dev before any remote promotion review."],
            }
        )

    ready = all(item["status"] == "pass" for item in checks if item["check_id"] != "branch_mutation_default")
    if any(item["status"] in {"fail", "blocked"} for item in checks):
        ready = False
    return {
        "schema_version": "dev_to_main_promotion_plan.v0",
        "task": "R0-10",
        "promotion_plan_only": True,
        "branch_mutation_performed": False,
        "source_branch": source_branch,
        "target_branch": target_branch,
        "ready": ready,
        "required_checks": checks,
        "promotion_steps": [
            "Confirm R0 production review has no blockers.",
            "Push dev after operator approval.",
            "Open a dev-to-main review with validation evidence attached.",
            "Merge to main only after explicit human approval.",
        ],
        "rollback_plan": [
            "Do not rewrite main history.",
            "If promotion is approved and later reverted, use a normal revert commit on main.",
            "Keep R0 audit evidence attached to the revert decision.",
        ],
        "risks": [
            "R0-10 found remaining contract taxonomy blockers." if not review_ready else "Promotion still does not imply public launch readiness.",
            "Local dev is ahead of origin/dev." if upstream_counts and upstream_counts["left"] else "Remote branch state should be rechecked by the operator.",
        ],
        "operator_action_required": True,
    }


def read_review_result(root: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads((root / REVIEW_RESULT).read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def check(check_id: str, passed: bool, evidence: list[str]) -> dict[str, Any]:
    return {
        "check_id": check_id,
        "status": "pass" if passed else "fail",
        "evidence": evidence,
        "notes": [],
    }


def git_value(root: Path, *args: str) -> str:
    completed = subprocess.run(["git", *args], cwd=root, text=True, capture_output=True, check=False)
    return completed.stdout.strip() if completed.returncode == 0 else ""


def git_lines(root: Path, *args: str) -> list[str]:
    value = git_value(root, *args)
    return [line for line in value.splitlines() if line]


def _ahead_behind(root: Path, left: str, right: str) -> dict[str, int] | None:
    value = git_value(root, "rev-list", "--left-right", "--count", f"{left}...{right}")
    parts = value.split()
    if len(parts) != 2:
        return None
    return {"left": int(parts[0]), "right": int(parts[1])}


def _contains(root: Path, left: str, right: str) -> bool:
    completed = subprocess.run(["git", "merge-base", "--is-ancestor", right, left], cwd=root, check=False)
    return completed.returncode == 0


def write_json(root: Path, target: Path, payload: Mapping[str, Any]) -> None:
    path = resolve_output(root, target)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def resolve_output(root: Path, target: Path) -> Path:
    path = target if target.is_absolute() else root / target
    resolved = path.resolve()
    try:
        relative = resolved.relative_to(root.resolve()).as_posix()
    except ValueError:
        return resolved
    first = relative.split("/", 1)[0]
    if first in FORBIDDEN_OUTPUT_ROOTS or relative == ".env":
        raise SystemExit(f"refusing forbidden output root: {relative}")
    return resolved


if __name__ == "__main__":
    raise SystemExit(main())
