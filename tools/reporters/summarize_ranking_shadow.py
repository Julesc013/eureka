#!/usr/bin/env python3
"""Summarize ranking shadow, regression, and gate artifacts."""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.extraction.guards import load_json  # noqa: E402
from runtime.search_quality.ranking_shadow import load_ranking_policy  # noqa: E402
from scripts.run_ranking_shadow import ensure_allowed_input_path, ensure_allowed_output_path  # noqa: E402


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", action="append", default=[], help="Ranking JSON file or directory. May repeat.")
    parser.add_argument("--output", help="Optional JSON summary output.")
    parser.add_argument("--summary-output", help="Optional markdown summary output.")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        policy = load_ranking_policy()
        paths = collect_inputs(args.input or ["examples/search_quality/ranking"], policy)
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
            print("Ranking shadow summary", file=stdout)
            print(f"status: {summary['status']}", file=stdout)
            print(f"record_count: {summary['record_count']}", file=stdout)
            print(f"ranking_shadow_count: {summary['ranking_shadow_count']}", file=stdout)
            print(f"gate_status_counts: {summary['gate_status_counts']}", file=stdout)
            print(f"wrote_files: {str(wrote).lower()}", file=stdout)
        return 0
    except Exception as exc:  # noqa: BLE001
        if args.json:
            print(json.dumps({"status": "invalid", "error": str(exc)}, indent=2, sort_keys=True), file=stdout)
        else:
            print("Ranking shadow summary", file=stdout)
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
        raise ValueError("no ranking inputs found")
    return paths


def summarize_records(records: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    schemas = Counter(str(item.get("schema_version", "unknown")) for item in records)
    gate_statuses = Counter(str(item.get("gate_status", "none")) for item in records if item.get("schema_version") == "public_ranking_gate.v0")
    factor_count = 0
    for item in records:
        if item.get("schema_version") == "ranking_shadow_result.v0":
            factor_count += len(item.get("factor_results", []))
        if item.get("schema_version") == "ranking_output_bundle.v0":
            factor_count += len(item.get("factor_results", []))
    return {
        "schema_version": "ranking_shadow_summary.v0",
        "status": "pass",
        "record_count": len(records),
        "schema_counts": dict(sorted(schemas.items())),
        "ranking_shadow_count": schemas.get("ranking_shadow_result.v0", 0) + schemas.get("ranking_output_bundle.v0", 0),
        "factor_result_count": factor_count,
        "blocked_record_count": gate_statuses.get("blocked_current", 0) + schemas.get("policy_blocked_ranking_shadow.v0", 0),
        "gate_status_counts": dict(sorted(gate_statuses.items())),
        "public_ranking_mutated": False,
        "public_search_mutated": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
    }


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
            "# Ranking Shadow Summary",
            "",
            f"- record_count: `{summary.get('record_count')}`",
            f"- ranking_shadow_count: `{summary.get('ranking_shadow_count')}`",
            f"- factor_result_count: `{summary.get('factor_result_count')}`",
            f"- gate_status_counts: `{summary.get('gate_status_counts')}`",
            "- public_ranking_mutated: `false`",
            "- public_search_mutated: `false`",
            "",
        ]
    )


if __name__ == "__main__":
    raise SystemExit(main())
