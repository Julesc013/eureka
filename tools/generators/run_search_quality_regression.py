#!/usr/bin/env python3
"""Run fixture-only search-quality regression over ranking shadow outputs."""

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

from runtime.extraction.guards import load_json, path_under, resolve_path  # noqa: E402
from runtime.search.quality.dedup_shadow import build_dedup_shadow  # noqa: E402
from runtime.search.quality.identity_shadow import build_identity_merge_shadow  # noqa: E402
from runtime.search.quality.public_ranking_gate import build_public_ranking_gate, summarize_public_ranking_gate  # noqa: E402
from runtime.search.quality.quality_harness import (  # noqa: E402
    build_search_quality_regression_report,
    summarize_regression_report,
)
from runtime.search.quality.ranking_shadow import build_ranking_output_bundle, build_ranking_shadow, load_ranking_policy  # noqa: E402
from scripts.run_ranking_shadow import ensure_allowed_input_path, ensure_allowed_output_path, render_markdown as render_ranking_markdown  # noqa: E402


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query-set", required=True, help="Search-quality query set JSON.")
    parser.add_argument("--ranking-output", action="append", default=[], help="Ranking output JSON. May repeat.")
    parser.add_argument("--output", help="Optional regression report JSON.")
    parser.add_argument("--gate-output", help="Optional public ranking gate JSON.")
    parser.add_argument("--summary-output", help="Optional markdown summary output.")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        policy = load_ranking_policy()
        query_set = load_json(ensure_allowed_input_path(args.query_set, policy))
        outputs = load_or_build_ranking_outputs(query_set, args.ranking_output, policy)
        report = build_search_quality_regression_report(query_set, outputs, policy)
        gate = build_public_ranking_gate([report], policy)
        summary = summarize_regression_report(report, policy)
        summary["public_ranking_gate_status"] = gate.get("gate_status")
        wrote = False
        if not args.check:
            if args.output:
                write_json(args.output, report, policy)
                wrote = True
            if args.gate_output:
                write_json(args.gate_output, gate, policy)
                wrote = True
            if args.summary_output:
                write_text(args.summary_output, render_markdown(summary, gate), policy)
                wrote = True
        summary["wrote_files"] = wrote
        if args.json:
            print(json.dumps(summary, indent=2, sort_keys=True), file=stdout)
        else:
            print("Search quality regression", file=stdout)
            print(f"status: {summary['status']}", file=stdout)
            print(f"query_set_ref: {summary.get('query_set_ref')}", file=stdout)
            print(f"exact_expected_present: {summary['exact_expected_present']}", file=stdout)
            print(f"public_ranking_gate_status: {gate['gate_status']}", file=stdout)
            print(f"wrote_files: {str(wrote).lower()}", file=stdout)
        return 0
    except Exception as exc:  # noqa: BLE001
        if args.json:
            print(json.dumps({"status": "invalid", "error": str(exc)}, indent=2, sort_keys=True), file=stdout)
        else:
            print("Search quality regression", file=stdout)
            print("status: invalid", file=stdout)
            print(f"ERROR: {exc}", file=stdout)
        return 1


def load_or_build_ranking_outputs(query_set: Mapping[str, Any], ranking_paths: Sequence[str], policy: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    if ranking_paths:
        return [load_json(ensure_allowed_input_path(path, policy)) for path in ranking_paths]
    outputs: list[Mapping[str, Any]] = []
    for case in query_set.get("query_cases", []):
        if not isinstance(case, Mapping) or not case.get("ranking_input_bundle_ref"):
            continue
        input_bundle = load_json(ensure_allowed_input_path(str(case["ranking_input_bundle_ref"]), policy))
        items = [item for item in input_bundle.get("items", []) if isinstance(item, Mapping)]
        ranking = build_ranking_shadow(input_bundle, policy)
        identity = build_identity_merge_shadow(items, policy)
        dedup = build_dedup_shadow(items, policy)
        outputs.append(build_ranking_output_bundle(input_bundle, ranking, identity, dedup, policy))
    if not outputs:
        raise ValueError("query set did not provide ranking inputs and no --ranking-output was supplied")
    return outputs


def write_json(path_text: str, payload: Mapping[str, Any], policy: Mapping[str, Any]) -> None:
    path = ensure_allowed_output_path(path_text, policy)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path_text: str, text: str, policy: Mapping[str, Any]) -> None:
    path = ensure_allowed_output_path(path_text, policy)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def render_markdown(summary: Mapping[str, Any], gate: Mapping[str, Any]) -> str:
    base = render_ranking_markdown({"ranking_shadow_status": "regression", "ranked_item_count": summary.get("ranking_shadow_count"), "factor_result_count": 0, "top_item_ref": ""})
    return base + "\n".join(
        [
            "# Search Quality Regression",
            "",
            f"- query_set_ref: `{summary.get('query_set_ref')}`",
            f"- status: `{summary.get('status')}`",
            f"- exact_expected_present: `{summary.get('exact_expected_present')}`",
            f"- public_ranking_gate_status: `{gate.get('gate_status')}`",
            "- production_quality_claimed: `false`",
            "",
        ]
    )


if __name__ == "__main__":
    raise SystemExit(main())
