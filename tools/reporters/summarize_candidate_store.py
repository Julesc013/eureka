#!/usr/bin/env python3
"""Summarize explicit candidate records without creating local state."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local_foundry import candidate_store  # noqa: E402
from scripts.record_candidate import output_path_allowed  # noqa: E402


def build_snapshot(input_paths: Sequence[Path]) -> dict[str, Any]:
    records = [candidate_store.build_candidate_record(candidate_store.load_json(path)) for path in input_paths]
    return candidate_store.build_candidate_store_snapshot(records)


def build_report(input_paths: Sequence[Path]) -> dict[str, Any]:
    snapshot = build_snapshot(input_paths)
    errors: list[str] = []
    for index, record in enumerate(snapshot["candidates"]):
        for error in candidate_store.validate_candidate_record(record):
            errors.append(f"candidates[{index}]: {error}")
    return {
        "schema_version": candidate_store.REPORT_SCHEMA_VERSION,
        "status": "pass" if not errors else "fail",
        "snapshot": snapshot,
        "summary": candidate_store.summarize_candidate_store(snapshot["candidates"]),
        "validation_errors": sorted(errors),
    }


def write_report(report: Mapping[str, Any], output_path: Path) -> None:
    if not output_path_allowed(output_path):
        raise ValueError(f"refusing forbidden output path: {output_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_summary(report: Mapping[str, Any], output_path: Path) -> None:
    if not output_path_allowed(output_path):
        raise ValueError(f"refusing forbidden output path: {output_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(candidate_store.format_candidate_summary_markdown(report["summary"]), encoding="utf-8")


def expand_inputs(paths: Sequence[Path]) -> list[Path]:
    expanded: list[Path] = []
    for path in paths:
        if path.is_dir():
            expanded.extend(sorted(item for item in path.glob("*.json") if item.is_file()))
        else:
            expanded.append(path)
    return sorted(expanded, key=lambda item: item.as_posix())


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None, stderr: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, action="append", type=Path, help="Candidate JSON file or simple directory.")
    parser.add_argument("--output", type=Path, help="Optional explicit JSON snapshot/report output path.")
    parser.add_argument("--summary-output", type=Path, help="Optional explicit Markdown summary output path.")
    parser.add_argument("--check", action="store_true", help="Validate and summarize without requiring output.")
    parser.add_argument("--json", action="store_true", help="Print JSON report to stdout.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    out = stdout or sys.stdout
    err = stderr or sys.stderr
    try:
        input_paths = expand_inputs(args.input)
        if not input_paths:
            raise ValueError("no candidate inputs found")
        report = build_report(input_paths)
        if args.output:
            write_report(report, args.output)
        if args.summary_output:
            write_summary(report, args.summary_output)
    except Exception as exc:
        err.write(f"summarize_candidate_store: ERROR: {exc}\n")
        return 2

    if args.json:
        out.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        summary = report["summary"]
        out.write("Candidate store summary\n")
        out.write(f"status: {report['status']}\n")
        out.write(f"candidate_count: {summary.get('candidate_count')}\n")
        out.write(f"review_required_count: {summary.get('review_required_count')}\n")
        out.write(f"duplicate_group_count: {summary.get('duplicate_group_count')}\n")
        if report["validation_errors"]:
            out.write("errors:\n")
            for error in report["validation_errors"]:
                out.write(f"- {error}\n")

    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

