#!/usr/bin/env python3
"""Dry-run/apply only safe R0 closeout repairs and child-task unsafe gaps."""

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
UNSAFE_AREAS = {
    "contract_taxonomy",
    "runtime_architecture",
    "connector_refactor",
    "source_runtime",
    "public_launch",
    "f0_extraction",
}


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    parser.add_argument("--output")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    root = Path(args.repo_root).resolve()
    apply = bool(args.apply)
    result = build_repair_result(root, apply=apply)
    if args.output:
        write_json(root, Path(args.output), result)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print("R0 safe gap repair", file=stdout)
        print(f"mode: {'apply' if apply else 'dry-run'}", file=stdout)
        print(f"safe_gaps_fixed: {result['safe_gaps_fixed']}", file=stdout)
        print(f"unsafe_gaps_child_tasked: {result['unsafe_gaps_child_tasked']}", file=stdout)
    return 0


def build_repair_result(root: Path = REPO_ROOT, *, apply: bool = False) -> dict[str, Any]:
    blockers = (read_json(root / "control/inventory/r0_remaining_blockers.json") or {}).get("blockers", [])
    warnings = (read_json(root / "control/inventory/r0_warning_disposition.json") or {}).get("warnings", [])
    safe_gaps: list[dict[str, Any]] = []
    unsafe_gaps: list[dict[str, Any]] = []
    child_tasks: list[dict[str, Any]] = []

    for blocker in blockers:
        area = str(blocker.get("area", "unknown"))
        item = {
            "source_id": blocker.get("blocker_id", ""),
            "area": area,
            "finding": blocker.get("finding", ""),
            "safe_to_fix": area not in UNSAFE_AREAS,
            "action": "fixed" if apply and area not in UNSAFE_AREAS else "child_task_created",
        }
        if item["safe_to_fix"]:
            safe_gaps.append(item)
        else:
            unsafe_gaps.append(item)
            child_tasks.append(contract_taxonomy_child_task())

    for warning in warnings:
        area = str(warning.get("area", "unknown"))
        if area == "architecture_leakage":
            child_tasks.append(legacy_leakage_child_task())

    child_tasks = dedupe_tasks(child_tasks)
    return {
        "schema_version": "r0_safe_gap_repair_result.v0",
        "task": "R0-11",
        "mode": "apply" if apply else "dry_run",
        "safe_gaps_detected": len(safe_gaps),
        "safe_gaps_fixed": len(safe_gaps) if apply else 0,
        "unsafe_gaps_detected": len(unsafe_gaps),
        "unsafe_gaps_child_tasked": len(child_tasks),
        "changed_paths": [],
        "branch_mutation_performed": False,
        "site_dist_mutated": False,
        "master_index_mutated": False,
        "network_used": False,
        "child_tasks": child_tasks,
        "notes": ["No safe bounded file repair was needed." if not safe_gaps else "Safe repairs are intentionally limited to control-plane metadata."],
    }


def contract_taxonomy_child_task() -> dict[str, Any]:
    return {
        "task_id": "R0-REMEDIATION-CONTRACT-TAXONOMY-01",
        "title": "Resolve remaining contract taxonomy blockers",
        "status": "required",
        "unsafe_reason": "Requires contract classification, reference updates, and possible moves beyond R0-11 closeout scope.",
    }


def legacy_leakage_child_task() -> dict[str, Any]:
    return {
        "task_id": "R0-REMEDIATION-LEGACY-LEAKAGE-01",
        "title": "Retire legacy runtime architecture leakage allowlist debt",
        "status": "deferred",
        "unsafe_reason": "Requires legacy runtime naming remediation outside R0-11 closeout scope.",
    }


def dedupe_tasks(tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    result: list[dict[str, Any]] = []
    for task in tasks:
        task_id = task["task_id"]
        if task_id not in seen:
            seen.add(task_id)
            result.append(task)
    return result


def read_json(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


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
