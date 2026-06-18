#!/usr/bin/env python3
"""Build and validate local evidence-summary ledger deltas."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local.evidence_ledger_summary import (  # noqa: E402
    EvidenceLedgerSummaryError,
    build_delta,
    load_delta_manifest,
    render_markdown_summary,
    status_for_delta,
    validate_delta_path,
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    build_parser = subparsers.add_parser("build-delta", help="Build a local evidence-summary ledger delta.")
    build_parser.add_argument("--source", required=True, choices=("ia_metadata",))
    build_parser.add_argument("--source-observation-delta", required=True)
    build_parser.add_argument("--candidate-index-delta", required=True)
    build_parser.add_argument("--out", required=True)
    build_parser.add_argument("--json", action="store_true")

    validate_parser = subparsers.add_parser("validate", help="Validate an evidence-summary delta manifest.")
    validate_parser.add_argument("--delta", required=True)
    validate_parser.add_argument("--strict", action="store_true")
    validate_parser.add_argument("--json", action="store_true")

    status_parser = subparsers.add_parser("status", help="Print evidence-summary delta status.")
    status_parser.add_argument("--delta", required=True)
    status_parser.add_argument("--json", action="store_true")

    report_parser = subparsers.add_parser("report", help="Render the evidence-summary delta Markdown report.")
    report_parser.add_argument("--delta", required=True)

    args = parser.parse_args(argv)
    try:
        if args.command == "build-delta":
            payload = build_delta(
                source=args.source,
                source_observation_delta_path=args.source_observation_delta,
                candidate_index_delta_path=args.candidate_index_delta,
                out_dir=args.out,
            )
            if args.json:
                print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True), file=stdout)
            else:
                manifest = dict(payload["manifest"])
                print(f"status: {payload['status']}", file=stdout)
                print(f"delta_id: {manifest.get('delta_id')}", file=stdout)
                print(f"evidence_summaries_written: {payload['evidence_summary_count']}", file=stdout)
                print(f"manifest: {payload['manifest_path']}", file=stdout)
            return 0
        if args.command == "validate":
            payload = validate_delta_path(args.delta, strict=args.strict)
            if args.json:
                print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True), file=stdout)
            elif payload["status"] == "PASS":
                print(f"status: {payload['status']}", file=stdout)
                print(f"delta_id: {payload.get('delta_id')}", file=stdout)
                print(f"evidence_summaries: {payload.get('evidence_summary_count')}", file=stdout)
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
    except EvidenceLedgerSummaryError as exc:
        print(f"error: {exc}", file=stderr)
        return 1

    parser.error(f"unsupported command: {args.command}")
    return 2


def _print_status(payload: Mapping[str, Any], stdout: TextIO) -> None:
    print(f"status: {payload.get('status')}", file=stdout)
    print(f"delta_id: {payload.get('delta_id')}", file=stdout)
    print(f"source_family: {payload.get('source_family')}", file=stdout)
    print(f"source_observations: {payload.get('source_observation_count')}", file=stdout)
    print(f"candidates: {payload.get('candidate_count')}", file=stdout)
    print(f"evidence_summaries: {payload.get('evidence_summary_count')}", file=stdout)
    print(f"deduplicated_summaries: {payload.get('deduplicated_evidence_summary_count')}", file=stdout)
    print(f"queries: {payload.get('query_count')}", file=stdout)
    print(f"provider_modes: {json.dumps(payload.get('provider_modes', []), sort_keys=True)}", file=stdout)
    print(f"evidence_type_counts: {json.dumps(payload.get('evidence_type_counts', {}), sort_keys=True)}", file=stdout)
    print(f"support_posture_counts: {json.dumps(payload.get('support_posture_counts', {}), sort_keys=True)}", file=stdout)
    print(f"contradictions: {payload.get('contradiction_count')}", file=stdout)
    print(f"absence_near_miss: {payload.get('absence_near_miss_count')}", file=stdout)
    print(f"insufficient_support: {payload.get('insufficient_support_count')}", file=stdout)
    print(f"source_unavailable: {payload.get('source_unavailable_count')}", file=stdout)
    print(f"orphan_candidate_refs: {payload.get('orphan_candidate_ref_count')}", file=stdout)
    print(f"orphan_source_observation_refs: {payload.get('orphan_source_observation_ref_count')}", file=stdout)
    print(f"diff_status: {payload.get('diff_status')}", file=stdout)
    print(f"reviewed_master_mutation: {str(payload.get('reviewed_master_mutation')).lower()}", file=stdout)
    print(f"public_index_mutation: {str(payload.get('public_index_mutation')).lower()}", file=stdout)
    print(f"candidate_index_store_mutation: {str(payload.get('candidate_index_store_mutation')).lower()}", file=stdout)
    print(f"evidence_ledger_store_mutation: {str(payload.get('evidence_ledger_store_mutation')).lower()}", file=stdout)
    print(f"review_promotion_mutation: {str(payload.get('review_promotion_mutation')).lower()}", file=stdout)
    print(f"accepted_truth_created: {str(payload.get('accepted_truth_created')).lower()}", file=stdout)
    print(f"recommended_next_task: {payload.get('recommended_next_task')}", file=stdout)


if __name__ == "__main__":
    raise SystemExit(main())
