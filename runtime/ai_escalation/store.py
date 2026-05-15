"""SQLite-backed disabled AI escalation gate store."""

from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator, Mapping
import json
import sqlite3

from .errors import AIEscalationClosedError, AIEscalationError, AIEscalationNotFoundError
from .records import AIEscalationGate, AIEscalationGateState, AIEscalationPreflightResult
from .schema import REQUIRED_TABLES, SCHEMA_VERSION, apply_schema, get_schema_events
from .validation import validate_ai_escalation_gate, validate_limit, validate_preflight, validate_store_path


class AIEscalationStore:
    def __init__(self, path: str | Path, connection: sqlite3.Connection):
        self.path = path
        self.connection = connection
        self.connection.row_factory = sqlite3.Row
        self._closed = False

    @classmethod
    def open(cls, path: str | Path) -> "AIEscalationStore":
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

    def __enter__(self) -> "AIEscalationStore":
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
            raise AIEscalationError(str(exc)) from exc

    def create_gate(self, gate: AIEscalationGate) -> AIEscalationGate:
        self._ensure_open()
        validate_ai_escalation_gate(gate)
        with self.transaction():
            self.connection.execute(
                "INSERT INTO ai_escalation_gates "
                "(gate_id, search_hunt_id, search_need_id, exhaustion_report_id, agent_research_task_id, "
                "query, normalized_query, state, eligibility_json, input_packet_json, output_classes_json, "
                "forbidden_actions_json, provider_enabled, execution_enabled, candidate_only_output, review_required, "
                "operator_label, created_at, updated_at, warnings_json, limitations_json) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                _gate_values(gate),
            )
        return gate

    def get_gate(self, gate_id: str) -> AIEscalationGate | None:
        self._ensure_open()
        row = self.connection.execute("SELECT * FROM ai_escalation_gates WHERE gate_id = ?", (str(gate_id),)).fetchone()
        return _row_to_gate(row) if row else None

    def list_gates(
        self,
        hunt_id: str | None = None,
        need_id: str | None = None,
        limit: int = 100,
    ) -> list[AIEscalationGate]:
        self._ensure_open()
        sql = "SELECT * FROM ai_escalation_gates"
        params: list[Any] = []
        clauses = []
        if hunt_id:
            clauses.append("search_hunt_id = ?")
            params.append(str(hunt_id))
        if need_id:
            clauses.append("search_need_id = ?")
            params.append(str(need_id))
        if clauses:
            sql += " WHERE " + " AND ".join(clauses)
        sql += " ORDER BY created_at DESC, gate_id LIMIT ?"
        params.append(validate_limit(limit))
        return [_row_to_gate(row) for row in self.connection.execute(sql, params).fetchall()]

    def write_preflight(self, preflight: AIEscalationPreflightResult) -> AIEscalationPreflightResult:
        self._ensure_open()
        validate_preflight(preflight)
        with self.transaction():
            self.connection.execute(
                "INSERT INTO ai_escalation_preflights "
                "(preflight_id, gate_id, search_hunt_id, search_need_id, exhaustion_report_id, agent_research_task_id, "
                "state, eligibility_json, input_packet_json, output_classes_json, forbidden_actions_json, safety_checks_json, "
                "provider_enabled, execution_enabled, operator_label, created_at, warnings_json, limitations_json) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                _preflight_values(preflight),
            )
        return preflight

    def get_latest_preflight(self, hunt_id: str | None = None, need_id: str | None = None) -> AIEscalationPreflightResult | None:
        self._ensure_open()
        sql = "SELECT * FROM ai_escalation_preflights"
        params: list[Any] = []
        clauses = []
        if hunt_id:
            clauses.append("search_hunt_id = ?")
            params.append(str(hunt_id))
        if need_id:
            clauses.append("search_need_id = ?")
            params.append(str(need_id))
        if clauses:
            sql += " WHERE " + " AND ".join(clauses)
        sql += " ORDER BY created_at DESC, preflight_id LIMIT 1"
        row = self.connection.execute(sql, params).fetchone()
        return _row_to_preflight(row) if row else None

    def summarize(self) -> dict[str, Any]:
        self._ensure_open()
        total = int(self.connection.execute("SELECT COUNT(*) FROM ai_escalation_gates").fetchone()[0])
        by_state = {
            str(row[0]): int(row[1])
            for row in self.connection.execute("SELECT state, COUNT(*) FROM ai_escalation_gates GROUP BY state ORDER BY state").fetchall()
        }
        preflight_count = int(self.connection.execute("SELECT COUNT(*) FROM ai_escalation_preflights").fetchone()[0])
        return {
            "schema_version": "ai_escalation_summary.v0",
            "total": total,
            "preflight_count": preflight_count,
            "by_state": by_state,
            "provider_enabled": False,
            "execution_enabled": False,
            "candidate_only_output": True,
            "review_required": True,
        }

    def check_integrity(self) -> dict[str, Any]:
        self._ensure_open()
        integrity = self.connection.execute("PRAGMA integrity_check").fetchone()[0]
        table_rows = self.connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall()
        tables = {str(row[0]) for row in table_rows}
        missing = [table for table in REQUIRED_TABLES if table not in tables]
        enabled_gates = int(
            self.connection.execute(
                "SELECT COUNT(*) FROM ai_escalation_gates WHERE provider_enabled != 0 OR execution_enabled != 0"
            ).fetchone()[0]
            or 0
        )
        enabled_preflights = int(
            self.connection.execute(
                "SELECT COUNT(*) FROM ai_escalation_preflights WHERE provider_enabled != 0 OR execution_enabled != 0"
            ).fetchone()[0]
            or 0
        )
        return {
            "status": "pass" if integrity == "ok" and not missing and enabled_gates == 0 and enabled_preflights == 0 else "fail",
            "sqlite_integrity": str(integrity),
            "schema_version": self.schema_version(),
            "missing_tables": missing,
            "enabled_gate_count": enabled_gates,
            "enabled_preflight_count": enabled_preflights,
            "applied_migrations": get_schema_events(self.connection),
        }

    def schema_version(self) -> str:
        self._ensure_open()
        row = self.connection.execute("SELECT value FROM ai_escalation_meta WHERE key = ?", ("schema_version",)).fetchone()
        return str(row[0]) if row else SCHEMA_VERSION

    def _ensure_open(self) -> None:
        if self._closed:
            raise AIEscalationClosedError("AI escalation store is closed")


def _gate_values(gate: AIEscalationGate) -> tuple[Any, ...]:
    return (
        gate.gate_id,
        gate.search_hunt_id,
        gate.search_need_id,
        gate.exhaustion_report_id,
        gate.agent_research_task_id,
        gate.query,
        gate.normalized_query,
        gate.state.value,
        encode_json(gate.eligibility.to_dict()),
        encode_json(gate.input_packet.to_dict()),
        encode_json([item.value for item in gate.output_classes]),
        encode_json([item.value for item in gate.forbidden_actions]),
        0,
        0,
        1,
        1,
        gate.operator_label,
        gate.created_at,
        gate.updated_at,
        encode_json(list(gate.warnings)),
        encode_json(list(gate.limitations)),
    )


def _preflight_values(preflight: AIEscalationPreflightResult) -> tuple[Any, ...]:
    return (
        preflight.preflight_id,
        preflight.gate_id,
        preflight.search_hunt_id,
        preflight.search_need_id,
        preflight.exhaustion_report_id,
        preflight.agent_research_task_id,
        preflight.state.value,
        encode_json(preflight.eligibility.to_dict()),
        encode_json(preflight.input_packet.to_dict()),
        encode_json([item.value for item in preflight.output_classes]),
        encode_json([item.value for item in preflight.forbidden_actions]),
        encode_json(dict(preflight.safety_checks)),
        0,
        0,
        preflight.operator_label,
        preflight.created_at,
        encode_json(list(preflight.warnings)),
        encode_json(list(preflight.limitations)),
    )


def _row_to_gate(row: sqlite3.Row) -> AIEscalationGate:
    payload = {
        "gate_id": row["gate_id"],
        "search_hunt_id": row["search_hunt_id"],
        "search_need_id": row["search_need_id"],
        "exhaustion_report_id": row["exhaustion_report_id"],
        "agent_research_task_id": row["agent_research_task_id"],
        "query": row["query"],
        "normalized_query": row["normalized_query"],
        "state": row["state"],
        "eligibility": decode_json(row["eligibility_json"]),
        "input_packet": decode_json(row["input_packet_json"]),
        "output_classes": decode_json(row["output_classes_json"]),
        "forbidden_actions": decode_json(row["forbidden_actions_json"]),
        "candidate_only_output": bool(row["candidate_only_output"]),
        "review_required": bool(row["review_required"]),
        "operator_label": row["operator_label"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
        "warnings": decode_json(row["warnings_json"]),
        "limitations": decode_json(row["limitations_json"]),
    }
    return AIEscalationGate.from_dict(payload)


def _row_to_preflight(row: sqlite3.Row) -> AIEscalationPreflightResult:
    payload = {
        "preflight_id": row["preflight_id"],
        "gate_id": row["gate_id"],
        "search_hunt_id": row["search_hunt_id"],
        "search_need_id": row["search_need_id"],
        "exhaustion_report_id": row["exhaustion_report_id"],
        "agent_research_task_id": row["agent_research_task_id"],
        "state": row["state"],
        "eligibility": decode_json(row["eligibility_json"]),
        "input_packet": decode_json(row["input_packet_json"]),
        "output_classes": decode_json(row["output_classes_json"]),
        "forbidden_actions": decode_json(row["forbidden_actions_json"]),
        "safety_checks": decode_json(row["safety_checks_json"]),
        "operator_label": row["operator_label"],
        "created_at": row["created_at"],
        "warnings": decode_json(row["warnings_json"]),
        "limitations": decode_json(row["limitations_json"]),
    }
    return AIEscalationPreflightResult.from_dict(payload)


def encode_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def decode_json(value: Any) -> Any:
    if value in (None, ""):
        return {}
    return json.loads(str(value))
