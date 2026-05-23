"""SQLite-backed local reviewed public index store."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from .absence import build_absence_report
from .errors import PublicIndexStoreError
from .migrations import apply_migrations, get_applied_migrations
from .records import (
    PublicIndexAbsenceReport,
    PublicIndexRebuild,
    PublicIndexRecord,
    PublicIndexSummary,
    canonical_json,
    utc_now,
)
from .schema import REQUIRED_TABLES, SCHEMA_VERSION
from .search import row_to_public_index_record, search_records
from .validation import (
    ensure_valid,
    validate_public_index_absence_report,
    validate_public_index_path,
    validate_public_index_rebuild,
    validate_public_index_record,
)


def encode_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


class PublicIndexStore:
    def __init__(self, path: str | Path, connection: sqlite3.Connection):
        self.path = path
        self.connection = connection
        self.connection.row_factory = sqlite3.Row

    @classmethod
    def open(cls, path: str | Path) -> "PublicIndexStore":
        ensure_valid(validate_public_index_path(path))
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

    def __enter__(self) -> "PublicIndexStore":
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
            raise PublicIndexStoreError(str(exc)) from exc

    def write_record(self, record: PublicIndexRecord) -> dict[str, object]:
        ensure_valid(validate_public_index_record(record))
        with self.transaction():
            self.connection.execute(
                "INSERT INTO public_index_records "
                "(id, created_at, updated_at, rebuild_id, source_id, source_cache_entry_id, evidence_id, review_item_id, "
                "review_decision_id, title, description, searchable_text, normalized_fields_json, source_family, trust_lane, "
                "limitations_json, warnings_json, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) "
                "ON CONFLICT(id) DO UPDATE SET updated_at = excluded.updated_at, title = excluded.title, "
                "description = excluded.description, searchable_text = excluded.searchable_text, "
                "normalized_fields_json = excluded.normalized_fields_json, limitations_json = excluded.limitations_json, "
                "warnings_json = excluded.warnings_json, status = excluded.status",
                (
                    record.record_id,
                    record.created_at,
                    record.updated_at,
                    None,
                    record.source_id,
                    record.source_cache_entry_id,
                    record.evidence_id,
                    record.review_item_id,
                    record.review_decision_id,
                    record.title,
                    record.description,
                    record.searchable_text,
                    encode_json(record.normalized_fields),
                    record.source_family,
                    record.trust_lane,
                    encode_json(list(record.limitations)),
                    encode_json(list(record.warnings)),
                    "reviewed",
                ),
            )
            self._replace_refs(record)
            self._replace_terms(record)
        return {"table": "public_index_records", "record_id": record.record_id, "status": "stored"}

    def write_rebuild(self, rebuild: PublicIndexRebuild) -> dict[str, object]:
        ensure_valid(validate_public_index_rebuild(rebuild))
        with self.transaction():
            self.connection.execute(
                "INSERT INTO public_index_rebuilds "
                "(id, created_at, rebuild_id, status, included_count, excluded_count, include_statuses_json, source_cache_db, "
                "evidence_ledger_db, review_queue_db, public_index_db, dry_run, limitations_json, warnings_json) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) "
                "ON CONFLICT(rebuild_id) DO UPDATE SET status = excluded.status, included_count = excluded.included_count, "
                "excluded_count = excluded.excluded_count, warnings_json = excluded.warnings_json",
                (
                    rebuild.rebuild_id,
                    rebuild.created_at,
                    rebuild.rebuild_id,
                    rebuild.status,
                    rebuild.included_count,
                    rebuild.excluded_count,
                    encode_json(list(rebuild.include_statuses)),
                    rebuild.source_cache_db,
                    rebuild.evidence_ledger_db,
                    rebuild.review_queue_db,
                    rebuild.public_index_db,
                    1 if rebuild.dry_run else 0,
                    encode_json(list(rebuild.limitations)),
                    encode_json(list(rebuild.warnings)),
                ),
            )
        return {"table": "public_index_rebuilds", "record_id": rebuild.rebuild_id, "status": rebuild.status}

    def get_record(self, record_id: str) -> PublicIndexRecord | None:
        row = self.connection.execute("SELECT * FROM public_index_records WHERE id = ?", (record_id,)).fetchone()
        return row_to_public_index_record(row) if row else None

    def list_records(self, source_id: str | None = None, limit: int = 100) -> list[PublicIndexRecord]:
        sql = "SELECT * FROM public_index_records"
        params: list[Any] = []
        if source_id:
            sql += " WHERE source_id = ?"
            params.append(source_id)
        sql += " ORDER BY updated_at DESC, id LIMIT ?"
        params.append(limit)
        return [row_to_public_index_record(row) for row in self.connection.execute(sql, params).fetchall()]

    def search(self, query: str, limit: int = 20):
        return search_records(self.connection, query, limit=limit)

    def absence_report(self, query: str, checked_sources: tuple[str, ...] | None = None) -> PublicIndexAbsenceReport:
        result_count = len(self.search(query, limit=1))
        if checked_sources is None:
            rows = self.connection.execute(
                "SELECT DISTINCT source_id FROM public_index_records ORDER BY source_id"
            ).fetchall()
            checked_sources = tuple(str(row[0]) for row in rows)
        report = build_absence_report(query, result_count=result_count, checked_sources=checked_sources)
        ensure_valid(validate_public_index_absence_report(report))
        return report

    def summarize(self) -> PublicIndexSummary:
        source_rows = self.connection.execute(
            "SELECT source_id, COUNT(*) FROM public_index_records GROUP BY source_id ORDER BY source_id"
        ).fetchall()
        return PublicIndexSummary(
            record_count=_count(self.connection, "public_index_records"),
            rebuild_count=_count(self.connection, "public_index_rebuilds"),
            source_ref_count=_count(self.connection, "public_index_source_refs"),
            evidence_ref_count=_count(self.connection, "public_index_evidence_refs"),
            review_ref_count=_count(self.connection, "public_index_review_refs"),
            source_counts={str(row[0]): int(row[1]) for row in source_rows},
        )

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
        row = self.connection.execute("SELECT value FROM public_index_meta WHERE key = ?", ("schema_version",)).fetchone()
        return str(row[0]) if row else SCHEMA_VERSION

    def _replace_refs(self, record: PublicIndexRecord) -> None:
        now = utc_now()
        for table in ("public_index_source_refs", "public_index_evidence_refs", "public_index_review_refs"):
            self.connection.execute(f"DELETE FROM {table} WHERE record_id = ?", (record.record_id,))
        source_ref_id = "pisr_" + hashlib.sha256(f"{record.record_id}:{record.source_cache_entry_id}".encode("utf-8")).hexdigest()[:16]
        evidence_ref_id = "pier_" + hashlib.sha256(f"{record.record_id}:{record.evidence_id}".encode("utf-8")).hexdigest()[:16]
        review_ref_id = "pirr_" + hashlib.sha256(
            f"{record.record_id}:{record.review_item_id}:{record.review_decision_id}".encode("utf-8")
        ).hexdigest()[:16]
        self.connection.execute(
            "INSERT INTO public_index_source_refs (id, created_at, record_id, source_id, source_cache_entry_id) "
            "VALUES (?, ?, ?, ?, ?)",
            (source_ref_id, now, record.record_id, record.source_id, record.source_cache_entry_id),
        )
        self.connection.execute(
            "INSERT INTO public_index_evidence_refs (id, created_at, record_id, evidence_id) VALUES (?, ?, ?, ?)",
            (evidence_ref_id, now, record.record_id, record.evidence_id),
        )
        self.connection.execute(
            "INSERT INTO public_index_review_refs (id, created_at, record_id, review_item_id, review_decision_id) "
            "VALUES (?, ?, ?, ?, ?)",
            (review_ref_id, now, record.record_id, record.review_item_id, record.review_decision_id),
        )

    def _replace_terms(self, record: PublicIndexRecord) -> None:
        now = utc_now()
        self.connection.execute("DELETE FROM public_index_search_terms WHERE record_id = ?", (record.record_id,))
        for term in sorted(_tokenize(record.searchable_text)):
            term_id = "pit_" + hashlib.sha256(f"{record.record_id}:{term}".encode("utf-8")).hexdigest()[:16]
            self.connection.execute(
                "INSERT OR IGNORE INTO public_index_search_terms (id, created_at, record_id, term) VALUES (?, ?, ?, ?)",
                (term_id, now, record.record_id, term),
            )


def _count(connection: sqlite3.Connection, table: str) -> int:
    row = connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()
    return int(row[0])


def _tokenize(text: str) -> set[str]:
    cleaned = "".join(char.lower() if char.isalnum() else " " for char in text)
    return {item for item in cleaned.split() if len(item) > 1}
