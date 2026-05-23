"""SQLite-backed durable local SearchNeed store."""

from contextlib import contextmanager
from dataclasses import replace
from pathlib import Path
from typing import Any, Iterator
import sqlite3
import uuid

from .errors import SearchNeedClosedError, SearchNeedError, SearchNeedNotFoundError
from .queries import encode_json, row_to_need, row_to_summary, row_to_transition
from .records import SearchNeed, SearchNeedKind, SearchNeedState, SearchNeedSummary, SearchNeedTransition, utc_now
from .schema import REQUIRED_TABLES, SCHEMA_VERSION, apply_schema, get_schema_events
from .summaries import build_search_need_summary
from .transitions import apply_transition
from .validation import validate_limit, validate_search_need, validate_store_path


class SearchNeedStore:
    def __init__(self, path: str | Path, connection: sqlite3.Connection):
        self.path = path
        self.connection = connection
        self.connection.row_factory = sqlite3.Row
        self._closed = False

    @classmethod
    def open(cls, path: str | Path) -> "SearchNeedStore":
        valid_path = validate_store_path(path)
        if str(valid_path) == ":memory:":
            return cls(":memory:", sqlite3.connect(":memory:"))
        db_path = Path(valid_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        return cls(db_path, sqlite3.connect(db_path))

    def init(self) -> list[dict[str, Any]]:
        self._ensure_open()
        return apply_schema(self.connection)

    def close(self) -> None:
        if self._closed:
            return
        self.connection.close()
        self._closed = True

    def __enter__(self) -> "SearchNeedStore":
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
            raise SearchNeedError(str(exc)) from exc

    def create_need(self, need: SearchNeed) -> SearchNeed:
        self._ensure_open()
        validate_search_need(need)
        existing = self._dedupe_need(need)
        if existing is not None:
            return existing
        with self.transaction():
            self.connection.execute(
                "INSERT INTO search_needs "
                "(id, hunt_id, exhaustion_report_id, query, normalized_query, need_title, need_summary, "
                "need_kind, desired_outcome, priority, state, local_result_state, checked_layers_json, "
                "deferred_layers_json, recommended_future_work_json, policy_limitations_json, warnings_json, "
                "public_safe_summary_allowed, private_notes_allowed, created_at, updated_at, idempotency_key, superseded_by) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                _need_values(need),
            )
            self._insert_transition(SearchNeedTransition.new(need.id, None, need.state, "created"))
            self._insert_hunt_link(need)
            self._insert_summary(SearchNeedSummary.new(need.id, "search_need_summary", build_search_need_summary(need)))
        return need

    def create_need_from_hunt(
        self,
        runtime: Any,
        hunt_id: str,
        *,
        operator_label: str | None = None,
        idempotency_key: str | None = None,
    ) -> SearchNeed:
        from .from_hunt import build_search_need_from_hunt

        need = build_search_need_from_hunt(runtime, hunt_id, operator_label=operator_label)
        if idempotency_key:
            need = replace(need, idempotency_key=idempotency_key)
        return self.create_need(need)

    def get_need(self, need_id: str) -> SearchNeed | None:
        self._ensure_open()
        row = self.connection.execute("SELECT * FROM search_needs WHERE id = ?", (need_id,)).fetchone()
        return row_to_need(row) if row else None

    def list_needs(self, state: SearchNeedState | str | None = None, kind: SearchNeedKind | str | None = None, limit: int = 100) -> list[SearchNeed]:
        self._ensure_open()
        sql = "SELECT * FROM search_needs"
        params: list[Any] = []
        clauses = []
        if state:
            clauses.append("state = ?")
            params.append(state.value if isinstance(state, SearchNeedState) else str(state))
        if kind:
            clauses.append("need_kind = ?")
            params.append(kind.value if isinstance(kind, SearchNeedKind) else str(kind))
        if clauses:
            sql += " WHERE " + " AND ".join(clauses)
        sql += " ORDER BY created_at DESC, id LIMIT ?"
        params.append(validate_limit(limit))
        return [row_to_need(row) for row in self.connection.execute(sql, params).fetchall()]

    def list_needs_for_hunt(self, hunt_id: str, limit: int = 100) -> list[SearchNeed]:
        self._ensure_open()
        rows = self.connection.execute(
            "SELECT n.* FROM search_needs n "
            "JOIN search_need_hunt_links l ON l.need_id = n.id "
            "WHERE l.hunt_id = ? ORDER BY n.created_at DESC, n.id LIMIT ?",
            (hunt_id, validate_limit(limit)),
        ).fetchall()
        return [row_to_need(row) for row in rows]

    def transition_need(self, need_id: str, target_state: SearchNeedState | str, reason: str | None = None) -> SearchNeed:
        self._ensure_open()
        current = self._require_need(need_id)
        updated = apply_transition(current, target_state, reason)
        if updated is current:
            return current
        with self.transaction():
            self.connection.execute(
                "UPDATE search_needs SET state = ?, updated_at = ? WHERE id = ?",
                (updated.state.value, updated.updated_at, updated.id),
            )
            self._insert_transition(SearchNeedTransition.new(updated.id, current.state, updated.state, reason))
        return updated

    def list_transitions(self, need_id: str | None = None, limit: int = 100) -> list[SearchNeedTransition]:
        self._ensure_open()
        sql = "SELECT * FROM search_need_transitions"
        params: list[Any] = []
        if need_id:
            sql += " WHERE need_id = ?"
            params.append(need_id)
        sql += " ORDER BY sequence LIMIT ?"
        params.append(validate_limit(limit))
        return [row_to_transition(row) for row in self.connection.execute(sql, params).fetchall()]

    def list_summaries(self, need_id: str | None = None, limit: int = 100) -> list[SearchNeedSummary]:
        self._ensure_open()
        sql = "SELECT * FROM search_need_summaries"
        params: list[Any] = []
        if need_id:
            sql += " WHERE need_id = ?"
            params.append(need_id)
        sql += " ORDER BY created_at, id LIMIT ?"
        params.append(validate_limit(limit))
        return [row_to_summary(row) for row in self.connection.execute(sql, params).fetchall()]

    def summarize(self) -> dict[str, Any]:
        self._ensure_open()
        total = int(self.connection.execute("SELECT COUNT(*) FROM search_needs").fetchone()[0])
        by_state = {
            str(row[0]): int(row[1])
            for row in self.connection.execute("SELECT state, COUNT(*) FROM search_needs GROUP BY state ORDER BY state").fetchall()
        }
        return {
            "schema_version": "search_need_summary.v0",
            "total": total,
            "by_state": by_state,
            "creation_from_hunt_enabled": True,
            "workunit_creation_enabled": False,
            "source_probe_execution_enabled": False,
            "model_provider_enabled": False,
            "sync_enabled": False,
        }

    def check_integrity(self) -> dict[str, Any]:
        self._ensure_open()
        integrity = self.connection.execute("PRAGMA integrity_check").fetchone()[0]
        table_rows = self.connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall()
        tables = {str(row[0]) for row in table_rows}
        missing = [table for table in REQUIRED_TABLES if table not in tables]
        orphan_transitions = self.connection.execute(
            "SELECT COUNT(*) FROM search_need_transitions t LEFT JOIN search_needs n ON t.need_id = n.id WHERE n.id IS NULL"
        ).fetchone()
        orphan_links = self.connection.execute(
            "SELECT COUNT(*) FROM search_need_hunt_links l LEFT JOIN search_needs n ON l.need_id = n.id WHERE n.id IS NULL"
        ).fetchone()
        orphan_summaries = self.connection.execute(
            "SELECT COUNT(*) FROM search_need_summaries s LEFT JOIN search_needs n ON s.need_id = n.id WHERE n.id IS NULL"
        ).fetchone()
        orphan_count = int(orphan_transitions[0] or 0) + int(orphan_links[0] or 0) + int(orphan_summaries[0] or 0)
        return {
            "status": "pass" if integrity == "ok" and not missing and orphan_count == 0 else "fail",
            "sqlite_integrity": str(integrity),
            "schema_version": self.schema_version(),
            "missing_tables": missing,
            "orphan_row_count": orphan_count,
            "applied_migrations": get_schema_events(self.connection),
        }

    def schema_version(self) -> str:
        self._ensure_open()
        row = self.connection.execute("SELECT value FROM search_need_meta WHERE key = ?", ("schema_version",)).fetchone()
        return str(row[0]) if row else SCHEMA_VERSION

    def _dedupe_need(self, need: SearchNeed) -> SearchNeed | None:
        if need.idempotency_key:
            row = self.connection.execute("SELECT * FROM search_needs WHERE idempotency_key = ?", (need.idempotency_key,)).fetchone()
            if row:
                return row_to_need(row)
        row = self.connection.execute(
            "SELECT * FROM search_needs WHERE hunt_id = ? AND normalized_query = ? ORDER BY created_at LIMIT 1",
            (need.hunt_id, need.normalized_query),
        ).fetchone()
        return row_to_need(row) if row else None

    def _require_need(self, need_id: str) -> SearchNeed:
        need = self.get_need(need_id)
        if need is None:
            raise SearchNeedNotFoundError(f"SearchNeed not found: {need_id}")
        return need

    def _insert_transition(self, transition: SearchNeedTransition) -> None:
        self.connection.execute(
            "INSERT INTO search_need_transitions (id, need_id, from_state, to_state, reason, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (transition.id, transition.need_id, transition.from_state, transition.to_state.value, transition.reason, transition.created_at),
        )

    def _insert_hunt_link(self, need: SearchNeed) -> None:
        self.connection.execute(
            "INSERT INTO search_need_hunt_links (id, need_id, hunt_id, exhaustion_report_id, link_kind, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            ("snl_" + uuid.uuid4().hex, need.id, need.hunt_id, need.exhaustion_report_id, "created_from_hunt", utc_now()),
        )

    def _insert_summary(self, summary: SearchNeedSummary) -> None:
        self.connection.execute(
            "INSERT INTO search_need_summaries (id, need_id, summary_type, payload_json, created_at) VALUES (?, ?, ?, ?, ?)",
            (summary.id, summary.need_id, summary.summary_type, encode_json(dict(summary.payload)), summary.created_at),
        )

    def _ensure_open(self) -> None:
        if self._closed:
            raise SearchNeedClosedError("SearchNeed store is closed")


def _need_values(need: SearchNeed) -> tuple[Any, ...]:
    return (
        need.id,
        need.hunt_id,
        need.exhaustion_report_id,
        need.query,
        need.normalized_query,
        need.need_title,
        need.need_summary,
        need.need_kind.value,
        need.desired_outcome.value,
        need.priority,
        need.state.value,
        need.local_result_state,
        encode_json(list(need.checked_layers)),
        encode_json(list(need.deferred_layers)),
        encode_json(list(need.recommended_future_work)),
        encode_json(list(need.policy_limitations)),
        encode_json(list(need.warnings)),
        1 if need.public_safe_summary_allowed else 0,
        1 if need.private_notes_allowed else 0,
        need.created_at,
        need.updated_at,
        need.idempotency_key,
        need.superseded_by,
    )
