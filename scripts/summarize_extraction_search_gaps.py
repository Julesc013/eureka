#!/usr/bin/env python3
"""Summarize extraction search gap and integration preview JSON files."""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.extraction.guards import ensure_allowed_input_path, ensure_allowed_output_path, load_json  # noqa: E402
from runtime.extraction.search_integration import load_extraction_search_policy  # noqa: E402


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", action="append", default=[], help="Search gap JSON, integration JSON, or directory. May repeat.")
    parser.add_argument("--output", help="Optional JSON summary output.")
    parser.add_argument("--summary-output", help="Optional markdown summary output.")
    parser.add_argument("--check", action="store_true", help="Validate only and write no files.")
    parser.add_argument("--json", action="store_true", help="Emit JSON summary.")
    args = parser.parse_args(argv)
    try:
        policy = load_extraction_search_policy()
        payloads = [load_json(path) for path in collect_inputs(args.input, policy)]
        summary = summarize_payloads(payloads)
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
            print("Extraction search gap summary", file=stdout)
            print(f"status: {summary['status']}", file=stdout)
            print(f"search_gap_count: {summary['search_gap_count']}", file=stdout)
            print(f"review_seed_count: {summary['review_seed_count']}", file=stdout)
            print(f"workunit_seed_count: {summary['workunit_seed_count']}", file=stdout)
            print(f"wrote_files: {str(wrote).lower()}", file=stdout)
        return 0
    except Exception as exc:  # noqa: BLE001
        if args.json:
            print(json.dumps({"status": "invalid", "error": str(exc)}, indent=2, sort_keys=True), file=stdout)
        else:
            print("Extraction search gap summary", file=stdout)
            print("status: invalid", file=stdout)
            print(f"ERROR: {exc}", file=stdout)
        return 1


def collect_inputs(inputs: Sequence[str], policy: Mapping[str, Any]) -> list[Path]:
    values = list(inputs) or ["examples/extraction/search_integration"]
    paths: list[Path] = []
    input_policy = {**policy, "allowed_input_roots": ["examples/extraction/search_integration", "control/audits", "explicit temp test directory"]}
    for value in values:
        path = ensure_allowed_input_path(value, input_policy)
        if path.is_dir():
            paths.extend(sorted(child for child in path.glob("*.json") if child.is_file()))
        else:
            paths.append(path)
    if not paths:
        raise ValueError("no extraction search gap inputs found")
    return paths


def summarize_payloads(payloads: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    gaps: list[Mapping[str, Any]] = []
    review_count = 0
    workunit_count = 0
    candidate_count = 0
    blocker_count = 0
    for payload in payloads:
        if payload.get("schema_version") == "extraction_search_integration.v0":
            gaps.extend(item for item in payload.get("search_gaps", []) if isinstance(item, Mapping))
            review_count += len(payload.get("review_seed_refs", []))
            workunit_count += len(payload.get("workunit_seed_refs", []))
            candidate_count += len(payload.get("candidate_effect_refs", []))
        else:
            gaps.append(payload)
        if payload.get("search_gap_status") == "policy_blocked":
            blocker_count += 1
    gap_types = Counter(str(item.get("gap_type", "unknown")) for item in gaps)
    return {
        "schema_version": "extraction_search_gap_summary.v0",
        "status": "pass",
        "search_gap_count": len(gaps),
        "gap_type_counts": dict(sorted(gap_types.items())),
        "candidate_effect_count": candidate_count,
        "review_seed_count": review_count,
        "workunit_seed_count": workunit_count,
        "blocker_count": blocker_count,
        "public_search_mutated": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
    }


def render_markdown(summary: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "# Extraction Search Gap Summary",
            "",
            f"- status: `{summary.get('status')}`",
            f"- search_gap_count: `{summary.get('search_gap_count', 0)}`",
            f"- review_seed_count: `{summary.get('review_seed_count', 0)}`",
            f"- workunit_seed_count: `{summary.get('workunit_seed_count', 0)}`",
            f"- blocker_count: `{summary.get('blocker_count', 0)}`",
            "- public_search_mutated: `false`",
            "- public_index_mutated: `false`",
            "- master_index_mutated: `false`",
            "",
        ]
    )


if __name__ == "__main__":
    raise SystemExit(main())
