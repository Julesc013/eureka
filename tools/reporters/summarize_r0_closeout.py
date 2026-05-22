#!/usr/bin/env python3
"""Summarize the final R0 closeout inventory."""

from __future__ import annotations

import argparse
import json
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


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--output")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    root = Path(args.repo_root).resolve()
    summary = build_summary(root)
    if args.output:
        write_text(root, Path(args.output), render_markdown(summary))
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True), file=stdout)
    else:
        print(render_text(summary), file=stdout)
    return 0


def build_summary(root: Path = REPO_ROOT) -> dict[str, Any]:
    closeout = read_json(root / "control/inventory/r0_final_closeout_result.json") or {}
    blockers = read_json(root / "control/inventory/r0_final_blocker_register.json") or {"blockers": []}
    decision = read_json(root / "control/inventory/r0_final_next_task_decision.json") or {}
    return {
        "schema_version": "r0_closeout_summary.v0",
        "task": "R0-11",
        "status": closeout.get("status", "missing"),
        "current_branch": closeout.get("current_branch", ""),
        "blockers_remaining": closeout.get("blockers_remaining", len(blockers.get("blockers", []))),
        "f0_decision": closeout.get("f0_decision", ""),
        "main_promotion_decision": closeout.get("main_promotion_decision", ""),
        "recommended_next_task": decision.get("recommended_next_task", closeout.get("recommended_next_task", "")),
    }


def render_text(summary: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "R0 final closeout summary",
            f"status: {summary['status']}",
            f"current_branch: {summary['current_branch']}",
            f"blockers_remaining: {summary['blockers_remaining']}",
            f"f0_decision: {summary['f0_decision']}",
            f"main_promotion_decision: {summary['main_promotion_decision']}",
            f"recommended_next_task: {summary['recommended_next_task']}",
        ]
    )


def render_markdown(summary: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "# R0 Final Closeout Summary",
            "",
            f"- status: {summary['status']}",
            f"- current_branch: {summary['current_branch']}",
            f"- blockers_remaining: {summary['blockers_remaining']}",
            f"- f0_decision: {summary['f0_decision']}",
            f"- main_promotion_decision: {summary['main_promotion_decision']}",
            f"- recommended_next_task: {summary['recommended_next_task']}",
            "",
        ]
    )


def read_json(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def write_text(root: Path, target: Path, text: str) -> None:
    path = resolve_output(root, target)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


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
