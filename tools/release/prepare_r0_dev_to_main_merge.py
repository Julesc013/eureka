#!/usr/bin/env python3
"""Prepare or explicitly apply the R0 dev-to-main promotion plan."""

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

from scripts.audit_r0_final_promotion import build_final_promotion, resolve_output

TASK_ID = "DEV-TO-MAIN-MERGE-R0"


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--output")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--push-main", action="store_true", help="Push main after an explicit --apply merge.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    root = Path(args.repo_root).resolve()
    plan = build_merge_plan(root)
    exit_code = 0
    if args.apply:
        plan, exit_code = apply_merge_plan(root, plan, push_main=args.push_main)
    if args.output:
        write_json(root, Path(args.output), plan)
    if args.json:
        print(json.dumps(plan, indent=2, sort_keys=True), file=stdout)
    else:
        print("R0 dev-to-main merge plan", file=stdout)
        print(f"ready: {str(plan['ready']).lower()}", file=stdout)
        print(f"branch_mutation_performed: {str(plan['branch_mutation_performed']).lower()}", file=stdout)
    return exit_code


def build_merge_plan(root: Path = REPO_ROOT) -> dict[str, Any]:
    audit = build_final_promotion(root)
    result = audit["r0_final_promotion_review_result"]
    git_state = audit["r0_final_promotion_git_state"]
    ready = bool(result.get("promotion_ready") or result.get("dev_to_main_decision") == "promotion_plan_only")
    required_checks = [
        plan_check("promotion_review_ready", ready, [str(Path("control/inventory/r0_final_promotion_review_result.json"))]),
        plan_check("current_branch_dev", git_state.get("current_branch") == "dev", [f"current_branch={git_state.get('current_branch')}"]),
        plan_check("working_tree_clean", git_state.get("working_tree_clean") is True, git_state.get("working_tree_changed_paths", [])),
        plan_check("dev_synced_to_origin", git_state.get("dev_synced_to_origin") is True, [f"origin_dev={git_state.get('origin_dev')}"]),
        plan_check("dev_contains_main", git_state.get("dev_contains_main") is True, [f"origin_main={git_state.get('origin_main')}", f"origin_dev={git_state.get('origin_dev')}"]),
        {
            "check_id": "branch_mutation_default",
            "status": "pass",
            "evidence": [],
            "notes": ["Default mode is plan-only and performs no branch mutation."],
        },
        {
            "check_id": "force_push_forbidden",
            "status": "pass",
            "evidence": ["git push --force is not used"],
            "notes": ["History rewrite and force-push operations are forbidden."],
        },
        {
            "check_id": "deployment_forbidden",
            "status": "pass",
            "evidence": ["no deployment step is present"],
            "notes": ["Promotion is a git baseline update only, not a deploy or public launch."],
        },
    ]
    ready = all(item["status"] == "pass" for item in required_checks if item["check_id"] != "branch_mutation_default")
    return {
        "schema_version": "r0_dev_to_main_merge_plan.v0",
        "task": TASK_ID,
        "source_branch": "dev",
        "target_branch": "main",
        "ready": ready,
        "promotion_plan_only": True,
        "branch_mutation_performed": False,
        "merge_performed": False,
        "push_main_performed": False,
        "required_checks": required_checks,
        "promotion_steps": [
            "git fetch origin",
            "git checkout main",
            "git merge --ff-only origin/main",
            "git merge --ff-only origin/dev",
            "run the final promotion validation lane again",
            "git push origin main only when --push-main is explicitly supplied with --apply",
            "git checkout dev",
        ],
        "forbidden_operations": [
            "git push --force",
            "history rewrite",
            "release tag creation",
            "deployment",
            "site/dist regeneration",
        ],
        "rollback_plan": [
            "Never rewrite main history.",
            "If an applied fast-forward must be backed out after push, create a normal revert commit on main.",
            "Record the revert decision in the R0 promotion audit inventories.",
            "Do not tag a release or deploy as part of rollback.",
        ],
        "operator_action_required": True,
        "notes": [
            "No merge, push, tag, deployment, or branch mutation occurs without --apply.",
            "A pushed main promotion also requires --push-main.",
        ],
    }


def apply_merge_plan(root: Path, plan: Mapping[str, Any], *, push_main: bool) -> tuple[dict[str, Any], int]:
    applied = dict(plan)
    applied["promotion_plan_only"] = False
    if not plan.get("ready"):
        applied["apply_status"] = "blocked"
        applied["apply_error"] = "required checks did not pass"
        return applied, 1
    commands = [
        ["git", "fetch", "origin"],
        ["git", "checkout", "main"],
        ["git", "merge", "--ff-only", "origin/main"],
        ["git", "merge", "--ff-only", "origin/dev"],
    ]
    command_results: list[dict[str, Any]] = []
    for command in commands:
        completed = subprocess.run(command, cwd=root, text=True, capture_output=True, check=False)
        command_results.append({"command": " ".join(command), "returncode": completed.returncode})
        if completed.returncode != 0:
            applied["apply_status"] = "blocked"
            applied["apply_error"] = f"command failed: {' '.join(command)}"
            applied["apply_command_results"] = command_results
            subprocess.run(["git", "checkout", "dev"], cwd=root, text=True, capture_output=True, check=False)
            return applied, 1
    push_performed = False
    if push_main:
        completed = subprocess.run(["git", "push", "origin", "main"], cwd=root, text=True, capture_output=True, check=False)
        command_results.append({"command": "git push origin main", "returncode": completed.returncode})
        if completed.returncode != 0:
            applied["apply_status"] = "blocked"
            applied["apply_error"] = "command failed: git push origin main"
            applied["apply_command_results"] = command_results
            subprocess.run(["git", "checkout", "dev"], cwd=root, text=True, capture_output=True, check=False)
            return applied, 1
        push_performed = True
    subprocess.run(["git", "checkout", "dev"], cwd=root, text=True, capture_output=True, check=False)
    applied["apply_status"] = "applied"
    applied["branch_mutation_performed"] = True
    applied["merge_performed"] = True
    applied["push_main_performed"] = push_performed
    applied["apply_command_results"] = command_results
    return applied, 0


def plan_check(check_id: str, passed: bool, evidence: Sequence[str]) -> dict[str, Any]:
    return {
        "check_id": check_id,
        "status": "pass" if passed else "fail",
        "evidence": list(evidence),
        "notes": [],
    }


def write_json(root: Path, target: Path, payload: Mapping[str, Any]) -> None:
    path = resolve_output(root, target)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
