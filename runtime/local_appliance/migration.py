"""Local appliance migration state loading and validation."""

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Mapping

from .errors import LocalMigrationStateError
from .instance import CURRENT_INSTANCE_SCHEMA_VERSION, resolve_instance_paths


MIGRATION_STATE_SCHEMA_VERSION = "eureka_local_migration_state.v0"


@dataclass(frozen=True)
class LocalMigrationState:
    schema_version: str
    instance_id: str
    current_instance_schema_version: int
    target_instance_schema_version: int
    migration_needed: bool
    migration_allowed: bool
    destructive_migration_required: bool
    backup_required: bool
    rollback_available: bool
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    raw: Mapping[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return dict(self.raw)


def load_migration_state(instance_path: str | Path) -> LocalMigrationState:
    paths = resolve_instance_paths(instance_path)
    try:
        payload = json.loads(paths.migration_state.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise LocalMigrationStateError("config/migration_state.json is required") from exc
    except json.JSONDecodeError as exc:
        raise LocalMigrationStateError("config/migration_state.json must be valid JSON") from exc
    if not isinstance(payload, dict):
        raise LocalMigrationStateError("config/migration_state.json must contain an object")
    state = _from_payload(payload)
    validate_migration_state(state)
    return state


def validate_migration_state(state: LocalMigrationState) -> LocalMigrationState:
    if state.schema_version != MIGRATION_STATE_SCHEMA_VERSION:
        raise LocalMigrationStateError("migration state schema_version mismatch")
    if not state.instance_id:
        raise LocalMigrationStateError("migration state instance_id is required")
    if state.target_instance_schema_version != CURRENT_INSTANCE_SCHEMA_VERSION:
        raise LocalMigrationStateError("migration target must match the current instance schema")
    if state.destructive_migration_required is not False:
        raise LocalMigrationStateError("destructive migration is required and runtime opening is blocked")
    if state.migration_allowed is not False:
        raise LocalMigrationStateError("migration apply must remain disabled")
    if state.blockers:
        raise LocalMigrationStateError("migration state has blockers: " + "; ".join(state.blockers))
    return state


def migration_needed(state: LocalMigrationState) -> bool:
    return bool(state.migration_needed)


def _from_payload(payload: Mapping[str, Any]) -> LocalMigrationState:
    try:
        current_version = int(payload.get("current_instance_schema_version"))
        target_version = int(payload.get("target_instance_schema_version"))
    except (TypeError, ValueError) as exc:
        raise LocalMigrationStateError("migration state versions must be integers") from exc
    blockers = payload.get("blockers", [])
    warnings = payload.get("warnings", [])
    return LocalMigrationState(
        schema_version=str(payload.get("schema_version") or ""),
        instance_id=str(payload.get("instance_id") or ""),
        current_instance_schema_version=current_version,
        target_instance_schema_version=target_version,
        migration_needed=bool(payload.get("migration_needed")),
        migration_allowed=bool(payload.get("migration_allowed")),
        destructive_migration_required=bool(payload.get("destructive_migration_required")),
        backup_required=bool(payload.get("backup_required")),
        rollback_available=bool(payload.get("rollback_available")),
        blockers=tuple(str(item) for item in blockers) if isinstance(blockers, list) else (),
        warnings=tuple(str(item) for item in warnings) if isinstance(warnings, list) else (),
        raw=payload,
    )
