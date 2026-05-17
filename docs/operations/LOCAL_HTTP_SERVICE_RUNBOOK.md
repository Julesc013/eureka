# Local HTTP Service Runbook

## Initialize

```powershell
$Workspace = "D:\Projects\Eureka"
$Instance = "$Workspace\instances\default"

python scripts/eureka_init_instance.py --instance $Instance --json
python scripts/eureka_validate_instance.py --instance $Instance --json
```

## Start

```powershell
python scripts/eureka_local_server.py --instance $Instance --host 127.0.0.1 --port 8765
```

The server refuses missing instances, write mode, and LAN-facing bind hosts
unless `--bind-lan` is explicit.

## Smoke

In another shell:

```powershell
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

After LOCAL-06 the same smoke also checks page hardening markers: non-claim banner, store status, local index limitation, object not-found state, source empty state, checked/unchecked absence layers, no mutation controls, no external assets, and JSON API compatibility.

## Validate

```powershell
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

LOCAL-06 adds operational page detail only. WorkUnits remain deferred until LOCAL-07, review/rebuild UI until LOCAL-08, and LAN until LOCAL-11/LOCAL-12.

## LOCAL-11 LAN Policy Check

Before any read-only LAN smoke, check the bind policy:

```powershell
python scripts/eureka_lan_policy_check.py --host 0.0.0.0 --json
python scripts/eureka_lan_policy_check.py --host 0.0.0.0 --bind-lan --json
```

The service still starts on `127.0.0.1` by default. A LAN-facing host requires:

```powershell
python scripts/eureka_local_server.py --instance $Instance --host 0.0.0.0 --port 8765 --bind-lan --json-startup
```

LOCAL-11 does not require cross-device LAN smoke; that proof is deferred to
LOCAL-12. Stop the service with Ctrl+C and do not commit local instance state.

## LOCAL-12 LAN Smoke

```powershell
python scripts/eureka_lan_smoke.py --instance $Instance --host 0.0.0.0 --port 8765 --bind-lan --read-only --json
python scripts/eureka_lan_read_only_probe.py --base-url http://127.0.0.1:8765 --json
python scripts/eureka_lan_shutdown_check.py --instance $Instance --port 8765 --json
```

Use the smoke script for an automated same-machine LAN-bind run. Use the probe
script against a private LAN URL only when a LAN client or safe local target is
available. Do not treat same-machine smoke as public hosting or cross-device
proof.
