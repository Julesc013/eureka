#!/usr/bin/env python3
"""Build fixture-only extraction search integration previews."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.extraction.guards import ensure_allowed_input_path, ensure_allowed_output_path, load_json  # noqa: E402
from runtime.extraction.search_integration import (  # noqa: E402
    build_extraction_search_integration,
    load_extraction_search_policy,
    summarize_extraction_search_integration,
)
from runtime.extraction.usefulness import (  # noqa: E402
    build_extraction_usefulness_report,
    build_track_g_readiness_recommendation,
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", action="append", default=[], help="Extraction result JSON file or directory. May repeat.")
    parser.add_argument("--output", help="Optional integration JSON output.")
    parser.add_argument("--search-gap-output", help="Optional first search-gap JSON output.")
    parser.add_argument("--review-seed-output", help="Optional first review-seed JSON output.")
    parser.add_argument("--workunit-seed-output", help="Optional first WorkUnit-seed JSON output.")
    parser.add_argument("--usefulness-output", help="Optional usefulness report JSON output.")
    parser.add_argument("--summary-output", help="Optional markdown summary output.")
    parser.add_argument("--check", action="store_true", help="Validate only and write no files.")
    parser.add_argument("--json", action="store_true", help="Emit JSON summary.")
    args = parser.parse_args(argv)
    try:
        policy = load_extraction_search_policy()
        paths = collect_inputs(args.input, policy)
        results = [load_json(path) for path in paths]
        integration = build_extraction_search_integration(results, policy)
        usefulness = build_extraction_usefulness_report([integration], policy)
        handoff = build_track_g_readiness_recommendation(usefulness, policy)
        summary = summarize_extraction_search_integration(integration)
        summary["track_g_readiness"] = handoff["track_g_readiness"]
        wrote = False
        if not args.check:
            outputs = [
                (args.output, integration),
                (args.search_gap_output, first_or_empty(integration.get("search_gaps", []))),
                (args.review_seed_output, first_or_empty(integration.get("review_seeds", []))),
                (args.workunit_seed_output, first_or_empty(integration.get("workunit_seeds", []))),
                (args.usefulness_output, usefulness),
            ]
            for path_text, payload in outputs:
                if path_text:
                    write_json(path_text, payload, policy)
                    wrote = True
            if args.summary_output:
                write_text(args.summary_output, render_markdown(summary), policy)
                wrote = True
        summary["wrote_files"] = wrote
        if args.json:
            print(json.dumps(summary, indent=2, sort_keys=True), file=stdout)
        else:
            print("Extraction search integration", file=stdout)
            print(f"status: {summary['integration_status']}", file=stdout)
            print(f"search_gap_count: {summary['search_gap_count']}", file=stdout)
            print(f"review_seed_count: {summary['review_seed_count']}", file=stdout)
            print(f"workunit_seed_count: {summary['workunit_seed_count']}", file=stdout)
            print(f"track_g_readiness: {summary['track_g_readiness']}", file=stdout)
            print(f"wrote_files: {str(wrote).lower()}", file=stdout)
        return 0
    except Exception as exc:  # noqa: BLE001
        payload = {"status": "invalid", "error": str(exc)}
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True), file=stdout)
        else:
            print("Extraction search integration", file=stdout)
            print("status: invalid", file=stdout)
            print(f"ERROR: {exc}", file=stdout)
        return 1


def collect_inputs(inputs: Sequence[str], policy: Mapping[str, Any]) -> list[Path]:
    values = list(inputs) or ["examples/extraction/results"]
    paths: list[Path] = []
    for value in values:
        path = ensure_allowed_input_path(value, policy)
        if path.is_dir():
            paths.extend(sorted(child for child in path.glob("*.json") if child.is_file()))
        else:
            paths.append(path)
    if not paths:
        raise ValueError("no extraction result inputs found")
    return paths


def first_or_empty(values: Any) -> Mapping[str, Any]:
    if isinstance(values, list) and values:
        return values[0]
    return {"schema_version": "empty_preview.v0", "limitations": ["No preview produced."]}


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
            "# Extraction Search Integration Summary",
            "",
            f"- integration_status: `{summary.get('integration_status')}`",
            f"- extraction_result_count: `{summary.get('extraction_result_count', 0)}`",
            f"- search_gap_count: `{summary.get('search_gap_count', 0)}`",
            f"- review_seed_count: `{summary.get('review_seed_count', 0)}`",
            f"- workunit_seed_count: `{summary.get('workunit_seed_count', 0)}`",
            f"- track_g_readiness: `{summary.get('track_g_readiness')}`",
            "- public_search_mutated: `false`",
            "- public_index_mutated: `false`",
            "- master_index_mutated: `false`",
            "",
        ]
    )


if __name__ == "__main__":
    raise SystemExit(main())
