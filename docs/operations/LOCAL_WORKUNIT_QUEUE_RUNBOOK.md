# Local WorkUnit Queue Runbook

## Initialize

```bash
python scripts/eureka_init_instance.py --instance ./eureka-instance --json
python scripts/eureka_validate_instance.py --instance ./eureka-instance --json
```

The instance manifest includes `workunit_queue` at `db/workunit_queue.sqlite`.

## CLI

Create a queued record:

```bash
python scripts/eureka_workunit_queue.py --instance ./eureka-instance create --kind search_need --title "Sample local search need" --json
```

List records:

```bash
python scripts/eureka_workunit_queue.py --instance ./eureka-instance list --json
```

Show a record:

```bash
python scripts/eureka_workunit_queue.py --instance ./eureka-instance show --id <workunit_id> --with-transitions --json
```

Transition a record:

```bash
python scripts/eureka_workunit_queue.py --instance ./eureka-instance transition --id <workunit_id> --state running --reason "operator selected" --json
```

Run the demo:

```bash
python scripts/demo_workunit_queue.py --instance ./eureka-instance --json
```

Validate:

```bash
python scripts/validate_workunit_queue.py
```

Run deterministic local workers after LOCAL-09:

```bash
python scripts/eureka_worker_runner.py --instance ./eureka-instance list-workers --json
python scripts/eureka_worker_runner.py --instance ./eureka-instance run-next --kind noop_worker --json
```

## Boundaries

LOCAL-07 queue commands record local queue state only. LOCAL-09 worker commands may execute only enabled deterministic local workers. They still do not run source probes, extraction, downloads, installs, executable actions, model/provider calls, LAN operations, deployment, production readiness checks, or public launch checks.

Queue state under `eureka-instance/` is local state and must not be committed.
