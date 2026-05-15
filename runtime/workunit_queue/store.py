"""SQLite-backed durable local work queue store."""

from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator
import sqlite3

from .errors import WorkUnitNotFoundError, WorkUnitQueueClosedError, WorkUnitQueueError
from .queries import encode_json, row_to_payload_ref, row_to_transition, row_to_workunit
from .records import WorkUnit, WorkUnitPayloadRef, WorkUnitState, WorkUnitSummary, WorkUnitTransition
from .schema import REQUIRED_TABLES, SCHEMA_VERSION, apply_schema, get_schema_events
from .transitions import apply_transition
from .validation import require_reason, validate_limit, validate_queue_path, validate_workunit


class WorkUnitQueueStore:
    def __init__(self, path: str | Path, connection: sqlite3.Connection):
        self.path = path
        self.connection = connection
        self.connection.row_factory = sqlite3.Row
        self._closed = False

    @classmethod
    def open(cls, path: str | Path) -> "WorkUnitQueueStore":
        valid_path = validate_queue_path(path)
        if str(path) == ":memory:":
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

    def __enter__(self) -> "WorkUnitQueueStore":
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
            raise WorkUnitQueueError(str(exc)) from exc

    def create_workunit(self, workunit: WorkUnit) -> WorkUnit:
        self._ensure_open()
        validate_workunit(workunit)
        if workunit.idempotency_key:
            existing = self._get_by_idempotency_key(workunit.idempotency_key)
            if existing is not None:
                return existing
        with self.transaction():
            self.connection.execute(
                "INSERT INTO workunits "
                "(id, kind, state, title, payload_json, priority, created_at, updated_at, idempotency_key, "
                "parent_id, blocked_reason, warnings_json, limitations_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    workunit.id,
                    workunit.kind.value,
                    workunit.state.value,
                    workunit.title,
                    encode_json(dict(workunit.payload)),
                    workunit.priority.value,
                    workunit.created_at,
                    workunit.updated_at,
                    workunit.idempotency_key,
                    workunit.parent_id,
                    workunit.blocked_reason,
                    encode_json(list(workunit.warnings)),
                    encode_json(list(workunit.limitations)),
                ),
            )
            self._insert_transition(WorkUnitTransition.new(workunit.id, None, workunit.state, "created"))
        return workunit

    def get_workunit(self, workunit_id: str) -> WorkUnit | None:
        self._ensure_open()
        row = self.connection.execute("SELECT * FROM workunits WHERE id = ?", (workunit_id,)).fetchone()
        return row_to_workunit(row) if row else None

    def list_workunits(
        self,
        state: WorkUnitState | str | None = None,
        kind: str | None = None,
        limit: int = 100,
    ) -> list[WorkUnit]:
        self._ensure_open()
        sql = "SELECT * FROM workunits"
        params: list[Any] = []
        clauses: list[str] = []
        if state:
            state_value = state.value if isinstance(state, WorkUnitState) else str(state)
            clauses.append("state = ?")
            params.append(state_value)
        if kind:
            clauses.append("kind = ?")
            params.append(str(kind))
        if clauses:
            sql += " WHERE " + " AND ".join(clauses)
        sql += " ORDER BY created_at, id LIMIT ?"
        params.append(validate_limit(limit))
        return [row_to_workunit(row) for row in self.connection.execute(sql, params).fetchall()]

    def transition_workunit(self, workunit_id: str, target_state: WorkUnitState | str, reason: str | None = None) -> WorkUnit:
        self._ensure_open()
        current = self._require_workunit(workunit_id)
        updated = apply_transition(current, target_state, reason)
        if updated is current:
            return current
        with self.transaction():
            self.connection.execute(
                "UPDATE workunits SET state = ?, updated_at = ?, blocked_reason = ? WHERE id = ?",
                (updated.state.value, updated.updated_at, updated.blocked_reason, updated.id),
            )
            self._insert_transition(WorkUnitTransition.new(updated.id, current.state, updated.state, reason))
        return updated

    def pause_workunit(self, workunit_id: str, reason: str | None = None) -> WorkUnit:
        return self.transition_workunit(workunit_id, WorkUnitState.PAUSED, reason)

    def resume_workunit(self, workunit_id: str, reason: str | None = None) -> WorkUnit:
        return self.transition_workunit(workunit_id, WorkUnitState.QUEUED, reason)

    def cancel_workunit(self, workunit_id: str, reason: str | None = None) -> WorkUnit:
        return self.transition_workunit(workunit_id, WorkUnitState.CANCELLED, reason)

    def block_workunit(self, workunit_id: str, reason: str) -> WorkUnit:
        return self.transition_workunit(workunit_id, WorkUnitState.BLOCKED, require_reason(reason, "block"))

    def complete_workunit(self, workunit_id: str, reason: str | None = None) -> WorkUnit:
        return self.transition_workunit(workunit_id, WorkUnitState.COMPLETE, reason)

    def fail_workunit(self, workunit_id: str, reason: str) -> WorkUnit:
        return self.transition_workunit(workunit_id, WorkUnitState.FAILED, require_reason(reason, "fail"))

    def list_transitions(self, workunit_id: str | None = None, limit: int = 100) -> list[WorkUnitTransition]:
        self._ensure_open()
        sql = "SELECT * FROM workunit_transitions"
        params: list[Any] = []
        if workunit_id:
            sql += " WHERE workunit_id = ?"
            params.append(workunit_id)
        sql += " ORDER BY sequence LIMIT ?"
        params.append(validate_limit(limit))
        return [row_to_transition(row) for row in self.connection.execute(sql, params).fetchall()]

    def record_payload_ref(self, workunit_id: str, ref_kind: str, ref_id: str) -> WorkUnitPayloadRef:
        self._ensure_open()
        self._require_workunit(workunit_id)
        ref = WorkUnitPayloadRef.new(workunit_id, ref_kind, ref_id)
        with self.transaction():
            self.connection.execute(
                "INSERT INTO workunit_payload_refs (id, workunit_id, ref_kind, ref_id, created_at) VALUES (?, ?, ?, ?, ?)",
                (ref.id, ref.workunit_id, ref.ref_kind, ref.ref_id, ref.created_at),
            )
        return ref

    def list_payload_refs(self, workunit_id: str | None = None, limit: int = 100) -> list[WorkUnitPayloadRef]:
        self._ensure_open()
        sql = "SELECT * FROM workunit_payload_refs"
        params: list[Any] = []
        if workunit_id:
            sql += " WHERE workunit_id = ?"
            params.append(workunit_id)
        sql += " ORDER BY created_at, id LIMIT ?"
        params.append(validate_limit(limit))
        return [row_to_payload_ref(row) for row in self.connection.execute(sql, params).fetchall()]

    def summarize(self) -> WorkUnitSummary:
        self._ensure_open()
        total = int(self.connection.execute("SELECT COUNT(*) FROM workunits").fetchone()[0])
        by_state = {
            str(row[0]): int(row[1])
            for row in self.connection.execute("SELECT state, COUNT(*) FROM workunits GROUP BY state ORDER BY state").fetchall()
        }
        by_kind = {
            str(row[0]): int(row[1])
            for row in self.connection.execute("SELECT kind, COUNT(*) FROM workunits GROUP BY kind ORDER BY kind").fetchall()
        }
        return WorkUnitSummary(total=total, by_state=by_state, by_kind=by_kind)

    def check_integrity(self) -> dict[str, Any]:
        self._ensure_open()
        integrity = self.connection.execute("PRAGMA integrity_check").fetchone()[0]
        table_rows = self.connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall()
        tables = {str(row[0]) for row in table_rows}
        missing = [table for table in REQUIRED_TABLES if table not in tables]
        orphan_rows = self.connection.execute(
            "SELECT COUNT(*) FROM workunit_transitions t LEFT JOIN workunits w ON t.workunit_id = w.id WHERE w.id IS NULL"
        ).fetchone()
        orphan_count = int(orphan_rows[0]) if orphan_rows else 0
        return {
            "status": "pass" if integrity == "ok" and not missing and orphan_count == 0 else "fail",
            "sqlite_integrity": str(integrity),
            "schema_version": self.schema_version(),
            "missing_tables": missing,
            "orphan_transition_count": orphan_count,
            "applied_migrations": get_schema_events(self.connection),
        }

    def schema_version(self) -> str:
        self._ensure_open()
        row = self.connection.execute("SELECT value FROM workunit_queue_meta WHERE key = ?", ("schema_version",)).fetchone()
        return str(row[0]) if row else SCHEMA_VERSION

    def _get_by_idempotency_key(self, key: str) -> WorkUnit | None:
        row = self.connection.execute("SELECT * FROM workunits WHERE idempotency_key = ?", (key,)).fetchone()
        return row_to_workunit(row) if row else None

    def _require_workunit(self, workunit_id: str) -> WorkUnit:
        workunit = self.get_workunit(workunit_id)
        if workunit is None:
            raise WorkUnitNotFoundError(f"workunit not found: {workunit_id}")
        return workunit

    def _insert_transition(self, transition: WorkUnitTransition) -> None:
        self.connection.execute(
            "INSERT INTO workunit_transitions (id, workunit_id, from_state, to_state, reason, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (
                transition.id,
                transition.workunit_id,
                transition.from_state,
                transition.to_state.value,
                transition.reason,
                transition.created_at,
            ),
        )

    def _ensure_open(self) -> None:
        if self._closed:
            raise WorkUnitQueueClosedError("workunit queue store is closed")
