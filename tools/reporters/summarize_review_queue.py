#!/usr/bin/env python3
"""Summarize explicit local review queue entries."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local.foundry import review_queue  # noqa: E402
from scripts.record_review_queue import FORBIDDEN_OUTPUT_ROOTS, output_path_allowed  # noqa: E402


def collect_entries(paths: Sequence[Path]) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for path in paths:
        if path.is_dir():
            for child in sorted(path.glob("*.json")):
                entries.extend(_entries_from_payload(review_queue.load_json(child)))
        else:
            entries.extend(_entries_from_payload(review_queue.load_json(path)))
    return entries


def build_report(paths: Sequence[Path]) -> dict[str, Any]:
    entries = collect_entries(paths)
    snapshot = review_queue.build_review_queue_snapshot(entries)
    summary = review_queue.summarize_review_queue(entries)
    status = "pass" if not snapshot["warnings"] else "fail"
    return {
        "schema_version": review_queue.SNAPSHOT_SCHEMA_VERSION,
        "status": status,
        "snapshot": snapshot,
        "summary": summary,
        "warnings": snapshot["warnings"],
        "runtime_scope": {
            "explicit_input_only": True,
            "local_only": True,
            "writes_no_files_by_default": True,
            "hosted_review_enabled": False,
            "master_index_mutation_enabled": False,
        },
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
    output_path.write_text(review_queue.format_review_queue_summary_markdown(report["summary"]), encoding="utf-8")


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None, stderr: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", action="append", required=True, type=Path, help="Review queue entry file or directory.")
    parser.add_argument("--output", type=Path, help="Optional explicit JSON summary output path.")
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
        err.write(f"summarize_review_queue: ERROR: {exc}\n")
        return 2

    if args.json:
        out.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        summary = report["summary"]
        out.write("Review queue summary\n")
        out.write(f"status: {report['status']}\n")
        out.write(f"review_entry_count: {summary.get('review_entry_count')}\n")
        out.write(f"promotion_dry_run_ready_count: {summary.get('promotion_dry_run_ready_count')}\n")
        out.write(f"blocked_count: {summary.get('blocked_count')}\n")
        out.write(f"warning_count: {summary.get('warning_count')}\n")
        if report["warnings"]:
            out.write("warnings:\n")
            for warning in report["warnings"]:
                out.write(f"- {warning}\n")

    return 0 if report["status"] == "pass" else 1


def _entries_from_payload(payload: Mapping[str, Any]) -> list[dict[str, Any]]:
    if payload.get("schema_version") == review_queue.SNAPSHOT_SCHEMA_VERSION:
        entries = payload.get("entries", [])
        if not isinstance(entries, list):
            raise ValueError("review queue snapshot entries must be a list")
        return [review_queue.build_review_queue_entry(entry) for entry in entries if isinstance(entry, Mapping)]
    if "entry" in payload and isinstance(payload["entry"], Mapping):
        return [review_queue.build_review_queue_entry(payload["entry"])]
    return [review_queue.build_review_queue_entry(payload)]


if __name__ == "__main__":
    raise SystemExit(main())
