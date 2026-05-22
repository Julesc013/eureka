#!/usr/bin/env python3
"""Summarize fixture-only search explanation artifacts."""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import sys
import tempfile
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.extraction.guards import load_json, path_under, resolve_path  # noqa: E402
from runtime.search_quality.explanation import load_search_quality_policy  # noqa: E402


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", action="append", default=[], help="Explanation JSON file or directory. May repeat.")
    parser.add_argument("--output", help="Optional JSON summary output.")
    parser.add_argument("--summary-output", help="Optional markdown summary output.")
    parser.add_argument("--check", action="store_true", help="Validate only and write no files.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        policy = load_search_quality_policy()
        paths = collect_inputs(args.input or ["examples/search_quality"], policy)
        records = [load_json(path) for path in paths]
        summary = summarize_records(records)
        wrote = False
        if not args.check:
            if args.output:
                write_json(args.output, summary, policy)
                wrote = True
            if args.summary_output:
                write_text(args.summary_output, render_markdown(summary), policy)
                wrote = True
        summary["wrote_files"] = wrote
        if args.json:
            print(json.dumps(summary, indent=2, sort_keys=True), file=stdout)
        else:
            print("Search explanation summary", file=stdout)
            print(f"status: {summary['status']}", file=stdout)
            print(f"record_count: {summary['record_count']}", file=stdout)
            print(f"result_explanation_count: {summary['result_explanation_count']}", file=stdout)
            print(f"known_absence_count: {summary['known_absence_count']}", file=stdout)
            print(f"wrote_files: {str(wrote).lower()}", file=stdout)
        return 0
    except Exception as exc:  # noqa: BLE001
        if args.json:
            print(json.dumps({"status": "invalid", "error": str(exc)}, indent=2, sort_keys=True), file=stdout)
        else:
            print("Search explanation summary", file=stdout)
            print("status: invalid", file=stdout)
            print(f"ERROR: {exc}", file=stdout)
        return 1


def collect_inputs(inputs: Sequence[str], policy: Mapping[str, Any]) -> list[Path]:
    paths: list[Path] = []
    for value in inputs:
        path = ensure_allowed_input_path(value, policy)
        if path.is_dir():
            paths.extend(sorted(child for child in path.rglob("*.json") if child.is_file()))
        else:
            paths.append(path)
    if not paths:
        raise ValueError("no explanation inputs found")
    return paths


def summarize_records(records: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    schemas = Counter(str(item.get("schema_version", "unknown")) for item in records)
    near_types = Counter(str(item.get("mismatch_type", "unknown")) for item in records if item.get("schema_version") == "near_miss_explanation.v0")
    absence_statuses = Counter(str(item.get("absence_status", "unknown")) for item in records if item.get("schema_version") == "known_absence_record.v0")
    gap_types = Counter(str(item.get("gap_type", "unknown")) for item in records if item.get("schema_version") == "search_gap_explanation.v0")
    for item in records:
        if item.get("schema_version") == "explanation_output_bundle.v0":
            for near in item.get("near_miss_explanations", []):
                if isinstance(near, Mapping):
                    near_types[str(near.get("mismatch_type", "unknown"))] += 1
            for absence in item.get("known_absence_records", []):
                if isinstance(absence, Mapping):
                    absence_statuses[str(absence.get("absence_status", "unknown"))] += 1
            for gap in item.get("search_gap_explanations", []):
                if isinstance(gap, Mapping):
                    gap_types[str(gap.get("gap_type", "unknown"))] += 1
    return {
        "schema_version": "search_explanation_summary.v0",
        "status": "pass",
        "record_count": len(records),
        "schema_counts": dict(sorted(schemas.items())),
        "result_explanation_count": schemas.get("search_result_explanation.v0", 0),
        "near_miss_count": schemas.get("near_miss_explanation.v0", 0) + sum(near_types.values()),
        "known_absence_count": schemas.get("known_absence_record.v0", 0) + sum(absence_statuses.values()),
        "search_gap_explanation_count": schemas.get("search_gap_explanation.v0", 0) + sum(gap_types.values()),
        "near_miss_type_counts": dict(sorted(near_types.items())),
        "absence_status_counts": dict(sorted(absence_statuses.items())),
        "gap_type_counts": dict(sorted(gap_types.items())),
        "public_search_mutated": False,
        "ranking_mutated": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
    }


def ensure_allowed_input_path(path_text: str, policy: Mapping[str, Any]) -> Path:
    path = resolve_path(path_text, REPO_ROOT)
    if not path.exists():
        raise ValueError(f"input path does not exist: {path}")
    if path_under(path, Path(tempfile.gettempdir())):
        return path
    for root_text in policy.get("allowed_input_roots", []):
        if "temp" in str(root_text).casefold():
            continue
        if path_under(path, resolve_path(str(root_text), REPO_ROOT)):
            return path
    raise ValueError(f"refusing input outside allowed search-quality roots: {path}")


def ensure_allowed_output_path(path_text: str, policy: Mapping[str, Any]) -> Path:
    from scripts.explain_search_fixture import ensure_allowed_output_path as ensure_output

    return ensure_output(path_text, policy)


def write_json(path_text: str, payload: Mapping[str, Any], policy: Mapping[str, Any]) -> None:
    path = ensure_allowed_output_path(path_text, policy)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path_text: str, text: str, policy: Mapping[str, Any]) -> None:
    path = ensure_allowed_output_path(path_text, policy)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def render_markdown(summary: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "# Search Explanation Summary",
            "",
            f"- record_count: `{summary.get('record_count')}`",
            f"- result_explanation_count: `{summary.get('result_explanation_count')}`",
            f"- near_miss_count: `{summary.get('near_miss_count')}`",
            f"- known_absence_count: `{summary.get('known_absence_count')}`",
            f"- search_gap_explanation_count: `{summary.get('search_gap_explanation_count')}`",
            "- public_search_mutated: `false`",
            "- ranking_mutated: `false`",
            "",
        ]
    )


if __name__ == "__main__":
    raise SystemExit(main())
