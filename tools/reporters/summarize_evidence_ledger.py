#!/usr/bin/env python3
"""Summarize explicit fixture-only evidence ledger records."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local_foundry import evidence_ledger  # noqa: E402
from scripts import record_evidence_ledger  # noqa: E402


def build_report(input_paths: Sequence[Path], *, repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    expanded = _expand_inputs(input_paths)
    records: list[dict[str, Any]] = []
    input_refs: list[str] = []
    for path in expanded:
        payload = evidence_ledger.load_json(path)
        input_refs.append(_display_path(path, repo_root))
        if payload.get("schema_version") == evidence_ledger.SNAPSHOT_SCHEMA_VERSION:
            records.extend(record for record in payload.get("records", []) if isinstance(record, dict))
        elif payload.get("schema_version") == evidence_ledger.REPORT_SCHEMA_VERSION and isinstance(payload.get("record"), dict):
            records.append(payload["record"])
        else:
            records.append(payload)
    snapshot = evidence_ledger.build_evidence_ledger_snapshot(records)
    summary = evidence_ledger.summarize_evidence_ledger(snapshot["records"])
    errors = list(snapshot["warnings"])
    return {
        "schema_version": evidence_ledger.REPORT_SCHEMA_VERSION,
        "status": "pass" if not errors else "fail",
        "input_refs": input_refs,
        "snapshot": snapshot,
        "summary": summary,
        "validation_errors": errors,
        "warnings": [],
        "runtime_scope": {
            "explicit_input_only": True,
            "local_only": True,
            "fixture_only": True,
            "writes_no_files_by_default": True,
            "source_cache_bridge_enabled": False,
            "evidence_acceptance_enabled": False,
            "live_source_access_enabled": False,
        },
        "truth_boundary": snapshot["truth_boundary"],
        "product_boundary": snapshot["product_boundary"],
    }


def write_report(report: Mapping[str, Any], output_path: Path) -> None:
    if not record_evidence_ledger.output_path_allowed(output_path):
        raise ValueError(f"refusing forbidden output path: {output_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_summary(report: Mapping[str, Any], output_path: Path) -> None:
    if not record_evidence_ledger.output_path_allowed(output_path):
        raise ValueError(f"refusing forbidden output path: {output_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(evidence_ledger.format_evidence_ledger_summary_markdown(report["summary"]), encoding="utf-8")


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None, stderr: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, action="append", type=Path, help="Evidence ledger record JSON file or directory.")
    parser.add_argument("--output", type=Path, help="Optional explicit JSON report output path.")
    parser.add_argument("--summary-output", type=Path, help="Optional explicit Markdown summary output path.")
    parser.add_argument("--check", action="store_true", help="Validate and report status without requiring output.")
    parser.add_argument("--json", action="store_true", help="Print JSON report to stdout.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    out = stdout or sys.stdout
    err = stderr or sys.stderr
    try:
        report = build_report(args.input)
        if args.output:
            write_report(report, args.output)
        if args.summary_output:
            write_summary(report, args.summary_output)
    except Exception as exc:
        err.write(f"summarize_evidence_ledger: ERROR: {exc}\n")
        return 2

    if args.json:
        out.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        summary = report["summary"]
        out.write("Evidence ledger summary\n")
        out.write(f"status: {report['status']}\n")
        out.write(f"evidence_record_count: {summary.get('evidence_record_count')}\n")
        out.write(f"review_required_count: {summary.get('review_required_count')}\n")
        out.write(f"conflicting_record_count: {summary.get('conflicting_record_count')}\n")
        out.write(f"warning_count: {summary.get('warning_count')}\n")
        if report["validation_errors"]:
            out.write("errors:\n")
            for error in report["validation_errors"]:
                out.write(f"- {error}\n")

    return 0 if report["status"] == "pass" else 1


def _expand_inputs(input_paths: Sequence[Path]) -> list[Path]:
    paths: list[Path] = []
    for input_path in input_paths:
        if input_path.is_dir():
            paths.extend(sorted(path for path in input_path.glob("*.json") if path.is_file()))
        else:
            paths.append(input_path)
    if not paths:
        raise ValueError("no evidence ledger JSON inputs found")
    return paths


def _display_path(path: Path, repo_root: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
