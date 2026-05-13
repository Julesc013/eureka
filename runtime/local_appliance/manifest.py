"""Local appliance store manifest loading and validation."""

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Mapping

from .errors import LocalStoreManifestError
from .instance import resolve_instance_paths


STORE_MANIFEST_SCHEMA_VERSION = "eureka_local_store_manifest.v0"
REQUIRED_STORE_KEYS = ("source_cache", "evidence_ledger", "review_queue", "public_index")
EXPECTED_RELATIVE_PATHS = {
    "source_cache": "db/source_cache.sqlite",
    "evidence_ledger": "db/evidence_ledger.sqlite",
    "review_queue": "db/review_queue.sqlite",
    "public_index": "db/public_index.sqlite",
}


@dataclass(frozen=True)
class LocalStoreEntry:
    store_id: str
    store_kind: str
    relative_path: str
    required: bool
    initialized: bool
    schema_version: str | None
    integrity_check_supported: bool
    migration_supported: bool
    last_checked_at: str
    raw: Mapping[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return dict(self.raw)


@dataclass(frozen=True)
class LocalStoreManifest:
    instance_root: Path
    schema_version: str
    instance_id: str
    instance_schema_version: int
    stores: Mapping[str, LocalStoreEntry]
    raw: Mapping[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return dict(self.raw)

    def store_path(self, store_id: str) -> Path:
        entry = self.stores.get(store_id)
        if entry is None:
            raise LocalStoreManifestError(f"missing store manifest entry: {store_id}")
        return (self.instance_root / entry.relative_path).resolve()


def load_store_manifest(instance_path: str | Path) -> LocalStoreManifest:
    paths = resolve_instance_paths(instance_path)
    try:
        payload = json.loads(paths.store_manifest.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise LocalStoreManifestError("config/store_manifest.json is required") from exc
    except json.JSONDecodeError as exc:
        raise LocalStoreManifestError("config/store_manifest.json must be valid JSON") from exc
    if not isinstance(payload, dict):
        raise LocalStoreManifestError("config/store_manifest.json must contain an object")
    manifest = _from_payload(paths.instance_root, payload)
    validate_store_manifest(manifest)
    return manifest


def validate_store_manifest(manifest: LocalStoreManifest) -> LocalStoreManifest:
    if manifest.schema_version != STORE_MANIFEST_SCHEMA_VERSION:
        raise LocalStoreManifestError("store manifest schema_version mismatch")
    if not manifest.instance_id:
        raise LocalStoreManifestError("store manifest instance_id is required")
    for store_id in REQUIRED_STORE_KEYS:
        entry = manifest.stores.get(store_id)
        if entry is None:
            raise LocalStoreManifestError(f"store manifest missing {store_id}")
        if entry.store_id != store_id:
            raise LocalStoreManifestError(f"store manifest {store_id} store_id mismatch")
        if entry.relative_path != EXPECTED_RELATIVE_PATHS[store_id]:
            raise LocalStoreManifestError(f"store manifest {store_id} relative_path mismatch")
        if Path(entry.relative_path).is_absolute():
            raise LocalStoreManifestError(f"store manifest {store_id} path must be relative")
        if set(Path(entry.relative_path).parts) & {".cache", ".local", "." + "ai" + "de.local", "secrets"}:
            raise LocalStoreManifestError(f"store manifest {store_id} path uses a forbidden root")
        if entry.required is not True:
            raise LocalStoreManifestError(f"store manifest {store_id} must be required")
        if entry.integrity_check_supported is not True:
            raise LocalStoreManifestError(f"store manifest {store_id} must support integrity checks")
    return manifest


def _from_payload(instance_root: Path, payload: Mapping[str, Any]) -> LocalStoreManifest:
    raw_stores = payload.get("stores")
    stores: dict[str, LocalStoreEntry] = {}
    if isinstance(raw_stores, Mapping):
        for key in REQUIRED_STORE_KEYS:
            value = raw_stores.get(key)
            if isinstance(value, Mapping):
                stores[str(key)] = _entry_from_payload(value)
        for key, value in raw_stores.items():
            if key not in stores and isinstance(value, Mapping):
                stores[str(key)] = _entry_from_payload(value)
    try:
        version = int(payload.get("instance_schema_version"))
    except (TypeError, ValueError) as exc:
        raise LocalStoreManifestError("store manifest instance_schema_version must be an integer") from exc
    return LocalStoreManifest(
        instance_root=instance_root,
        schema_version=str(payload.get("schema_version") or ""),
        instance_id=str(payload.get("instance_id") or ""),
        instance_schema_version=version,
        stores=stores,
        raw=payload,
    )


def _entry_from_payload(payload: Mapping[str, Any]) -> LocalStoreEntry:
    schema_value = payload.get("schema_version")
    return LocalStoreEntry(
        store_id=str(payload.get("store_id") or ""),
        store_kind=str(payload.get("store_kind") or ""),
        relative_path=str(payload.get("relative_path") or ""),
        required=bool(payload.get("required")),
        initialized=bool(payload.get("initialized")),
        schema_version=str(schema_value) if schema_value is not None else None,
        integrity_check_supported=bool(payload.get("integrity_check_supported")),
        migration_supported=bool(payload.get("migration_supported")),
        last_checked_at=str(payload.get("last_checked_at") or ""),
        raw=payload,
    )
