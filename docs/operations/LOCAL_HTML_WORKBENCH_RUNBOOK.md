# Local HTML Workbench Runbook

## Initialize

```bash
python scripts/eureka_init_instance.py --instance ./eureka-instance --json
python scripts/eureka_validate_instance.py --instance ./eureka-instance --json
```

## Start

```bash
python scripts/eureka_local_server.py --instance ./eureka-instance --host 127.0.0.1 --port 8765
```

The service refuses LAN and wildcard hosts. Keep the bind on `127.0.0.1` for LOCAL-05.

## Browse

Open:

```text
http://127.0.0.1:8765/
```

Useful pages:

- `http://127.0.0.1:8765/search?q=sampleproject`
- `http://127.0.0.1:8765/status`
- `http://127.0.0.1:8765/absence?q=definitely-not-present-local-05`

## Smoke

```bash
python scripts/eureka_local_workbench_smoke.py --base-url http://127.0.0.1:8765 --json
python scripts/eureka_local_service_smoke.py --base-url http://127.0.0.1:8765 --json
```

## Validate

```bash
python scripts/validate_local_html_workbench.py
```

The validator checks policies, workbench renderers, localhost smoke behavior, JSON API compatibility, read-only HTML, no external assets, no mutation controls, queue handoff, and leakage baseline.

## Deferrals

LOCAL-05 does not add review decision controls, WorkUnits, Search Hunt Sessions, source probes, index rebuild UI, LAN, deployment, production readiness, or public launch readiness.
