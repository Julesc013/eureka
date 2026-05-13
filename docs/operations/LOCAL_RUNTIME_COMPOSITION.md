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

The demo opens `LocalApplianceRuntime`, checks the composed store handles, runs integrity checks, emits unified status, and closes the runtime. It writes no files unless `--output` is provided.

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

LOCAL-04 builds the read-only localhost HTTP service over this runtime API. LOCAL-07 adds the manifest-defined WorkUnit queue store to the composition boundary. LAN, deployment, index rebuild execution, WorkUnit execution, and broader workbench behavior remain disabled until later LOCAL tasks explicitly enable them.

LOCAL-04 now provides that service through `scripts/eureka_local_server.py` and `scripts/eureka_local_service_smoke.py`. Use the service runbook for HTTP operation, and keep this composition runbook for direct runtime status and integrity checks.

## WorkUnit Queue Status

```bash
python scripts/eureka_workunit_queue.py --instance ./eureka-instance summary --json
```

The queue summary reports local queue records only. It is not worker execution and does not mutate source cache, evidence ledger, review queue, or public index state.
