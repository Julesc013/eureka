"""Query helpers for the durable evidence ledger store."""

from __future__ import annotations

import json
import sqlite3
from typing import Any, Mapping

from .records import (
    EvidenceCandidateRecord,
    EvidenceConflict,
    EvidenceEvent,
    EvidenceEventKind,
    EvidenceLedgerSummary,
    EvidenceReviewStatus,
)


def decode_json(text: str) -> Any:
    return json.loads(text)


def encode_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def row_to_candidate(row: sqlite3.Row | Mapping[str, Any]) -> EvidenceCandidateRecord:
    return EvidenceCandidateRecord(
        evidence_id=str(row["evidence_id"]),
        source_id=str(row["source_id"]),
        source_cache_entry_id=row["source_cache_entry_id"],
        observation_id=str(row["observation_id"]),
        normalized_observation_id=str(row["normalized_observation_id"]),
        claim_kind=str(row["claim_kind"]),
        claim_subject=str(row["claim_subject"]),
        claim_payload=dict(decode_json(str(row["claim_payload_json"]))),
        status=EvidenceReviewStatus(str(row["status"])),
        limitations=tuple(str(item) for item in decode_json(str(row["limitations_json"]))),
        warnings=tuple(str(item) for item in decode_json(str(row["warnings_json"]))),
        created_at=str(row["created_at"]),
        updated_at=str(row["updated_at"]),
    )


def row_to_event(row: sqlite3.Row | Mapping[str, Any]) -> EvidenceEvent:
    return EvidenceEvent(
        event_id=str(row["id"]),
        evidence_id=str(row["evidence_id"]),
        event_kind=EvidenceEventKind(str(row["event_kind"])),
        event_payload=dict(decode_json(str(row["event_payload_json"]))),
        limitations=tuple(str(item) for item in decode_json(str(row["limitations_json"]))),
        warnings=tuple(str(item) for item in decode_json(str(row["warnings_json"]))),
        created_at=str(row["created_at"]),
    )


def row_to_conflict(row: sqlite3.Row | Mapping[str, Any]) -> EvidenceConflict:
    return EvidenceConflict(
        conflict_id=str(row["id"]),
        evidence_id=str(row["evidence_id"]),
        conflicting_evidence_id=row["conflicting_evidence_id"],
        conflict_kind=str(row["conflict_kind"]),
        conflict_payload=dict(decode_json(str(row["conflict_payload_json"]))),
        status=EvidenceReviewStatus(str(row["status"])),
        limitations=tuple(str(item) for item in decode_json(str(row["limitations_json"]))),
        warnings=tuple(str(item) for item in decode_json(str(row["warnings_json"]))),
        created_at=str(row["created_at"]),
        updated_at=str(row["updated_at"]),
    )


def summarize_connection(connection: sqlite3.Connection) -> EvidenceLedgerSummary:
    status_rows = connection.execute(
        "SELECT status, COUNT(*) FROM evidence_candidates GROUP BY status ORDER BY status"
    ).fetchall()
    claim_rows = connection.execute(
        "SELECT claim_kind, COUNT(*) FROM evidence_candidates GROUP BY claim_kind ORDER BY claim_kind"
    ).fetchall()
    return EvidenceLedgerSummary(
        evidence_candidate_count=_count(connection, "evidence_candidates"),
        evidence_event_count=_count(connection, "evidence_events"),
        source_cache_link_count=_count(connection, "evidence_source_cache_links"),
        conflict_count=_count(connection, "evidence_conflicts"),
        review_status_count=_count(connection, "evidence_review_status"),
        status_counts={str(row[0]): int(row[1]) for row in status_rows},
        claim_kind_counts={str(row[0]): int(row[1]) for row in claim_rows},
    )


def _count(connection: sqlite3.Connection, table: str) -> int:
    row = connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()
    return int(row[0])
