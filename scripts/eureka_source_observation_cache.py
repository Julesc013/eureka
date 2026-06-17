#!/usr/bin/env python3
"""Build and validate local source-observation cache deltas."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local.source_observation_cache import (  # noqa: E402
    SourceObservationCacheError,
    build_delta,
    load_delta_manifest,
    render_markdown_summary,
    status_for_delta,
    validate_delta_path,
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    build_parser = subparsers.add_parser("build-delta", help="Build a local source-observation cache delta.")
    build_parser.add_argument("--source", required=True, choices=("ia_metadata",))
    build_parser.add_argument("--smoke-report", required=True)
    build_parser.add_argument("--out", required=True)
    build_parser.add_argument("--json", action="store_true")

    validate_parser = subparsers.add_parser("validate", help="Validate a source-observation cache delta manifest.")
    validate_parser.add_argument("--delta", required=True)
    validate_parser.add_argument("--strict", action="store_true")
    validate_parser.add_argument("--json", action="store_true")

    status_parser = subparsers.add_parser("status", help="Print source-observation cache delta status.")
    status_parser.add_argument("--delta", required=True)
    status_parser.add_argument("--json", action="store_true")

    report_parser = subparsers.add_parser("report", help="Render the source-observation cache delta Markdown report.")
    report_parser.add_argument("--delta", required=True)

    args = parser.parse_args(argv)
    try:
        if args.command == "build-delta":
            payload = build_delta(source=args.source, smoke_report_path=args.smoke_report, out_dir=args.out)
            if args.json:
                print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True), file=stdout)
            else:
                manifest = dict(payload["manifest"])
                print(f"status: {payload['status']}", file=stdout)
                print(f"delta_id: {manifest.get('delta_id')}", file=stdout)
                print(f"observations_written: {payload['observation_count']}", file=stdout)
                print(f"manifest: {payload['manifest_path']}", file=stdout)
            return 0
        if args.command == "validate":
            payload = validate_delta_path(args.delta, strict=args.strict)
            if args.json:
                print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True), file=stdout)
            elif payload["status"] == "PASS":
                print(f"status: {payload['status']}", file=stdout)
                print(f"delta_id: {payload.get('delta_id')}", file=stdout)
                print(f"observations: {payload.get('observation_count')}", file=stdout)
            else:
                print(f"status: {payload['status']}", file=stderr)
                for error in payload.get("errors", []):
                    print(f"error: {error}", file=stderr)
            return 0 if payload["status"] == "PASS" else 1
        if args.command == "status":
            payload = status_for_delta(args.delta)
            if args.json:
                print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True), file=stdout)
            else:
                _print_status(payload, stdout)
            return 0
        if args.command == "report":
            manifest = load_delta_manifest(args.delta)
            print(render_markdown_summary(manifest), end="", file=stdout)
            return 0
    except SourceObservationCacheError as exc:
        print(f"error: {exc}", file=stderr)
        return 1

    parser.error(f"unsupported command: {args.command}")
    return 2


def _print_status(payload: Mapping[str, Any], stdout: TextIO) -> None:
    print(f"status: {payload.get('status')}", file=stdout)
    print(f"delta_id: {payload.get('delta_id')}", file=stdout)
    print(f"source_family: {payload.get('source_family')}", file=stdout)
    print(f"provider_mode: {payload.get('provider_mode')}", file=stdout)
    print(f"observations: {payload.get('observation_count')}", file=stdout)
    print(f"queries: {payload.get('query_count')}", file=stdout)
    print(f"unsafe_records: {payload.get('unsafe_record_count')}", file=stdout)
    print(f"redacted_errors: {payload.get('redacted_error_count')}", file=stdout)
    print(f"diff_status: {payload.get('diff_status')}", file=stdout)
    print(f"reviewed_master_mutation: {str(payload.get('reviewed_master_mutation')).lower()}", file=stdout)
    print(f"public_index_mutation: {str(payload.get('public_index_mutation')).lower()}", file=stdout)
    print(f"candidate_index_mutation: {str(payload.get('candidate_index_mutation')).lower()}", file=stdout)
    print(f"evidence_ledger_mutation: {str(payload.get('evidence_ledger_mutation')).lower()}", file=stdout)
    print(f"recommended_next_task: {payload.get('recommended_next_task')}", file=stdout)


if __name__ == "__main__":
    raise SystemExit(main())
