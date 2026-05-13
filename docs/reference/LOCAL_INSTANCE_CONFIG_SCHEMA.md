# Local Instance Config Schema

LOCAL-02 defines local appliance instance schema version `1`.

## `config/instance.json`

Required fields:

- `schema_version`
- `instance_id`
- `instance_schema_version`
- `created_at`
- `updated_at`
- `instance_root`
- `appliance_mode`
- `server_enabled`
- `lan_enabled`
- `stores`
- `policies`
- `warnings`
- `limitations`

LOCAL-02 invariants:

- `server_enabled` is `false`
- `lan_enabled` is `false`
- `production_readiness_claimed` is `false`
- `public_launch_readiness_claimed` is `false`
- destructive migration is not allowed

Unsupported instance schema versions fail closed during validation. The init command preserves `instance_id` on rerun and updates `updated_at` while keeping the instance explicit and local.

## `config/store_manifest.json`

The store manifest lists required stores:

- `source_cache`
- `evidence_ledger`
- `review_queue`
- `public_index`

Each entry records `store_id`, `store_kind`, `relative_path`, `required`, `initialized`, `schema_version`, `integrity_check_supported`, `migration_supported`, and `last_checked_at`.

## `config/migration_state.json`

The migration state records `current_instance_schema_version`, `target_instance_schema_version`, `migration_needed`, `migration_allowed`, `destructive_migration_required`, `backup_required`, `rollback_available`, `migration_history`, `blockers`, and `warnings`.
