"""Unified local appliance runtime status."""

from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class LocalRuntimeStatus:
    schema_version: str
    status: str
    instance_root: str
    instance_id: str
    instance_schema_version: int
    store_count: int
    stores: Mapping[str, Any]
    migration_needed: bool
    read_only: bool
    server_enabled: bool
    lan_enabled: bool
    deployment_performed: bool
    production_readiness_claimed: bool
    public_launch_readiness_claimed: bool
    workunit_queue: Mapping[str, Any]
    search_hunt: Mapping[str, Any]
    search_need: Mapping[str, Any]
    warnings: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "status": self.status,
            "instance_root": self.instance_root,
            "instance_id": self.instance_id,
            "instance_schema_version": self.instance_schema_version,
            "store_count": self.store_count,
            "stores": dict(self.stores),
            "migration_needed": self.migration_needed,
            "read_only": self.read_only,
            "server_enabled": self.server_enabled,
            "lan_enabled": self.lan_enabled,
            "deployment_performed": self.deployment_performed,
            "production_readiness_claimed": self.production_readiness_claimed,
            "public_launch_readiness_claimed": self.public_launch_readiness_claimed,
            "workunit_queue": dict(self.workunit_queue),
            "search_hunt": dict(self.search_hunt),
            "search_need": dict(self.search_need),
            "warnings": list(self.warnings),
        }


def build_local_runtime_status(runtime: Any) -> LocalRuntimeStatus:
    integrity = runtime.check_integrity()
    store_status = {
        store_id: {
            "store_id": store_id,
            "relative_path": runtime.store_manifest.stores[store_id].relative_path,
            "path": str(runtime.store_manifest.store_path(store_id)),
            "opened": True,
            "integrity_check_supported": True,
            "integrity_status": payload.get("status"),
            "schema_version": payload.get("schema_version"),
        }
        for store_id, payload in integrity["stores"].items()
    }
    status = "pass" if integrity.get("status") == "pass" else "fail"
    return LocalRuntimeStatus(
        schema_version="local_runtime_status.v0",
        status=status,
        instance_root=str(runtime.instance_ref.instance_root),
        instance_id=runtime.instance_ref.instance_id,
        instance_schema_version=runtime.instance_ref.instance_schema_version,
        store_count=len(store_status),
        stores=store_status,
        migration_needed=bool(runtime.migration_state.migration_needed),
        read_only=bool(runtime.read_only),
        server_enabled=False,
        lan_enabled=False,
        deployment_performed=False,
        production_readiness_claimed=False,
        public_launch_readiness_claimed=False,
        workunit_queue=_workunit_queue_status(runtime),
        search_hunt=_search_hunt_status(runtime),
        search_need=_search_need_status(runtime),
        warnings=tuple(runtime.config.warnings) + tuple(runtime.migration_state.warnings),
    )


def _workunit_queue_status(runtime: Any) -> Mapping[str, Any]:
    summary = runtime.workunit_queue.summarize()
    payload = summary.to_dict() if hasattr(summary, "to_dict") else dict(summary)
    payload.update(
        {
            "store_id": "workunit_queue",
            "relative_path": runtime.store_manifest.stores["workunit_queue"].relative_path,
            "execution_enabled": False,
            "worker_runner_enabled": False,
        }
    )
    return payload


def _search_hunt_status(runtime: Any) -> Mapping[str, Any]:
    summary = runtime.search_hunt.summarize()
    payload = dict(summary)
    payload.update(
        {
            "store_id": "search_hunt",
            "relative_path": runtime.store_manifest.stores["search_hunt"].relative_path,
            "session_creation_enabled": True,
            "workunit_creation_enabled": False,
            "source_probe_execution_enabled": False,
            "model_provider_enabled": False,
        }
    )
    return payload


def _search_need_status(runtime: Any) -> Mapping[str, Any]:
    summary = runtime.search_need.summarize()
    payload = dict(summary)
    payload.update(
        {
            "store_id": "search_need",
            "relative_path": runtime.store_manifest.stores["search_need"].relative_path,
            "creation_from_hunt_enabled": True,
            "workunit_creation_enabled": False,
            "source_probe_execution_enabled": False,
            "model_provider_enabled": False,
            "sync_enabled": False,
        }
    )
    return payload
