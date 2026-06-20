#!/usr/bin/env python3
"""Build, inspect, and validate the local Eureka search index."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local.search_index import (
    DEFAULT_INDEX_PATH,
    DEFAULT_PREVIEW_INDEX_PATH,
    LOCAL_DEMO_SOURCE,
    build_local_demo_index,
    load_index,
    render_index_json,
    stats_payload,
    validate_index,
    write_index,
)
from runtime.index.preview import (
    DEFAULT_PREVIEW_INDEX_ROOT,
    PreviewIndexError,
    build_preview_index,
    compare_preview_generations,
    list_preview_generations,
    preview_stats_payload,
    rollback_preview_index,
    search_preview_index,
    validate_preview_index,
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    build_parser = subparsers.add_parser("build", help="Build a deterministic local search index.")
    build_parser.add_argument("--source", choices=(LOCAL_DEMO_SOURCE,), default=LOCAL_DEMO_SOURCE)
    build_parser.add_argument("--reviewed-records", default="", help="Optional local reviewed-record JSONL input.")
    build_parser.add_argument("--out", default=DEFAULT_INDEX_PATH)
    build_parser.add_argument("--print-json", action="store_true", help="Print the built index JSON instead of a summary.")

    stats_parser = subparsers.add_parser("stats", help="Print local search index counts.")
    stats_parser.add_argument("--index", default=DEFAULT_INDEX_PATH)
    stats_parser.add_argument("--json", action="store_true")

    validate_parser = subparsers.add_parser("validate", help="Validate a local search index.")
    validate_parser.add_argument("--index", default=DEFAULT_INDEX_PATH)
    validate_parser.add_argument("--json", action="store_true")

    preview_build = subparsers.add_parser("preview-build", help="Build an E2E Preview Index generation.")
    preview_build.add_argument("--runs-root", default="")
    preview_build.add_argument("--candidate-delta", default="")
    preview_build.add_argument("--evidence-delta", default="")
    preview_build.add_argument("--source-observation-delta", default="")
    preview_build.add_argument("--reviewed-records", default="")
    preview_build.add_argument("--out", default=str(DEFAULT_PREVIEW_INDEX_ROOT))
    preview_build.add_argument("--json", action="store_true")

    preview_validate = subparsers.add_parser("preview-validate", help="Validate an E2E Preview Index generation.")
    preview_validate.add_argument("--index", default=DEFAULT_PREVIEW_INDEX_PATH)
    preview_validate.add_argument("--strict", action="store_true")
    preview_validate.add_argument("--json", action="store_true")

    preview_stats = subparsers.add_parser("preview-stats", help="Print E2E Preview Index stats.")
    preview_stats.add_argument("--index", default=DEFAULT_PREVIEW_INDEX_PATH)
    preview_stats.add_argument("--json", action="store_true")

    preview_search = subparsers.add_parser("preview-search", help="Search an E2E Preview Index.")
    preview_search.add_argument("--index", default=DEFAULT_PREVIEW_INDEX_PATH)
    preview_search.add_argument("--query", required=True)
    preview_search.add_argument("--limit", type=int, default=10)
    preview_search.add_argument("--include-synthetic", action="store_true")
    preview_search.add_argument("--include-rejected", action="store_true")
    preview_search.add_argument("--include-superseded", action="store_true")
    preview_search.add_argument("--status", default="")
    preview_search.add_argument("--authority", default="")
    preview_search.add_argument("--source-family", default="")
    preview_search.add_argument("--run-id", default="")
    preview_search.add_argument("--json", action="store_true")

    preview_list = subparsers.add_parser("preview-list-generations", help="List E2E Preview Index generations.")
    preview_list.add_argument("--root", default=str(DEFAULT_PREVIEW_INDEX_ROOT))
    preview_list.add_argument("--json", action="store_true")

    preview_rollback = subparsers.add_parser("preview-rollback", help="Rollback the E2E Preview Index current pointer.")
    preview_rollback.add_argument("--root", default=str(DEFAULT_PREVIEW_INDEX_ROOT))
    preview_rollback.add_argument("--to", required=True)
    preview_rollback.add_argument("--json", action="store_true")

    preview_compare = subparsers.add_parser("preview-compare", help="Compare two E2E Preview Index generations.")
    preview_compare.add_argument("--root", default=str(DEFAULT_PREVIEW_INDEX_ROOT))
    preview_compare.add_argument("--left", required=True)
    preview_compare.add_argument("--right", required=True)
    preview_compare.add_argument("--json", action="store_true")

    args = parser.parse_args(argv)
    if args.command == "build":
        try:
            index = build_local_demo_index(reviewed_records_path=args.reviewed_records or None)
        except ValueError as exc:
            print(f"Index build failed: {exc}", file=stderr)
            return 1
        errors = validate_index(index)
        if errors:
            print("Index build produced invalid output:", file=stderr)
            for error in errors:
                print(f"- {error}", file=stderr)
            return 1
        write_index(args.out, index)
        if args.print_json:
            print(render_index_json(index), end="", file=stdout)
        else:
            stats = stats_payload(index)
            print(f"Built Eureka local search index: {args.out}", file=stdout)
            print(f"source: {stats['source']}", file=stdout)
            print(f"source_digest: {stats['source_digest']}", file=stdout)
            print(f"document_count: {stats['document_count']}", file=stdout)
            print(f"status_counts: {json.dumps(stats['status_counts'], sort_keys=True)}", file=stdout)
            print(f"source_family_counts: {json.dumps(stats['source_family_counts'], sort_keys=True)}", file=stdout)
            print(f"reviewed_record_count: {stats['reviewed_record_count']}", file=stdout)
            print(f"review_state_counts: {json.dumps(stats['review_state_counts'], sort_keys=True)}", file=stdout)
            print(f"artifact_verified_count: {stats['artifact_verified_count']}", file=stdout)
        return 0

    if args.command == "stats":
        try:
            index = load_index(args.index)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"Could not read index: {type(exc).__name__}", file=stderr)
            return 1
        stats = stats_payload(index)
        if args.json:
            print(json.dumps(stats, indent=2, sort_keys=True, ensure_ascii=True), file=stdout)
        else:
            print(f"index: {args.index}", file=stdout)
            print(f"schema: {stats['index_schema_version']}", file=stdout)
            print(f"source: {stats['source']}", file=stdout)
            print(f"source_digest: {stats['source_digest']}", file=stdout)
            print(f"document_count: {stats['document_count']}", file=stdout)
            print(f"status_counts: {json.dumps(stats['status_counts'], sort_keys=True)}", file=stdout)
            print(f"source_family_counts: {json.dumps(stats['source_family_counts'], sort_keys=True)}", file=stdout)
            print(f"reviewed_record_count: {stats['reviewed_record_count']}", file=stdout)
            print(f"review_state_counts: {json.dumps(stats['review_state_counts'], sort_keys=True)}", file=stdout)
            print(f"artifact_verified_count: {stats['artifact_verified_count']}", file=stdout)
        return 0

    if args.command == "validate":
        try:
            index = load_index(args.index)
        except (OSError, json.JSONDecodeError) as exc:
            payload = {"status": "fail", "index": args.index, "errors": [f"Could not read index: {type(exc).__name__}"]}
            if args.json:
                print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True), file=stdout)
            else:
                print(payload["errors"][0], file=stderr)
            return 1
        errors = validate_index(index)
        payload = {"status": "pass" if not errors else "fail", "index": args.index, "errors": errors}
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True), file=stdout)
        elif errors:
            print(f"Index validation failed: {args.index}", file=stderr)
            for error in errors:
                print(f"- {error}", file=stderr)
        else:
            print(f"Index validation passed: {args.index}", file=stdout)
        return 0 if not errors else 1

    if args.command == "preview-build":
        try:
            payload = build_preview_index(
                out_root=args.out,
                runs_root=args.runs_root or None,
                candidate_delta=args.candidate_delta or None,
                evidence_delta=args.evidence_delta or None,
                source_observation_delta=args.source_observation_delta or None,
                reviewed_records=args.reviewed_records or None,
                activate=True,
            )
        except (OSError, json.JSONDecodeError, PreviewIndexError, ValueError) as exc:
            print(f"Preview index build failed: {exc}", file=stderr)
            return 1
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True), file=stdout)
        else:
            print(f"Built Eureka E2E Preview Index: {payload['current_path']}", file=stdout)
            print(f"preview_index_id: {payload['preview_index_id']}", file=stdout)
            print(f"record_count: {payload['record_count']}", file=stdout)
            print(f"status_counts: {json.dumps(payload['status_counts'], sort_keys=True)}", file=stdout)
        return 0

    if args.command == "preview-validate":
        payload = validate_preview_index(args.index, strict=args.strict, write_report=True)
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True), file=stdout)
        elif payload["status"] == "pass":
            print(f"Preview index validation passed: {args.index}", file=stdout)
        else:
            print(f"Preview index validation failed: {args.index}", file=stderr)
            for error in payload["errors"]:
                print(f"- {error}", file=stderr)
        return 0 if payload["status"] == "pass" else 1

    if args.command == "preview-stats":
        try:
            payload = preview_stats_payload(args.index)
        except (OSError, json.JSONDecodeError, PreviewIndexError) as exc:
            print(f"Could not read preview index: {type(exc).__name__}", file=stderr)
            return 1
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True), file=stdout)
        else:
            print(f"preview_index_id: {payload['preview_index_id']}", file=stdout)
            print(f"generation_id: {payload['generation_id']}", file=stdout)
            print(f"record_count: {payload['record_count']}", file=stdout)
            print(f"status_counts: {json.dumps(payload['status_counts'], sort_keys=True)}", file=stdout)
        return 0

    if args.command == "preview-search":
        try:
            payload = search_preview_index(
                args.index,
                args.query,
                limit=args.limit,
                include_synthetic=args.include_synthetic,
                include_rejected=args.include_rejected,
                include_superseded=args.include_superseded,
                status=args.status or None,
                authority=args.authority or None,
                source_family=args.source_family or None,
                run_id=args.run_id or None,
            )
        except (OSError, json.JSONDecodeError, PreviewIndexError) as exc:
            print(f"Preview search failed: {exc}", file=stderr)
            return 1
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True), file=stdout)
        else:
            print(f"Preview search results: {payload['result_count']}", file=stdout)
            for result in payload["results"]:
                print(f"- [{result['status']}/{result['authority']}] {result['title']}", file=stdout)
        return 0

    if args.command == "preview-list-generations":
        payload = list_preview_generations(args.root)
        print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) if args.json else f"generation_count: {payload['generation_count']}", file=stdout)
        return 0

    if args.command == "preview-rollback":
        try:
            payload = rollback_preview_index(args.root, args.to)
        except (OSError, json.JSONDecodeError, PreviewIndexError) as exc:
            print(f"Preview rollback failed: {exc}", file=stderr)
            return 1
        print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) if args.json else f"rolled back to: {payload['to_generation']}", file=stdout)
        return 0

    if args.command == "preview-compare":
        try:
            payload = compare_preview_generations(args.root, args.left, args.right)
        except (OSError, json.JSONDecodeError, PreviewIndexError) as exc:
            print(f"Preview compare failed: {exc}", file=stderr)
            return 1
        print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) if args.json else f"unchanged_count: {payload['unchanged_count']}", file=stdout)
        return 0

    parser.error(f"unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
