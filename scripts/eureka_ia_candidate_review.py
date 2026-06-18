#!/usr/bin/env python3
"""Prepare and gate IA candidate review batches."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local.ia_candidate_review_batch import (  # noqa: E402
    IACandidateReviewBatchError,
    build_review_batch,
    load_review_batch_manifest,
    record_decisions,
    render_markdown_summary,
    status_for_batch,
    validate_batch_path,
    validate_decision_file,
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    prepare_parser = subparsers.add_parser("prepare", help="Prepare a deterministic IA candidate review batch.")
    prepare_parser.add_argument("--source", required=True, choices=("ia_metadata",))
    prepare_parser.add_argument("--source-observation-delta", required=True)
    prepare_parser.add_argument("--candidate-index-delta", required=True)
    prepare_parser.add_argument("--evidence-summary-delta", required=True)
    prepare_parser.add_argument("--out", required=True)
    prepare_parser.add_argument("--json", action="store_true")

    validate_parser = subparsers.add_parser("validate-batch", help="Validate a review batch manifest.")
    validate_parser.add_argument("--batch", required=True)
    validate_parser.add_argument("--strict", action="store_true")
    validate_parser.add_argument("--json", action="store_true")

    status_parser = subparsers.add_parser("status", help="Print review batch status.")
    status_parser.add_argument("--batch", required=True)
    status_parser.add_argument("--json", action="store_true")

    report_parser = subparsers.add_parser("report", help="Render the review batch Markdown report.")
    report_parser.add_argument("--batch", required=True)

    validate_decisions_parser = subparsers.add_parser(
        "validate-decisions",
        help="Validate an explicit operator decision file for a review batch.",
    )
    validate_decisions_parser.add_argument("--batch", required=True)
    validate_decisions_parser.add_argument("--decisions", required=True)
    validate_decisions_parser.add_argument("--strict", action="store_true")
    validate_decisions_parser.add_argument("--json", action="store_true")

    record_parser = subparsers.add_parser(
        "record-decisions",
        help="Record explicit operator decisions to an explicit local review store.",
    )
    record_parser.add_argument("--batch", required=True)
    record_parser.add_argument("--decisions", required=True)
    record_parser.add_argument("--review-store", required=True)
    record_parser.add_argument("--strict", action="store_true")
    record_parser.add_argument("--json", action="store_true")

    args = parser.parse_args(argv)
    try:
        if args.command == "prepare":
            payload = build_review_batch(
                source=args.source,
                source_observation_delta_path=args.source_observation_delta,
                candidate_index_delta_path=args.candidate_index_delta,
                evidence_summary_delta_path=args.evidence_summary_delta,
                out_dir=args.out,
            )
            if args.json:
                print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True), file=stdout)
            else:
                manifest = dict(payload["manifest"])
                print(f"status: {payload['status']}", file=stdout)
                print(f"batch_id: {manifest.get('batch_id')}", file=stdout)
                print(f"review_items_prepared: {payload['review_item_count']}", file=stdout)
                print(f"pending_review_items: {payload['pending_review_count']}", file=stdout)
                print(f"decisions_recorded: {payload['decisions_recorded']}", file=stdout)
                print(f"manifest: {payload['manifest_path']}", file=stdout)
                print(f"operator_review_packet: {payload['operator_packet_path']}", file=stdout)
                print(f"decision_template: {payload['decision_template_path']}", file=stdout)
            return 0
        if args.command == "validate-batch":
            payload = validate_batch_path(args.batch, strict=args.strict)
            if args.json:
                print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True), file=stdout)
            elif payload["status"] == "PASS":
                print(f"status: {payload['status']}", file=stdout)
                print(f"batch_id: {payload.get('batch_id')}", file=stdout)
                print(f"review_items: {payload.get('review_item_count')}", file=stdout)
            else:
                print(f"status: {payload['status']}", file=stderr)
                for error in payload.get("errors", []):
                    print(f"error: {error}", file=stderr)
            return 0 if payload["status"] == "PASS" else 1
        if args.command == "status":
            payload = status_for_batch(args.batch)
            if args.json:
                print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True), file=stdout)
            else:
                _print_status(payload, stdout)
            return 0
        if args.command == "report":
            manifest = load_review_batch_manifest(args.batch)
            print(render_markdown_summary(manifest), end="", file=stdout)
            return 0
        if args.command == "validate-decisions":
            payload = validate_decision_file(
                batch_manifest_path=args.batch,
                decision_file_path=args.decisions,
                strict=args.strict,
            )
            if args.json:
                print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True), file=stdout)
            elif payload["status"] == "PASS":
                print(f"status: {payload['status']}", file=stdout)
                print(f"batch_id: {payload.get('batch_id')}", file=stdout)
                print(f"decisions_validated: {payload.get('decisions_validated')}", file=stdout)
                print(f"omitted_pending: {payload.get('omitted_pending_count')}", file=stdout)
            else:
                print(f"status: {payload['status']}", file=stderr)
                for error in payload.get("errors", []):
                    print(f"error: {error}", file=stderr)
            return 0 if payload["status"] == "PASS" else 1
        if args.command == "record-decisions":
            payload = record_decisions(
                batch_manifest_path=args.batch,
                decision_file_path=args.decisions,
                review_store_path=args.review_store,
                strict=args.strict,
            )
            if args.json:
                print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True), file=stdout)
            else:
                print(f"status: {payload['status']}", file=stdout)
                print(f"batch_id: {payload.get('batch_id')}", file=stdout)
                print(f"actor: {payload.get('actor')}", file=stdout)
                print(f"decisions_recorded: {payload.get('decisions_recorded')}", file=stdout)
                print(f"review_ledger_events_written: {payload.get('review_ledger_events_written')}", file=stdout)
                print(f"reviewed_record_created: {str(payload.get('reviewed_record_created')).lower()}", file=stdout)
                print(f"public_index_mutated: {str(payload.get('public_index_mutated')).lower()}", file=stdout)
            return 0
    except IACandidateReviewBatchError as exc:
        print(f"error: {exc}", file=stderr)
        return 1

    parser.error(f"unsupported command: {args.command}")
    return 2


def _print_status(payload: Mapping[str, Any], stdout: TextIO) -> None:
    print(f"status: {payload.get('status')}", file=stdout)
    print(f"batch_id: {payload.get('batch_id')}", file=stdout)
    print(f"source_family: {payload.get('source_family')}", file=stdout)
    print(f"source_observations: {payload.get('source_observations')}", file=stdout)
    print(f"candidates: {payload.get('candidates')}", file=stdout)
    print(f"evidence_summaries: {payload.get('evidence_summaries')}", file=stdout)
    print(f"review_items: {payload.get('review_items')}", file=stdout)
    print(f"pending_review_items: {payload.get('pending_review_items')}", file=stdout)
    print(f"review_group_counts: {json.dumps(payload.get('review_group_counts', {}), sort_keys=True)}", file=stdout)
    print(f"attention_band_counts: {json.dumps(payload.get('attention_band_counts', {}), sort_keys=True)}", file=stdout)
    print(f"missing_field_counts: {json.dumps(payload.get('missing_field_counts', {}), sort_keys=True)}", file=stdout)
    print(f"insufficient_support_items: {payload.get('insufficient_support_items')}", file=stdout)
    print(f"absence_near_miss_items: {payload.get('absence_near_miss_items')}", file=stdout)
    print(f"live_derived_items: {payload.get('live_derived_items')}", file=stdout)
    print(f"fixture_derived_items: {payload.get('fixture_derived_items')}", file=stdout)
    print(f"decisions_supplied: {str(payload.get('decisions_supplied')).lower()}", file=stdout)
    print(f"decisions_recorded: {payload.get('decisions_recorded')}", file=stdout)
    print(f"automatic_decisions: {str(payload.get('automatic_decisions')).lower()}", file=stdout)
    print(f"automatic_promotion: {str(payload.get('automatic_promotion')).lower()}", file=stdout)
    print(f"reviewed_record_creation: {str(payload.get('reviewed_record_creation')).lower()}", file=stdout)
    print(f"reviewed_master_mutation: {str(payload.get('reviewed_master_mutation')).lower()}", file=stdout)
    print(f"public_index_mutation: {str(payload.get('public_index_mutation')).lower()}", file=stdout)
    print(f"recommended_next_action: {payload.get('recommended_next_action')}", file=stdout)
    print(f"blockers: {json.dumps(payload.get('blockers', []), sort_keys=True)}", file=stdout)


if __name__ == "__main__":
    raise SystemExit(main())
