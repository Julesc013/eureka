#!/usr/bin/env python3
"""Demonstrate the durable review queue store with synthetic data."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.evidence_ledger import EvidenceCandidateRecord, EvidenceLedgerStore
from runtime.evidence_ledger.validation import validate_evidence_ledger_path
from runtime.review_queue import (
    ReviewDecision,
    ReviewDecisionKind,
    ReviewEvent,
    ReviewEventKind,
    ReviewItemRecord,
    ReviewQueueStatus,
    ReviewQueueStore,
)
from runtime.review_queue.validation import validate_review_queue_path
from runtime.source_cache import SourceCacheStatus, SourceCacheStore, build_cache_entry
from runtime.source_cache.validation import validate_cache_path
from runtime.source_observation import build_evidence_candidate
from scripts.demo_source_cache_store import build_demo_objects


FORBIDDEN_OUTPUT_ROOTS = {
    "runtime",
    "contracts",
    "surfaces",
    "site",
    "native",
    "crates",
    "examples",
    ".git",
    ".env",
    "secrets",
    ".aide.local",
    ".local",
    ".cache",
}


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--source-cache-db")
    parser.add_argument("--evidence-db")
    parser.add_argument("--review-db")
    parser.add_argument("--decision", choices=[item.value for item in ReviewDecisionKind], default=ReviewDecisionKind.ACCEPT.value)
    parser.add_argument("--reason")
    parser.add_argument("--output")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    root = Path(args.repo_root).resolve()
    source_cache_db = args.source_cache_db or ":memory:"
    evidence_db = args.evidence_db or ":memory:"
    review_db = args.review_db or ":memory:"
    errors = (
        list(validate_cache_path(source_cache_db))
        + list(validate_evidence_ledger_path(evidence_db))
        + list(validate_review_queue_path(review_db))
    )
    if errors:
        print(json.dumps({"status": "fail", "errors": errors}, indent=2, sort_keys=True), file=stderr)
        return 2
    if args.output:
        output = resolve_output_path(root, args.output)
        if is_forbidden_output(root, output):
            print(f"refusing forbidden output root: {output}", file=stderr)
            return 2
    else:
        output = None

    result = run_demo(source_cache_db, evidence_db, review_db, decision_kind=ReviewDecisionKind(args.decision), reason=args.reason)
    text = json.dumps(result, indent=2, sort_keys=True)
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text + "\n", encoding="utf-8")
    if args.json:
        print(text, file=stdout)
    else:
        print("review queue store demo", file=stdout)
        print(f"review_item_id: {result['review_item']['review_item_id']}", file=stdout)
        print(f"decision_count: {result['summary']['decision_count']}", file=stdout)
    return 0


def run_demo(
    source_cache_db: str | Path = ":memory:",
    evidence_db: str | Path = ":memory:",
    review_db: str | Path = ":memory:",
    decision_kind: ReviewDecisionKind = ReviewDecisionKind.ACCEPT,
    reason: str | None = None,
) -> dict[str, Any]:
    source_record, response, source_observation, normalized_observation = build_demo_objects()
    with SourceCacheStore.open(source_cache_db) as cache_store:
        cache_store.init()
        cache_store.write_source_record(source_record)
        cache_store.write_metadata_response(response)
        cache_store.write_source_observation(source_observation)
        cache_store.write_normalized_observation(normalized_observation)
        cache_entry = build_cache_entry(source_record, response, source_observation, normalized_observation, SourceCacheStatus.CACHED)
        cache_store.write_cache_entry(cache_entry)

    evidence_candidate = build_evidence_candidate(normalized_observation)
    evidence_record = EvidenceCandidateRecord.from_candidate(
        evidence_candidate,
        normalized_observation_id=normalized_observation.normalized_observation_id,
        source_cache_entry_id=cache_entry.entry_id,
    )
    with EvidenceLedgerStore.open(evidence_db) as ledger:
        ledger.init()
        ledger.write_evidence_candidate(evidence_record)
        ledger.link_source_cache_entry(evidence_record.evidence_id, cache_entry.entry_id)
        fetched_evidence = ledger.get_evidence_candidate(evidence_record.evidence_id)

    review_item = ReviewItemRecord.from_evidence(fetched_evidence or evidence_record, source_cache_entry_id=cache_entry.entry_id)
    decision_reason = reason
    if decision_kind in {ReviewDecisionKind.REJECT, ReviewDecisionKind.BLOCK, ReviewDecisionKind.SUPERSEDE} and not decision_reason:
        decision_reason = "synthetic review decision reason"
    decision = ReviewDecision(
        review_item_id=review_item.review_item_id,
        decision_kind=decision_kind,
        decision_actor="operator:local",
        reason=decision_reason,
        payload={"scope": "local_review_flow"},
        limitations=("local review state only",),
    )
    with ReviewQueueStore.open(review_db) as queue:
        queue.init()
        queue.enqueue_review_item(review_item)
        queue.link_evidence(review_item.review_item_id, evidence_record.evidence_id)
        queue.link_source_cache_entry(review_item.review_item_id, cache_entry.entry_id)
        queue.append_event(
            ReviewEvent(
                review_item_id=review_item.review_item_id,
                event_kind=ReviewEventKind.NOTE_ADDED,
                event_payload={"note": "synthetic durable review queue demonstration"},
            )
        )
        queue.record_decision(review_item.review_item_id, decision)
        fetched_item = queue.get_review_item(review_item.review_item_id)
        item_list = queue.list_review_items(subject_kind=review_item.subject_kind)
        event_list = queue.list_events(review_item.review_item_id)
        decision_list = queue.list_decisions(review_item.review_item_id)
        summary = queue.summarize()
        integrity = queue.check_integrity()

    return {
        "schema_version": "review_queue_demo_output.v0",
        "status": "pass",
        "source_cache_entry": cache_entry.to_dict(),
        "evidence_candidate_record": evidence_record.to_dict(),
        "review_item": fetched_item.to_dict() if fetched_item else {},
        "review_items": [item.to_dict() for item in item_list],
        "review_events": [item.to_dict() for item in event_list],
        "review_decisions": [item.to_dict() for item in decision_list],
        "summary": summary.to_dict(),
        "integrity": integrity,
        "public_index_writes_enabled": False,
        "master_index_writes_enabled": False,
        "automatic_acceptance_enabled": False,
    }


def resolve_output_path(root: Path, value: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = root / path
    return path.resolve()


def is_forbidden_output(root: Path, output: Path) -> bool:
    try:
        rel = output.relative_to(root).as_posix()
    except ValueError:
        return False
    return any(rel == item or rel.startswith(item.rstrip("/") + "/") for item in FORBIDDEN_OUTPUT_ROOTS)


if __name__ == "__main__":
    raise SystemExit(main())
