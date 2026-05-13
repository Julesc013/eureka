# Local Instance Migration Guard

LOCAL-02 is a check-only migration guard. It detects unsupported or mismatched instance schema versions before server work begins.

## Supported Versions

- current instance schema version: `1`
- minimum supported instance schema version: `1`
- unsupported version behavior: `fail_closed`

Unsupported versions block validation. The read-only migration status command reports the blocker and marks `migration_needed: true`.

## Migration Needed Detection

Migration is needed when:

- `instance_schema_version` is missing or not an integer
- `instance_schema_version` is outside the supported range
- `instance_schema_version` differs from the current version
- migration state explicitly reports blockers

LOCAL-02 does not perform migrations. It only records status and metadata.

## Backup and Rollback

Backup metadata is required before any future migration apply command. Rollback metadata is also required before any future apply command. LOCAL-02 records this posture but does not create backups, apply migrations, or roll back state.

## Destructive Migration Ban

Destructive migrations are disabled. If an instance reports `destructive_migration_required: true`, validation blocks.
