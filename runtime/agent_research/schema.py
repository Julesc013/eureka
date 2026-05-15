"""SQLite schema for disabled agent research task records."""

from typing import Any
import sqlite3


SCHEMA_VERSION = "agent_research_store.v0"
REQUIRED_TABLES = (
    "agent_research_meta",
    "agent_research_tasks",
    "agent_research_task_links",
    "agent_research_report_schemas",
)


def apply_schema(connection: sqlite3.Connection) -> list[dict[str, Any]]:
    connection.execute("CREATE TABLE IF NOT EXISTS agent_research_meta (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
    connection.execute(
        "CREATE TABLE IF NOT EXISTS agent_research_tasks ("
        "task_id TEXT PRIMARY KEY, search_hunt_id TEXT NOT NULL, search_need_id TEXT NOT NULL, "
        "exhaustion_report_id TEXT NOT NULL, query TEXT NOT NULL, normalized_query TEXT NOT NULL, "
        "intent TEXT NOT NULL, destination TEXT NOT NULL, checked_layers_json TEXT NOT NULL, "
        "deferred_layers_json TEXT NOT NULL, blocked_by_policy_json TEXT NOT NULL, "
        "known_candidates_json TEXT NOT NULL, known_absence_state TEXT NOT NULL, "
        "steering_preferences_json TEXT NOT NULL, allowed_source_families_json TEXT NOT NULL, "
        "blocked_source_families_json TEXT NOT NULL, research_goals_json TEXT NOT NULL, "
        "forbidden_actions_json TEXT NOT NULL, output_schema_json TEXT NOT NULL, "
        "provider_enabled INTEGER NOT NULL, execution_enabled INTEGER NOT NULL, "
        "created_at TEXT NOT NULL, updated_at TEXT NOT NULL, state TEXT NOT NULL, "
        "warnings_json TEXT NOT NULL, limitations_json TEXT NOT NULL)"
    )
    connection.execute(
        "CREATE TABLE IF NOT EXISTS agent_research_task_links ("
        "id TEXT PRIMARY KEY, task_id TEXT NOT NULL, hunt_id TEXT NOT NULL, need_id TEXT NOT NULL, "
        "exhaustion_report_id TEXT NOT NULL, link_kind TEXT NOT NULL, created_at TEXT NOT NULL)"
    )
    connection.execute(
        "CREATE TABLE IF NOT EXISTS agent_research_report_schemas ("
        "id TEXT PRIMARY KEY, schema_payload_json TEXT NOT NULL, created_at TEXT NOT NULL)"
    )
    connection.execute("CREATE INDEX IF NOT EXISTS idx_agent_research_tasks_state ON agent_research_tasks(state)")
    connection.execute("CREATE INDEX IF NOT EXISTS idx_agent_research_tasks_hunt ON agent_research_tasks(search_hunt_id)")
    connection.execute("CREATE INDEX IF NOT EXISTS idx_agent_research_tasks_need ON agent_research_tasks(search_need_id)")
    connection.execute("CREATE INDEX IF NOT EXISTS idx_agent_research_links_hunt ON agent_research_task_links(hunt_id)")
    connection.execute("CREATE INDEX IF NOT EXISTS idx_agent_research_links_need ON agent_research_task_links(need_id)")
    connection.execute("INSERT OR REPLACE INTO agent_research_meta (key, value) VALUES (?, ?)", ("schema_version", SCHEMA_VERSION))
    connection.execute(
        "INSERT INTO agent_research_meta (key, value) VALUES (?, ?) ON CONFLICT(key) DO NOTHING",
        ("created_by", "runtime.agent_research"),
    )
    connection.commit()
    return get_schema_events(connection)


def get_schema_events(connection: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = connection.execute("SELECT key, value FROM agent_research_meta ORDER BY key").fetchall()
    return [{"key": str(row[0]), "value": str(row[1])} for row in rows]
