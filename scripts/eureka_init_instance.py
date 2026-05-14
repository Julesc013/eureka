#!/usr/bin/env python3
"""Initialize an explicit local Eureka appliance instance."""

from __future__ import annotations

import argparse
import importlib
import json
import sqlite3
import sys
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

TASK_ID = "LOCAL-02"
INSTANCE_SCHEMA_VERSION = "eureka_local_instance.v0"
STATUS_SCHEMA_VERSION = "eureka_local_instance_status.v0"
STORE_MANIFEST_SCHEMA_VERSION = "eureka_local_store_manifest.v0"
MIGRATION_STATE_SCHEMA_VERSION = "eureka_local_migration_state.v0"
CURRENT_INSTANCE_SCHEMA_VERSION = 1
MINIMUM_SUPPORTED_INSTANCE_SCHEMA_VERSION = 1
DEFAULT_INSTANCE_NAME = "eureka-instance"

REQUIRED_DIRS = ("config", "db", "logs", "run", "tmp", "exports", "imports")
REQUIRED_FILES = (
    "config/instance.json",
    "config/store_manifest.json",
    "config/migration_state.json",
    "run/status.json",
)
STATE_FILES = ("logs/eureka.log", "run/instance.lock", "tmp/.keep", "exports/.keep", "imports/.keep")
PLANNED_DB_FILES = (
    "db/source_cache.sqlite",
    "db/evidence_ledger.sqlite",
    "db/review_queue.sqlite",
    "db/public_index.sqlite",
    "db/workunit_queue.sqlite",
    "db/search_hunt.sqlite",
)
FORBIDDEN_ROOT_NAMES = {".cache", ".local", ".aide.local", "secrets"}
FORBIDDEN_REPO_PATHS = ("runtime", "contracts", "surfaces", "site", "native", "crates", "examples", "control/prototypes")


@dataclass(frozen=True)
class StoreSpec:
    name: str
    relative_path: str
    module: str
    class_name: str
    store_kind: str


STORE_SPECS = (
    StoreSpec("source_cache", "db/source_cache.sqlite", "runtime.source_cache.store", "SourceCacheStore", "sqlite_source_cache"),
    StoreSpec("evidence_ledger", "db/evidence_ledger.sqlite", "runtime.evidence_ledger.store", "EvidenceLedgerStore", "sqlite_evidence_ledger"),
    StoreSpec("review_queue", "db/review_queue.sqlite", "runtime.review_queue.store", "ReviewQueueStore", "sqlite_review_queue"),
    StoreSpec("public_index", "db/public_index.sqlite", "runtime.public_index.store", "PublicIndexStore", "sqlite_public_index"),
    StoreSpec("workunit_queue", "db/workunit_queue.sqlite", "runtime.workunit_queue.store", "WorkUnitQueueStore", "sqlite_workunit_queue"),
    StoreSpec("search_hunt", "db/search_hunt.sqlite", "runtime.search_hunt.store", "SearchHuntStore", "sqlite_search_hunt"),
)


class InstancePathError(ValueError):
    """Raised when an instance path violates LOCAL instance path policy."""


class InstanceVersionError(ValueError):
    """Raised when an existing instance version is unsupported."""


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", help="Explicit local instance root to initialize.")
    parser.add_argument("--force", action="store_true", help="Rewrite existing manifest/status files.")
    parser.add_argument("--dry-run", action="store_true", help="Report actions without creating files.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    parser.add_argument("--output", help="Optional JSON result output path.")
    args = parser.parse_args(argv)

    if not args.instance:
        result = error_result("missing_instance", "--instance is required")
        emit_result(result, args.json, args.output, stdout)
        print("ERROR: --instance is required", file=stderr)
        return 2

    try:
        result = initialize_instance(Path(args.instance), force=args.force, dry_run=args.dry_run)
    except (InstancePathError, InstanceVersionError) as exc:
        result = error_result("forbidden_instance_path" if isinstance(exc, InstancePathError) else "unsupported_instance_schema_version", str(exc), instance=args.instance)
        emit_result(result, args.json, args.output, stdout)
        print(f"ERROR: {exc}", file=stderr)
        return 2
    except Exception as exc:  # pragma: no cover - defensive CLI boundary
        result = error_result("init_failed", str(exc), instance=args.instance)
        emit_result(result, args.json, args.output, stdout)
        print(f"ERROR: {exc}", file=stderr)
        return 1

    emit_result(result, args.json, args.output, stdout)
    return 0 if result["status"] in {"pass", "pass_with_warnings"} else 1


def initialize_instance(instance: Path, *, force: bool = False, dry_run: bool = False) -> dict[str, Any]:
    instance_root = validate_instance_path(instance)
    now = utc_now()
    planned_actions: list[str] = []
    warnings: list[str] = []
    limitations = default_limitations()
    manifest_path = instance_root / "config" / "instance.json"
    status_path = instance_root / "run" / "status.json"
    store_manifest_path = instance_root / "config" / "store_manifest.json"
    migration_state_path = instance_root / "config" / "migration_state.json"

    existing_manifest = load_json_if_exists(manifest_path)
    existing_version = existing_manifest.get("instance_schema_version") if existing_manifest else None
    if existing_manifest and existing_version is not None:
        ensure_supported_instance_version(existing_version)
    elif existing_manifest:
        warnings.append("existing LOCAL-01 unversioned instance metadata completed as schema version 1")

    if existing_manifest and not force:
        instance_id = str(existing_manifest.get("instance_id") or generate_instance_id(instance_root))
        created_at = str(existing_manifest.get("created_at") or now)
        planned_actions.append("reuse existing config/instance.json identity")
    else:
        instance_id = generate_instance_id(instance_root)
        created_at = now
        planned_actions.append("write config/instance.json")

    stores: dict[str, dict[str, Any]] = {}
    for rel in REQUIRED_DIRS:
        planned_actions.append(f"ensure directory {rel}")
    for rel in STATE_FILES:
        planned_actions.append(f"ensure local state file {rel}")
    for spec in STORE_SPECS:
        planned_actions.append(f"initialize store {spec.name}")
    planned_actions.extend(("write config/store_manifest.json", "write config/migration_state.json", "write run/status.json"))

    if dry_run:
        stores = {
            spec.name: {
                "status": "planned",
                "path": (instance_root / spec.relative_path).as_posix(),
                "runtime_api": f"{spec.module}.{spec.class_name}",
            }
            for spec in STORE_SPECS
        }
        manifest = build_manifest(instance_root, instance_id, created_at, now, stores, warnings, limitations)
        store_manifest = build_store_manifest(instance_id, now, stores)
        migration_state = build_migration_state(instance_id, now, warnings=warnings)
    else:
        for rel in REQUIRED_DIRS:
            (instance_root / rel).mkdir(parents=True, exist_ok=True)
        write_text_if_missing(instance_root / "tmp" / ".keep", "")
        write_text_if_missing(instance_root / "exports" / ".keep", "")
        write_text_if_missing(instance_root / "imports" / ".keep", "")
        write_text_if_missing(instance_root / "logs" / "eureka.log", "")
        write_text(instance_root / "run" / "instance.lock", f"{instance_id}\n")

        for spec in STORE_SPECS:
            store_result = initialize_store(spec, instance_root / spec.relative_path)
            stores[spec.name] = store_result
            if store_result.get("status") != "pass":
                warnings.append(f"{spec.name} store initialization did not pass")

        manifest = build_manifest(instance_root, instance_id, created_at, now, stores, warnings, limitations)
        store_manifest = build_store_manifest(instance_id, now, stores)
        migration_state = build_migration_state(instance_id, now, warnings=warnings)
        write_json(manifest_path, manifest)
        write_json(store_manifest_path, store_manifest)
        write_json(migration_state_path, migration_state)
        write_json(status_path, build_status(instance_id, stores, warnings, limitations, migration_state))

    result_status = "pass_with_warnings" if warnings else "pass"
    return {
        "schema_version": "local_instance_init_result.v0",
        "task": TASK_ID,
        "status": result_status,
        "dry_run": dry_run,
        "instance_root": str(instance_root),
        "instance_id": instance_id,
        "instance_schema_version": CURRENT_INSTANCE_SCHEMA_VERSION,
        "created_directories": list(REQUIRED_DIRS),
        "required_files": list(REQUIRED_FILES),
        "planned_database_files": list(PLANNED_DB_FILES),
        "store_manifest": store_manifest,
        "migration_state": migration_state,
        "stores": stores,
        "warnings": warnings,
        "limitations": limitations,
        "planned_actions": planned_actions,
        "server_enabled": False,
        "lan_enabled": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def build_manifest(
    instance_root: Path,
    instance_id: str,
    created_at: str,
    updated_at: str,
    stores: dict[str, dict[str, Any]],
    warnings: Sequence[str],
    limitations: Sequence[str],
) -> dict[str, Any]:
    return {
        "schema_version": INSTANCE_SCHEMA_VERSION,
        "instance_id": instance_id,
        "instance_schema_version": CURRENT_INSTANCE_SCHEMA_VERSION,
        "created_at": created_at,
        "updated_at": updated_at,
        "instance_root": str(instance_root),
        "appliance_mode": "local",
        "server_enabled": False,
        "lan_enabled": False,
        "deployment_enabled": False,
        "stores": {
            name: {
                "relative_path": spec.relative_path,
                "required": True,
                "schema_version": store_schema_version(stores.get(name, {})),
            }
            for name, spec in store_specs_by_name().items()
        },
        "policies": {
            "silent_upgrade_allowed": False,
            "destructive_migration_allowed": False,
            "backup_before_migration_required": True,
            "migration_history_required": True,
        },
        "warnings": list(warnings),
        "limitations": list(limitations),
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def build_store_manifest(instance_id: str, checked_at: str, stores: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": STORE_MANIFEST_SCHEMA_VERSION,
        "instance_id": instance_id,
        "instance_schema_version": CURRENT_INSTANCE_SCHEMA_VERSION,
        "last_checked_at": checked_at,
        "stores": {
            spec.name: {
                "store_id": spec.name,
                "store_kind": spec.store_kind,
                "relative_path": spec.relative_path,
                "required": True,
                "initialized": stores.get(spec.name, {}).get("status") == "pass",
                "schema_version": store_schema_version(stores.get(spec.name, {})),
                "integrity_check_supported": True,
                "migration_supported": True,
                "last_checked_at": checked_at,
            }
            for spec in STORE_SPECS
        },
    }


def build_migration_state(
    instance_id: str,
    checked_at: str,
    *,
    warnings: Sequence[str] = (),
    blockers: Sequence[str] = (),
) -> dict[str, Any]:
    return {
        "schema_version": MIGRATION_STATE_SCHEMA_VERSION,
        "instance_id": instance_id,
        "current_instance_schema_version": CURRENT_INSTANCE_SCHEMA_VERSION,
        "target_instance_schema_version": CURRENT_INSTANCE_SCHEMA_VERSION,
        "migration_needed": False,
        "migration_allowed": False,
        "destructive_migration_required": False,
        "backup_required": False,
        "rollback_available": False,
        "backup_plan": {
            "required_before_apply": True,
            "metadata_only_in_LOCAL_02": True,
        },
        "rollback_plan": {
            "metadata_required_before_apply": True,
            "automatic_rollback_implemented": False,
        },
        "migration_history": [
            {
                "event": "schema_guard_initialized",
                "at": checked_at,
                "from_instance_schema_version": CURRENT_INSTANCE_SCHEMA_VERSION,
                "to_instance_schema_version": CURRENT_INSTANCE_SCHEMA_VERSION,
                "destructive": False,
            }
        ],
        "blockers": list(blockers),
        "warnings": list(warnings),
    }


def build_status(
    instance_id: str,
    stores: dict[str, dict[str, Any]],
    warnings: Sequence[str],
    limitations: Sequence[str],
    migration_state: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": STATUS_SCHEMA_VERSION,
        "instance_id": instance_id,
        "instance_schema_version": CURRENT_INSTANCE_SCHEMA_VERSION,
        "status": "initialized",
        "stores": stores,
        "migration_needed": migration_state.get("migration_needed", False),
        "migration_allowed": migration_state.get("migration_allowed", False),
        "warnings": list(warnings),
        "limitations": list(limitations),
        "server_enabled": False,
        "lan_enabled": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def initialize_store(spec: StoreSpec, db_path: Path) -> dict[str, Any]:
    try:
        module = importlib.import_module(spec.module)
        store_class = getattr(module, spec.class_name)
    except Exception as exc:
        return sqlite_blocked_store_result(spec, db_path, "runtime_store_api_unavailable", exc)

    try:
        with store_class.open(db_path) as store:
            migrations = store.init()
            integrity = store.check_integrity() if hasattr(store, "check_integrity") else sqlite_integrity(db_path)
        return {
            "status": "pass" if integrity.get("status") == "pass" else "fail",
            "path": str(db_path),
            "runtime_api": f"{spec.module}.{spec.class_name}",
            "initialization_method": "runtime_store_api",
            "migrations": migrations,
            "integrity": integrity,
        }
    except Exception as exc:
        return sqlite_blocked_store_result(spec, db_path, "runtime_store_init_failed", exc)


def sqlite_blocked_store_result(spec: StoreSpec, db_path: Path, reason: str, exc: Exception) -> dict[str, Any]:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with sqlite3.connect(db_path) as connection:
            connection.execute(
                "CREATE TABLE IF NOT EXISTS local_instance_store_blockers "
                "(store_name TEXT NOT NULL, reason TEXT NOT NULL, message TEXT NOT NULL)"
            )
            connection.execute(
                "INSERT INTO local_instance_store_blockers (store_name, reason, message) VALUES (?, ?, ?)",
                (spec.name, reason, str(exc)),
            )
    except sqlite3.Error:
        pass
    return {
        "status": "blocked",
        "path": str(db_path),
        "runtime_api": f"{spec.module}.{spec.class_name}",
        "initialization_method": "blocked_runtime_store_api",
        "blocker": reason,
        "message": str(exc),
    }


def sqlite_integrity(db_path: Path) -> dict[str, Any]:
    with sqlite3.connect(db_path) as connection:
        integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
    return {"status": "pass" if integrity == "ok" else "fail", "sqlite_integrity": str(integrity)}


def validate_instance_path(instance: Path) -> Path:
    if not str(instance).strip():
        raise InstancePathError("instance path is required")
    resolved = instance.expanduser().resolve()
    repo = REPO_ROOT.resolve()
    if resolved == repo:
        raise InstancePathError("repo root may not be used as an instance path")
    if resolved == Path.home().resolve():
        raise InstancePathError("home directory may not be used as an implicit instance root")
    parts = set(resolved.parts)
    if parts & FORBIDDEN_ROOT_NAMES:
        raise InstancePathError("hidden/private state roots are forbidden for local instances")
    for rel in FORBIDDEN_REPO_PATHS:
        forbidden = repo / rel
        if is_relative_to(resolved, forbidden.resolve()):
            raise InstancePathError(f"instance path may not live under {rel}")
    site_dist = (repo / "site" / "dist").resolve()
    if is_relative_to(resolved, site_dist):
        raise InstancePathError("instance path may not target generated site outputs")
    return resolved


def ensure_supported_instance_version(value: Any) -> int:
    try:
        version = int(value)
    except (TypeError, ValueError) as exc:
        raise InstanceVersionError("instance_schema_version must be an integer") from exc
    if version < MINIMUM_SUPPORTED_INSTANCE_SCHEMA_VERSION or version > CURRENT_INSTANCE_SCHEMA_VERSION:
        raise InstanceVersionError(
            f"unsupported instance_schema_version {version}; supported range is "
            f"{MINIMUM_SUPPORTED_INSTANCE_SCHEMA_VERSION}..{CURRENT_INSTANCE_SCHEMA_VERSION}"
        )
    return version


def store_schema_version(store_result: dict[str, Any]) -> str | None:
    integrity = store_result.get("integrity")
    if isinstance(integrity, dict) and integrity.get("schema_version"):
        return str(integrity["schema_version"])
    return None


def store_specs_by_name() -> dict[str, StoreSpec]:
    return {spec.name: spec for spec in STORE_SPECS}


def default_limitations() -> list[str]:
    return [
        "LOCAL-02 initializes explicit versioned local state only",
        "HTTP service is not implemented",
        "HTML workbench is not implemented",
        "LAN mode is disabled",
        "deployment is disabled",
        "destructive migration is disabled",
        "Work queue records do not execute background work",
    ]


def generate_instance_id(instance_root: Path) -> str:
    return "eureka-local-" + uuid.uuid5(uuid.NAMESPACE_URL, str(instance_root)).hex[:16]


def load_json_if_exists(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_text_if_missing(path: Path, text: str) -> None:
    if not path.exists():
        write_text(path, text)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def error_result(code: str, message: str, *, instance: str | None = None) -> dict[str, Any]:
    result: dict[str, Any] = {
        "schema_version": "local_instance_init_result.v0",
        "task": TASK_ID,
        "status": "fail",
        "error": code,
        "message": message,
        "server_enabled": False,
        "lan_enabled": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }
    if instance is not None:
        result["instance"] = instance
    return result


def emit_result(result: dict[str, Any], as_json: bool, output: str | None, stdout: TextIO) -> None:
    if output:
        write_json(Path(output), result)
    if as_json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print(f"status: {result['status']}", file=stdout)
        if "instance_root" in result:
            print(f"instance_root: {result['instance_root']}", file=stdout)
        if result.get("warnings"):
            print("warnings:", file=stdout)
            for warning in result["warnings"]:
                print(f"- {warning}", file=stdout)


def is_relative_to(path: Path, base: Path) -> bool:
    try:
        path.relative_to(base)
        return True
    except ValueError:
        return False


if __name__ == "__main__":
    raise SystemExit(main())
