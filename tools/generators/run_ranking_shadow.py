#!/usr/bin/env python3
"""Run fixture-only ranking shadow scoring."""

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
from runtime.search_quality.dedup_shadow import build_dedup_shadow  # noqa: E402
from runtime.search_quality.identity_shadow import build_identity_merge_shadow  # noqa: E402
from runtime.search_quality.ranking_shadow import (  # noqa: E402
    build_ranking_output_bundle,
    build_ranking_shadow,
    load_ranking_policy,
    summarize_ranking_shadow,
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", help="Ranking input bundle JSON.")
    parser.add_argument("--query-set", help="Optional query set containing a ranking input ref.")
    parser.add_argument("--output", help="Optional ranking shadow result JSON.")
    parser.add_argument("--bundle-output", help="Optional ranking output bundle JSON.")
    parser.add_argument("--identity-output", help="Optional identity shadow JSON.")
    parser.add_argument("--dedup-output", help="Optional dedup shadow JSON.")
    parser.add_argument("--summary-output", help="Optional markdown summary output.")
    parser.add_argument("--check", action="store_true", help="Validate only and write no files.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        policy = load_ranking_policy()
        input_bundle = load_input_bundle(args, policy)
        items = [item for item in input_bundle.get("items", []) if isinstance(item, Mapping)]
        ranking = build_ranking_shadow(input_bundle, policy)
        identity = build_identity_merge_shadow(items, policy)
        dedup = build_dedup_shadow(items, policy)
        output_bundle = build_ranking_output_bundle(input_bundle, ranking, identity, dedup, policy)
        summary = summarize_ranking_shadow(ranking, policy)
        wrote = False
        if not args.check:
            if args.output:
                write_json(args.output, ranking, policy)
                wrote = True
            if args.bundle_output:
                write_json(args.bundle_output, output_bundle, policy)
                wrote = True
            if args.identity_output:
                write_json(args.identity_output, identity, policy)
                wrote = True
            if args.dedup_output:
                write_json(args.dedup_output, dedup, policy)
                wrote = True
            if args.summary_output:
                write_text(args.summary_output, render_markdown(summary), policy)
                wrote = True
        summary["wrote_files"] = wrote
        if args.json:
            print(json.dumps(summary, indent=2, sort_keys=True), file=stdout)
        else:
            print("Ranking shadow", file=stdout)
            print(f"status: {summary['ranking_shadow_status']}", file=stdout)
            print(f"ranked_item_count: {summary['ranked_item_count']}", file=stdout)
            print(f"factor_result_count: {summary['factor_result_count']}", file=stdout)
            print(f"top_item_ref: {summary.get('top_item_ref')}", file=stdout)
            print(f"wrote_files: {str(wrote).lower()}", file=stdout)
        return 0
    except Exception as exc:  # noqa: BLE001
        if args.json:
            print(json.dumps({"status": "invalid", "error": str(exc)}, indent=2, sort_keys=True), file=stdout)
        else:
            print("Ranking shadow", file=stdout)
            print("status: invalid", file=stdout)
            print(f"ERROR: {exc}", file=stdout)
        return 1


def load_input_bundle(args: argparse.Namespace, policy: Mapping[str, Any]) -> dict[str, Any]:
    if args.input:
        return load_json(ensure_allowed_input_path(args.input, policy))
    if args.query_set:
        query_set = load_json(ensure_allowed_input_path(args.query_set, policy))
        for case in query_set.get("query_cases", []):
            if isinstance(case, Mapping) and case.get("ranking_input_bundle_ref"):
                return load_json(ensure_allowed_input_path(str(case["ranking_input_bundle_ref"]), policy))
    raise ValueError("provide --input or --query-set with ranking_input_bundle_ref")


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
    raise ValueError(f"refusing input outside allowed ranking roots: {path}")


def ensure_allowed_output_path(path_text: str, policy: Mapping[str, Any]) -> Path:
    path = resolve_path(path_text, REPO_ROOT)
    if path_under(path, Path(tempfile.gettempdir())):
        return path
    try:
        rel = path.relative_to(REPO_ROOT.resolve()).as_posix().casefold().rstrip("/")
    except ValueError as exc:
        raise ValueError(f"refusing output outside repository approved roots or temp directory: {path}") from exc
    for root_text in policy.get("forbidden_output_roots", []):
        root = str(root_text).casefold().rstrip("/")
        if rel == root or rel.startswith(root + "/"):
            raise ValueError(f"refusing forbidden output root: {root_text}")
    for root_text in policy.get("allowed_output_roots", []):
        root = str(root_text).casefold().rstrip("/")
        if root.endswith("/**/generated"):
            prefix = root[: -len("/**/generated")]
            if rel.startswith(prefix + "/") and "/generated/" in rel:
                return path
            continue
        if "temp" in root:
            continue
        if rel == root or rel.startswith(root + "/"):
            return path
    raise ValueError(f"refusing output outside approved ranking roots: {rel}")


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
            f"- ranking_shadow_status: `{summary.get('ranking_shadow_status')}`",
            f"- ranked_item_count: `{summary.get('ranked_item_count')}`",
            f"- factor_result_count: `{summary.get('factor_result_count')}`",
            f"- top_item_ref: `{summary.get('top_item_ref')}`",
            "- public_ranking_mutated: `false`",
            "- public_search_mutated: `false`",
            "",
        ]
    )


if __name__ == "__main__":
    raise SystemExit(main())
