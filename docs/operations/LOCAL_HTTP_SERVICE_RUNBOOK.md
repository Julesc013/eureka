# Local HTTP Service Runbook

## Initialize

```bash
python scripts/eureka_init_instance.py --instance ./eureka-instance --json
python scripts/eureka_validate_instance.py --instance ./eureka-instance --json
```

## Start

```bash
python scripts/eureka_local_server.py --instance ./eureka-instance --host 127.0.0.1 --port 8765
```

The server refuses missing instances, write mode, `0.0.0.0`, and non-localhost hosts.

## Smoke

In another shell:

```bash
python scripts/eureka_local_service_smoke.py --base-url http://127.0.0.1:8765 --json
python scripts/eureka_local_workbench_smoke.py --base-url http://127.0.0.1:8765 --json
```

The smoke script checks:

- `/`
- `/status`
- `/api/v1/status`
- `/api/v1/search?q=sampleproject`
- `/api/v1/absence?q=definitely-not-present-local-04`

It refuses non-localhost URLs before opening any request.

The workbench smoke checks the LOCAL-05 HTML routes:

- `/`
- `/status`
- `/search?q=sampleproject`
- `/absence?q=definitely-not-present-local-05`

It also verifies JSON API compatibility.

## Validate

```bash
python scripts/validate_local_http_service.py
```

The validator checks policies, routes, runtime imports, app routes, localhost server startup, smoke behavior, write-method rejection, LAN rejection, audit evidence, queue handoff, and leakage baseline.

## Failure Modes

- missing `--instance`
- uninitialized instance path
- unsupported instance schema version
- blocked migration state
- forbidden bind host
- non-localhost smoke URL
- write method request
- query longer than 256 characters
- limit above the route maximum

## Explicit Deferrals

LOCAL-05 implements only the minimal read-only HTML workbench. It still does not implement WorkUnit queue, source probes, review mutation, index rebuilds, LAN mode, deployment, production readiness, or public launch readiness.
