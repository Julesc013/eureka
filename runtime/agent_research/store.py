"""SQLite-backed disabled agent research task store."""

from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator
import sqlite3
import uuid

from .errors import AgentResearchClosedError, AgentResearchError, AgentResearchNotFoundError
from .queries import encode_json, row_to_task
from .records import AgentResearchTask, AgentResearchTaskState, utc_now
from .report_schema import build_agent_research_report_schema
from .schema import REQUIRED_TABLES, SCHEMA_VERSION, apply_schema, get_schema_events
from .task_builder import build_agent_research_task_from_hunt, build_agent_research_task_from_need
from .validation import validate_agent_research_task, validate_limit, validate_store_path


class AgentResearchStore:
    def __init__(self, path: str | Path, connection: sqlite3.Connection):
        self.path = path
        self.connection = connection
        self.connection.row_factory = sqlite3.Row
        self._closed = False

    @classmethod
    def open(cls, path: str | Path) -> "AgentResearchStore":
        valid_path = validate_store_path(path)
        if str(valid_path) == ":memory:":
            return cls(":memory:", sqlite3.connect(":memory:"))
        db_path = Path(valid_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        return cls(db_path, sqlite3.connect(db_path))

    def init(self) -> list[dict[str, Any]]:
        self._ensure_open()
        migrations = apply_schema(self.connection)
        self._ensure_report_schema_record()
        return migrations

    def close(self) -> None:
        if self._closed:
            return
        self.connection.close()
        self._closed = True

    def __enter__(self) -> "AgentResearchStore":
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self.close()

    @contextmanager
    def transaction(self) -> Iterator[None]:
        self._ensure_open()
        try:
            self.connection.execute("BEGIN")
            yield
            self.connection.commit()
        except sqlite3.Error as exc:
            self.connection.rollback()
            raise AgentResearchError(str(exc)) from exc

    def create_task(self, task: AgentResearchTask) -> AgentResearchTask:
        self._ensure_open()
        validate_agent_research_task(task)
        with self.transaction():
            self.connection.execute(
                "INSERT INTO agent_research_tasks "
                "(task_id, search_hunt_id, search_need_id, exhaustion_report_id, query, normalized_query, "
                "intent, destination, checked_layers_json, deferred_layers_json, blocked_by_policy_json, "
                "known_candidates_json, known_absence_state, steering_preferences_json, allowed_source_families_json, "
                "blocked_source_families_json, research_goals_json, forbidden_actions_json, output_schema_json, "
                "provider_enabled, execution_enabled, created_at, updated_at, state, warnings_json, limitations_json) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                _task_values(task),
            )
            self._insert_link(task)
        return task

    def draft_task_from_hunt(self, runtime: Any, hunt_id: str, *, operator_label: str | None = None) -> AgentResearchTask:
        task = build_agent_research_task_from_hunt(runtime, hunt_id)
        return self.create_task(task)

    def draft_task_from_need(self, runtime: Any, need_id: str, *, operator_label: str | None = None) -> AgentResearchTask:
        task = build_agent_research_task_from_need(runtime, need_id)
        return self.create_task(task)

    def get_task(self, task_id: str) -> AgentResearchTask | None:
        self._ensure_open()
        row = self.connection.execute("SELECT * FROM agent_research_tasks WHERE task_id = ?", (task_id,)).fetchone()
        return row_to_task(row) if row else None

    def list_tasks(
        self,
        state: AgentResearchTaskState | str | None = None,
        hunt_id: str | None = None,
        need_id: str | None = None,
        limit: int = 100,
    ) -> list[AgentResearchTask]:
        self._ensure_open()
        sql = "SELECT * FROM agent_research_tasks"
        params: list[Any] = []
        clauses = []
        if state:
            clauses.append("state = ?")
            params.append(state.value if isinstance(state, AgentResearchTaskState) else str(state))
        if hunt_id:
            clauses.append("search_hunt_id = ?")
            params.append(str(hunt_id))
        if need_id:
            clauses.append("search_need_id = ?")
            params.append(str(need_id))
        if clauses:
            sql += " WHERE " + " AND ".join(clauses)
        sql += " ORDER BY created_at DESC, task_id LIMIT ?"
        params.append(validate_limit(limit))
        return [row_to_task(row) for row in self.connection.execute(sql, params).fetchall()]

    def cancel_task(self, task_id: str, reason: str | None = None) -> AgentResearchTask:
        self._ensure_open()
        task = self.get_task(task_id)
        if task is None:
            raise AgentResearchNotFoundError(f"Agent research task not found: {task_id}")
        if task.state == AgentResearchTaskState.CANCELLED:
            return task
        updated = task.cancelled()
        with self.transaction():
            self.connection.execute(
                "UPDATE agent_research_tasks SET state = ?, updated_at = ? WHERE task_id = ?",
                (updated.state.value, updated.updated_at, updated.task_id),
            )
        return updated

    def summarize(self) -> dict[str, Any]:
        self._ensure_open()
        total = int(self.connection.execute("SELECT COUNT(*) FROM agent_research_tasks").fetchone()[0])
        by_state = {
            str(row[0]): int(row[1])
            for row in self.connection.execute("SELECT state, COUNT(*) FROM agent_research_tasks GROUP BY state ORDER BY state").fetchall()
        }
        return {
            "schema_version": "agent_research_summary.v0",
            "total": total,
            "by_state": by_state,
            "provider_enabled": False,
            "execution_enabled": False,
            "browser_enabled": False,
            "source_probe_enabled": False,
            "candidate_only_output": True,
        }

    def check_integrity(self) -> dict[str, Any]:
        self._ensure_open()
        integrity = self.connection.execute("PRAGMA integrity_check").fetchone()[0]
        table_rows = self.connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall()
        tables = {str(row[0]) for row in table_rows}
        missing = [table for table in REQUIRED_TABLES if table not in tables]
        orphan_links = self.connection.execute(
            "SELECT COUNT(*) FROM agent_research_task_links l LEFT JOIN agent_research_tasks t ON l.task_id = t.task_id WHERE t.task_id IS NULL"
        ).fetchone()
        orphan_count = int(orphan_links[0] or 0)
        disabled_count = self.connection.execute(
            "SELECT COUNT(*) FROM agent_research_tasks WHERE provider_enabled != 0 OR execution_enabled != 0"
        ).fetchone()
        enabled_count = int(disabled_count[0] or 0)
        return {
            "status": "pass" if integrity == "ok" and not missing and orphan_count == 0 and enabled_count == 0 else "fail",
            "sqlite_integrity": str(integrity),
            "schema_version": self.schema_version(),
            "missing_tables": missing,
            "orphan_row_count": orphan_count,
            "enabled_task_count": enabled_count,
            "applied_migrations": get_schema_events(self.connection),
        }

    def schema_version(self) -> str:
        self._ensure_open()
        row = self.connection.execute("SELECT value FROM agent_research_meta WHERE key = ?", ("schema_version",)).fetchone()
        return str(row[0]) if row else SCHEMA_VERSION

    def _ensure_report_schema_record(self) -> None:
        row = self.connection.execute("SELECT id FROM agent_research_report_schemas LIMIT 1").fetchone()
        if row:
            return
        schema = build_agent_research_report_schema().to_dict()
        self.connection.execute(
            "INSERT INTO agent_research_report_schemas (id, schema_payload_json, created_at) VALUES (?, ?, ?)",
            ("ars_" + uuid.uuid4().hex, encode_json(schema), utc_now()),
        )
        self.connection.commit()

    def _insert_link(self, task: AgentResearchTask) -> None:
        self.connection.execute(
            "INSERT INTO agent_research_task_links (id, task_id, hunt_id, need_id, exhaustion_report_id, link_kind, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                "arl_" + uuid.uuid4().hex,
                task.task_id,
                task.search_hunt_id,
                task.search_need_id,
                task.exhaustion_report_id,
                "drafted_from_need" if task.search_need_id else "drafted_from_hunt",
                utc_now(),
            ),
        )

    def _ensure_open(self) -> None:
        if self._closed:
            raise AgentResearchClosedError("AgentResearch store is closed")


def _task_values(task: AgentResearchTask) -> tuple[Any, ...]:
    return (
        task.task_id,
        task.search_hunt_id,
        task.search_need_id,
        task.exhaustion_report_id,
        task.query,
        task.normalized_query,
        task.intent,
        task.destination,
        encode_json(list(task.checked_layers)),
        encode_json(list(task.deferred_layers)),
        encode_json(list(task.blocked_by_policy)),
        encode_json([dict(item) for item in task.known_candidates]),
        task.known_absence_state,
        encode_json([dict(item) for item in task.steering_preferences]),
        encode_json(list(task.allowed_source_families)),
        encode_json(list(task.blocked_source_families)),
        encode_json([item.value for item in task.research_goals]),
        encode_json([item.value for item in task.forbidden_actions]),
        encode_json(dict(task.output_schema)),
        1 if task.provider_enabled else 0,
        1 if task.execution_enabled else 0,
        task.created_at,
        task.updated_at,
        task.state.value,
        encode_json(list(task.warnings)),
        encode_json(list(task.limitations)),
    )
