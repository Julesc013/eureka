"""SQLite-backed evidence ledger store."""

from __future__ import annotations

import hashlib
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from runtime.source_observation import EvidenceCandidate

from .errors import EvidenceLedgerStoreError
from .migrations import apply_migrations, get_applied_migrations
from .queries import encode_json, row_to_candidate, row_to_conflict, row_to_event, summarize_connection
from .records import (
    EvidenceCandidateRecord,
    EvidenceConflict,
    EvidenceEvent,
    EvidenceEventKind,
    EvidenceReviewStatus,
    utc_now,
)
from .schema import REQUIRED_TABLES, SCHEMA_VERSION
from .validation import (
    ensure_valid,
    validate_evidence_candidate_record,
    validate_evidence_conflict,
    validate_evidence_event,
    validate_evidence_ledger_path,
)


class EvidenceLedgerStore:
    def __init__(self, path: str | Path, connection: sqlite3.Connection):
        self.path = path
        self.connection = connection
        self.connection.row_factory = sqlite3.Row

    @classmethod
    def open(cls, path: str | Path) -> "EvidenceLedgerStore":
        ensure_valid(validate_evidence_ledger_path(path))
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

    def __enter__(self) -> "EvidenceLedgerStore":
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
            raise EvidenceLedgerStoreError(str(exc)) from exc

    def write_evidence_candidate(self, candidate: EvidenceCandidateRecord | EvidenceCandidate) -> dict[str, object]:
        record = candidate if isinstance(candidate, EvidenceCandidateRecord) else EvidenceCandidateRecord.from_candidate(candidate)
        ensure_valid(validate_evidence_candidate_record(record))
        existing = self.get_evidence_candidate(record.evidence_id)
        with self.transaction():
            self.connection.execute(
                "INSERT INTO evidence_candidates "
                "(id, created_at, updated_at, evidence_id, source_id, source_cache_entry_id, observation_id, "
                "normalized_observation_id, claim_kind, claim_subject, claim_payload_json, status, limitations_json, warnings_json) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) "
                "ON CONFLICT(evidence_id) DO UPDATE SET updated_at = excluded.updated_at, source_cache_entry_id = excluded.source_cache_entry_id, "
                "normalized_observation_id = excluded.normalized_observation_id, claim_payload_json = excluded.claim_payload_json, "
                "status = excluded.status, limitations_json = excluded.limitations_json, warnings_json = excluded.warnings_json",
                (
                    record.evidence_id,
                    record.created_at,
                    record.updated_at,
                    record.evidence_id,
                    record.source_id,
                    record.source_cache_entry_id,
                    record.observation_id,
                    record.normalized_observation_id,
                    record.claim_kind,
                    record.claim_subject,
                    encode_json(record.claim_payload),
                    record.status.value,
                    encode_json(list(record.limitations)),
                    encode_json(list(record.warnings)),
                ),
            )
            if existing is None:
                self._insert_event(
                    EvidenceEvent(
                        evidence_id=record.evidence_id,
                        event_kind=EvidenceEventKind.CANDIDATE_CREATED,
                        event_payload={"claim_kind": record.claim_kind, "status": record.status.value},
                    )
                )
        return {"table": "evidence_candidates", "record_id": record.evidence_id, "status": "stored"}

    def append_event(self, event: EvidenceEvent) -> dict[str, object]:
        ensure_valid(validate_evidence_event(event))
        with self.transaction():
            self._insert_event(event)
        return {"table": "evidence_events", "record_id": event.event_id, "status": "appended"}

    def link_source_cache_entry(self, evidence_id: str, source_cache_entry_id: str) -> dict[str, object]:
        link_id = "escl_" + hashlib.sha256(f"{evidence_id}:{source_cache_entry_id}".encode("utf-8")).hexdigest()[:16]
        now = utc_now()
        with self.transaction():
            self.connection.execute(
                "INSERT OR IGNORE INTO evidence_source_cache_links (id, created_at, evidence_id, source_cache_entry_id) "
                "VALUES (?, ?, ?, ?)",
                (link_id, now, evidence_id, source_cache_entry_id),
            )
            self.connection.execute(
                "UPDATE evidence_candidates SET source_cache_entry_id = ?, updated_at = ? WHERE evidence_id = ?",
                (source_cache_entry_id, now, evidence_id),
            )
            self._insert_event(
                EvidenceEvent(
                    evidence_id=evidence_id,
                    event_kind=EvidenceEventKind.SOURCE_CACHE_LINKED,
                    event_payload={"source_cache_entry_id": source_cache_entry_id},
                )
            )
        return {"table": "evidence_source_cache_links", "record_id": link_id, "status": "linked"}

    def record_conflict(self, conflict: EvidenceConflict) -> dict[str, object]:
        ensure_valid(validate_evidence_conflict(conflict))
        with self.transaction():
            self.connection.execute(
                "INSERT INTO evidence_conflicts "
                "(id, created_at, updated_at, evidence_id, conflicting_evidence_id, conflict_kind, conflict_payload_json, "
                "status, limitations_json, warnings_json) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?) "
                "ON CONFLICT(id) DO UPDATE SET updated_at = excluded.updated_at, status = excluded.status, "
                "conflict_payload_json = excluded.conflict_payload_json, limitations_json = excluded.limitations_json, "
                "warnings_json = excluded.warnings_json",
                (
                    conflict.conflict_id,
                    conflict.created_at,
                    conflict.updated_at,
                    conflict.evidence_id,
                    conflict.conflicting_evidence_id,
                    conflict.conflict_kind,
                    encode_json(conflict.conflict_payload),
                    conflict.status.value,
                    encode_json(list(conflict.limitations)),
                    encode_json(list(conflict.warnings)),
                ),
            )
            self._insert_event(
                EvidenceEvent(
                    evidence_id=conflict.evidence_id,
                    event_kind=EvidenceEventKind.CONFLICT_DETECTED,
                    event_payload={"conflict_id": conflict.conflict_id, "conflict_kind": conflict.conflict_kind},
                )
            )
        return {"table": "evidence_conflicts", "record_id": conflict.conflict_id, "status": "stored"}

    def set_review_status(
        self,
        evidence_id: str,
        status: EvidenceReviewStatus | str,
        reason: str | None = None,
    ) -> dict[str, object]:
        review_status = status if isinstance(status, EvidenceReviewStatus) else EvidenceReviewStatus(str(status))
        now = utc_now()
        event = EvidenceEvent(
            evidence_id=evidence_id,
            event_kind=EvidenceEventKind.REVIEW_STATUS_CHANGED,
            event_payload={"status": review_status.value, "reason": reason},
        )
        ensure_valid(validate_evidence_event(event))
        with self.transaction():
            self._insert_event(event)
            self.connection.execute(
                "INSERT INTO evidence_review_status (evidence_id, created_at, updated_at, status, reason, event_id) "
                "VALUES (?, ?, ?, ?, ?, ?) "
                "ON CONFLICT(evidence_id) DO UPDATE SET updated_at = excluded.updated_at, status = excluded.status, "
                "reason = excluded.reason, event_id = excluded.event_id",
                (evidence_id, now, now, review_status.value, reason, event.event_id),
            )
            self.connection.execute(
                "UPDATE evidence_candidates SET status = ?, updated_at = ? WHERE evidence_id = ?",
                (review_status.value, now, evidence_id),
            )
        return {"table": "evidence_review_status", "record_id": evidence_id, "status": review_status.value}

    def get_evidence_candidate(self, evidence_id: str) -> EvidenceCandidateRecord | None:
        row = self.connection.execute("SELECT * FROM evidence_candidates WHERE evidence_id = ?", (evidence_id,)).fetchone()
        return row_to_candidate(row) if row else None

    def list_evidence_candidates(
        self,
        source_id: str | None = None,
        status: EvidenceReviewStatus | str | None = None,
        claim_kind: str | None = None,
        limit: int = 100,
    ) -> list[EvidenceCandidateRecord]:
        sql = "SELECT * FROM evidence_candidates"
        params: list[Any] = []
        clauses: list[str] = []
        if source_id:
            clauses.append("source_id = ?")
            params.append(source_id)
        if status:
            clauses.append("status = ?")
            params.append(status.value if isinstance(status, EvidenceReviewStatus) else str(status))
        if claim_kind:
            clauses.append("claim_kind = ?")
            params.append(claim_kind)
        if clauses:
            sql += " WHERE " + " AND ".join(clauses)
        sql += " ORDER BY created_at, evidence_id LIMIT ?"
        params.append(limit)
        return [row_to_candidate(row) for row in self.connection.execute(sql, params).fetchall()]

    def list_events(self, evidence_id: str | None = None, limit: int = 100) -> list[EvidenceEvent]:
        sql = "SELECT * FROM evidence_events"
        params: list[Any] = []
        if evidence_id:
            sql += " WHERE evidence_id = ?"
            params.append(evidence_id)
        sql += " ORDER BY sequence LIMIT ?"
        params.append(limit)
        return [row_to_event(row) for row in self.connection.execute(sql, params).fetchall()]

    def list_conflicts(self, evidence_id: str | None = None, limit: int = 100) -> list[EvidenceConflict]:
        sql = "SELECT * FROM evidence_conflicts"
        params: list[Any] = []
        if evidence_id:
            sql += " WHERE evidence_id = ?"
            params.append(evidence_id)
        sql += " ORDER BY created_at, id LIMIT ?"
        params.append(limit)
        return [row_to_conflict(row) for row in self.connection.execute(sql, params).fetchall()]

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
        row = self.connection.execute("SELECT value FROM evidence_ledger_meta WHERE key = ?", ("schema_version",)).fetchone()
        return str(row[0]) if row else SCHEMA_VERSION

    def _insert_event(self, event: EvidenceEvent) -> None:
        ensure_valid(validate_evidence_event(event))
        self.connection.execute(
            "INSERT INTO evidence_events "
            "(id, created_at, evidence_id, event_kind, event_payload_json, limitations_json, warnings_json) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                event.event_id,
                event.created_at,
                event.evidence_id,
                event.event_kind.value,
                encode_json(event.event_payload),
                encode_json(list(event.limitations)),
                encode_json(list(event.warnings)),
            ),
        )
