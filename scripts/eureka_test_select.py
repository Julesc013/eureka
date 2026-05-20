#!/usr/bin/env python3
"""Select Eureka test lanes from changed paths and the failure ledger."""

from __future__ import annotations

import argparse
import fnmatch
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Iterable, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = REPO_ROOT / "control/policies/test_lane_policy.json"
IMPACT_MAP_PATH = REPO_ROOT / "control/inventory/test_impact_map.json"
FAILURE_LEDGER_PATH = REPO_ROOT / "control/inventory/test_failure_ledger.json"

ACTIVE_FAILURE_STATUSES = {"new", "reproduced", "fixed_pending_full"}
BLOCKING_LEVELS = {"promotion_blocker", "release_blocker", "commit_blocker"}
FULL_DISCOVERY_COMMAND = "python -m unittest discover -s tests -t ."


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--changed", action="store_true", help="Select tests from unstaged/staged/untracked changed paths.")
    parser.add_argument("--since", help="Select tests from git diff --name-only <ref>...HEAD.")
    parser.add_argument("--task", help="Select tests mapped to a task id.")
    parser.add_argument("--failed-first", action="store_true", help="Prioritize active known failures before broad suites.")
    parser.add_argument("--promotion", action="store_true", help="Select promotion-grade lanes including full discovery.")
    parser.add_argument("--full", action="store_true", help="Select L3 full discovery.")
    parser.add_argument("--json", action="store_true", help="Emit JSON.")
    parser.add_argument("--output", help="Write JSON result to this path.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help=argparse.SUPPRESS)
    args = parser.parse_args(argv)

    root = Path(args.repo_root).resolve()
    result = select_tests(args, root)
    text = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        output_path = Path(args.output)
        if not output_path.is_absolute():
            output_path = root / output_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(text + "\n", encoding="utf-8")
    if args.json:
        print(text, file=stdout)
    else:
        print(_format_plain(result), file=stdout)
    return 0


def select_tests(args: argparse.Namespace, root: Path = REPO_ROOT) -> dict[str, Any]:
    policy = load_json(root / POLICY_PATH.relative_to(REPO_ROOT))
    impact_map = load_json(root / IMPACT_MAP_PATH.relative_to(REPO_ROOT))
    ledger = load_json(root / FAILURE_LEDGER_PATH.relative_to(REPO_ROOT))

    changed_paths = collect_changed_paths(args, root)
    mode = determine_mode(args)
    selected_lanes: set[str] = {"L0_static_preflight"}
    selected_commands: list[dict[str, str]] = []
    skipped_commands: list[dict[str, str]] = []
    warnings: list[str] = []

    for command in policy.get("base_l0_commands", []):
        add_command(
            selected_commands,
            command,
            "L0_static_preflight",
            "base preflight",
            "test_lane_policy",
        )

    mappings = list(impact_map.get("mappings", []))
    matched_mappings = [
        mapping
        for mapping in mappings
        if mapping_matches(mapping, changed_paths, args.task)
    ]

    if args.task and not matched_mappings:
        warnings.append(f"no impact-map rows matched task {args.task}")

    for mapping in matched_mappings:
        if mapping.get("validators") or mapping.get("test_modules"):
            selected_lanes.add("L1_focused_unit")
        if mapping.get("smoke_commands"):
            selected_lanes.add("L2_impact_integration")
        for command in mapping.get("validators", []):
            add_command(selected_commands, command, "L1_focused_unit", f"{mapping['owning_subsystem']} validator", mapping["path_pattern"])
        for module in mapping.get("test_modules", []):
            add_command(selected_commands, f"python -m unittest {module}", "L1_focused_unit", f"{mapping['owning_subsystem']} focused test", mapping["path_pattern"])
        for command in mapping.get("smoke_commands", []):
            add_command(selected_commands, command, "L2_impact_integration", f"{mapping['owning_subsystem']} smoke", mapping["path_pattern"])

    known_failures = active_failures(ledger)
    failed_first_commands: list[str] = []
    if args.failed_first:
        for failure in known_failures:
            command = str(failure.get("rerun_command", "")).strip()
            if command:
                failed_first_commands.append(command)
                selected_lanes.add("L1_focused_unit")
                add_command(selected_commands, command, "L1_focused_unit", f"failed-first {failure.get('failure_id')}", "test_failure_ledger")

    full_discovery_required = bool(args.full or args.promotion)
    full_discovery_deferred_until: list[str] = []
    if args.full or args.promotion:
        selected_lanes.add("L3_full_discovery")
        add_command(selected_commands, FULL_DISCOVERY_COMMAND, "L3_full_discovery", "explicit full/promotion mode", "selector")
    else:
        skipped_commands.append(
            {
                "command": FULL_DISCOVERY_COMMAND,
                "lane_id": "L3_full_discovery",
                "reason": "not selected for per-commit default; required before promotion/high-risk gates",
            }
        )
        if any(mapping.get("full_discovery_required_before_promotion") for mapping in matched_mappings):
            full_discovery_deferred_until = [
                "main_promotion",
                "release_candidate",
                "high_risk_runtime_bridge",
            ]

    if args.promotion:
        selected_lanes.update({"L1_focused_unit", "L2_impact_integration"})
        selected_lanes.add("L4_promotion_release")
        add_command(
            selected_commands,
            "python scripts/validate_test_lane_policy.py",
            "L4_promotion_release",
            "promotion policy validation",
            "selector",
        )

    promotion_blockers = [
        failure
        for failure in known_failures
        if failure.get("blocking_level") in BLOCKING_LEVELS
    ]
    promotion_allowed = not bool(args.promotion and promotion_blockers)
    if args.promotion and promotion_blockers:
        warnings.append("promotion mode refused: known blocking failures require rerun or confirmation")

    skip_reasons = [item["reason"] for item in skipped_commands]
    if not matched_mappings:
        skipped_commands.append(
            {
                "command": "impact mapped focused subsystem tests",
                "lane_id": "L1_focused_unit",
                "reason": "no changed path or task id selected an owning subsystem",
            }
        )
        skip_reasons.append("no changed path or task id selected an owning subsystem")
    if not skip_reasons:
        skip_reasons.append("no commands skipped")

    return {
        "schema_version": "test_selection_result.v0",
        "mode": mode,
        "task": args.task or "",
        "changed_paths": changed_paths,
        "matched_impact_patterns": [mapping["path_pattern"] for mapping in matched_mappings],
        "selected_lanes": sorted(selected_lanes),
        "selected_commands": selected_commands,
        "skipped_commands": skipped_commands,
        "skip_reasons": skip_reasons,
        "known_failures": known_failures,
        "failed_first_commands": failed_first_commands,
        "full_discovery_required": full_discovery_required,
        "full_discovery_deferred_until": full_discovery_deferred_until,
        "promotion_allowed": promotion_allowed,
        "warnings": warnings,
    }


def determine_mode(args: argparse.Namespace) -> str:
    modes: list[str] = []
    if args.changed:
        modes.append("changed")
    if args.since:
        modes.append(f"since:{args.since}")
    if args.task:
        modes.append(f"task:{args.task}")
    if args.failed_first:
        modes.append("failed_first")
    if args.promotion:
        modes.append("promotion")
    if args.full:
        modes.append("full")
    return "+".join(modes) if modes else "default"


def collect_changed_paths(args: argparse.Namespace, root: Path) -> list[str]:
    paths: set[str] = set()
    if args.since:
        paths.update(git_lines(root, "diff", "--name-only", f"{args.since}...HEAD"))
    if args.changed:
        paths.update(git_lines(root, "diff", "--name-only"))
        paths.update(git_lines(root, "diff", "--name-only", "--cached"))
        for line in git_lines(root, "ls-files", "--others", "--exclude-standard"):
            paths.add(line)
    return sorted(normalize_path(path) for path in paths if path.strip())


def git_lines(root: Path, *args: str) -> list[str]:
    completed = subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        return []
    return [line.strip() for line in completed.stdout.splitlines() if line.strip()]


def mapping_matches(mapping: Mapping[str, Any], changed_paths: Sequence[str], task: str | None) -> bool:
    if task and task in mapping.get("task_ids", []):
        return True
    pattern = str(mapping.get("path_pattern", ""))
    return any(fnmatch.fnmatch(path, pattern) for path in changed_paths)


def active_failures(ledger: Mapping[str, Any]) -> list[dict[str, Any]]:
    failures = []
    for failure in ledger.get("failures", []):
        if failure.get("status") in ACTIVE_FAILURE_STATUSES:
            failures.append(dict(failure))
    return failures


def add_command(commands: list[dict[str, str]], command: str, lane_id: str, reason: str, source: str) -> None:
    if any(item["command"] == command for item in commands):
        return
    commands.append(
        {
            "command": command,
            "lane_id": lane_id,
            "reason": reason,
            "source": source,
        }
    )


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_path(path: str) -> str:
    return path.replace("\\", "/")


def _format_plain(result: Mapping[str, Any]) -> str:
    lines = [
        "Eureka test selection",
        f"mode: {result['mode']}",
        f"selected_lanes: {', '.join(result['selected_lanes'])}",
        f"selected_command_count: {len(result['selected_commands'])}",
        f"known_failure_count: {len(result['known_failures'])}",
        f"full_discovery_required: {str(result['full_discovery_required']).lower()}",
        f"promotion_allowed: {str(result['promotion_allowed']).lower()}",
    ]
    if result.get("warnings"):
        lines.append("warnings:")
        lines.extend(f"- {warning}" for warning in result["warnings"])
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
