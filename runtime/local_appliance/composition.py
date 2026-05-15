"""Local appliance runtime composition."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from runtime.evidence_ledger.store import EvidenceLedgerStore
from runtime.public_index.store import PublicIndexStore
from runtime.review_queue.store import ReviewQueueStore
from runtime.search_hunt.store import SearchHuntStore
from runtime.search_need.store import SearchNeedStore
from runtime.source_cache.store import SourceCacheStore

from .config import LocalInstanceConfig, load_instance_config, validate_instance_config
from .errors import (
    LocalReadOnlyStoreMutationError,
    LocalRuntimeClosedError,
    LocalRuntimeCompositionError,
)
from .instance import LocalInstanceRef, load_instance_ref, resolve_instance_paths
from .manifest import LocalStoreManifest, load_store_manifest, validate_store_manifest
from .migration import LocalMigrationState, load_migration_state, validate_migration_state
from .validation import validate_supported_instance_version


STORE_CLASSES = {
    "source_cache": SourceCacheStore,
    "evidence_ledger": EvidenceLedgerStore,
    "review_queue": ReviewQueueStore,
    "public_index": PublicIndexStore,
    "search_hunt": SearchHuntStore,
    "search_need": SearchNeedStore,
}
STORE_IDS = ("source_cache", "evidence_ledger", "review_queue", "public_index", "workunit_queue", "search_hunt", "search_need")


@dataclass
class LocalApplianceRuntime:
    instance_ref: LocalInstanceRef
    config: LocalInstanceConfig
    store_manifest: LocalStoreManifest
    migration_state: LocalMigrationState
    source_cache: Any
    evidence_ledger: Any
    review_queue: Any
    public_index: Any
    workunit_queue: Any
    search_hunt: Any
    search_need: Any
    read_only: bool = False
    _closed: bool = False

    def status(self):
        self._ensure_open()
        from .status import build_local_runtime_status

        return build_local_runtime_status(self)

    def check_integrity(self) -> dict[str, Any]:
        self._ensure_open()
        stores = {
            "source_cache": self.source_cache.check_integrity(),
            "evidence_ledger": self.evidence_ledger.check_integrity(),
            "review_queue": self.review_queue.check_integrity(),
            "public_index": self.public_index.check_integrity(),
            "workunit_queue": self.workunit_queue.check_integrity(),
            "search_hunt": self.search_hunt.check_integrity(),
            "search_need": self.search_need.check_integrity(),
        }
        return {
            "schema_version": "local_runtime_integrity.v0",
            "status": "pass" if all(item.get("status") == "pass" for item in stores.values()) else "fail",
            "stores": stores,
        }

    def close(self) -> None:
        if self._closed:
            return
        for store in (self.search_need, self.search_hunt, self.workunit_queue, self.public_index, self.review_queue, self.evidence_ledger, self.source_cache):
            if hasattr(store, "close"):
                store.close()
        self._closed = True

    def _ensure_open(self) -> None:
        if self._closed:
            raise LocalRuntimeClosedError("local appliance runtime is closed")


class LocalRuntimeStoreHandle:
    def __init__(self, store: Any, read_only: bool):
        self._store = store
        self._read_only = read_only

    def __getattr__(self, name: str) -> Any:
        if self._read_only and _is_mutation_name(name):
            raise LocalReadOnlyStoreMutationError(f"{name} is not available in read-only mode")
        return getattr(self._store, name)

    def close(self) -> None:
        self._store.close()

    def check_integrity(self) -> dict[str, Any]:
        return self._store.check_integrity()

    def schema_version(self) -> str:
        return self._store.schema_version()

    @property
    def path(self) -> Any:
        return self._store.path


def open_local_appliance(instance_path: str | Path, read_only: bool = False) -> LocalApplianceRuntime:
    paths = resolve_instance_paths(instance_path)
    config = validate_supported_instance_version(validate_instance_config(load_instance_config(paths.instance_root)))
    manifest = validate_store_manifest(load_store_manifest(paths.instance_root))
    migration_state = validate_migration_state(load_migration_state(paths.instance_root))
    instance_ref = load_instance_ref(paths.instance_root)
    _validate_identity_alignment(instance_ref, config, manifest, migration_state)

    opened: dict[str, Any] = {}
    try:
        for store_id in STORE_IDS:
            store_class = _store_class(store_id)
            store_path = manifest.store_path(store_id)
            _require_manifest_store_path(paths.instance_root, store_path, store_id)
            store = store_class.open(store_path)
            opened[store_id] = LocalRuntimeStoreHandle(store, read_only=read_only)
        return LocalApplianceRuntime(
            instance_ref=instance_ref,
            config=config,
            store_manifest=manifest,
            migration_state=migration_state,
            source_cache=opened["source_cache"],
            evidence_ledger=opened["evidence_ledger"],
            review_queue=opened["review_queue"],
            public_index=opened["public_index"],
            workunit_queue=opened["workunit_queue"],
            search_hunt=opened["search_hunt"],
            search_need=opened["search_need"],
            read_only=read_only,
        )
    except Exception:
        for store in reversed(list(opened.values())):
            if hasattr(store, "close"):
                store.close()
        raise


def close_local_appliance(runtime: LocalApplianceRuntime) -> None:
    runtime.close()


def _validate_identity_alignment(
    instance_ref: LocalInstanceRef,
    config: LocalInstanceConfig,
    manifest: LocalStoreManifest,
    migration_state: LocalMigrationState,
) -> None:
    if config.instance_id != instance_ref.instance_id:
        raise LocalRuntimeCompositionError("instance identity mismatch")
    if manifest.instance_id != instance_ref.instance_id:
        raise LocalRuntimeCompositionError("store manifest identity mismatch")
    if migration_state.instance_id != instance_ref.instance_id:
        raise LocalRuntimeCompositionError("migration state identity mismatch")
    if manifest.instance_schema_version != instance_ref.instance_schema_version:
        raise LocalRuntimeCompositionError("store manifest schema version mismatch")
    if migration_state.current_instance_schema_version != instance_ref.instance_schema_version:
        raise LocalRuntimeCompositionError("migration state schema version mismatch")


def _require_manifest_store_path(instance_root: Path, store_path: Path, store_id: str) -> None:
    resolved_root = instance_root.resolve()
    resolved_store = store_path.resolve()
    try:
        resolved_store.relative_to(resolved_root)
    except ValueError as exc:
        raise LocalRuntimeCompositionError(f"{store_id} store path escapes the instance root") from exc
    if not resolved_store.is_file():
        raise LocalRuntimeCompositionError(f"{store_id} store file is required before runtime opening")


def _store_class(store_id: str) -> Any:
    if store_id == "workunit_queue":
        module = __import__("runtime.workunit_queue.store", fromlist=["WorkUnitQueueStore"])
        return getattr(module, "WorkUnitQueueStore")
    return STORE_CLASSES[store_id]


def _is_mutation_name(name: str) -> bool:
    mutation_prefixes = (
        "write",
        "append",
        "record",
        "set",
        "enqueue",
        "link",
        "create",
        "transition",
        "attach",
        "apply",
        "add",
        "remove",
        "pause",
        "resume",
        "cancel",
        "block",
        "complete",
        "fail",
    )
    mutation_names = {"transaction", "connection", "init"}
    return name in mutation_names or any(name.startswith(prefix) for prefix in mutation_prefixes)
