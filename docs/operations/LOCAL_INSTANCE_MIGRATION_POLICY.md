# Local Instance Migration Policy

LOCAL-02 sets the migration default mode to `check_only`.

## Rules

- Migration apply requires an explicit future flag.
- Destructive migrations are disabled.
- Unknown stores fail closed.
- Missing stores warn or block according to requiredness.
- Required stores block when missing.
- Backup metadata is required before future apply.
- Rollback metadata is required before future apply.
- Migration history is required.
- Committed local instance state is forbidden.

## Commands

Inspect migration status:

```bash
python scripts/eureka_instance_migration_status.py --instance ./eureka-instance --json
```

Validate instance state:

```bash
python scripts/eureka_validate_instance.py --instance ./eureka-instance --json
```

No command in LOCAL-02 applies a migration.

## LOCAL-03 Handoff

LOCAL-03 should use the versioned instance boundary and fail closed when the instance is unsupported, missing required stores, or marked as needing migration before composition work can safely proceed.
