"""SQLite schema for the durable local work queue."""

from datetime import datetime, timezone
import sqlite3
from typing import Any


SCHEMA_VERSION = "workunit_queue_store.v0"

REQUIRED_TABLES = (
    "workunit_queue_meta",
    "workunits",
    "workunit_transitions",
    "workunit_payload_refs",
)

INITIAL_SCHEMA_STATEMENTS = (
    """
CREATE TABLE IF NOT EXISTS workunit_queue_meta (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL,
  updated_at TEXT NOT NULL
)
""",
    """
CREATE TABLE IF NOT EXISTS workunits (
  id TEXT PRIMARY KEY,
  kind TEXT NOT NULL,
  state TEXT NOT NULL,
  title TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  priority TEXT NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  idempotency_key TEXT UNIQUE,
  parent_id TEXT,
  blocked_reason TEXT,
  warnings_json TEXT NOT NULL,
  limitations_json TEXT NOT NULL
)
""",
    """
CREATE TABLE IF NOT EXISTS workunit_transitions (
  sequence INTEGER PRIMARY KEY AUTOINCREMENT,
  id TEXT NOT NULL UNIQUE,
  workunit_id TEXT NOT NULL,
  from_state TEXT NOT NULL,
  to_state TEXT NOT NULL,
  reason TEXT,
  created_at TEXT NOT NULL,
  FOREIGN KEY(workunit_id) REFERENCES workunits(id)
)
""",
    """
CREATE TABLE IF NOT EXISTS workunit_payload_refs (
  id TEXT PRIMARY KEY,
  workunit_id TEXT NOT NULL,
  ref_kind TEXT NOT NULL,
  ref_id TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY(workunit_id) REFERENCES workunits(id)
)
""",
    "CREATE INDEX IF NOT EXISTS idx_workunits_state ON workunits(state)",
    "CREATE INDEX IF NOT EXISTS idx_workunits_kind ON workunits(kind)",
    "CREATE INDEX IF NOT EXISTS idx_workunits_parent_id ON workunits(parent_id)",
    "CREATE INDEX IF NOT EXISTS idx_workunit_transitions_workunit_id ON workunit_transitions(workunit_id)",
)


def apply_schema(connection: sqlite3.Connection) -> list[dict[str, Any]]:
    existing = _schema_version(connection)
    try:
        connection.execute("BEGIN")
        for statement in INITIAL_SCHEMA_STATEMENTS:
            connection.execute(statement)
        connection.execute(
            "INSERT INTO workunit_queue_meta (key, value, updated_at) VALUES (?, ?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = excluded.updated_at",
            ("schema_version", SCHEMA_VERSION, utc_now()),
        )
        connection.commit()
    except sqlite3.Error:
        connection.rollback()
        raise
    if existing == SCHEMA_VERSION:
        return []
    return [
        {
            "migration_id": "001_initial_workunit_queue_store",
            "version": SCHEMA_VERSION,
            "statement_count": len(INITIAL_SCHEMA_STATEMENTS),
        }
    ]


def get_schema_events(connection: sqlite3.Connection) -> list[dict[str, str]]:
    version = _schema_version(connection)
    if not version:
        return []
    return [{"id": "001_initial_workunit_queue_store", "version": version}]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _schema_version(connection: sqlite3.Connection) -> str | None:
    table = connection.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'workunit_queue_meta'"
    ).fetchone()
    if table is None:
        return None
    row = connection.execute("SELECT value FROM workunit_queue_meta WHERE key = ?", ("schema_version",)).fetchone()
    return str(row[0]) if row else None
