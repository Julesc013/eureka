"""SQLite-backed durable local Search Hunt session store."""

from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator, Mapping
import sqlite3
import uuid

from .absence_summary import build_local_absence_summary
from .commands import (
    SearchHuntCommand,
    SearchHuntCommandResult,
    SearchHuntCommandType,
    coerce_command_type,
    command_requires_reason,
    default_command_side_effects,
    target_state_for_command,
)
from .errors import SearchHuntClosedError, SearchHuntError, SearchHuntNotFoundError, SearchHuntTransitionError
from .queries import encode_json, row_to_command, row_to_session, row_to_steering_preference, row_to_summary, row_to_transition
from .queries import row_to_exhaustion_report
from .records import (
    SearchHuntDestination,
    SearchHuntExhaustionReport,
    SearchHuntIntent,
    SearchHuntSession,
    SearchHuntState,
    SearchHuntSummary,
    SearchHuntTransition,
    utc_now,
)
from .schema import REQUIRED_TABLES, SCHEMA_VERSION, apply_schema, get_schema_events
from .search_summary import build_reviewed_index_search_summary
from .steering import SearchHuntSteeringPreference, SearchHuntSteeringType, coerce_steering_type, steering_type_text
from .transitions import apply_transition
from .validation import (
    validate_limit,
    validate_query_text,
    validate_search_hunt_command,
    validate_search_hunt_exhaustion_report,
    validate_search_hunt_session,
    validate_search_hunt_steering_preference,
    validate_store_path,
)


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

    def record_command(self, command: SearchHuntCommand) -> SearchHuntCommand:
        self._ensure_open()
        validate_search_hunt_command(command)
        self._require_session(command.hunt_id)
        with self.transaction():
            self._insert_command(command)
        return command

    def list_commands(self, hunt_id: str | None = None, limit: int = 100) -> list[SearchHuntCommand]:
        self._ensure_open()
        sql = "SELECT * FROM search_hunt_commands"
        params: list[Any] = []
        if hunt_id:
            sql += " WHERE hunt_id = ?"
            params.append(hunt_id)
        sql += " ORDER BY sequence LIMIT ?"
        params.append(validate_limit(limit))
        return [row_to_command(row) for row in self.connection.execute(sql, params).fetchall()]

    def apply_command(
        self,
        hunt_id: str,
        command_type: SearchHuntCommandType | str,
        value: str | None = None,
        reason: str | None = None,
        operator_label: str | None = None,
    ) -> SearchHuntCommandResult:
        self._ensure_open()
        command_kind = coerce_command_type(command_type)
        if command_requires_reason(command_kind) and not str(reason or "").strip():
            raise SearchHuntTransitionError(f"{command_kind.value} requires reason")
        current = self._require_session(hunt_id)
        target_state = target_state_for_command(command_kind)
        side_effects = default_command_side_effects()
        side_effects["hunt_state_mutated"] = current.state != target_state
        if current.state == target_state:
            updated = current
        else:
            updated = apply_transition(current, target_state, reason)
        command = SearchHuntCommand.new(
            hunt_id,
            command_kind,
            previous_state=current.state,
            resulting_state=updated.state,
            operator_label=operator_label,
            reason=reason,
            value=value,
            side_effects=side_effects,
        )
        validate_search_hunt_command(command)
        with self.transaction():
            if updated is not current:
                self.connection.execute(
                    "UPDATE search_hunt_sessions SET state = ?, updated_at = ? WHERE id = ?",
                    (updated.state.value, updated.updated_at, updated.id),
                )
                self._insert_transition(SearchHuntTransition.new(updated.id, current.state, updated.state, reason))
            self._insert_command(command)
        return SearchHuntCommandResult(command=command, hunt=updated.to_dict())

    def add_steering_preference(
        self,
        hunt_id: str,
        steering_type: SearchHuntSteeringType | str,
        value: str | None = None,
        reason: str | None = None,
        operator_label: str | None = None,
    ) -> SearchHuntSteeringPreference:
        self._ensure_open()
        self._require_session(hunt_id)
        steering_kind = coerce_steering_type(steering_type)
        side_effects = default_command_side_effects()
        side_effects["hunt_steering_mutated"] = True
        command = SearchHuntCommand.new(
            hunt_id,
            steering_type_text(steering_kind),
            previous_state=None,
            resulting_state=None,
            operator_label=operator_label,
            reason=reason,
            value=value,
            policy_decision="allowed_local_operator_steering",
            side_effects=side_effects,
        )
        preference = SearchHuntSteeringPreference.new(
            hunt_id,
            steering_kind,
            command_id=command.command_id,
            value=value,
            reason=reason,
            operator_label=operator_label,
        )
        validate_search_hunt_steering_preference(preference)
        with self.transaction():
            self._insert_command(command)
            self._insert_steering_preference(preference)
        return preference

    def remove_steering_preference(
        self,
        hunt_id: str,
        steering_id: str,
        reason: str | None = None,
        operator_label: str | None = None,
    ) -> SearchHuntSteeringPreference:
        self._ensure_open()
        self._require_session(hunt_id)
        row = self.connection.execute(
            "SELECT * FROM search_hunt_steering_preferences WHERE id = ? AND hunt_id = ?",
            (steering_id, hunt_id),
        ).fetchone()
        if row is None:
            raise SearchHuntNotFoundError(f"Search Hunt steering preference not found: {steering_id}")
        preference = row_to_steering_preference(row)
        if not preference.active:
            return preference
        side_effects = default_command_side_effects()
        side_effects["hunt_steering_mutated"] = True
        command = SearchHuntCommand.new(
            hunt_id,
            SearchHuntCommandType.REMOVE_STEERING,
            previous_state=None,
            resulting_state=None,
            operator_label=operator_label,
            reason=reason,
            value=steering_id,
            policy_decision="allowed_local_operator_steering_deactivation",
            side_effects=side_effects,
        )
        now = utc_now()
        with self.transaction():
            self._insert_command(command)
            self.connection.execute(
                "UPDATE search_hunt_steering_preferences SET active = 0, updated_at = ? WHERE id = ? AND hunt_id = ?",
                (now, steering_id, hunt_id),
            )
        row = self.connection.execute(
            "SELECT * FROM search_hunt_steering_preferences WHERE id = ? AND hunt_id = ?",
            (steering_id, hunt_id),
        ).fetchone()
        return row_to_steering_preference(row)

    def list_steering_preferences(self, hunt_id: str, active_only: bool = True) -> list[SearchHuntSteeringPreference]:
        self._ensure_open()
        self._require_session(hunt_id)
        sql = "SELECT * FROM search_hunt_steering_preferences WHERE hunt_id = ?"
        params: list[Any] = [hunt_id]
        if active_only:
            sql += " AND active = 1"
        sql += " ORDER BY created_at, id"
        return [row_to_steering_preference(row) for row in self.connection.execute(sql, params).fetchall()]

    def write_exhaustion_report(self, report: SearchHuntExhaustionReport) -> SearchHuntExhaustionReport:
        self._ensure_open()
        validate_search_hunt_exhaustion_report(report)
        self._require_session(report.hunt_id)
        with self.transaction():
            self._insert_exhaustion_report(report)
        return report

    def get_latest_exhaustion_report(self, hunt_id: str) -> SearchHuntExhaustionReport | None:
        self._ensure_open()
        self._require_session(hunt_id)
        row = self.connection.execute(
            "SELECT * FROM search_hunt_exhaustion_reports WHERE hunt_id = ? ORDER BY sequence DESC LIMIT 1",
            (hunt_id,),
        ).fetchone()
        return row_to_exhaustion_report(row) if row else None

    def list_exhaustion_reports(self, hunt_id: str | None = None, limit: int = 100) -> list[SearchHuntExhaustionReport]:
        self._ensure_open()
        sql = "SELECT * FROM search_hunt_exhaustion_reports"
        params: list[Any] = []
        if hunt_id:
            self._require_session(hunt_id)
            sql += " WHERE hunt_id = ?"
            params.append(hunt_id)
        sql += " ORDER BY sequence DESC LIMIT ?"
        params.append(validate_limit(limit))
        return [row_to_exhaustion_report(row) for row in self.connection.execute(sql, params).fetchall()]

    def attach_exhaustion_report(self, hunt_id: str, report: SearchHuntExhaustionReport) -> SearchHuntExhaustionReport:
        self._ensure_open()
        session = self._require_session(hunt_id)
        if report.hunt_id != hunt_id:
            raise SearchHuntError("exhaustion report hunt_id mismatch")
        validate_search_hunt_exhaustion_report(report)
        side_effects = default_command_side_effects()
        side_effects["hunt_state_mutated"] = False
        side_effects["hunt_exhaustion_report_mutated"] = True
        command = SearchHuntCommand.new(
            hunt_id,
            "generate_exhaustion_report",
            previous_state=session.state,
            resulting_state=session.state,
            operator_label=report.operator_label,
            reason="deterministic local exhaustion report generated",
            policy_decision="allowed_local_exhaustion_report_generation",
            value=report.report_id,
            side_effects=side_effects,
        )
        with self.transaction():
            self._insert_exhaustion_report(report)
            self._insert_command(command)
        return report

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
        orphan_commands = self.connection.execute(
            "SELECT COUNT(*) FROM search_hunt_commands c LEFT JOIN search_hunt_sessions s ON c.hunt_id = s.id WHERE s.id IS NULL"
        ).fetchone()
        orphan_steering = self.connection.execute(
            "SELECT COUNT(*) FROM search_hunt_steering_preferences p LEFT JOIN search_hunt_sessions s ON p.hunt_id = s.id WHERE s.id IS NULL"
        ).fetchone()
        orphan_exhaustion = self.connection.execute(
            "SELECT COUNT(*) FROM search_hunt_exhaustion_reports r LEFT JOIN search_hunt_sessions s ON r.hunt_id = s.id WHERE s.id IS NULL"
        ).fetchone()
        orphan_count = (
            int(orphan_transitions[0] or 0)
            + int(orphan_summaries[0] or 0)
            + int(orphan_layers[0] or 0)
            + int(orphan_commands[0] or 0)
            + int(orphan_steering[0] or 0)
            + int(orphan_exhaustion[0] or 0)
        )
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

    def _insert_command(self, command: SearchHuntCommand) -> None:
        self.connection.execute(
            "INSERT INTO search_hunt_commands "
            "(command_id, hunt_id, command_type, value, reason, operator_label, previous_state, resulting_state, "
            "policy_decision, side_effects_json, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                command.command_id,
                command.hunt_id,
                command.command_type,
                command.value,
                command.reason,
                command.operator_label,
                command.previous_state,
                command.resulting_state,
                command.policy_decision,
                encode_json(dict(command.side_effects)),
                command.created_at,
            ),
        )

    def _insert_steering_preference(self, preference: SearchHuntSteeringPreference) -> None:
        self.connection.execute(
            "INSERT INTO search_hunt_steering_preferences "
            "(id, command_id, hunt_id, command_type, value, reason, operator_label, active, limitations_json, warnings_json, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                preference.id,
                preference.command_id,
                preference.hunt_id,
                preference.command_type,
                preference.value,
                preference.reason,
                preference.operator_label,
                1 if preference.active else 0,
                encode_json(list(preference.limitations)),
                encode_json(list(preference.warnings)),
                preference.created_at,
                preference.updated_at,
            ),
        )

    def _insert_exhaustion_report(self, report: SearchHuntExhaustionReport) -> None:
        self.connection.execute(
            "INSERT INTO search_hunt_exhaustion_reports "
            "(report_id, hunt_id, report_version, exhaustion_state, payload_json, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (
                report.report_id,
                report.hunt_id,
                report.report_version,
                report.state.value,
                encode_json(report.to_dict()),
                report.created_at,
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
