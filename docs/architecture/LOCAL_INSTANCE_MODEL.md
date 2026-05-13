# Local Instance Model

LOCAL-01 introduces an explicit local appliance instance root. The root is the only place where bootstrap commands may write local appliance state, and it must be passed with `--instance`.

## Model

The local instance is a disposable filesystem tree owned by the operator. It is portable, inspectable, and safe to delete. Eureka must not infer a hidden state root from the home directory, `.cache`, `.local`, `.aide.local`, or the repo root.

The instance has these layers:

- `config/` stores instance identity and local mode flags.
- `db/` stores file-backed SQLite stores for source cache, evidence ledger, review queue, and reviewed public index.
- `logs/` stores local logs only.
- `run/` stores process/status files only.
- `tmp/`, `exports/`, and `imports/` are explicit local work areas and are not committed.

LOCAL-01 initializes empty store schemas through the existing R0 runtime store APIs. LOCAL-02 adds version metadata around that state:

- `config/instance.json` records `instance_schema_version`, timestamps, store references, and policy flags.
- `config/store_manifest.json` records required stores, relative paths, detected store schema versions, and integrity support.
- `config/migration_state.json` records whether a migration is needed, whether migration apply is allowed, backup/rollback metadata posture, blockers, warnings, and migration history.

The current instance schema version is `1`. Unsupported versions fail closed. LOCAL-02 does not implement migration apply; it only detects and reports migration state.

## Boundaries

- No HTTP server exists in LOCAL-01.
- No HTML workbench exists in LOCAL-01.
- No WorkUnit runtime exists in LOCAL-01.
- LAN remains disabled.
- Deployment is not performed.
- Production readiness is not claimed.
- Public launch readiness is not claimed.
- Destructive migration is not allowed.

## Next

LOCAL-03 uses the versioned instance boundary to define local runtime composition before any service or workbench work begins.
