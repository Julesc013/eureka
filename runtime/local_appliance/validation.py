"""Validation helpers for local appliance composition."""

from pathlib import Path
from typing import Any, Mapping

from .config import LocalInstanceConfig
from .errors import LocalInstanceConfigError, LocalRuntimeCompositionError, LocalUnsupportedInstanceVersionError
from .instance import CURRENT_INSTANCE_SCHEMA_VERSION, MINIMUM_SUPPORTED_INSTANCE_SCHEMA_VERSION, resolve_instance_paths


def validate_instance_root(path: str | Path) -> Path:
    return resolve_instance_paths(path).instance_root


def validate_supported_instance_version(config: LocalInstanceConfig) -> LocalInstanceConfig:
    version = config.instance_schema_version
    if version < MINIMUM_SUPPORTED_INSTANCE_SCHEMA_VERSION or version > CURRENT_INSTANCE_SCHEMA_VERSION:
        raise LocalUnsupportedInstanceVersionError(
            f"unsupported instance_schema_version {version}; supported range is "
            f"{MINIMUM_SUPPORTED_INSTANCE_SCHEMA_VERSION}..{CURRENT_INSTANCE_SCHEMA_VERSION}"
        )
    return config


def validate_runtime_composition(runtime: Any) -> Any:
    required = (
        "source_cache",
        "evidence_ledger",
        "review_queue",
        "public_index",
        "workunit_queue",
        "search_hunt",
        "search_need",
        "agent_research",
        "ai_escalation",
    )
    for name in required:
        if getattr(runtime, name, None) is None:
            raise LocalRuntimeCompositionError(f"runtime missing store: {name}")
        if name not in runtime.store_manifest.stores:
            raise LocalRuntimeCompositionError(f"manifest missing store: {name}")
    status = runtime.status()
    validate_no_forbidden_runtime_flags(status)
    if status.to_dict().get("store_count") != len(required):
        raise LocalRuntimeCompositionError("runtime store count mismatch")
    return runtime


def validate_no_forbidden_runtime_flags(status: Any) -> Mapping[str, Any]:
    payload = status.to_dict() if hasattr(status, "to_dict") else status
    if not isinstance(payload, Mapping):
        raise LocalInstanceConfigError("runtime status must be a mapping")
    expected_false = (
        "server_enabled",
        "lan_enabled",
        "deployment_performed",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    )
    for key in expected_false:
        if payload.get(key) is not False:
            raise LocalRuntimeCompositionError(f"{key} must be false")
    return payload
