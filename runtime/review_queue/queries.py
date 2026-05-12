"""Query helpers for the durable review queue store."""

from __future__ import annotations

import json
import sqlite3
from typing import Any, Mapping

from .decisions import ReviewDecision, ReviewDecisionKind
from .records import ReviewEvent, ReviewEventKind, ReviewItemRecord, ReviewQueueStatus, ReviewQueueSummary


def decode_json(text: str) -> Any:
    return json.loads(text)


def encode_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def row_to_review_item(row: sqlite3.Row | Mapping[str, Any]) -> ReviewItemRecord:
    return ReviewItemRecord(
        review_item_id=str(row["review_item_id"]),
        subject_kind=str(row["subject_kind"]),
        subject_id=str(row["subject_id"]),
        queue_status=ReviewQueueStatus(str(row["queue_status"])),
        priority=int(row["priority"]),
        evidence_id=row["evidence_id"],
        source_cache_entry_id=row["source_cache_entry_id"],
        summary=str(row["summary"]),
        payload=dict(decode_json(str(row["payload_json"]))),
        limitations=tuple(str(item) for item in decode_json(str(row["limitations_json"]))),
        warnings=tuple(str(item) for item in decode_json(str(row["warnings_json"]))),
        created_at=str(row["created_at"]),
        updated_at=str(row["updated_at"]),
    )


def row_to_event(row: sqlite3.Row | Mapping[str, Any]) -> ReviewEvent:
    return ReviewEvent(
        event_id=str(row["id"]),
        review_item_id=str(row["review_item_id"]),
        event_kind=ReviewEventKind(str(row["event_kind"])),
        event_payload=dict(decode_json(str(row["event_payload_json"]))),
        limitations=tuple(str(item) for item in decode_json(str(row["limitations_json"]))),
        warnings=tuple(str(item) for item in decode_json(str(row["warnings_json"]))),
        created_at=str(row["created_at"]),
    )


def row_to_decision(row: sqlite3.Row | Mapping[str, Any]) -> ReviewDecision:
    return ReviewDecision(
        decision_id=str(row["id"]),
        review_item_id=str(row["review_item_id"]),
        decision_kind=ReviewDecisionKind(str(row["decision_kind"])),
        decision_status=ReviewQueueStatus(str(row["decision_status"])),
        decision_actor=str(row["decision_actor"]),
        reason=row["reason"],
        payload=dict(decode_json(str(row["payload_json"]))),
        limitations=tuple(str(item) for item in decode_json(str(row["limitations_json"]))),
        warnings=tuple(str(item) for item in decode_json(str(row["warnings_json"]))),
        created_at=str(row["created_at"]),
    )


def summarize_connection(connection: sqlite3.Connection) -> ReviewQueueSummary:
    status_rows = connection.execute(
        "SELECT queue_status, COUNT(*) FROM review_items GROUP BY queue_status ORDER BY queue_status"
    ).fetchall()
    subject_rows = connection.execute(
        "SELECT subject_kind, COUNT(*) FROM review_items GROUP BY subject_kind ORDER BY subject_kind"
    ).fetchall()
    return ReviewQueueSummary(
        review_item_count=_count(connection, "review_items"),
        review_event_count=_count(connection, "review_events"),
        evidence_link_count=_count(connection, "review_evidence_links"),
        source_cache_link_count=_count(connection, "review_source_cache_links"),
        decision_count=_count(connection, "review_decisions"),
        status_counts={str(row[0]): int(row[1]) for row in status_rows},
        subject_kind_counts={str(row[0]): int(row[1]) for row in subject_rows},
    )


def _count(connection: sqlite3.Connection, table: str) -> int:
    row = connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()
    return int(row[0])
