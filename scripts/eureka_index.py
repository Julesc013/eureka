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
    LOCAL_DEMO_SOURCE,
    build_local_demo_index,
    load_index,
    render_index_json,
    stats_payload,
    validate_index,
    write_index,
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    build_parser = subparsers.add_parser("build", help="Build a deterministic local search index.")
    build_parser.add_argument("--source", choices=(LOCAL_DEMO_SOURCE,), default=LOCAL_DEMO_SOURCE)
    build_parser.add_argument("--out", default=DEFAULT_INDEX_PATH)
    build_parser.add_argument("--print-json", action="store_true", help="Print the built index JSON instead of a summary.")

    stats_parser = subparsers.add_parser("stats", help="Print local search index counts.")
    stats_parser.add_argument("--index", default=DEFAULT_INDEX_PATH)
    stats_parser.add_argument("--json", action="store_true")

    validate_parser = subparsers.add_parser("validate", help="Validate a local search index.")
    validate_parser.add_argument("--index", default=DEFAULT_INDEX_PATH)
    validate_parser.add_argument("--json", action="store_true")

    args = parser.parse_args(argv)
    if args.command == "build":
        index = build_local_demo_index()
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

    parser.error(f"unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
