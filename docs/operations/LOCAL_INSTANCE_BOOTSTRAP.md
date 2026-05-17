# Local Instance Bootstrap

LOCAL-01 makes local appliance state explicit. The init command refuses to run without `--instance`, refuses the repo root, and rejects hidden private roots such as `.cache`, `.local`, and `.aide.local`.

## Preferred Workspace Layout

Use the sibling instance layout from `docs/operations/LOCAL_INSTANCE_LAYOUT.md` for normal development:

```text
D:\Projects\Eureka\
  eureka\
  instances\
    default\
```

From the repo root:

```powershell
$Instance = "..\instances\default"
```

The older `./eureka-instance` name remains a valid explicit instance path and is still used by LOCAL-01/LOCAL-02 validation fixtures.

## Initialize

```powershell
python scripts/eureka_init_instance.py --instance $Instance --json
```

The command creates the instance directories, writes `config/instance.json`, writes `config/store_manifest.json`, writes `config/migration_state.json`, writes `run/status.json`, and initializes empty SQLite store schemas through the existing source cache, evidence ledger, review queue, and reviewed public index store APIs.

The command is idempotent. A rerun keeps the same instance identity unless `--force` is explicitly used.

## Validate

```powershell
python scripts/eureka_validate_instance.py --instance $Instance --json
```

Validation checks the directory layout, manifest, status file, database presence, SQLite integrity, store integrity where available, ignored local state, disabled server and LAN flags, and absence of production or public launch claims.
It also checks `instance_schema_version`, store manifest entries, migration state, and fail-closed behavior for unsupported versions.

## Status

```powershell
python scripts/eureka_instance_status.py --instance $Instance --json
```

The status command is read-only and does not mutate the instance.

## Migration Status

```powershell
python scripts/eureka_instance_migration_status.py --instance $Instance --json
```

The migration status command is read-only. It reports whether migration is needed, blockers, warnings, backup requirements, and rollback posture. LOCAL-02 does not implement migration apply.

## Boundaries

LOCAL-02 does not create an HTTP server, HTML workbench, WorkUnit runtime, Search Hunt Session runtime, source probe runner, LAN binding, deployment, or F0 extraction path. LOCAL-03 is the next step and owns the local runtime composition boundary.

## Runtime Composition

After initialization and validation, inspect the composed runtime with:

```powershell
python scripts/eureka_local_runtime_status.py --instance $Instance --json
python scripts/demo_local_runtime_composition.py --instance $Instance --json
```

These commands open `LocalApplianceRuntime`, validate supported instance schema and migration state, open the source cache, evidence ledger, review queue, and reviewed public index through manifest paths, run status/integrity checks, and close the runtime.

They do not start a server, enable LAN, deploy, run source probes, create review decisions, or rebuild indexes.
