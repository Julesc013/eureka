"""SQLite-backed durable local Search Hunt session store."""

from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator, Mapping
import sqlite3
import uuid

from .absence_summary import build_local_absence_summary
from .errors import SearchHuntClosedError, SearchHuntError, SearchHuntNotFoundError
from .queries import encode_json, row_to_session, row_to_summary, row_to_transition
from .records import SearchHuntDestination, SearchHuntIntent, SearchHuntSession, SearchHuntState, SearchHuntSummary, SearchHuntTransition, utc_now
from .schema import REQUIRED_TABLES, SCHEMA_VERSION, apply_schema, get_schema_events
from .search_summary import build_reviewed_index_search_summary
from .transitions import apply_transition
from .validation import validate_limit, validate_query_text, validate_search_hunt_session, validate_store_path


class SearchHuntStore:
    def __init__(self, path: str | Path, connection: sqlite3.Connection):
        self.path = path
        self.connection = connection
        self.connection.row_factory = sqlite3.Row
        self._closed = False

    @classmethod
    def open(cls, path: str | Path) -> "SearchHuntStore":
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

    def __enter__(self) -> "SearchHuntStore":
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
            raise SearchHuntError(str(exc)) from exc

    def create_session(self, session: SearchHuntSession) -> SearchHuntSession:
        self._ensure_open()
        validate_search_hunt_session(session)
        if session.idempotency_key:
            existing = self._get_by_idempotency_key(session.idempotency_key)
            if existing is not None:
                return existing
        with self.transaction():
            self.connection.execute(
                "INSERT INTO search_hunt_sessions "
                "(id, query, normalized_query, state, intent, destination, created_at, updated_at, "
                "index_snapshot_id, reviewed_result_count, candidate_result_count, absence_report_id, "
                "checked_layers_json, unchecked_layers_json, limitations_json, warnings_json, idempotency_key, parent_id) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                _session_values(session),
            )
            self._insert_transition(SearchHuntTransition.new(session.id, None, session.state, "created"))
        return session

    def create_session_from_query(
        self,
        query: str,
        runtime: Any = None,
        idempotency_key: str | None = None,
        *,
        intent: SearchHuntIntent | str = SearchHuntIntent.UNKNOWN,
        destination: SearchHuntDestination | str = SearchHuntDestination.UNKNOWN,
        parent_id: str | None = None,
    ) -> SearchHuntSession:
        text = validate_query_text(query)
        search_summary: Mapping[str, Any] | None = None
        reviewed_count = 0
        if runtime is not None:
            search_summary = build_reviewed_index_search_summary(runtime, text)
            reviewed_count = int(search_summary.get("result_count") or 0)
        session = SearchHuntSession.new(
            text,
            intent=intent,
            destination=destination,
            reviewed_result_count=reviewed_count,
            idempotency_key=idempotency_key,
            parent_id=parent_id,
        )
        created = self.create_session(session)
        if search_summary is not None and created.id == session.id:
            self.attach_search_summary(created.id, search_summary)
            if reviewed_count == 0:
                self.attach_absence_summary(created.id, build_local_absence_summary(runtime, text))
            created = self.get_session(created.id) or created
        return created

    def get_session(self, session_id: str) -> SearchHuntSession | None:
        self._ensure_open()
        row = self.connection.execute("SELECT * FROM search_hunt_sessions WHERE id = ?", (session_id,)).fetchone()
        return row_to_session(row) if row else None

    def list_sessions(self, state: SearchHuntState | str | None = None, limit: int = 100) -> list[SearchHuntSession]:
        self._ensure_open()
        sql = "SELECT * FROM search_hunt_sessions"
        params: list[Any] = []
        if state:
            state_value = state.value if isinstance(state, SearchHuntState) else str(state)
            sql += " WHERE state = ?"
            params.append(state_value)
        sql += " ORDER BY created_at DESC, id LIMIT ?"
        params.append(validate_limit(limit))
        return [row_to_session(row) for row in self.connection.execute(sql, params).fetchall()]

    def transition_session(self, session_id: str, target_state: SearchHuntState | str, reason: str | None = None) -> SearchHuntSession:
        self._ensure_open()
        current = self._require_session(session_id)
        updated = apply_transition(current, target_state, reason)
        if updated is current:
            return current
        with self.transaction():
            self.connection.execute(
                "UPDATE search_hunt_sessions SET state = ?, updated_at = ? WHERE id = ?",
                (updated.state.value, updated.updated_at, updated.id),
            )
            self._insert_transition(SearchHuntTransition.new(updated.id, current.state, updated.state, reason))
        return updated

    def attach_search_summary(self, session_id: str, summary: SearchHuntSummary | Mapping[str, Any]) -> SearchHuntSummary:
        payload = summary.payload if isinstance(summary, SearchHuntSummary) else dict(summary)
        record = summary if isinstance(summary, SearchHuntSummary) else SearchHuntSummary.new(session_id, "reviewed_index_search", payload)
        result_count = int(payload.get("result_count") or 0)
        return self._attach_summary(record, "checked", "reviewed_public_index", {"reviewed_result_count": result_count})

    def attach_absence_summary(self, session_id: str, summary: SearchHuntSummary | Mapping[str, Any]) -> SearchHuntSummary:
        payload = summary.payload if isinstance(summary, SearchHuntSummary) else dict(summary)
        record = summary if isinstance(summary, SearchHuntSummary) else SearchHuntSummary.new(session_id, "local_absence", payload)
        return self._attach_summary(record, "checked", "local_absence_report", {"absence_report_id": record.id})

    def list_transitions(self, session_id: str | None = None, limit: int = 100) -> list[SearchHuntTransition]:
        self._ensure_open()
        sql = "SELECT * FROM search_hunt_transitions"
        params: list[Any] = []
        if session_id:
            sql += " WHERE session_id = ?"
            params.append(session_id)
        sql += " ORDER BY sequence LIMIT ?"
        params.append(validate_limit(limit))
        return [row_to_transition(row) for row in self.connection.execute(sql, params).fetchall()]

    def list_summaries(self, session_id: str | None = None, limit: int = 100) -> list[SearchHuntSummary]:
        self._ensure_open()
        sql = "SELECT * FROM search_hunt_summaries"
        params: list[Any] = []
        if session_id:
            sql += " WHERE session_id = ?"
            params.append(session_id)
        sql += " ORDER BY created_at, id LIMIT ?"
        params.append(validate_limit(limit))
        return [row_to_summary(row) for row in self.connection.execute(sql, params).fetchall()]

    def summarize(self) -> dict[str, Any]:
        self._ensure_open()
        total = int(self.connection.execute("SELECT COUNT(*) FROM search_hunt_sessions").fetchone()[0])
        by_state = {
            str(row[0]): int(row[1])
            for row in self.connection.execute("SELECT state, COUNT(*) FROM search_hunt_sessions GROUP BY state ORDER BY state").fetchall()
        }
        return {
            "schema_version": "search_hunt_summary.v0",
            "total": total,
            "by_state": by_state,
            "workunit_creation_enabled": False,
            "source_probe_execution_enabled": False,
            "model_provider_enabled": False,
        }

    def check_integrity(self) -> dict[str, Any]:
        self._ensure_open()
        integrity = self.connection.execute("PRAGMA integrity_check").fetchone()[0]
        table_rows = self.connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall()
        tables = {str(row[0]) for row in table_rows}
        missing = [table for table in REQUIRED_TABLES if table not in tables]
        orphan_transitions = self.connection.execute(
            "SELECT COUNT(*) FROM search_hunt_transitions t LEFT JOIN search_hunt_sessions s ON t.session_id = s.id WHERE s.id IS NULL"
        ).fetchone()
        orphan_summaries = self.connection.execute(
            "SELECT COUNT(*) FROM search_hunt_summaries m LEFT JOIN search_hunt_sessions s ON m.session_id = s.id WHERE s.id IS NULL"
        ).fetchone()
        orphan_layers = self.connection.execute(
            "SELECT COUNT(*) FROM search_hunt_layers l LEFT JOIN search_hunt_sessions s ON l.session_id = s.id WHERE s.id IS NULL"
        ).fetchone()
        orphan_count = int(orphan_transitions[0] or 0) + int(orphan_summaries[0] or 0) + int(orphan_layers[0] or 0)
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
        row = self.connection.execute("SELECT value FROM search_hunt_meta WHERE key = ?", ("schema_version",)).fetchone()
        return str(row[0]) if row else SCHEMA_VERSION

    def _attach_summary(
        self,
        summary: SearchHuntSummary,
        layer_kind: str,
        layer_id: str,
        session_updates: Mapping[str, Any],
    ) -> SearchHuntSummary:
        self._ensure_open()
        self._require_session(summary.session_id)
        with self.transaction():
            self.connection.execute(
                "INSERT INTO search_hunt_summaries (id, session_id, summary_type, payload_json, created_at) VALUES (?, ?, ?, ?, ?)",
                (summary.id, summary.session_id, summary.summary_type, encode_json(dict(summary.payload)), summary.created_at),
            )
            self.connection.execute(
                "INSERT INTO search_hunt_layers (id, session_id, layer_kind, layer_id, summary_json, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                ("shl_" + uuid.uuid4().hex, summary.session_id, layer_kind, layer_id, encode_json(dict(summary.payload)), utc_now()),
            )
            if session_updates:
                assignments = ", ".join(f"{key} = ?" for key in session_updates)
                params = list(session_updates.values()) + [utc_now(), summary.session_id]
                self.connection.execute(
                    f"UPDATE search_hunt_sessions SET {assignments}, updated_at = ? WHERE id = ?",
                    params,
                )
        return summary

    def _get_by_idempotency_key(self, key: str) -> SearchHuntSession | None:
        row = self.connection.execute("SELECT * FROM search_hunt_sessions WHERE idempotency_key = ?", (key,)).fetchone()
        return row_to_session(row) if row else None

    def _require_session(self, session_id: str) -> SearchHuntSession:
        session = self.get_session(session_id)
        if session is None:
            raise SearchHuntNotFoundError(f"Search Hunt session not found: {session_id}")
        return session

    def _insert_transition(self, transition: SearchHuntTransition) -> None:
        self.connection.execute(
            "INSERT INTO search_hunt_transitions (id, session_id, from_state, to_state, reason, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (
                transition.id,
                transition.session_id,
                transition.from_state,
                transition.to_state.value,
                transition.reason,
                transition.created_at,
            ),
        )

    def _ensure_open(self) -> None:
        if self._closed:
            raise SearchHuntClosedError("Search Hunt store is closed")


def _session_values(session: SearchHuntSession) -> tuple[Any, ...]:
    return (
        session.id,
        session.query,
        session.normalized_query,
        session.state.value,
        session.intent.value,
        session.destination.value,
        session.created_at,
        session.updated_at,
        session.index_snapshot_id,
        session.reviewed_result_count,
        session.candidate_result_count,
        session.absence_report_id,
        encode_json(list(session.checked_layers)),
        encode_json(list(session.unchecked_layers)),
        encode_json(list(session.limitations)),
        encode_json(list(session.warnings)),
        session.idempotency_key,
        session.parent_id,
    )
