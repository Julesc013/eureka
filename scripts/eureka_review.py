#!/usr/bin/env python3
"""Materialize local reviewed records from local search index candidates."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local.review_materialization import (
    DEFAULT_REVIEW_LEDGER_PATH,
    DEFAULT_REVIEWED_RECORDS_PATH,
    SUPPORTED_DECISIONS,
    accept_candidate,
    list_candidates,
    review_stats,
)
from runtime.local.search_index import DEFAULT_INDEX_PATH


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    candidates_parser = subparsers.add_parser("candidates", help="List reviewable local index candidates.")
    candidates_parser.add_argument("--index", default=DEFAULT_INDEX_PATH)
    candidates_parser.add_argument("--query", required=True)
    candidates_parser.add_argument("--limit", type=int, default=10)
    candidates_parser.add_argument("--json", action="store_true")

    accept_parser = subparsers.add_parser("accept", help="Accept the deterministic best local index candidate.")
    accept_parser.add_argument("--index", default=DEFAULT_INDEX_PATH)
    accept_parser.add_argument("--query", required=True)
    accept_parser.add_argument("--ledger", default=DEFAULT_REVIEW_LEDGER_PATH)
    accept_parser.add_argument("--records", default=DEFAULT_REVIEWED_RECORDS_PATH)
    accept_parser.add_argument("--reviewer", default="local_demo")
    accept_parser.add_argument("--reason", required=True)
    accept_parser.add_argument("--candidate-id", default="")
    accept_parser.add_argument("--decision", choices=SUPPORTED_DECISIONS, default="accept")
    accept_parser.add_argument("--reviewed-at", default="")
    accept_parser.add_argument("--dry-run", action="store_true")
    accept_parser.add_argument("--json", action="store_true")

    stats_parser = subparsers.add_parser("stats", help="Summarize local review artifacts.")
    stats_parser.add_argument("--ledger", default=DEFAULT_REVIEW_LEDGER_PATH)
    stats_parser.add_argument("--records", default=DEFAULT_REVIEWED_RECORDS_PATH)
    stats_parser.add_argument("--json", action="store_true")

    args = parser.parse_args(argv)
    try:
        if args.command == "candidates":
            payload = list_candidates(args.index, args.query, limit=args.limit)
            if not payload["index_loaded"]:
                return _emit(payload, args.json, stdout, stderr, failed=True)
            return _emit(payload, args.json, stdout, stderr)

        if args.command == "accept":
            payload = accept_candidate(
                index_path=args.index,
                query=args.query,
                ledger_path=args.ledger,
                records_path=args.records,
                reviewer=args.reviewer,
                reason=args.reason,
                candidate_id=args.candidate_id or None,
                decision=args.decision,
                reviewed_at=args.reviewed_at or None,
                dry_run=args.dry_run,
            )
            return _emit(payload, args.json, stdout, stderr)

        if args.command == "stats":
            return _emit(review_stats(args.ledger, args.records), args.json, stdout, stderr)
    except ValueError as exc:
        payload = {
            "schema_version": "eureka.local_review_error.v0",
            "status": "fail",
            "command": args.command,
            "error": str(exc),
            "reviewed_record_created": False,
            "artifact_verified": False,
            "public_index_mutated": False,
            "master_index_mutated": False,
        }
        return _emit(payload, getattr(args, "json", False), stdout, stderr, failed=True)

    parser.error(f"unsupported command: {args.command}")
    return 2


def _emit(payload: Mapping[str, Any], as_json: bool, stdout: TextIO, stderr: TextIO, *, failed: bool = False) -> int:
    if as_json:
        print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True), file=stdout)
    elif payload.get("schema_version") == "eureka.local_review_candidates.v0":
        _print_candidates(payload, stdout)
    elif payload.get("schema_version") == "eureka.local_review_accept_result.v0":
        _print_accept(payload, stdout)
    elif payload.get("schema_version") == "eureka.local_review_stats.v0":
        _print_stats(payload, stdout)
    else:
        print(f"status: {payload.get('status', 'fail')}", file=stderr if failed else stdout)
        print(f"error: {payload.get('error', 'unknown error')}", file=stderr if failed else stdout)
    return 1 if failed else 0


def _print_candidates(payload: Mapping[str, Any], stdout: TextIO) -> None:
    print(f"query: {payload.get('query')}", file=stdout)
    print(f"index: {payload.get('index_path')} loaded={str(payload.get('index_loaded')).lower()}", file=stdout)
    print(f"candidate_count: {payload.get('candidate_count')}", file=stdout)
    for index, candidate in enumerate(payload.get("candidates") or [], start=1):
        if not isinstance(candidate, Mapping):
            continue
        print(f"{index}. [{candidate.get('status')}] {candidate.get('title')}", file=stdout)
        print(f"   candidate_id: {candidate.get('candidate_id')}", file=stdout)
        print(f"   review_state: {candidate.get('review_state')}", file=stdout)
        print(f"   artifact_verified: {str(candidate.get('artifact_verified')).lower()}", file=stdout)
        print(f"   evidence: {', '.join(candidate.get('evidence_hints') or [])}", file=stdout)
        print(f"   non_verified_reason: {candidate.get('non_verified_reason')}", file=stdout)


def _print_accept(payload: Mapping[str, Any], stdout: TextIO) -> None:
    print(f"status: {payload.get('status')}", file=stdout)
    print(f"decision: {payload.get('decision')}", file=stdout)
    print(f"candidate_id: {payload.get('candidate_id')}", file=stdout)
    print(f"review_event_id: {payload.get('review_event_id')}", file=stdout)
    print(f"reviewed_record_id: {payload.get('reviewed_record_id')}", file=stdout)
    print(f"event_written: {str(payload.get('event_written')).lower()}", file=stdout)
    print(f"record_written: {str(payload.get('record_written')).lower()}", file=stdout)
    print(f"artifact_verified: {str(payload.get('artifact_verified')).lower()}", file=stdout)
    print("note: local reviewed metadata/source lead; not verified artifact truth", file=stdout)


def _print_stats(payload: Mapping[str, Any], stdout: TextIO) -> None:
    print(f"ledger: {payload.get('ledger_path')}", file=stdout)
    print(f"records: {payload.get('records_path')}", file=stdout)
    print(f"review_event_count: {payload.get('review_event_count')}", file=stdout)
    print(f"reviewed_record_count: {payload.get('reviewed_record_count')}", file=stdout)
    print(f"decision_counts: {json.dumps(payload.get('decision_counts') or {}, sort_keys=True)}", file=stdout)
    print(f"review_state_counts: {json.dumps(payload.get('review_state_counts') or {}, sort_keys=True)}", file=stdout)
    print(f"artifact_verified_count: {payload.get('artifact_verified_count')}", file=stdout)


if __name__ == "__main__":
    raise SystemExit(main())
