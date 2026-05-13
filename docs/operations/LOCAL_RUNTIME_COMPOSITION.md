# Local Runtime Composition Operations

LOCAL-03 adds a local runtime composition boundary without starting a service.

## Initialize And Validate An Instance

```bash
python scripts/eureka_init_instance.py --instance ./eureka-instance --json
python scripts/eureka_validate_instance.py --instance ./eureka-instance --json
```

## Runtime Status

```bash
python scripts/eureka_local_runtime_status.py --instance ./eureka-instance --json
```

Read-only composition mode:

```bash
python scripts/eureka_local_runtime_status.py --instance ./eureka-instance --read-only --json
```

## Composition Demo

```bash
python scripts/demo_local_runtime_composition.py --instance ./eureka-instance --json
```

The demo opens `LocalApplianceRuntime`, checks all four store handles, runs integrity checks, emits unified status, and closes the runtime. It writes no files unless `--output` is provided.

## Validator

```bash
python scripts/validate_local_runtime_composition.py
```

The validator checks policies, runtime imports, no forbidden runtime vocabulary, temp instance composition, read-only mode, close idempotency, forbidden root rejection, unsupported schema fail-closed behavior, audit evidence, queue handoff, and leakage baseline.

## Failure Modes

Runtime opening fails when:

- `--instance` is missing
- the instance path is a forbidden root
- required config, manifest, migration, or database files are missing
- instance schema version is unsupported
- migration state has blockers
- destructive migration is required
- a manifest store path escapes the instance root

## Next Step

LOCAL-04 should build the read-only localhost HTTP service over this runtime API. LAN, deployment, index rebuilds, WorkUnit execution, and workbench behavior remain disabled until later LOCAL tasks explicitly enable them.
