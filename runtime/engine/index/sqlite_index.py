from __future__ import annotations

import json
from pathlib import Path
import sqlite3
from contextlib import closing

from runtime.engine.index.index_record import IndexRecord
from runtime.engine.interfaces.public import Notice
from runtime.engine.interfaces.public.local_index import (
    LocalIndexMetadata,
    LocalIndexRecordSummary,
)


SCHEMA_VERSION = "local_index_v0"
RECORD_KINDS = (
    "resolved_object",
    "synthetic_member",
    "state_or_release",
    "representation",
    "member",
    "evidence",
    "source_record",
)


class LocalIndexError(Exception):
    """Base class for bounded Local Index v0 runtime errors."""


class LocalIndexNotFoundError(LocalIndexError, FileNotFoundError):
    def __init__(self, index_path: Path) -> None:
        self.index_path = index_path
        super().__init__(f"Local index '{index_path}' was not found.")


class LocalIndexSchemaError(LocalIndexError, ValueError):
    def __init__(self, index_path: Path, message: str) -> None:
        self.index_path = index_path
        super().__init__(f"{index_path}: {message}")


class LocalIndexSqliteStore:
    def build(
        self,
        index_path: Path,
        records: tuple[IndexRecord, ...],
    ) -> LocalIndexMetadata:
        index_path.parent.mkdir(parents=True, exist_ok=True)
        if index_path.exists():
            index_path.unlink()
        with closing(sqlite3.connect(index_path)) as connection:
            connection.row_factory = sqlite3.Row
            fts5_available = _detect_fts5_available(connection)
            fts_mode = "fts5" if fts5_available else "fallback_like"
            _create_schema(connection, fts5_available=fts5_available)
            _write_metadata(connection, index_path=index_path, fts_mode=fts_mode)
            _insert_records(connection, records, fts5_available=fts5_available)
            connection.commit()
        return self.read_metadata(index_path)

    def read_metadata(self, index_path: Path) -> LocalIndexMetadata:
        with closing(_open_existing_index(index_path)) as connection:
            _ensure_schema(connection, index_path)
            return _read_metadata(connection, index_path)

    def query(
        self,
        index_path: Path,
        query: str,
        *,
        limit: int = 50,
    ) -> tuple[LocalIndexMetadata, tuple[LocalIndexRecordSummary, ...], tuple[Notice, ...]]:
        normalized_query = query.strip()
        if not normalized_query:
            raise ValueError("query must be a non-empty string.")
        with closing(_open_existing_index(index_path)) as connection:
            _ensure_schema(connection, index_path)
            metadata = _read_metadata(connection, index_path)
            rows = _query_rows(
                connection,
                normalized_query,
                use_fts5=metadata.fts_mode == "fts5",
                limit=limit,
            )
            results = tuple(_row_to_summary(row) for row in rows)
            notices: tuple[Notice, ...] = ()
            if not results:
                notices = (
                    Notice(
                        code="local_index_no_results",
                        severity="info",
                        message=f"No Local Index v0 records matched '{normalized_query}'.",
                    ),
                )
            return metadata, results, notices


def _open_existing_index(index_path: Path) -> sqlite3.Connection:
    if not index_path.is_file():
        raise LocalIndexNotFoundError(index_path)
    connection = sqlite3.connect(index_path)
    connection.row_factory = sqlite3.Row
    return connection


def _detect_fts5_available(connection: sqlite3.Connection) -> bool:
    try:
        connection.execute("CREATE VIRTUAL TABLE temp.fts5_probe USING fts5(content)")
        connection.execute("DROP TABLE temp.fts5_probe")
        return True
    except sqlite3.OperationalError:
        return False


def _create_schema(connection: sqlite3.Connection, *, fts5_available: bool) -> None:
    connection.execute(
        """
        CREATE TABLE index_metadata (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE index_records (
            index_record_id TEXT PRIMARY KEY,
            record_kind TEXT NOT NULL,
            label TEXT NOT NULL,
            summary TEXT,
            target_ref TEXT,
            resolved_resource_id TEXT,
            source_id TEXT,
            source_family TEXT,
            source_label TEXT,
            subject_key TEXT,
            version_or_state TEXT,
            representation_id TEXT,
            member_path TEXT,
            parent_target_ref TEXT,
            parent_resolved_resource_id TEXT,
            parent_representation_id TEXT,
            parent_object_label TEXT,
            member_kind TEXT,
            media_type TEXT,
            size_bytes INTEGER,
            content_hash TEXT,
            content_text TEXT,
            evidence_json TEXT NOT NULL,
            action_hints_json TEXT NOT NULL,
            route_hints_json TEXT NOT NULL,
            search_text TEXT NOT NULL,
            created_by_slice TEXT NOT NULL
        )
        """
    )
    connection.execute(
        "CREATE INDEX idx_index_records_kind ON index_records(record_kind)"
    )
    connection.execute(
        "CREATE INDEX idx_index_records_label ON index_records(label, index_record_id)"
    )
    if fts5_available:
        connection.execute(
            """
            CREATE VIRTUAL TABLE index_records_fts USING fts5(
                index_record_id UNINDEXED,
                search_text
            )
            """
        )


def _write_metadata(
    connection: sqlite3.Connection,
    *,
    index_path: Path,
    fts_mode: str,
) -> None:
    values = {
        "schema_version": SCHEMA_VERSION,
        "fts_mode": fts_mode,
        "index_path": str(index_path),
    }
    for key, value in values.items():
        connection.execute(
            "INSERT INTO index_metadata(key, value) VALUES (?, ?)",
            (key, value),
        )


def _insert_records(
    connection: sqlite3.Connection,
    records: tuple[IndexRecord, ...],
    *,
    fts5_available: bool,
) -> None:
    for record in records:
        search_text = record.search_text()
        connection.execute(
            """
            INSERT INTO index_records(
                index_record_id,
                record_kind,
                label,
                summary,
                target_ref,
                resolved_resource_id,
                source_id,
                source_family,
                source_label,
                subject_key,
                version_or_state,
                representation_id,
                member_path,
                parent_target_ref,
                parent_resolved_resource_id,
                parent_representation_id,
                parent_object_label,
                member_kind,
                media_type,
                size_bytes,
                content_hash,
                content_text,
                evidence_json,
                action_hints_json,
                route_hints_json,
                search_text,
                created_by_slice
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record.index_record_id,
                record.record_kind,
                record.label,
                record.summary,
                record.target_ref,
                record.resolved_resource_id,
                record.source_id,
                record.source_family,
                record.source_label,
                record.subject_key,
                record.version_or_state,
                record.representation_id,
                record.member_path,
                record.parent_target_ref,
                record.parent_resolved_resource_id,
                record.parent_representation_id,
                record.parent_object_label,
                record.member_kind,
                record.media_type,
                record.size_bytes,
                record.content_hash,
                record.content_text,
                json.dumps(list(record.evidence), sort_keys=True),
                json.dumps(list(record.action_hints), sort_keys=True),
                json.dumps(record.route_hints or {}, sort_keys=True),
                search_text,
                record.created_by_slice,
            ),
        )
        if fts5_available:
            connection.execute(
                """
                INSERT INTO index_records_fts(index_record_id, search_text)
                VALUES (?, ?)
                """,
                (record.index_record_id, search_text),
            )


def _ensure_schema(connection: sqlite3.Connection, index_path: Path) -> None:
    try:
        schema_version = connection.execute(
            "SELECT value FROM index_metadata WHERE key = 'schema_version'"
        ).fetchone()
    except sqlite3.OperationalError as error:
        raise LocalIndexSchemaError(index_path, f"Missing Local Index v0 metadata table: {error}.") from error
    if schema_version is None:
        raise LocalIndexSchemaError(index_path, "Missing Local Index v0 schema_version metadata.")
    if schema_version["value"] != SCHEMA_VERSION:
        raise LocalIndexSchemaError(
            index_path,
            f"Unsupported Local Index schema_version '{schema_version['value']}'.",
        )


def _read_metadata(connection: sqlite3.Connection, index_path: Path) -> LocalIndexMetadata:
    metadata_rows = connection.execute(
        "SELECT key, value FROM index_metadata"
    ).fetchall()
    metadata = {str(row["key"]): str(row["value"]) for row in metadata_rows}
    record_count = int(
        connection.execute("SELECT COUNT(*) AS record_count FROM index_records").fetchone()["record_count"]
    )
    counts_rows = connection.execute(
        """
        SELECT record_kind, COUNT(*) AS record_count
        FROM index_records
        GROUP BY record_kind
        ORDER BY record_kind
        """
    ).fetchall()
    record_kind_counts = {
        str(row["record_kind"]): int(row["record_count"]) for row in counts_rows
    }
    for record_kind in RECORD_KINDS:
        record_kind_counts.setdefault(record_kind, 0)
    return LocalIndexMetadata(
        index_path=metadata.get("index_path", str(index_path)),
        fts_mode=metadata.get("fts_mode", "fallback_like"),
        record_count=record_count,
        record_kind_counts=record_kind_counts,
    )


def _query_rows(
    connection: sqlite3.Connection,
    query: str,
    *,
    use_fts5: bool,
    limit: int,
) -> list[sqlite3.Row]:
    normalized_limit = max(1, min(limit, 200))
    if use_fts5:
        try:
            return list(
                connection.execute(
                    """
                    SELECT records.*
                    FROM index_records AS records
                    JOIN index_records_fts AS fts
                      ON fts.index_record_id = records.index_record_id
                    WHERE fts.search_text MATCH ?
                    ORDER BY LOWER(records.label), records.index_record_id
                    LIMIT ?
                    """,
                    (_fts_query(query), normalized_limit),
                ).fetchall()
            )
        except sqlite3.OperationalError:
            pass
    return list(
        connection.execute(
            """
            SELECT *
            FROM index_records
            WHERE search_text LIKE ?
            ORDER BY LOWER(label), index_record_id
            LIMIT ?
            """,
            (f"%{query.casefold()}%", normalized_limit),
        ).fetchall()
    )


def _fts_query(query: str) -> str:
    terms = [term for term in query.strip().split() if term]
    if not terms:
        return '""'
    quoted_terms = ['"' + term.replace('"', '""') + '"' for term in terms]
    return " AND ".join(quoted_terms)


def _row_to_summary(row: sqlite3.Row) -> LocalIndexRecordSummary:
    evidence = json.loads(row["evidence_json"])
    action_hints = json.loads(row["action_hints_json"])
    route_hints = json.loads(row["route_hints_json"])
    return LocalIndexRecordSummary(
        index_record_id=str(row["index_record_id"]),
        record_kind=str(row["record_kind"]),
        label=str(row["label"]),
        summary=_optional_text(row["summary"]),
        target_ref=_optional_text(row["target_ref"]),
        resolved_resource_id=_optional_text(row["resolved_resource_id"]),
        source_id=_optional_text(row["source_id"]),
        source_family=_optional_text(row["source_family"]),
        source_label=_optional_text(row["source_label"]),
        subject_key=_optional_text(row["subject_key"]),
        version_or_state=_optional_text(row["version_or_state"]),
        representation_id=_optional_text(row["representation_id"]),
        member_path=_optional_text(row["member_path"]),
        parent_target_ref=_optional_text(row["parent_target_ref"]),
        parent_resolved_resource_id=_optional_text(row["parent_resolved_resource_id"]),
        parent_representation_id=_optional_text(row["parent_representation_id"]),
        parent_object_label=_optional_text(row["parent_object_label"]),
        member_kind=_optional_text(row["member_kind"]),
        media_type=_optional_text(row["media_type"]),
        size_bytes=_optional_non_negative_int(row["size_bytes"]),
        content_hash=_optional_text(row["content_hash"]),
        evidence=tuple(str(item) for item in evidence if isinstance(item, str)),
        action_hints=tuple(str(item) for item in action_hints if isinstance(item, str)),
        route_hints=route_hints if isinstance(route_hints, dict) else {},
    )


def _optional_text(value: object) -> str | None:
    if isinstance(value, str) and value:
        return value
    return None


def _optional_non_negative_int(value: object) -> int | None:
    if isinstance(value, int) and value >= 0:
        return value
    return None
