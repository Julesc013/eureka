# Local Worker Runner Runbook

## Initialize

```bash
python scripts/eureka_init_instance.py --instance ./eureka-instance --json
python scripts/eureka_validate_instance.py --instance ./eureka-instance --json
```

## Create A Worker WorkUnit

```bash
python scripts/eureka_workunit_queue.py --instance ./eureka-instance create --kind regression_test --title "Sample local deterministic worker item" --payload-json "{\"worker_kind\":\"noop_worker\"}" --json
```

## Run

```bash
python scripts/eureka_worker_runner.py --instance ./eureka-instance list-workers --json
python scripts/eureka_worker_runner.py --instance ./eureka-instance run-next --kind noop_worker --json
python scripts/demo_local_worker_runner.py --instance ./eureka-instance --json
```

For the reviewed-index rebuild worker:

```bash
python scripts/eureka_worker_runner.py --instance ./eureka-instance --operator-token "<token>" run-next --kind reviewed_index_rebuild_worker --json
```

Do not commit tokens or local instance state.

## Validate

```bash
python scripts/validate_local_worker_runner.py
```

## Boundaries

The runner does not run source probes, extraction, AI/model calls, downloads, installs, executable actions, source sync, LAN operations, deployment, site/dist generation, or master-index mutation.

## LOCAL-10 Harness Use

The auto-test harness verifies worker safety by inspecting the enabled and
blocked worker-kind matrix. It does not run queued workers; explicit worker
execution remains a separate operator command.
