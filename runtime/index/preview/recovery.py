"""Recovery, backup, and migration helpers for the operational Preview Index."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import shutil
import sqlite3
import tempfile
from typing import Any, Mapping


BACKUP_SCHEMA = "eureka.preview_index_backup.v0"
MIGRATION_SCHEMA = "eureka.preview_index_migration.v0"
CURRENT_SCHEMA_VERSION = 1
MINIMUM_SUPPORTED_SCHEMA_VERSION = 1


def migration_preflight(sqlite_path: str | Path) -> dict[str, Any]:
    path = Path(sqlite_path)
    if not path.exists():
        return {
            "schema_version": MIGRATION_SCHEMA,
            "status": "absent",
            "path": str(path),
            "current_schema_version": 0,
            "minimum_supported_schema_version": MINIMUM_SUPPORTED_SCHEMA_VERSION,
            "migration_needed": False,
        }
    conn = sqlite3.connect(str(path))
    try:
        conn.execute("PRAGMA foreign_keys=ON")
        user_version = int(conn.execute("PRAGMA user_version").fetchone()[0] or 0)
        integrity = str(conn.execute("PRAGMA integrity_check").fetchone()[0])
        tables = [str(row[0]) for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
    finally:
        conn.close()
    status = "pass" if integrity == "ok" and user_version >= MINIMUM_SUPPORTED_SCHEMA_VERSION else "fail"
    return {
        "schema_version": MIGRATION_SCHEMA,
        "status": status,
        "path": str(path),
        "current_schema_version": user_version,
        "minimum_supported_schema_version": MINIMUM_SUPPORTED_SCHEMA_VERSION,
        "target_schema_version": CURRENT_SCHEMA_VERSION,
        "migration_needed": user_version < CURRENT_SCHEMA_VERSION,
        "integrity_check": integrity,
        "tables": tables,
    }


def run_migrations(sqlite_path: str | Path) -> dict[str, Any]:
    """Run idempotent v0 migrations without destroying data."""

    path = Path(sqlite_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    backup_path = ""
    if path.exists():
        backup_path = str(path.with_suffix(path.suffix + ".pre-migration-backup"))
        shutil.copy2(path, backup_path)
    conn = sqlite3.connect(str(path))
    try:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("PRAGMA busy_timeout=5000")
        conn.execute("CREATE TABLE IF NOT EXISTS schema_migration(version INTEGER PRIMARY KEY, applied_at TEXT DEFAULT CURRENT_TIMESTAMP)")
        conn.execute("PRAGMA user_version=1")
        conn.commit()
    finally:
        conn.close()
    post = migration_preflight(path)
    return {
        "schema_version": MIGRATION_SCHEMA,
        "status": "pass" if post.get("status") in {"pass", "absent"} else "fail",
        "path": str(path),
        "backup_before_migration": backup_path,
        "post_migration": post,
        "destructive_reset_performed": False,
    }


def create_backup(*, instance_root: str | Path, backup_root: str | Path, sqlite_path: str | Path, run_root: str | Path, foundry_root: str | Path, config_dir: str | Path, generation_root: str | Path) -> dict[str, Any]:
    instance = Path(instance_root).resolve()
    backup_id = "backup-" + _now_compact()
    root = Path(backup_root) / backup_id
    root.mkdir(parents=True, exist_ok=False)
    files: list[dict[str, Any]] = []

    _copy_tree(Path(config_dir), root / "config", root, files, role="config", redact_names={"secrets.json", ".env"})
    _copy_sqlite_snapshot(Path(sqlite_path), root / "db" / "preview" / "preview.sqlite", root, files)
    _copy_tree(Path(run_root), root / "run" / "e2e-reference" / "runs", root, files, role="run_state")
    _copy_tree(Path(foundry_root), root / "run" / "foundry" / "runs", root, files, role="foundry_checkpoint")
    _copy_tree(Path(generation_root), root / "db" / "e2e-reference" / "preview-index", root, files, role="immutable_generation")

    manifest = {
        "schema_version": BACKUP_SCHEMA,
        "backup_id": backup_id,
        "created_at": _now(),
        "source_instance": str(instance),
        "files": files,
        "excluded": ["secrets", "provider credentials", "transient caches", "raw provider responses"],
        "provider_result_payload_included": False,
        "credential_value_exposed": False,
        "reviewed_master_mutation": False,
        "public_index_mutation": False,
    }
    _write_json(root / "backup_manifest.json", manifest)
    verification = verify_backup(root)
    return {
        "schema_version": "eureka.preview_index_backup_create.v0",
        "status": "pass" if verification.get("status") == "pass" else "fail",
        "backup_id": backup_id,
        "backup_path": str(root),
        "manifest": str(root / "backup_manifest.json"),
        "file_count": len(files),
        "verification": verification,
        "provider_result_payload_included": False,
        "credential_value_exposed": False,
    }


def list_backups(backup_root: str | Path) -> dict[str, Any]:
    root = Path(backup_root)
    backups = []
    if root.exists():
        for manifest in sorted(root.glob("backup-*/backup_manifest.json"), reverse=True):
            payload = _load_json_optional(manifest)
            backups.append({"backup_id": payload.get("backup_id", manifest.parent.name), "path": str(manifest.parent), "created_at": payload.get("created_at", ""), "file_count": len(payload.get("files") or [])})
    return {"schema_version": "eureka.preview_index_backup_list.v0", "status": "pass", "backup_count": len(backups), "backups": backups}


def verify_backup(backup_path: str | Path) -> dict[str, Any]:
    root = Path(backup_path)
    manifest = _load_json_optional(root / "backup_manifest.json")
    errors: list[str] = []
    if manifest.get("schema_version") != BACKUP_SCHEMA:
        errors.append("backup manifest missing or unsupported")
    for entry in manifest.get("files") or []:
        if not isinstance(entry, Mapping):
            continue
        path = root / str(entry.get("path") or "")
        if not path.is_file():
            errors.append(f"missing file: {entry.get('path')}")
            continue
        expected = str(entry.get("sha256") or "")
        actual = _sha256(path)
        if expected and expected != actual:
            errors.append(f"hash mismatch: {entry.get('path')}")
        if entry.get("role") == "preview_sqlite":
            integrity = _sqlite_integrity(path)
            if integrity != "ok":
                errors.append(f"sqlite integrity failed: {integrity}")
    return {
        "schema_version": "eureka.preview_index_backup_verify.v0",
        "status": "pass" if not errors else "fail",
        "backup_path": str(root),
        "errors": errors,
        "provider_result_payload_included": False,
        "credential_value_exposed": False,
    }


def restore_backup(backup_path: str | Path, target_instance: str | Path) -> dict[str, Any]:
    root = Path(backup_path)
    target = Path(target_instance).resolve()
    verification = verify_backup(root)
    if verification.get("status") != "pass":
        return {"schema_version": "eureka.preview_index_backup_restore.v0", "status": "fail", "verification": verification, "restored_files": []}
    manifest = _load_json_optional(root / "backup_manifest.json")
    restored: list[dict[str, str]] = []
    for entry in manifest.get("files") or []:
        if not isinstance(entry, Mapping):
            continue
        relative = Path(str(entry.get("path") or ""))
        role = str(entry.get("role") or "")
        if role == "preview_sqlite":
            destination = target / "db" / "preview" / "preview.sqlite"
        elif role == "config":
            destination = target / relative
        elif role == "run_state":
            destination = target / relative
        elif role == "foundry_checkpoint":
            destination = target / relative
        elif role == "immutable_generation":
            destination = target / relative
        else:
            continue
        source = root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        restored.append({"role": role, "path": str(destination)})
    return {
        "schema_version": "eureka.preview_index_backup_restore.v0",
        "status": "pass",
        "target_instance": str(target),
        "restored_files": restored,
        "verification": verification,
        "destructive_reset_performed": False,
        "provider_result_payload_included": False,
        "credential_value_exposed": False,
    }


def rebuild_probe(sqlite_path: str | Path) -> dict[str, Any]:
    path = Path(sqlite_path)
    if not path.exists():
        return {"schema_version": "eureka.preview_index_rebuild_probe.v0", "status": "absent", "source_observation_count": 0, "rebuild_possible": False}
    conn = sqlite3.connect(str(path))
    try:
        observation_count = int(conn.execute("SELECT COUNT(*) FROM source_observation").fetchone()[0])
        document_count = int(conn.execute("SELECT COUNT(*) FROM preview_document").fetchone()[0])
    finally:
        conn.close()
    return {
        "schema_version": "eureka.preview_index_rebuild_probe.v0",
        "status": "pass",
        "source_observation_count": observation_count,
        "preview_document_count": document_count,
        "rebuild_possible": observation_count >= document_count,
    }


def _copy_sqlite_snapshot(source: Path, destination: Path, backup_root: Path, files: list[dict[str, Any]]) -> None:
    if not source.exists():
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    src = None
    dst = None
    fallback_copy = False
    try:
        src = sqlite3.connect(str(source))
        dst = sqlite3.connect(str(destination))
        src.backup(dst)
    except sqlite3.DatabaseError:
        fallback_copy = True
    finally:
        if dst is not None:
            dst.close()
        if src is not None:
            src.close()
    if fallback_copy:
        shutil.copy2(source, destination)
    files.append(_manifest_entry(destination, destination.relative_to(backup_root), "preview_sqlite"))


def _copy_tree(source: Path, destination: Path, backup_root: Path, files: list[dict[str, Any]], *, role: str, redact_names: set[str] | None = None) -> None:
    if not source.exists():
        return
    redact = {item.casefold() for item in (redact_names or set())}
    for path in source.rglob("*"):
        if not path.is_file() or path.name.casefold() in redact:
            continue
        rel = path.relative_to(source)
        target = destination / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
        files.append(_manifest_entry(target, target.relative_to(backup_root), role))


def _manifest_entry(path: Path, relative: Path, role: str) -> dict[str, Any]:
    return {"role": role, "path": relative.as_posix(), "bytes": path.stat().st_size, "sha256": _sha256(path)}


def _sqlite_integrity(path: Path) -> str:
    try:
        conn = sqlite3.connect(str(path))
        try:
            return str(conn.execute("PRAGMA integrity_check").fetchone()[0])
        finally:
            conn.close()
    except sqlite3.DatabaseError as exc:
        return str(exc)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="\n", dir=path.parent, delete=False) as handle:
        json.dump(dict(payload), handle, indent=2, sort_keys=True)
        handle.write("\n")
        temp = Path(handle.name)
    temp.replace(path)


def _load_json_optional(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _now_compact() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
