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
        warnings=tuple(runtime.config.warnings) + tuple(runtime.migration_state.warnings),
    )
