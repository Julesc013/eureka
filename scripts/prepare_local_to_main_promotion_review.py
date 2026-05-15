#!/usr/bin/env python3
"""Prepare a plan-only LOCAL-to-main promotion review."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_ROOT = Path(__file__).resolve().parent
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))

from audit_local_appliance_closeout import build_closeout_records, write_json


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--output")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    root = Path(args.repo_root).resolve()
    payload = build_promotion_plan(root)
    if args.output:
        write_json(Path(args.output), payload)
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True), file=stdout)
    else:
        print("LOCAL-to-main promotion review", file=stdout)
        print(f"promotion_recommended: {payload['promotion_recommended']}", file=stdout)
    return 0


def build_promotion_plan(root: Path) -> dict[str, Any]:
    records = build_closeout_records(root)
    promotion = dict(records["promotion_review"])
    branch = run_git(root, "branch", "--show-current")
    dev_counts = run_git(root, "rev-list", "--left-right", "--count", "origin/main...origin/dev").split()
    current_counts = run_git(root, "rev-list", "--left-right", "--count", "origin/main...HEAD").split()
    promotion.update(
        {
            "schema_version": "local_appliance_promotion_review.v0",
            "current_branch": branch,
            "origin_main_to_origin_dev_count": parse_count(dev_counts),
            "origin_main_to_current_count": parse_count(current_counts),
            "promotion_review_required": True,
            "merge_performed": False,
            "push_performed": False,
            "deployment_performed": False,
            "next_step": "LOCAL-TO-MAIN-PROMOTION-REVIEW",
        }
    )
    return promotion


def parse_count(parts: list[str]) -> dict[str, int]:
    if len(parts) != 2:
        return {"left": 0, "right": 0}
    return {"left": int(parts[0]), "right": int(parts[1])}


def run_git(root: Path, *args: str) -> str:
    completed = subprocess.run(["git", *args], cwd=root, text=True, capture_output=True, check=False)
    return completed.stdout.strip()


if __name__ == "__main__":
    raise SystemExit(main())
