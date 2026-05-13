"""Stable local appliance runtime composition API."""

from .composition import LocalApplianceRuntime, close_local_appliance, open_local_appliance
from .config import LocalInstanceConfig, load_instance_config, validate_instance_config
from .errors import (
    LocalApplianceError,
    LocalInstanceConfigError,
    LocalInstancePathError,
    LocalMigrationStateError,
    LocalReadOnlyStoreMutationError,
    LocalRuntimeClosedError,
    LocalRuntimeCompositionError,
    LocalRuntimeIntegrityError,
    LocalStoreManifestError,
    LocalUnsupportedInstanceVersionError,
)
from .instance import LocalInstancePaths, LocalInstanceRef, load_instance_ref, resolve_instance_paths
from .manifest import LocalStoreEntry, LocalStoreManifest, load_store_manifest, validate_store_manifest
from .migration import LocalMigrationState, load_migration_state, migration_needed, validate_migration_state
from .status import LocalRuntimeStatus, build_local_runtime_status
from .validation import (
    validate_instance_root,
    validate_no_forbidden_runtime_flags,
    validate_runtime_composition,
    validate_supported_instance_version,
)

__all__ = [
    "LocalApplianceError",
    "LocalApplianceRuntime",
    "LocalInstanceConfig",
    "LocalInstanceConfigError",
    "LocalInstancePathError",
    "LocalInstancePaths",
    "LocalInstanceRef",
    "LocalMigrationState",
    "LocalMigrationStateError",
    "LocalReadOnlyStoreMutationError",
    "LocalRuntimeClosedError",
    "LocalRuntimeCompositionError",
    "LocalRuntimeIntegrityError",
    "LocalRuntimeStatus",
    "LocalStoreEntry",
    "LocalStoreManifest",
    "LocalStoreManifestError",
    "LocalUnsupportedInstanceVersionError",
    "build_local_runtime_status",
    "close_local_appliance",
    "load_instance_config",
    "load_instance_ref",
    "load_migration_state",
    "load_store_manifest",
    "migration_needed",
    "open_local_appliance",
    "resolve_instance_paths",
    "validate_instance_config",
    "validate_instance_root",
    "validate_migration_state",
    "validate_no_forbidden_runtime_flags",
    "validate_runtime_composition",
    "validate_store_manifest",
    "validate_supported_instance_version",
]
