# Runtime API Summary

Public API added under `runtime/local/appliance`:

- `LocalInstanceRef`
- `LocalInstancePaths`
- `load_instance_ref`
- `resolve_instance_paths`
- `LocalInstanceConfig`
- `load_instance_config`
- `validate_instance_config`
- `LocalStoreManifest`
- `LocalStoreEntry`
- `load_store_manifest`
- `validate_store_manifest`
- `LocalMigrationState`
- `load_migration_state`
- `validate_migration_state`
- `migration_needed`
- `LocalApplianceRuntime`
- `open_local_appliance`
- `close_local_appliance`
- `LocalRuntimeStatus`
- `build_local_runtime_status`
- `validate_instance_root`
- `validate_supported_instance_version`
- `validate_runtime_composition`
- `validate_no_forbidden_runtime_flags`

The API is domain-named and contains no task IDs or H-series vocabulary.
