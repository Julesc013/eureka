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

TASK_ID = "LOCAL-01"
INSTANCE_SCHEMA_VERSION = "eureka_local_instance.v0"
STATUS_SCHEMA_VERSION = "eureka_local_instance_status.v0"
DEFAULT_INSTANCE_NAME = "eureka-instance"

REQUIRED_DIRS = ("config", "db", "logs", "run", "tmp", "exports", "imports")
REQUIRED_FILES = ("config/instance.json", "run/status.json")
STATE_FILES = ("logs/eureka.log", "run/instance.lock", "tmp/.keep", "exports/.keep", "imports/.keep")
PLANNED_DB_FILES = (
    "db/source_cache.sqlite",
    "db/evidence_ledger.sqlite",
    "db/review_queue.sqlite",
    "db/public_index.sqlite",
)
FORBIDDEN_ROOT_NAMES = {".cache", ".local", ".aide.local", "secrets"}
FORBIDDEN_REPO_PATHS = ("runtime", "contracts", "surfaces", "site", "native", "crates", "examples", "control/prototypes")


@dataclass(frozen=True)
class StoreSpec:
    name: str
    relative_path: str
    module: str
    class_name: str


STORE_SPECS = (
    StoreSpec("source_cache", "db/source_cache.sqlite", "runtime.source_cache.store", "SourceCacheStore"),
    StoreSpec("evidence_ledger", "db/evidence_ledger.sqlite", "runtime.evidence_ledger.store", "EvidenceLedgerStore"),
    StoreSpec("review_queue", "db/review_queue.sqlite", "runtime.review_queue.store", "ReviewQueueStore"),
    StoreSpec("public_index", "db/public_index.sqlite", "runtime.public_index.store", "PublicIndexStore"),
)


class InstancePathError(ValueError):
    """Raised when an instance path violates LOCAL-01 path policy."""


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
        result = initialize_instance(
            Path(args.instance),
            force=args.force,
            dry_run=args.dry_run,
        )
    except InstancePathError as exc:
        result = error_result("forbidden_instance_path", str(exc), instance=args.instance)
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
    planned_actions: list[str] = []
    warnings: list[str] = []
    limitations = [
        "LOCAL-01 initializes explicit local state only",
        "HTTP service is not implemented",
        "HTML workbench is not implemented",
        "LAN mode is disabled",
        "deployment is disabled",
    ]
    manifest_path = instance_root / "config" / "instance.json"
    status_path = instance_root / "run" / "status.json"

    existing_manifest = load_json_if_exists(manifest_path)
    if existing_manifest and not force:
        instance_id = str(existing_manifest.get("instance_id") or generate_instance_id(instance_root))
        created_at = str(existing_manifest.get("created_at") or utc_now())
        planned_actions.append("reuse existing config/instance.json")
    else:
        instance_id = generate_instance_id(instance_root)
        created_at = utc_now()
        planned_actions.append("write config/instance.json")

    manifest = build_manifest(instance_root, instance_id, created_at)
    stores: dict[str, dict[str, Any]] = {}

    for rel in REQUIRED_DIRS:
        planned_actions.append(f"ensure directory {rel}")
    for rel in STATE_FILES:
        planned_actions.append(f"ensure local state file {rel}")
    for spec in STORE_SPECS:
        planned_actions.append(f"initialize store {spec.name}")

    if not dry_run:
        for rel in REQUIRED_DIRS:
            (instance_root / rel).mkdir(parents=True, exist_ok=True)
        write_text_if_missing(instance_root / "tmp" / ".keep", "")
        write_text_if_missing(instance_root / "exports" / ".keep", "")
        write_text_if_missing(instance_root / "imports" / ".keep", "")
        write_text_if_missing(instance_root / "logs" / "eureka.log", "")
        write_text(instance_root / "run" / "instance.lock", f"{instance_id}\n")

        if force or not manifest_path.exists():
            write_json(manifest_path, manifest)
        elif load_json_if_exists(manifest_path) != manifest:
            existing = load_json_if_exists(manifest_path) or {}
            for key in ("lan_enabled", "server_enabled", "production_readiness_claimed", "public_launch_readiness_claimed"):
                if existing.get(key) is not False:
                    raise ValueError(f"existing manifest has unsafe {key}=true")
            manifest = existing

        for spec in STORE_SPECS:
            store_result = initialize_store(spec, instance_root / spec.relative_path)
            stores[spec.name] = store_result
            if store_result.get("status") != "pass":
                warnings.append(f"{spec.name} store initialization did not pass")

        status_payload = build_status(instance_id, stores, warnings, limitations)
        write_json(status_path, status_payload)
    else:
        stores = {
            spec.name: {
                "status": "planned",
                "path": (instance_root / spec.relative_path).as_posix(),
                "runtime_api": f"{spec.module}.{spec.class_name}",
            }
            for spec in STORE_SPECS
        }

    result_status = "pass_with_warnings" if warnings else "pass"
    return {
        "schema_version": "local_instance_init_result.v0",
        "task": TASK_ID,
        "status": result_status,
        "dry_run": dry_run,
        "instance_root": str(instance_root),
        "instance_id": instance_id,
        "created_directories": list(REQUIRED_DIRS),
        "required_files": list(REQUIRED_FILES),
        "planned_database_files": list(PLANNED_DB_FILES),
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


def build_manifest(instance_root: Path, instance_id: str, created_at: str) -> dict[str, Any]:
    return {
        "schema_version": INSTANCE_SCHEMA_VERSION,
        "instance_id": instance_id,
        "created_at": created_at,
        "instance_root": str(instance_root),
        "appliance_mode": "local",
        "lan_enabled": False,
        "server_enabled": False,
        "deployment_enabled": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def build_status(
    instance_id: str,
    stores: dict[str, dict[str, Any]],
    warnings: Sequence[str],
    limitations: Sequence[str],
) -> dict[str, Any]:
    return {
        "schema_version": STATUS_SCHEMA_VERSION,
        "instance_id": instance_id,
        "status": "initialized",
        "stores": stores,
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
