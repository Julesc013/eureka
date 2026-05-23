"""Local appliance instance configuration."""

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Mapping

from .errors import LocalInstanceConfigError
from .instance import CURRENT_INSTANCE_SCHEMA_VERSION, MINIMUM_SUPPORTED_INSTANCE_SCHEMA_VERSION, resolve_instance_paths


INSTANCE_CONFIG_SCHEMA_VERSION = "eureka_local_instance.v0"


@dataclass(frozen=True)
class LocalInstanceConfig:
    instance_root: Path
    schema_version: str
    instance_id: str
    instance_schema_version: int
    appliance_mode: str
    server_enabled: bool
    lan_enabled: bool
    deployment_enabled: bool
    production_readiness_claimed: bool
    public_launch_readiness_claimed: bool
    stores: Mapping[str, Any]
    policies: Mapping[str, Any]
    warnings: tuple[str, ...]
    limitations: tuple[str, ...]
    raw: Mapping[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return dict(self.raw)


def load_instance_config(instance_path: str | Path) -> LocalInstanceConfig:
    paths = resolve_instance_paths(instance_path)
    try:
        payload = json.loads(paths.instance_config.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise LocalInstanceConfigError("config/instance.json is required") from exc
    except json.JSONDecodeError as exc:
        raise LocalInstanceConfigError("config/instance.json must be valid JSON") from exc
    if not isinstance(payload, dict):
        raise LocalInstanceConfigError("config/instance.json must contain an object")
    config = _from_payload(paths.instance_root, payload)
    validate_instance_config(config)
    return config


def validate_instance_config(config: LocalInstanceConfig) -> LocalInstanceConfig:
    if config.schema_version != INSTANCE_CONFIG_SCHEMA_VERSION:
        raise LocalInstanceConfigError("instance config schema_version mismatch")
    if not config.instance_id:
        raise LocalInstanceConfigError("instance_id is required")
    if config.instance_schema_version < MINIMUM_SUPPORTED_INSTANCE_SCHEMA_VERSION:
        raise LocalInstanceConfigError("instance_schema_version is below the supported range")
    if config.instance_schema_version > CURRENT_INSTANCE_SCHEMA_VERSION:
        raise LocalInstanceConfigError("instance_schema_version is above the supported range")
    if config.appliance_mode != "local":
        raise LocalInstanceConfigError("appliance_mode must be local")
    expected_root = str(config.instance_root)
    configured_root = str(config.raw.get("instance_root", ""))
    if Path(configured_root).resolve() != config.instance_root:
        raise LocalInstanceConfigError("instance_root does not match the explicit path")
    if not isinstance(config.stores, Mapping):
        raise LocalInstanceConfigError("stores must be an object")
    if not isinstance(config.policies, Mapping):
        raise LocalInstanceConfigError("policies must be an object")
    for key, value in {
        "server_enabled": config.server_enabled,
        "lan_enabled": config.lan_enabled,
        "deployment_enabled": config.deployment_enabled,
        "production_readiness_claimed": config.production_readiness_claimed,
        "public_launch_readiness_claimed": config.public_launch_readiness_claimed,
    }.items():
        if value is not False:
            raise LocalInstanceConfigError(f"{key} must be false")
    if configured_root != expected_root and Path(configured_root).resolve() == config.instance_root:
        return config
    return config


def _from_payload(instance_root: Path, payload: Mapping[str, Any]) -> LocalInstanceConfig:
    try:
        version = int(payload.get("instance_schema_version"))
    except (TypeError, ValueError) as exc:
        raise LocalInstanceConfigError("instance_schema_version must be an integer") from exc
    return LocalInstanceConfig(
        instance_root=instance_root,
        schema_version=str(payload.get("schema_version") or ""),
        instance_id=str(payload.get("instance_id") or ""),
        instance_schema_version=version,
        appliance_mode=str(payload.get("appliance_mode") or ""),
        server_enabled=bool(payload.get("server_enabled")),
        lan_enabled=bool(payload.get("lan_enabled")),
        deployment_enabled=bool(payload.get("deployment_enabled")),
        production_readiness_claimed=bool(payload.get("production_readiness_claimed")),
        public_launch_readiness_claimed=bool(payload.get("public_launch_readiness_claimed")),
        stores=payload.get("stores") if isinstance(payload.get("stores"), Mapping) else {},
        policies=payload.get("policies") if isinstance(payload.get("policies"), Mapping) else {},
        warnings=tuple(str(item) for item in payload.get("warnings", []) if isinstance(payload.get("warnings", []), list)),
        limitations=tuple(str(item) for item in payload.get("limitations", []) if isinstance(payload.get("limitations", []), list)),
        raw=payload,
    )
