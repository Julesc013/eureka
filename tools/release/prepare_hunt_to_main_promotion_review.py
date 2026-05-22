#!/usr/bin/env python3
"""Prepare a plan-only review for promoting the HUNT dev baseline to main."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--closeout-result", default="control/inventory/search_hunt_closeout_result.json")
    parser.add_argument("--output")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    root = Path(args.repo_root).resolve()
    result = prepare_review(root, args.closeout_result)
    if args.output:
        write_json(Path(args.output), result)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print(f"promotion_recommended: {str(result['promotion_recommended']).lower()}", file=stdout)
        print("branch_mutation_performed: false", file=stdout)
    return 0 if result["status"] in {"pass", "pass_with_warnings"} else 1


def prepare_review(root: Path = REPO_ROOT, closeout_rel: str = "control/inventory/search_hunt_closeout_result.json") -> dict[str, Any]:
    closeout = load_json(root / closeout_rel)
    branch = git(root, "branch", "--show-current")
    ahead = git(root, "rev-list", "--left-right", "--count", "origin/main...origin/dev")
    try:
        main_only, dev_only = [int(part) for part in ahead.split()]
    except ValueError:
        main_only, dev_only = 0, 0
    ready = closeout.get("hunt_track_complete") is True and int(closeout.get("hard_blockers_remaining", 0) or 0) == 0
    promotion_recommended = ready and dev_only > 0
    return {
        "schema_version": "search_hunt_promotion_review.v0",
        "task": "HUNT-12",
        "status": "pass_with_warnings" if closeout.get("warnings_remaining", 0) else "pass",
        "current_branch": branch,
        "hunt_track_ready_for_main_promotion": ready,
        "dev_ahead_of_main": dev_only > 0,
        "origin_main_only_commits": main_only,
        "origin_dev_only_commits": dev_only,
        "promotion_recommended": promotion_recommended,
        "promotion_task": "HUNT-TO-MAIN-PROMOTION-REVIEW",
        "branch_mutation_performed": False,
        "merge_performed": False,
        "push_performed": False,
        "no_deployment": True,
        "no_production_readiness_claim": True,
        "no_public_launch_readiness_claim": True,
        "limitations": [
            "plan only; no merge or push",
            "main promotion still requires explicit operator task",
        ],
    }


def git(root: Path, *args: str) -> str:
    completed = subprocess.run(["git", *args], cwd=root, text=True, capture_output=True, check=False, timeout=60)
    return completed.stdout.strip()


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
