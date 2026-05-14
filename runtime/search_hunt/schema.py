"""SQLite schema for durable local Search Hunt sessions."""

from datetime import datetime, timezone
import sqlite3
from typing import Any


SCHEMA_VERSION = "search_hunt_store.v0"

REQUIRED_TABLES = (
    "search_hunt_meta",
    "search_hunt_sessions",
    "search_hunt_transitions",
    "search_hunt_layers",
    "search_hunt_summaries",
    "search_hunt_commands",
    "search_hunt_steering_preferences",
)

INITIAL_SCHEMA_STATEMENTS = (
    """
CREATE TABLE IF NOT EXISTS search_hunt_meta (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL,
  updated_at TEXT NOT NULL
)
""",
    """
CREATE TABLE IF NOT EXISTS search_hunt_sessions (
  id TEXT PRIMARY KEY,
  query TEXT NOT NULL,
  normalized_query TEXT NOT NULL,
  state TEXT NOT NULL,
  intent TEXT NOT NULL,
  destination TEXT NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  index_snapshot_id TEXT,
  reviewed_result_count INTEGER NOT NULL,
  candidate_result_count INTEGER NOT NULL,
  absence_report_id TEXT,
  checked_layers_json TEXT NOT NULL,
  unchecked_layers_json TEXT NOT NULL,
  limitations_json TEXT NOT NULL,
  warnings_json TEXT NOT NULL,
  idempotency_key TEXT UNIQUE,
  parent_id TEXT
)
""",
    """
CREATE TABLE IF NOT EXISTS search_hunt_transitions (
  sequence INTEGER PRIMARY KEY AUTOINCREMENT,
  id TEXT NOT NULL UNIQUE,
  session_id TEXT NOT NULL,
  from_state TEXT NOT NULL,
  to_state TEXT NOT NULL,
  reason TEXT,
  created_at TEXT NOT NULL,
  FOREIGN KEY(session_id) REFERENCES search_hunt_sessions(id)
)
""",
    """
CREATE TABLE IF NOT EXISTS search_hunt_layers (
  id TEXT PRIMARY KEY,
  session_id TEXT NOT NULL,
  layer_kind TEXT NOT NULL,
  layer_id TEXT NOT NULL,
  summary_json TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY(session_id) REFERENCES search_hunt_sessions(id)
)
""",
    """
CREATE TABLE IF NOT EXISTS search_hunt_summaries (
  id TEXT PRIMARY KEY,
  session_id TEXT NOT NULL,
  summary_type TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY(session_id) REFERENCES search_hunt_sessions(id)
)
""",
    """
CREATE TABLE IF NOT EXISTS search_hunt_commands (
  sequence INTEGER PRIMARY KEY AUTOINCREMENT,
  command_id TEXT NOT NULL UNIQUE,
  hunt_id TEXT NOT NULL,
  command_type TEXT NOT NULL,
  value TEXT,
  reason TEXT NOT NULL,
  operator_label TEXT NOT NULL,
  previous_state TEXT NOT NULL,
  resulting_state TEXT NOT NULL,
  policy_decision TEXT NOT NULL,
  side_effects_json TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY(hunt_id) REFERENCES search_hunt_sessions(id)
)
""",
    """
CREATE TABLE IF NOT EXISTS search_hunt_steering_preferences (
  id TEXT PRIMARY KEY,
  command_id TEXT NOT NULL,
  hunt_id TEXT NOT NULL,
  command_type TEXT NOT NULL,
  value TEXT NOT NULL,
  reason TEXT NOT NULL,
  operator_label TEXT NOT NULL,
  active INTEGER NOT NULL,
  limitations_json TEXT NOT NULL,
  warnings_json TEXT NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  FOREIGN KEY(hunt_id) REFERENCES search_hunt_sessions(id),
  FOREIGN KEY(command_id) REFERENCES search_hunt_commands(command_id)
)
""",
    "CREATE INDEX IF NOT EXISTS idx_search_hunt_sessions_state ON search_hunt_sessions(state)",
    "CREATE INDEX IF NOT EXISTS idx_search_hunt_sessions_query ON search_hunt_sessions(normalized_query)",
    "CREATE INDEX IF NOT EXISTS idx_search_hunt_sessions_parent_id ON search_hunt_sessions(parent_id)",
    "CREATE INDEX IF NOT EXISTS idx_search_hunt_transitions_session_id ON search_hunt_transitions(session_id)",
    "CREATE INDEX IF NOT EXISTS idx_search_hunt_layers_session_id ON search_hunt_layers(session_id)",
    "CREATE INDEX IF NOT EXISTS idx_search_hunt_summaries_session_id ON search_hunt_summaries(session_id)",
    "CREATE INDEX IF NOT EXISTS idx_search_hunt_commands_hunt_id ON search_hunt_commands(hunt_id)",
    "CREATE INDEX IF NOT EXISTS idx_search_hunt_steering_hunt_id ON search_hunt_steering_preferences(hunt_id)",
    "CREATE INDEX IF NOT EXISTS idx_search_hunt_steering_active ON search_hunt_steering_preferences(active)",
)


def apply_schema(connection: sqlite3.Connection) -> list[dict[str, Any]]:
    existing = _schema_version(connection)
    try:
        connection.execute("BEGIN")
        for statement in INITIAL_SCHEMA_STATEMENTS:
            connection.execute(statement)
        connection.execute(
            "INSERT INTO search_hunt_meta (key, value, updated_at) VALUES (?, ?, ?) "
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
            "migration_id": "001_initial_search_hunt_store",
            "version": SCHEMA_VERSION,
            "statement_count": len(INITIAL_SCHEMA_STATEMENTS),
        }
    ]


def get_schema_events(connection: sqlite3.Connection) -> list[dict[str, str]]:
    version = _schema_version(connection)
    if not version:
        return []
    return [{"id": "001_initial_search_hunt_store", "version": version}]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _schema_version(connection: sqlite3.Connection) -> str | None:
    table = connection.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'search_hunt_meta'"
    ).fetchone()
    if table is None:
        return None
    row = connection.execute("SELECT value FROM search_hunt_meta WHERE key = ?", ("schema_version",)).fetchone()
    return str(row[0]) if row else None
