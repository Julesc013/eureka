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
python scripts/validate_local_workbench_page_hardening.py
```

The validator checks policies, workbench renderers, localhost smoke behavior, JSON API compatibility, read-only HTML, no external assets, no mutation controls, queue handoff, and leakage baseline.

## Deferrals

LOCAL-05 does not add review decision controls, WorkUnits, Search Hunt Sessions, source probes, index rebuild UI, LAN, deployment, production readiness, or public launch readiness.

LOCAL-06 hardens the same routes with store status, provenance, source-local scope, current-index absence semantics, and unavailable capability markers. WorkUnits remain next, review/rebuild remains later, LAN remains disabled, and no deployment occurs.

## LOCAL-08 Review/Rebuild

Configure a local operator token before using review mutation forms:

```bash
python scripts/eureka_set_operator_token.py --instance ./eureka-instance --token "<operator-token>" --json
```

Then start the service with an in-memory operator token or rely on the stored
hash for CLI checks:

```bash
python scripts/eureka_local_server.py --instance ./eureka-instance --host 127.0.0.1 --port 8765 --operator-token "<operator-token>"
python scripts/eureka_local_review_smoke.py --base-url http://127.0.0.1:8765 --operator-token "<operator-token>" --json
```

LOCAL-08 keeps LAN disabled and does not run source probes, execute queued work,
mutate a master index, write `site/dist`, or deploy.
