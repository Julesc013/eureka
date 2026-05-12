"""Query helpers for durable source cache store."""

from __future__ import annotations

import json
import sqlite3
from typing import Any, Mapping

from .records import SourceCacheEntry, SourceCacheStatus, SourceCacheSummary


def decode_json(text: str) -> Any:
    return json.loads(text)


def encode_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def row_to_cache_entry(row: sqlite3.Row | Mapping[str, Any]) -> SourceCacheEntry:
    return SourceCacheEntry(
        entry_id=str(row["id"]),
        source_id=str(row["source_id"]),
        source_family=str(row["source_family"]),
        trust_lane=str(row["trust_lane"]),
        request_id=str(row["request_id"]),
        response_id=str(row["response_id"]),
        observation_id=str(row["observation_id"]),
        normalized_observation_id=str(row["normalized_observation_id"]),
        response_fingerprint=str(row["response_fingerprint"]),
        status=SourceCacheStatus(str(row["status"])),
        payload=dict(decode_json(str(row["payload_json"]))),
        limitations=tuple(str(item) for item in decode_json(str(row["limitations_json"]))),
        warnings=tuple(str(item) for item in decode_json(str(row["warnings_json"]))),
        created_at=str(row["created_at"]),
        updated_at=str(row["updated_at"]),
    )


def summarize_connection(connection: sqlite3.Connection) -> SourceCacheSummary:
    counts = {
        "source_records": _count(connection, "source_records"),
        "metadata_responses": _count(connection, "metadata_responses"),
        "source_observations": _count(connection, "source_observations"),
        "normalized_observations": _count(connection, "normalized_observations"),
        "cache_entries": _count(connection, "cache_entries"),
    }
    status_rows = connection.execute("SELECT status, COUNT(*) FROM cache_entries GROUP BY status ORDER BY status").fetchall()
    return SourceCacheSummary(
        source_record_count=counts["source_records"],
        metadata_response_count=counts["metadata_responses"],
        source_observation_count=counts["source_observations"],
        normalized_observation_count=counts["normalized_observations"],
        cache_entry_count=counts["cache_entries"],
        status_counts={str(row[0]): int(row[1]) for row in status_rows},
    )


def _count(connection: sqlite3.Connection, table: str) -> int:
    row = connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()
    return int(row[0])
