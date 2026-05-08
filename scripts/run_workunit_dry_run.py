#!/usr/bin/env python3
"""Run a local-only WorkUnit dry-run from one explicit WorkUnit JSON file.

The command writes no files by default. It performs no WorkUnit execution, no
network/API/model/provider calls, no public search mutation, no local private
state creation, and no master-index mutation.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local_foundry.workunit_dry_run import (  # noqa: E402
    build_workunit_dry_run_result,
    default_policies,
    format_summary_markdown,
    load_workunit,
    summarize_workunit_dry_run,
    validate_dry_run_result,
)


FORBIDDEN_OUTPUT_ROOTS = (
    "site/dist/",
    "runtime/",
    "contracts/",
    "control/inventory/publication/",
    "control/inventory/master_index/",
    "master_index/",
    ".aide.local/",
    ".local/eureka/",
    ".cache/eureka/",
)


def list_example_workunits(repo_root: Path = REPO_ROOT) -> list[str]:
    return sorted(path.relative_to(repo_root).as_posix() for path in (repo_root / "examples" / "work_units").glob("*/work_unit.json"))


def build_report(workunit_path: Path, *, repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    workunit = load_workunit(workunit_path)
    result = build_workunit_dry_run_result(
        workunit,
        default_policies(),
        source_workunit_ref=_display_path(workunit_path, repo_root),
    )
    errors = validate_dry_run_result(result)
    result["validation_summary"]["errors_count"] = len(errors)
    result["validation_summary"]["validation_status"] = "pass" if not errors else "fail"
    result["errors"] = errors
    if errors:
        result["workunit_result_status"] = "fail"
    return result


def output_path_allowed(path: Path, *, repo_root: Path = REPO_ROOT) -> bool:
    resolved = path.resolve()
    try:
        relative = resolved.relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        temp_root = Path(tempfile.gettempdir()).resolve()
        try:
            resolved.relative_to(temp_root)
            return True
        except ValueError:
            return False

    normalized = relative.rstrip("/") + "/"
    if any(normalized.startswith(root) or relative == root.rstrip("/") for root in FORBIDDEN_OUTPUT_ROOTS):
        return False
    if relative.startswith("control/audits/") and "/generated/" in f"/{relative}":
        return True
    if relative.startswith("examples/workunit_dry_runs/") and relative.endswith("/work_unit_result.json"):
        return True
    return False


def write_json(payload: Mapping[str, Any], output_path: Path) -> None:
    if not output_path_allowed(output_path):
        raise ValueError(f"refusing forbidden output path: {output_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_summary(result: Mapping[str, Any], output_path: Path) -> None:
    if not output_path_allowed(output_path):
        raise ValueError(f"refusing forbidden output path: {output_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(format_summary_markdown(summarize_workunit_dry_run(result)), encoding="utf-8")


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None, stderr: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workunit", type=Path, help="Explicit WorkUnit JSON file to dry-run.")
    parser.add_argument("--output", type=Path, help="Optional explicit WorkUnitResult JSON output path.")
    parser.add_argument("--summary-output", type=Path, help="Optional explicit markdown summary output path.")
    parser.add_argument("--check", action="store_true", help="Validate and report status without requiring output.")
    parser.add_argument("--json", action="store_true", help="Print JSON result to stdout.")
    parser.add_argument("--list-examples", action="store_true", help="List committed WorkUnit examples.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    out = stdout or sys.stdout
    err = stderr or sys.stderr
    if args.list_examples:
        for example in list_example_workunits():
            out.write(f"{example}\n")
        return 0
    if not args.workunit:
        err.write("run_workunit_dry_run: ERROR: --workunit is required unless --list-examples is used\n")
        return 2

    try:
        result = build_report(args.workunit)
        if args.output:
            write_json(result, args.output)
        if args.summary_output:
            write_summary(result, args.summary_output)
    except Exception as exc:
        err.write(f"run_workunit_dry_run: ERROR: {exc}\n")
        return 2

    if args.json:
        out.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        summary = summarize_workunit_dry_run(result)
        out.write("WorkUnit dry-run\n")
        out.write(f"status: {result['workunit_result_status']}\n")
        out.write(f"workunit_result_id: {summary.get('workunit_result_id')}\n")
        out.write(f"workunit_id: {summary.get('workunit_id')}\n")
        out.write(f"execution_mode: {summary.get('execution_mode')}\n")
        out.write(f"executed_actions: {summary.get('executed_action_count')}\n")
        out.write(f"review_required: {str(summary.get('review_required')).lower()}\n")
        if result.get("errors"):
            out.write("errors:\n")
            for error in result["errors"]:
                out.write(f"- {error}\n")

    return 0 if not result.get("errors") else 1


def _display_path(path: Path, repo_root: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
