"""SQLite schema for the local SearchNeed store."""

from typing import Any
import sqlite3


SCHEMA_VERSION = "search_need_store.v0"
REQUIRED_TABLES = (
    "search_need_meta",
    "search_needs",
    "search_need_transitions",
    "search_need_hunt_links",
    "search_need_summaries",
)


def apply_schema(connection: sqlite3.Connection) -> list[dict[str, Any]]:
    connection.execute(
        "CREATE TABLE IF NOT EXISTS search_need_meta "
        "(key TEXT PRIMARY KEY, value TEXT NOT NULL)"
    )
    connection.execute(
        "CREATE TABLE IF NOT EXISTS search_needs ("
        "id TEXT PRIMARY KEY, hunt_id TEXT NOT NULL, exhaustion_report_id TEXT NOT NULL, "
        "query TEXT NOT NULL, normalized_query TEXT NOT NULL, need_title TEXT NOT NULL, "
        "need_summary TEXT NOT NULL, need_kind TEXT NOT NULL, desired_outcome TEXT NOT NULL, "
        "priority INTEGER NOT NULL, state TEXT NOT NULL, local_result_state TEXT NOT NULL, "
        "checked_layers_json TEXT NOT NULL, deferred_layers_json TEXT NOT NULL, "
        "recommended_future_work_json TEXT NOT NULL, policy_limitations_json TEXT NOT NULL, "
        "warnings_json TEXT NOT NULL, public_safe_summary_allowed INTEGER NOT NULL, "
        "private_notes_allowed INTEGER NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, "
        "idempotency_key TEXT, superseded_by TEXT)"
    )
    connection.execute(
        "CREATE TABLE IF NOT EXISTS search_need_transitions ("
        "sequence INTEGER PRIMARY KEY AUTOINCREMENT, id TEXT NOT NULL UNIQUE, need_id TEXT NOT NULL, "
        "from_state TEXT, to_state TEXT NOT NULL, reason TEXT, created_at TEXT NOT NULL)"
    )
    connection.execute(
        "CREATE TABLE IF NOT EXISTS search_need_hunt_links ("
        "id TEXT PRIMARY KEY, need_id TEXT NOT NULL, hunt_id TEXT NOT NULL, "
        "exhaustion_report_id TEXT NOT NULL, link_kind TEXT NOT NULL, created_at TEXT NOT NULL)"
    )
    connection.execute(
        "CREATE TABLE IF NOT EXISTS search_need_summaries ("
        "id TEXT PRIMARY KEY, need_id TEXT NOT NULL, summary_type TEXT NOT NULL, "
        "payload_json TEXT NOT NULL, created_at TEXT NOT NULL)"
    )
    connection.execute("CREATE INDEX IF NOT EXISTS idx_search_needs_state ON search_needs(state)")
    connection.execute("CREATE INDEX IF NOT EXISTS idx_search_needs_kind ON search_needs(need_kind)")
    connection.execute("CREATE INDEX IF NOT EXISTS idx_search_needs_hunt ON search_needs(hunt_id)")
    connection.execute("CREATE INDEX IF NOT EXISTS idx_search_needs_idempotency ON search_needs(idempotency_key)")
    connection.execute("CREATE INDEX IF NOT EXISTS idx_search_need_links_hunt ON search_need_hunt_links(hunt_id)")
    connection.execute(
        "INSERT OR REPLACE INTO search_need_meta (key, value) VALUES (?, ?)",
        ("schema_version", SCHEMA_VERSION),
    )
    connection.execute(
        "INSERT INTO search_need_meta (key, value) VALUES (?, ?) "
        "ON CONFLICT(key) DO NOTHING",
        ("created_by", "runtime.search_need"),
    )
    connection.commit()
    return get_schema_events(connection)


def get_schema_events(connection: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = connection.execute("SELECT key, value FROM search_need_meta ORDER BY key").fetchall()
    return [{"key": str(row[0]), "value": str(row[1])} for row in rows]
