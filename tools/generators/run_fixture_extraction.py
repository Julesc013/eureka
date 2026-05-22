#!/usr/bin/env python3
"""Run fixture-only Tier 0-2 extraction on an explicit repo-local target."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.extraction.candidate_effects import build_extraction_candidate_effects  # noqa: E402
from runtime.extraction.guards import ensure_allowed_input_path, ensure_allowed_output_path, load_json  # noqa: E402
from runtime.extraction.sandbox import load_extraction_policy, run_fixture_extraction, target_from_fixture  # noqa: E402
from runtime.extraction.summaries import render_extraction_summary_markdown, summarize_extraction_result  # noqa: E402


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", help="Extraction target JSON.")
    parser.add_argument("--fixture", help="Explicit fixture archive path.")
    parser.add_argument("--tiers", default="0,1,2", help="Comma-separated tiers: 0,1,2.")
    parser.add_argument("--output", help="Optional extraction result JSON output.")
    parser.add_argument("--candidate-output", help="Optional candidate-effect JSON output.")
    parser.add_argument("--summary-output", help="Optional markdown summary output.")
    parser.add_argument("--check", action="store_true", help="Validate only and write no files.")
    parser.add_argument("--json", action="store_true", help="Emit JSON summary.")
    args = parser.parse_args(argv)
    try:
        policy = load_extraction_policy()
        tiers = [item.strip() for item in args.tiers.split(",") if item.strip()]
        target = load_target(args.target, args.fixture, tiers, policy)
        result = run_fixture_extraction(target, tiers, policy)
        effects = result.get("candidate_effects") or build_extraction_candidate_effects(result, policy)
        summary = summarize_extraction_result(result)
        wrote = False
        if not args.check:
            if args.output:
                write_json(args.output, result, policy)
                wrote = True
            if args.candidate_output:
                payload: Any = effects[0] if len(effects) == 1 else {"schema_version": "extraction_candidate_effect_set.v0", "candidate_effects": effects}
                write_json(args.candidate_output, payload, policy)
                wrote = True
            if args.summary_output:
                write_text(args.summary_output, render_extraction_summary_markdown(summary), policy)
                wrote = True
        summary["wrote_files"] = wrote
        if args.json:
            print(json.dumps(summary, indent=2, sort_keys=True), file=stdout)
        else:
            print("Fixture extraction", file=stdout)
            print(f"status: {summary['status']}", file=stdout)
            print(f"extraction_status: {summary['extraction_status']}", file=stdout)
            print(f"container_type: {summary['container_type']}", file=stdout)
            print(f"tiers_completed: {','.join(summary['tiers_completed'])}", file=stdout)
            print(f"member_count: {summary['member_count']}", file=stdout)
            print(f"manifest_candidate_count: {summary['manifest_candidate_count']}", file=stdout)
            print(f"blocked_member_count: {summary['blocked_member_count']}", file=stdout)
            print(f"wrote_files: {str(wrote).lower()}", file=stdout)
        return 0
    except Exception as exc:  # noqa: BLE001 - deterministic CLI errors.
        if args.json:
            print(json.dumps({"status": "invalid", "error": str(exc)}, indent=2, sort_keys=True), file=stdout)
        else:
            print("Fixture extraction", file=stdout)
            print("status: invalid", file=stdout)
            print(f"ERROR: {exc}", file=stdout)
        return 1


def load_target(target_path: str | None, fixture_path: str | None, tiers: Sequence[str], policy: Mapping[str, Any]) -> dict[str, Any]:
    if target_path and fixture_path:
        raise ValueError("use either --target or --fixture, not both")
    if target_path:
        path = ensure_allowed_input_path(target_path, policy)
        return dict(load_json(path))
    if fixture_path:
        path = ensure_allowed_input_path(fixture_path, policy)
        return target_from_fixture(path, tiers)
    raise ValueError("one of --target or --fixture is required")


def write_json(path_text: str, payload: Mapping[str, Any], policy: Mapping[str, Any]) -> None:
    path = ensure_allowed_output_path(path_text, policy)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path_text: str, text: str, policy: Mapping[str, Any]) -> None:
    path = ensure_allowed_output_path(path_text, policy)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
