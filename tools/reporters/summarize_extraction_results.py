#!/usr/bin/env python3
"""Summarize explicit fixture extraction result JSON files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.extraction.guards import ensure_allowed_input_path, ensure_allowed_output_path, load_extraction_policy, load_json  # noqa: E402


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", action="append", default=[], help="Result JSON file or directory. May repeat.")
    parser.add_argument("--output", help="Optional JSON summary output.")
    parser.add_argument("--summary-output", help="Optional markdown summary output.")
    parser.add_argument("--check", action="store_true", help="Validate only and write no files.")
    parser.add_argument("--json", action="store_true", help="Emit JSON summary.")
    args = parser.parse_args(argv)
    try:
        policy = load_extraction_policy()
        paths = collect_inputs(args.input, policy)
        results = [load_json(path) for path in paths]
        summary = summarize_results(results)
        wrote = False
        if not args.check:
            if args.output:
                path = ensure_allowed_output_path(args.output, policy)
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
                wrote = True
            if args.summary_output:
                path = ensure_allowed_output_path(args.summary_output, policy)
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(render_markdown(summary), encoding="utf-8")
                wrote = True
        summary["wrote_files"] = wrote
        if args.json:
            print(json.dumps(summary, indent=2, sort_keys=True), file=stdout)
        else:
            print("Extraction results summary", file=stdout)
            print(f"status: {summary['status']}", file=stdout)
            print(f"result_count: {summary['result_count']}", file=stdout)
            print(f"manifest_candidate_count: {summary['manifest_candidate_count']}", file=stdout)
            print(f"blocked_result_count: {summary['blocked_result_count']}", file=stdout)
            print(f"wrote_files: {str(wrote).lower()}", file=stdout)
        return 0
    except Exception as exc:  # noqa: BLE001
        if args.json:
            print(json.dumps({"status": "invalid", "error": str(exc)}, indent=2, sort_keys=True), file=stdout)
        else:
            print("Extraction results summary", file=stdout)
            print("status: invalid", file=stdout)
            print(f"ERROR: {exc}", file=stdout)
        return 1


def collect_inputs(inputs: Sequence[str], policy: Mapping[str, Any]) -> list[Path]:
    values = list(inputs) or ["examples/extraction/results"]
    paths: list[Path] = []
    for value in values:
        path = ensure_allowed_input_path(value, {**policy, "allowed_input_roots": ["examples/extraction/results", "explicit temp test directory"]})
        if path.is_dir():
            paths.extend(sorted(child for child in path.glob("*.json") if child.is_file()))
        else:
            paths.append(path)
    if not paths:
        raise ValueError("no extraction result inputs found")
    return paths


def summarize_results(results: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    statuses = [str(item.get("extraction_status", "unknown")) for item in results]
    return {
        "schema_version": "extraction_result_collection_summary.v0",
        "status": "pass",
        "result_count": len(results),
        "container_types": sorted({str(item.get("container_type", "unknown")) for item in results}),
        "tiers": sorted({tier for item in results for tier in item.get("tiers_completed", [])}),
        "member_count": sum(len(item.get("member_listing", [])) for item in results),
        "manifest_candidate_count": sum(len(item.get("manifest_candidates", [])) for item in results),
        "blocked_result_count": sum(1 for status in statuses if status.startswith("blocked")),
        "blocked_statuses": sorted({status for status in statuses if status.startswith("blocked")}),
        "warnings": sorted({str(warning) for item in results for warning in item.get("warnings", [])}),
        "accepted_evidence": False,
        "accepted_candidate": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
    }


def render_markdown(summary: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "# Extraction Results Summary",
            "",
            f"- status: `{summary.get('status')}`",
            f"- result_count: `{summary.get('result_count', 0)}`",
            f"- container_types: `{', '.join(summary.get('container_types', []))}`",
            f"- tiers: `{', '.join(summary.get('tiers', []))}`",
            f"- member_count: `{summary.get('member_count', 0)}`",
            f"- manifest_candidate_count: `{summary.get('manifest_candidate_count', 0)}`",
            f"- blocked_result_count: `{summary.get('blocked_result_count', 0)}`",
            "- accepted_evidence: `false`",
            "- accepted_candidate: `false`",
            "- public_index_mutated: `false`",
            "- master_index_mutated: `false`",
            "",
        ]
    )


if __name__ == "__main__":
    raise SystemExit(main())
