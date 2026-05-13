# Local Instance Layout

Initialize the default local instance with:

```bash
python scripts/eureka_init_instance.py --instance ./eureka-instance
```

Validate it with:

```bash
python scripts/eureka_validate_instance.py --instance ./eureka-instance
```

Inspect it with:

```bash
python scripts/eureka_instance_status.py --instance ./eureka-instance
```

## Required Tree

```text
eureka-instance/
  config/
    instance.json
    store_manifest.json
    migration_state.json
  db/
    source_cache.sqlite
    evidence_ledger.sqlite
    review_queue.sqlite
    public_index.sqlite
  logs/
    eureka.log
  run/
    instance.lock
    status.json
  tmp/
    .keep
  exports/
    .keep
  imports/
    .keep
```

## Committed vs Local

Committed:

- bootstrap scripts
- policies
- docs
- validators
- tests
- audit evidence

Not committed:

- `eureka-instance/**`
- SQLite database files created for an instance
- logs
- run locks
- temp files
- imports and exports

The default `eureka-instance/` root is ignored by git. Operators may choose another explicit root, but hidden or product/runtime roots are rejected.

## Versioned Config Files

`config/instance.json` is the instance identity and policy manifest. It includes `instance_schema_version: 1`, `created_at`, `updated_at`, explicit local mode flags, store references, and no production or public launch claims.

`config/store_manifest.json` is the local store manifest. It lists the required R0 stores: `source_cache`, `evidence_ledger`, `review_queue`, and `public_index`.

`config/migration_state.json` is the migration guard state. It records whether a migration is needed, whether migration apply is allowed, whether a backup is required, rollback metadata posture, blockers, warnings, and history.

## Runtime Composition

LOCAL-03 adds `runtime/local_appliance` as the supported way to open an initialized instance:

```bash
python scripts/eureka_local_runtime_status.py --instance ./eureka-instance --json
python scripts/demo_local_runtime_composition.py --instance ./eureka-instance --json
```

The runtime composition boundary loads the three config files above and opens the four SQLite stores from `config/store_manifest.json`. Future service, workbench, worker, and test code should use that boundary rather than hard-coding paths under `db/`.
