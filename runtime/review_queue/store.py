"""SQLite-backed review queue store."""

from __future__ import annotations

import hashlib
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from .decisions import ReviewDecision, ReviewDecisionKind
from .errors import ReviewQueueStoreError
from .migrations import apply_migrations, get_applied_migrations
from .queries import encode_json, row_to_decision, row_to_event, row_to_review_item, summarize_connection
from .records import ReviewEvent, ReviewEventKind, ReviewItemRecord, ReviewQueueStatus, utc_now
from .schema import REQUIRED_TABLES, SCHEMA_VERSION
from .validation import (
    ensure_valid,
    validate_review_decision,
    validate_review_event,
    validate_review_item_record,
    validate_review_queue_path,
)


class ReviewQueueStore:
    def __init__(self, path: str | Path, connection: sqlite3.Connection):
        self.path = path
        self.connection = connection
        self.connection.row_factory = sqlite3.Row

    @classmethod
    def open(cls, path: str | Path) -> "ReviewQueueStore":
        ensure_valid(validate_review_queue_path(path))
        if str(path) != ":memory:":
            db_path = Path(path)
            db_path.parent.mkdir(parents=True, exist_ok=True)
            connection = sqlite3.connect(db_path)
            return cls(db_path, connection)
        return cls(":memory:", sqlite3.connect(":memory:"))

    def init(self) -> list[dict[str, object]]:
        return apply_migrations(self.connection)

    def close(self) -> None:
        self.connection.close()

    def __enter__(self) -> "ReviewQueueStore":
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self.close()

    @contextmanager
    def transaction(self) -> Iterator[None]:
        try:
            self.connection.execute("BEGIN")
            yield
            self.connection.commit()
        except sqlite3.Error as exc:
            self.connection.rollback()
            raise ReviewQueueStoreError(str(exc)) from exc

    def enqueue_review_item(self, item: ReviewItemRecord) -> dict[str, object]:
        ensure_valid(validate_review_item_record(item))
        existing = self.get_review_item(item.review_item_id)
        with self.transaction():
            self.connection.execute(
                "INSERT INTO review_items "
                "(id, created_at, updated_at, review_item_id, evidence_id, source_cache_entry_id, subject_kind, subject_id, "
                "queue_status, priority, summary, payload_json, limitations_json, warnings_json) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) "
                "ON CONFLICT(review_item_id) DO UPDATE SET updated_at = excluded.updated_at, evidence_id = excluded.evidence_id, "
                "source_cache_entry_id = excluded.source_cache_entry_id, queue_status = excluded.queue_status, priority = excluded.priority, "
                "summary = excluded.summary, payload_json = excluded.payload_json, limitations_json = excluded.limitations_json, "
                "warnings_json = excluded.warnings_json",
                (
                    item.review_item_id,
                    item.created_at,
                    item.updated_at,
                    item.review_item_id,
                    item.evidence_id,
                    item.source_cache_entry_id,
                    item.subject_kind,
                    item.subject_id,
                    item.queue_status.value,
                    item.priority,
                    item.summary,
                    encode_json(item.payload),
                    encode_json(list(item.limitations)),
                    encode_json(list(item.warnings)),
                ),
            )
            if existing is None:
                self._insert_event(
                    ReviewEvent(
                        review_item_id=item.review_item_id,
                        event_kind=ReviewEventKind.ITEM_CREATED,
                        event_payload={"subject_kind": item.subject_kind, "status": item.queue_status.value},
                    )
                )
        return {"table": "review_items", "record_id": item.review_item_id, "status": "stored"}

    def link_evidence(self, review_item_id: str, evidence_id: str) -> dict[str, object]:
        link_id = "rvel_" + hashlib.sha256(f"{review_item_id}:{evidence_id}".encode("utf-8")).hexdigest()[:16]
        now = utc_now()
        with self.transaction():
            self.connection.execute(
                "INSERT OR IGNORE INTO review_evidence_links (id, created_at, review_item_id, evidence_id) VALUES (?, ?, ?, ?)",
                (link_id, now, review_item_id, evidence_id),
            )
            self.connection.execute(
                "UPDATE review_items SET evidence_id = ?, updated_at = ? WHERE review_item_id = ?",
                (evidence_id, now, review_item_id),
            )
            self._insert_event(
                ReviewEvent(
                    review_item_id=review_item_id,
                    event_kind=ReviewEventKind.EVIDENCE_LINKED,
                    event_payload={"evidence_id": evidence_id},
                )
            )
        return {"table": "review_evidence_links", "record_id": link_id, "status": "linked"}

    def link_source_cache_entry(self, review_item_id: str, source_cache_entry_id: str) -> dict[str, object]:
        link_id = "rvscl_" + hashlib.sha256(f"{review_item_id}:{source_cache_entry_id}".encode("utf-8")).hexdigest()[:16]
        now = utc_now()
        with self.transaction():
            self.connection.execute(
                "INSERT OR IGNORE INTO review_source_cache_links "
                "(id, created_at, review_item_id, source_cache_entry_id) VALUES (?, ?, ?, ?)",
                (link_id, now, review_item_id, source_cache_entry_id),
            )
            self.connection.execute(
                "UPDATE review_items SET source_cache_entry_id = ?, updated_at = ? WHERE review_item_id = ?",
                (source_cache_entry_id, now, review_item_id),
            )
            self._insert_event(
                ReviewEvent(
                    review_item_id=review_item_id,
                    event_kind=ReviewEventKind.SOURCE_CACHE_LINKED,
                    event_payload={"source_cache_entry_id": source_cache_entry_id},
                )
            )
        return {"table": "review_source_cache_links", "record_id": link_id, "status": "linked"}

    def record_decision(self, review_item_id: str, decision: ReviewDecision) -> dict[str, object]:
        if decision.review_item_id != review_item_id:
            decision = ReviewDecision(
                review_item_id=review_item_id,
                decision_kind=decision.decision_kind,
                decision_actor=decision.decision_actor,
                reason=decision.reason,
                decision_status=decision.decision_status,
                decision_id=decision.decision_id,
                payload=decision.payload,
                limitations=decision.limitations,
                warnings=decision.warnings,
                created_at=decision.created_at,
            )
        ensure_valid(validate_review_decision(decision))
        current = self.get_review_item(review_item_id)
        current_status = current.queue_status if current else ReviewQueueStatus.NEEDS_REVIEW
        status = decision.resolved_status(current_status)
        with self.transaction():
            self.connection.execute(
                "INSERT INTO review_decisions "
                "(id, created_at, review_item_id, decision_kind, decision_status, decision_actor, reason, payload_json, "
                "limitations_json, warnings_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    decision.decision_id,
                    decision.created_at,
                    review_item_id,
                    decision.decision_kind.value,
                    status.value,
                    decision.decision_actor,
                    decision.reason,
                    encode_json(decision.payload),
                    encode_json(list(decision.limitations)),
                    encode_json(list(decision.warnings)),
                ),
            )
            self.connection.execute(
                "UPDATE review_items SET queue_status = ?, updated_at = ? WHERE review_item_id = ?",
                (status.value, utc_now(), review_item_id),
            )
            self._insert_event(
                ReviewEvent(
                    review_item_id=review_item_id,
                    event_kind=ReviewEventKind.DECISION_RECORDED,
                    event_payload={
                        "decision_id": decision.decision_id,
                        "decision_kind": decision.decision_kind.value,
                        "decision_status": status.value,
                    },
                )
            )
            if decision.decision_kind in {ReviewDecisionKind.BLOCK, ReviewDecisionKind.SUPERSEDE}:
                self._insert_event(
                    ReviewEvent(
                        review_item_id=review_item_id,
                        event_kind=ReviewEventKind.BLOCKED if decision.decision_kind == ReviewDecisionKind.BLOCK else ReviewEventKind.SUPERSEDED,
                        event_payload={"decision_id": decision.decision_id, "reason": decision.reason},
                    )
                )
            elif status != current_status:
                self._insert_event(
                    ReviewEvent(
                        review_item_id=review_item_id,
                        event_kind=ReviewEventKind.STATUS_CHANGED,
                        event_payload={"from": current_status.value, "to": status.value},
                    )
                )
        return {"table": "review_decisions", "record_id": decision.decision_id, "status": status.value}

    def append_event(self, event: ReviewEvent) -> dict[str, object]:
        ensure_valid(validate_review_event(event))
        with self.transaction():
            self._insert_event(event)
        return {"table": "review_events", "record_id": event.event_id, "status": "appended"}

    def get_review_item(self, review_item_id: str) -> ReviewItemRecord | None:
        row = self.connection.execute("SELECT * FROM review_items WHERE review_item_id = ?", (review_item_id,)).fetchone()
        return row_to_review_item(row) if row else None

    def list_review_items(
        self,
        status: ReviewQueueStatus | str | None = None,
        subject_kind: str | None = None,
        limit: int = 100,
    ) -> list[ReviewItemRecord]:
        sql = "SELECT * FROM review_items"
        params: list[Any] = []
        clauses: list[str] = []
        if status:
            clauses.append("queue_status = ?")
            params.append(status.value if isinstance(status, ReviewQueueStatus) else str(status))
        if subject_kind:
            clauses.append("subject_kind = ?")
            params.append(subject_kind)
        if clauses:
            sql += " WHERE " + " AND ".join(clauses)
        sql += " ORDER BY priority, created_at, review_item_id LIMIT ?"
        params.append(limit)
        return [row_to_review_item(row) for row in self.connection.execute(sql, params).fetchall()]

    def list_events(self, review_item_id: str | None = None, limit: int = 100) -> list[ReviewEvent]:
        sql = "SELECT * FROM review_events"
        params: list[Any] = []
        if review_item_id:
            sql += " WHERE review_item_id = ?"
            params.append(review_item_id)
        sql += " ORDER BY sequence LIMIT ?"
        params.append(limit)
        return [row_to_event(row) for row in self.connection.execute(sql, params).fetchall()]

    def list_decisions(self, review_item_id: str | None = None, limit: int = 100) -> list[ReviewDecision]:
        sql = "SELECT * FROM review_decisions"
        params: list[Any] = []
        if review_item_id:
            sql += " WHERE review_item_id = ?"
            params.append(review_item_id)
        sql += " ORDER BY created_at, id LIMIT ?"
        params.append(limit)
        return [row_to_decision(row) for row in self.connection.execute(sql, params).fetchall()]

    def summarize(self):
        return summarize_connection(self.connection)

    def check_integrity(self) -> dict[str, object]:
        integrity = self.connection.execute("PRAGMA integrity_check").fetchone()[0]
        table_rows = self.connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall()
        tables = {str(row[0]) for row in table_rows}
        missing = [table for table in REQUIRED_TABLES if table not in tables]
        return {
            "status": "pass" if integrity == "ok" and not missing else "fail",
            "sqlite_integrity": str(integrity),
            "schema_version": self.schema_version(),
            "missing_tables": missing,
            "applied_migrations": get_applied_migrations(self.connection),
        }

    def schema_version(self) -> str:
        row = self.connection.execute("SELECT value FROM review_queue_meta WHERE key = ?", ("schema_version",)).fetchone()
        return str(row[0]) if row else SCHEMA_VERSION

    def _insert_event(self, event: ReviewEvent) -> None:
        ensure_valid(validate_review_event(event))
        self.connection.execute(
            "INSERT INTO review_events "
            "(id, created_at, review_item_id, event_kind, event_payload_json, limitations_json, warnings_json) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                event.event_id,
                event.created_at,
                event.review_item_id,
                event.event_kind.value,
                encode_json(event.event_payload),
                encode_json(list(event.limitations)),
                encode_json(list(event.warnings)),
            ),
        )
