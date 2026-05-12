"""SQLite-backed source cache store."""

from __future__ import annotations

import hashlib
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from runtime.source_observation import (
    MetadataResponse,
    NormalizedObservation,
    SourceObservation,
    SourceRecord,
)

from .errors import SourceCacheStoreError
from .migrations import apply_migrations, get_applied_migrations
from .queries import encode_json, row_to_cache_entry, summarize_connection
from .records import SourceCacheEntry, SourceCacheStatus, SourceCacheWrite, utc_now
from .schema import REQUIRED_TABLES, SCHEMA_VERSION
from .validation import ensure_valid, validate_cache_path, validate_source_cache_entry


class SourceCacheStore:
    def __init__(self, path: str | Path, connection: sqlite3.Connection):
        self.path = path
        self.connection = connection
        self.connection.row_factory = sqlite3.Row

    @classmethod
    def open(cls, path: str | Path) -> "SourceCacheStore":
        ensure_valid(validate_cache_path(path))
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

    def __enter__(self) -> "SourceCacheStore":
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
            raise SourceCacheStoreError(str(exc)) from exc

    def write_source_record(self, record: SourceRecord) -> SourceCacheWrite:
        payload = record.to_dict()
        now = utc_now()
        with self.transaction():
            self.connection.execute(
                "INSERT INTO source_records "
                "(id, created_at, updated_at, source_id, source_family, trust_lane, payload_json, limitations_json, warnings_json) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?) "
                "ON CONFLICT(source_id) DO UPDATE SET updated_at = excluded.updated_at, source_family = excluded.source_family, "
                "trust_lane = excluded.trust_lane, payload_json = excluded.payload_json, limitations_json = excluded.limitations_json, "
                "warnings_json = excluded.warnings_json",
                (
                    str(record.source_id),
                    now,
                    now,
                    str(record.source_id),
                    record.source_family,
                    record.trust_lane,
                    encode_json(payload),
                    encode_json(list(record.limitations)),
                    encode_json([]),
                ),
            )
        return SourceCacheWrite("source_records", str(record.source_id), "stored")

    def write_metadata_response(self, response: MetadataResponse) -> SourceCacheWrite:
        payload = response.to_dict()
        now = utc_now()
        with self.transaction():
            self.connection.execute(
                "INSERT INTO metadata_responses "
                "(id, created_at, updated_at, source_id, request_id, response_id, response_fingerprint, status, payload_json, limitations_json, warnings_json) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) "
                "ON CONFLICT(response_id) DO UPDATE SET updated_at = excluded.updated_at, status = excluded.status, "
                "payload_json = excluded.payload_json, limitations_json = excluded.limitations_json, warnings_json = excluded.warnings_json",
                (
                    response.response_id,
                    now,
                    now,
                    str(response.source_id),
                    response.request_id,
                    response.response_id,
                    response.fingerprint.value,
                    response.status,
                    encode_json(payload),
                    encode_json(list(response.limitations)),
                    encode_json(list(response.warnings)),
                ),
            )
        return SourceCacheWrite("metadata_responses", response.response_id, "stored")

    def write_source_observation(self, observation: SourceObservation) -> SourceCacheWrite:
        payload = observation.to_dict()
        now = utc_now()
        with self.transaction():
            self.connection.execute(
                "INSERT INTO source_observations "
                "(id, created_at, updated_at, source_id, request_id, response_id, observation_id, response_fingerprint, status, payload_json, limitations_json, warnings_json) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) "
                "ON CONFLICT(observation_id) DO UPDATE SET updated_at = excluded.updated_at, status = excluded.status, "
                "payload_json = excluded.payload_json, limitations_json = excluded.limitations_json, warnings_json = excluded.warnings_json",
                (
                    observation.observation_id,
                    now,
                    now,
                    str(observation.source_id),
                    observation.request_id,
                    observation.response_id,
                    observation.observation_id,
                    observation.response_fingerprint.value,
                    SourceCacheStatus.CACHED.value,
                    encode_json(payload),
                    encode_json(list(observation.limitations)),
                    encode_json(list(observation.warnings)),
                ),
            )
        return SourceCacheWrite("source_observations", observation.observation_id, "stored")

    def write_normalized_observation(self, observation: NormalizedObservation) -> SourceCacheWrite:
        payload = observation.to_dict()
        now = utc_now()
        with self.transaction():
            self.connection.execute(
                "INSERT INTO normalized_observations "
                "(id, created_at, updated_at, source_id, source_family, observation_id, normalized_observation_id, status, payload_json, limitations_json, warnings_json) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) "
                "ON CONFLICT(normalized_observation_id) DO UPDATE SET updated_at = excluded.updated_at, status = excluded.status, "
                "payload_json = excluded.payload_json, limitations_json = excluded.limitations_json, warnings_json = excluded.warnings_json",
                (
                    observation.normalized_observation_id,
                    now,
                    now,
                    str(observation.source_id),
                    observation.source_family,
                    observation.observation_id,
                    observation.normalized_observation_id,
                    SourceCacheStatus.CACHED.value,
                    encode_json(payload),
                    encode_json(list(observation.limitations)),
                    encode_json(list(observation.warnings)),
                ),
            )
        return SourceCacheWrite("normalized_observations", observation.normalized_observation_id, "stored")

    def write_cache_entry(self, entry: SourceCacheEntry) -> SourceCacheWrite:
        ensure_valid(validate_source_cache_entry(entry))
        with self.transaction():
            self.connection.execute(
                "INSERT INTO cache_entries "
                "(id, created_at, updated_at, source_id, source_family, trust_lane, request_id, response_id, observation_id, "
                "normalized_observation_id, response_fingerprint, status, payload_json, limitations_json, warnings_json) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) "
                "ON CONFLICT(id) DO UPDATE SET updated_at = excluded.updated_at, status = excluded.status, payload_json = excluded.payload_json, "
                "limitations_json = excluded.limitations_json, warnings_json = excluded.warnings_json",
                (
                    entry.entry_id,
                    entry.created_at,
                    entry.updated_at,
                    entry.source_id,
                    entry.source_family,
                    entry.trust_lane,
                    entry.request_id,
                    entry.response_id,
                    entry.observation_id,
                    entry.normalized_observation_id,
                    entry.response_fingerprint,
                    entry.status.value,
                    encode_json(entry.payload),
                    encode_json(list(entry.limitations)),
                    encode_json(list(entry.warnings)),
                ),
            )
        return SourceCacheWrite("cache_entries", entry.entry_id, "stored")

    def get_cache_entry(self, entry_id: str) -> SourceCacheEntry | None:
        row = self.connection.execute("SELECT * FROM cache_entries WHERE id = ?", (entry_id,)).fetchone()
        return row_to_cache_entry(row) if row else None

    def get_source_record(self, source_id: str) -> SourceRecord | None:
        row = self.connection.execute("SELECT payload_json FROM source_records WHERE source_id = ?", (source_id,)).fetchone()
        return SourceRecord.from_dict(_decode_payload(row[0])) if row else None

    def list_cache_entries(
        self,
        source_id: str | None = None,
        status: SourceCacheStatus | str | None = None,
        limit: int = 100,
    ) -> list[SourceCacheEntry]:
        sql = "SELECT * FROM cache_entries"
        params: list[Any] = []
        clauses: list[str] = []
        if source_id:
            clauses.append("source_id = ?")
            params.append(source_id)
        if status:
            clauses.append("status = ?")
            params.append(status.value if isinstance(status, SourceCacheStatus) else str(status))
        if clauses:
            sql += " WHERE " + " AND ".join(clauses)
        sql += " ORDER BY created_at, id LIMIT ?"
        params.append(limit)
        return [row_to_cache_entry(row) for row in self.connection.execute(sql, params).fetchall()]

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
        row = self.connection.execute("SELECT value FROM source_cache_meta WHERE key = ?", ("schema_version",)).fetchone()
        return str(row[0]) if row else SCHEMA_VERSION


def build_cache_entry(
    source_record: SourceRecord,
    response: MetadataResponse,
    observation: SourceObservation,
    normalized_observation: NormalizedObservation,
    status: SourceCacheStatus = SourceCacheStatus.CACHED,
) -> SourceCacheEntry:
    payload = {
        "source_record": source_record.to_dict(),
        "metadata_response": response.to_dict(),
        "source_observation": observation.to_dict(),
        "normalized_observation": normalized_observation.to_dict(),
    }
    entry_id = "sce_" + hashlib.sha256(encode_json(payload).encode("utf-8")).hexdigest()[:16]
    now = utc_now()
    return SourceCacheEntry(
        entry_id=entry_id,
        source_id=str(source_record.source_id),
        source_family=source_record.source_family,
        trust_lane=source_record.trust_lane,
        request_id=response.request_id,
        response_id=response.response_id,
        observation_id=observation.observation_id,
        normalized_observation_id=normalized_observation.normalized_observation_id,
        response_fingerprint=response.fingerprint.value,
        status=status,
        payload=payload,
        limitations=tuple(source_record.limitations + response.limitations + observation.limitations + normalized_observation.limitations),
        warnings=tuple(response.warnings + observation.warnings + normalized_observation.warnings),
        created_at=now,
        updated_at=now,
    )


def _decode_payload(text: str) -> dict[str, Any]:
    import json

    return json.loads(text)
