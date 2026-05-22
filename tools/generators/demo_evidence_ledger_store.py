#!/usr/bin/env python3
"""Demonstrate the durable evidence ledger store with synthetic data."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.evidence_ledger import (
    EvidenceCandidateRecord,
    EvidenceConflict,
    EvidenceEvent,
    EvidenceEventKind,
    EvidenceLedgerStore,
    EvidenceReviewStatus,
)
from runtime.evidence_ledger.validation import validate_evidence_ledger_path
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
    parser.add_argument("--output")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    root = Path(args.repo_root).resolve()
    source_cache_db = args.source_cache_db or ":memory:"
    evidence_db = args.evidence_db or ":memory:"
    errors = list(validate_cache_path(source_cache_db)) + list(validate_evidence_ledger_path(evidence_db))
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

    result = run_demo(source_cache_db, evidence_db)
    text = json.dumps(result, indent=2, sort_keys=True)
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text + "\n", encoding="utf-8")
    if args.json:
        print(text, file=stdout)
    else:
        print("evidence ledger store demo", file=stdout)
        print(f"evidence_id: {result['evidence_candidate_record']['evidence_id']}", file=stdout)
        print(f"event_count: {result['summary']['evidence_event_count']}", file=stdout)
    return 0


def run_demo(source_cache_db: str | Path = ":memory:", evidence_db: str | Path = ":memory:") -> dict[str, Any]:
    source_record, response, source_observation, normalized_observation = build_demo_objects()
    with SourceCacheStore.open(source_cache_db) as cache_store:
        cache_store.init()
        cache_store.write_source_record(source_record)
        cache_store.write_metadata_response(response)
        cache_store.write_source_observation(source_observation)
        cache_store.write_normalized_observation(normalized_observation)
        cache_entry = build_cache_entry(
            source_record,
            response,
            source_observation,
            normalized_observation,
            status=SourceCacheStatus.CACHED,
        )
        cache_store.write_cache_entry(cache_entry)

    evidence_candidate = build_evidence_candidate(normalized_observation)
    evidence_record = EvidenceCandidateRecord.from_candidate(
        evidence_candidate,
        normalized_observation_id=normalized_observation.normalized_observation_id,
        source_cache_entry_id=cache_entry.entry_id,
    )
    conflict = EvidenceConflict(
        conflict_id="evcon_" + hashlib.sha256(evidence_record.evidence_id.encode("utf-8")).hexdigest()[:16],
        evidence_id=evidence_record.evidence_id,
        conflict_kind="metadata_disagreement_candidate",
        conflict_payload={"field": "version", "observed": "1.0.0", "other_candidate": "unknown"},
        limitations=("synthetic conflict candidate only",),
    )
    note = EvidenceEvent(
        evidence_id=evidence_record.evidence_id,
        event_kind=EvidenceEventKind.NOTE_ADDED,
        event_payload={"note": "synthetic durable evidence ledger demonstration"},
    )

    with EvidenceLedgerStore.open(evidence_db) as ledger:
        ledger.init()
        ledger.write_evidence_candidate(evidence_record)
        ledger.link_source_cache_entry(evidence_record.evidence_id, cache_entry.entry_id)
        ledger.append_event(note)
        ledger.record_conflict(conflict)
        ledger.set_review_status(evidence_record.evidence_id, EvidenceReviewStatus.NEEDS_REVIEW, reason="manual review required")
        fetched = ledger.get_evidence_candidate(evidence_record.evidence_id)
        evidence_list = ledger.list_evidence_candidates(source_id=evidence_record.source_id)
        event_list = ledger.list_events(evidence_id=evidence_record.evidence_id)
        conflict_list = ledger.list_conflicts(evidence_id=evidence_record.evidence_id)
        summary = ledger.summarize()
        integrity = ledger.check_integrity()

    return {
        "schema_version": "evidence_ledger_demo_output.v0",
        "status": "pass",
        "source_cache_entry": cache_entry.to_dict(),
        "evidence_candidate_record": fetched.to_dict() if fetched else {},
        "evidence_events": [item.to_dict() for item in event_list],
        "evidence_conflicts": [item.to_dict() for item in conflict_list],
        "evidence_list": [item.to_dict() for item in evidence_list],
        "summary": summary.to_dict(),
        "integrity": integrity,
        "review_queue_writes_enabled": False,
        "public_index_writes_enabled": False,
        "master_index_writes_enabled": False,
        "evidence_acceptance_enabled": False,
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
