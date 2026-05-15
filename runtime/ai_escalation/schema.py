"""SQLite schema for disabled AI escalation gate records."""

from datetime import datetime, timezone
from typing import Any
import sqlite3


SCHEMA_VERSION = "ai_escalation_store.v0"
REQUIRED_TABLES = (
    "ai_escalation_meta",
    "ai_escalation_gates",
    "ai_escalation_preflights",
)


def apply_schema(connection: sqlite3.Connection) -> list[dict[str, Any]]:
    started = utc_now()
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS ai_escalation_meta (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS ai_escalation_gates (
            gate_id TEXT PRIMARY KEY,
            search_hunt_id TEXT NOT NULL,
            search_need_id TEXT NOT NULL DEFAULT '',
            exhaustion_report_id TEXT NOT NULL DEFAULT '',
            agent_research_task_id TEXT NOT NULL DEFAULT '',
            query TEXT NOT NULL,
            normalized_query TEXT NOT NULL,
            state TEXT NOT NULL,
            eligibility_json TEXT NOT NULL,
            input_packet_json TEXT NOT NULL,
            output_classes_json TEXT NOT NULL,
            forbidden_actions_json TEXT NOT NULL,
            provider_enabled INTEGER NOT NULL DEFAULT 0,
            execution_enabled INTEGER NOT NULL DEFAULT 0,
            candidate_only_output INTEGER NOT NULL DEFAULT 1,
            review_required INTEGER NOT NULL DEFAULT 1,
            operator_label TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            warnings_json TEXT NOT NULL,
            limitations_json TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS ai_escalation_preflights (
            preflight_id TEXT PRIMARY KEY,
            gate_id TEXT NOT NULL DEFAULT '',
            search_hunt_id TEXT NOT NULL,
            search_need_id TEXT NOT NULL DEFAULT '',
            exhaustion_report_id TEXT NOT NULL DEFAULT '',
            agent_research_task_id TEXT NOT NULL DEFAULT '',
            state TEXT NOT NULL,
            eligibility_json TEXT NOT NULL,
            input_packet_json TEXT NOT NULL,
            output_classes_json TEXT NOT NULL,
            forbidden_actions_json TEXT NOT NULL,
            safety_checks_json TEXT NOT NULL,
            provider_enabled INTEGER NOT NULL DEFAULT 0,
            execution_enabled INTEGER NOT NULL DEFAULT 0,
            operator_label TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL,
            warnings_json TEXT NOT NULL,
            limitations_json TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_ai_escalation_gates_hunt ON ai_escalation_gates(search_hunt_id, created_at);
        CREATE INDEX IF NOT EXISTS idx_ai_escalation_gates_need ON ai_escalation_gates(search_need_id, created_at);
        CREATE INDEX IF NOT EXISTS idx_ai_escalation_preflights_hunt ON ai_escalation_preflights(search_hunt_id, created_at);
        CREATE INDEX IF NOT EXISTS idx_ai_escalation_preflights_need ON ai_escalation_preflights(search_need_id, created_at);
        """
    )
    connection.execute(
        "INSERT OR REPLACE INTO ai_escalation_meta (key, value, updated_at) VALUES (?, ?, ?)",
        ("schema_version", SCHEMA_VERSION, started),
    )
    connection.execute(
        "INSERT OR REPLACE INTO ai_escalation_meta (key, value, updated_at) VALUES (?, ?, ?)",
        ("schema_event:" + started, "apply_schema", started),
    )
    connection.commit()
    return [{"schema_version": SCHEMA_VERSION, "applied_at": started, "status": "pass"}]


def get_schema_events(connection: sqlite3.Connection) -> list[dict[str, str]]:
    rows = connection.execute(
        "SELECT key, value, updated_at FROM ai_escalation_meta WHERE key LIKE 'schema_event:%' ORDER BY updated_at"
    ).fetchall()
    return [{"key": str(row[0]), "value": str(row[1]), "updated_at": str(row[2])} for row in rows]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
