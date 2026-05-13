# Local Appliance Runtime API

The public runtime API lives in `runtime/local_appliance`.

## Instance API

- `LocalInstanceRef`
- `LocalInstancePaths`
- `load_instance_ref(instance_path)`
- `resolve_instance_paths(instance_path)`

These functions normalize and validate explicit instance roots. They do not infer hidden state locations.

## Config API

- `LocalInstanceConfig`
- `load_instance_config(instance_path)`
- `validate_instance_config(config)`

Config validation requires local appliance mode, supported instance schema version, and disabled server, LAN, deployment, production readiness, and public launch flags.

## Manifest API

- `LocalStoreManifest`
- `LocalStoreEntry`
- `load_store_manifest(instance_path)`
- `validate_store_manifest(manifest)`

The manifest is the only source for store paths. The required manifest keys are `source_cache`, `evidence_ledger`, `review_queue`, and `public_index`.

## Migration API

- `LocalMigrationState`
- `load_migration_state(instance_path)`
- `validate_migration_state(state)`
- `migration_needed(state)`

Runtime opening fails closed when migration state records blockers or destructive migration requirements.

## Composition API

- `LocalApplianceRuntime`
- `open_local_appliance(instance_path, read_only=False)`
- `close_local_appliance(runtime)`

`LocalApplianceRuntime.status()` returns `LocalRuntimeStatus`.
`LocalApplianceRuntime.check_integrity()` returns one status object for all four stores.
`LocalApplianceRuntime.close()` is idempotent.

## Status API

- `LocalRuntimeStatus`
- `build_local_runtime_status(runtime)`

Status includes `instance_id`, `instance_schema_version`, per-store status, `migration_needed`, `read_only`, and disabled server/LAN/deployment/readiness flags.

## Validation API

- `validate_instance_root(path)`
- `validate_supported_instance_version(config)`
- `validate_runtime_composition(runtime)`
- `validate_no_forbidden_runtime_flags(status)`

These helpers are intended for future service/workbench/worker startup checks and tests.

## LOCAL-04 Service Consumer

`runtime/local_service` is the first product-facing consumer of this API. It opens the runtime with `read_only=True` and serves status/search/object/source/absence reads over localhost.

The service does not receive a direct database path. Store paths continue to come from the local instance manifest.
