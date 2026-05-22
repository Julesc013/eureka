"""Explicit local appliance instance path handling."""

from dataclasses import dataclass
from pathlib import Path
import json
from typing import Any

from .errors import LocalInstanceConfigError, LocalInstancePathError
from .paths import resolve_instance_root, resolve_repo_root


REPO_ROOT = resolve_repo_root()
CURRENT_INSTANCE_SCHEMA_VERSION = 1
MINIMUM_SUPPORTED_INSTANCE_SCHEMA_VERSION = 1
FORBIDDEN_REPO_PATHS = (
    "runtime/connectors",
    "runtime/local_foundry",
    "runtime/extraction",
    "runtime/search_quality",
    "contracts",
    "surfaces",
    "site",
    "native",
    "crates",
    "examples",
    "archive/prototypes",
)


@dataclass(frozen=True)
class LocalInstanceRef:
    instance_root: Path
    instance_id: str
    instance_schema_version: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "instance_root": str(self.instance_root),
            "instance_id": self.instance_id,
            "instance_schema_version": self.instance_schema_version,
        }


@dataclass(frozen=True)
class LocalInstancePaths:
    instance_root: Path
    config_dir: Path
    db_dir: Path
    logs_dir: Path
    run_dir: Path
    tmp_dir: Path
    exports_dir: Path
    imports_dir: Path
    instance_config: Path
    store_manifest: Path
    migration_state: Path
    status: Path
    source_cache_db: Path
    evidence_ledger_db: Path
    review_queue_db: Path
    public_index_db: Path

    def to_dict(self) -> dict[str, str]:
        return {
            "instance_root": str(self.instance_root),
            "config_dir": str(self.config_dir),
            "db_dir": str(self.db_dir),
            "logs_dir": str(self.logs_dir),
            "run_dir": str(self.run_dir),
            "tmp_dir": str(self.tmp_dir),
            "exports_dir": str(self.exports_dir),
            "imports_dir": str(self.imports_dir),
            "instance_config": str(self.instance_config),
            "store_manifest": str(self.store_manifest),
            "migration_state": str(self.migration_state),
            "status": str(self.status),
            "source_cache_db": str(self.source_cache_db),
            "evidence_ledger_db": str(self.evidence_ledger_db),
            "review_queue_db": str(self.review_queue_db),
            "public_index_db": str(self.public_index_db),
        }


def load_instance_ref(instance_path: str | Path) -> LocalInstanceRef:
    paths = resolve_instance_paths(instance_path)
    payload = _read_json(paths.instance_config)
    instance_id = str(payload.get("instance_id") or "")
    if not instance_id:
        raise LocalInstanceConfigError("instance_id is required")
    try:
        version = int(payload.get("instance_schema_version"))
    except (TypeError, ValueError) as exc:
        raise LocalInstanceConfigError("instance_schema_version must be an integer") from exc
    return LocalInstanceRef(
        instance_root=paths.instance_root,
        instance_id=instance_id,
        instance_schema_version=version,
    )


def resolve_instance_paths(instance_path: str | Path) -> LocalInstancePaths:
    root = _validate_instance_path(instance_path)
    return LocalInstancePaths(
        instance_root=root,
        config_dir=root / "config",
        db_dir=root / "db",
        logs_dir=root / "logs",
        run_dir=root / "run",
        tmp_dir=root / "tmp",
        exports_dir=root / "exports",
        imports_dir=root / "imports",
        instance_config=root / "config" / "instance.json",
        store_manifest=root / "config" / "store_manifest.json",
        migration_state=root / "config" / "migration_state.json",
        status=root / "run" / "status.json",
        source_cache_db=root / "db" / "source_cache.sqlite",
        evidence_ledger_db=root / "db" / "evidence_ledger.sqlite",
        review_queue_db=root / "db" / "review_queue.sqlite",
        public_index_db=root / "db" / "public_index.sqlite",
    )


def _validate_instance_path(instance_path: str | Path) -> Path:
    if instance_path is None:
        raise LocalInstancePathError("instance path is required")
    text = str(instance_path).strip()
    if not text:
        raise LocalInstancePathError("instance path is required")
    resolved = resolve_instance_root(text, REPO_ROOT)
    repo = REPO_ROOT.resolve()
    for rel in FORBIDDEN_REPO_PATHS:
        if _is_relative_to(resolved, (repo / rel).resolve()):
            raise LocalInstancePathError(f"instance path may not live under {rel}")
    if _is_relative_to(resolved, (repo / "site" / "dist").resolve()):
        raise LocalInstancePathError("instance path may not target generated site outputs")
    return resolved


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise LocalInstanceConfigError(f"missing instance file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise LocalInstanceConfigError(f"invalid JSON in instance file: {path}") from exc
    if not isinstance(payload, dict):
        raise LocalInstanceConfigError("instance JSON must contain an object")
    return payload


def _is_relative_to(path: Path, base: Path) -> bool:
    try:
        path.relative_to(base)
        return True
    except ValueError:
        return False
