# Local Instance Bootstrap

LOCAL-01 makes local appliance state explicit. The init command refuses to run without `--instance`, refuses the repo root, and rejects hidden private roots such as `.cache`, `.local`, and `.aide.local`.

## Initialize

```bash
python scripts/eureka_init_instance.py --instance ./eureka-instance --json
```

The command creates the instance directories, writes `config/instance.json`, writes `run/status.json`, and initializes empty SQLite store schemas through the existing source cache, evidence ledger, review queue, and reviewed public index store APIs.

The command is idempotent. A rerun keeps the same instance identity unless `--force` is explicitly used.

## Validate

```bash
python scripts/eureka_validate_instance.py --instance ./eureka-instance --json
```

Validation checks the directory layout, manifest, status file, database presence, SQLite integrity, store integrity where available, ignored local state, disabled server and LAN flags, and absence of production or public launch claims.

## Status

```bash
python scripts/eureka_instance_status.py --instance ./eureka-instance --json
```

The status command is read-only and does not mutate the instance.

## Boundaries

LOCAL-01 does not create an HTTP server, HTML workbench, WorkUnit runtime, Search Hunt Session runtime, source probe runner, LAN binding, deployment, or F0 extraction path. LOCAL-02 is the next step and owns configuration schema plus migration guard work.
