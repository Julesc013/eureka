# Local Worker Runtime

The worker runtime API lives in `runtime/local_worker`.

## Registry

- `LocalWorkerRegistry`
- `get_default_worker_registry()`
- `get_worker(kind)`
- `is_worker_enabled(kind)`

The default registry exposes five enabled deterministic workers and marks risky workers disabled.

## Runner

`LocalWorkerRunner(runtime)` requires a `LocalApplianceRuntime`.

Methods:

- `plan_run(workunit_id)`
- `run_one(workunit_id, worker_kind=None, operator_context=None)`
- `run_next(kind=None, limit=1, operator_context=None)`
- `block_unsupported_worker(workunit_id, worker_kind, reason)`

`run_one` requires the WorkUnit to be queued. It transitions queued records to `running`, runs the worker, and then transitions to `complete`, `failed`, or `blocked`.

## Results

Result models:

- `LocalWorkerRun`
- `LocalWorkerResult`
- `LocalWorkerStatus`
- `LocalWorkerAuditEvent`

Each result records policy decision, inputs, outputs, store mutations, warnings, limitations, and explicit false flags for external network, source probes, extraction, model/provider use, downloads, site/dist writes, master-index mutation, LAN, deployment, production readiness, and public launch readiness.

## CLI

```bash
python scripts/eureka_worker_runner.py --instance ./eureka-instance list-workers --json
python scripts/eureka_worker_runner.py --instance ./eureka-instance plan --id <workunit_id> --json
python scripts/eureka_worker_runner.py --instance ./eureka-instance run-one --id <workunit_id> --json
python scripts/eureka_worker_runner.py --instance ./eureka-instance run-next --kind noop_worker --json
```

The reviewed-index rebuild worker requires `--operator-token`. Raw tokens are not persisted by the worker CLI.
