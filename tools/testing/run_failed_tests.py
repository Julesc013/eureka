#!/usr/bin/env python3
"""Print or run focused unittest commands from a full discovery summary."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("summary", nargs="?", help="Path to full_unittest_summary.json")
    parser.add_argument("--summary", dest="summary_flag")
    parser.add_argument("--modules-only", action="store_true")
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--out", default="failed_rerun_summary.json")
    args = parser.parse_args(argv)

    summary_path = Path(args.summary_flag or args.summary or "")
    if not str(summary_path):
        parser.error("summary path is required")
    result = plan_or_run_failed_tests(
        summary_path=summary_path,
        modules_only=args.modules_only,
        run=args.run,
        out_path=Path(args.out),
    )
    for command in result["commands"]:
        print(command, file=stdout)
    return 0 if result["status"] in {"planned", "pass", "empty"} else 1


def plan_or_run_failed_tests(
    *,
    summary_path: Path,
    modules_only: bool = False,
    run: bool = False,
    out_path: Path = Path("failed_rerun_summary.json"),
) -> dict[str, Any]:
    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    commands = rerun_commands(payload, modules_only=modules_only)
    results: list[dict[str, Any]] = []
    status = "empty" if not commands else "planned"
    if run and commands:
        status = "pass"
        for command in commands:
            args = command.split()
            completed = subprocess.run(args, text=True, capture_output=True, check=False)
            command_result = {
                "command": command,
                "exit_code": completed.returncode,
                "stdout_tail": tail(completed.stdout),
                "stderr_tail": tail(completed.stderr),
            }
            results.append(command_result)
            if completed.returncode != 0:
                status = "fail"
    result = {
        "schema_version": "failed_unittest_rerun_summary.v0",
        "source_summary": str(summary_path),
        "mode": "modules_only" if modules_only else "tests",
        "run_performed": run,
        "status": status,
        "commands": commands,
        "results": results,
        "full_discovery_run": False,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def rerun_commands(summary: Mapping[str, Any], *, modules_only: bool = False) -> list[str]:
    if modules_only:
        targets = sorted(set(str(item) for item in summary.get("failed_modules", []) if item))
    else:
        targets = sorted(set(target_from_failed_test(str(item)) for item in summary.get("failed_tests", []) if item))
    return [f"{sys.executable} -m unittest {target}" for target in targets if target]


def target_from_failed_test(test_name: str) -> str:
    if "(" in test_name and ")" in test_name:
        inner = test_name.split("(", 1)[1].split(")", 1)[0].strip()
        if inner:
            return inner
    return test_name.strip()


def tail(text: str, max_lines: int = 20) -> str:
    lines = text.splitlines()
    return "\n".join(lines[-max_lines:])


if __name__ == "__main__":
    raise SystemExit(main())
