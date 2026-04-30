# Public Alpha Wrapper

LIVE_ALPHA_01 Production Public-Alpha Wrapper adds a stdlib-only process
entrypoint for running Eureka's existing web/API backend in the constrained
`public_alpha` posture.

This is not deployment. It does not add provider configuration, DNS, auth,
accounts, HTTPS/TLS, rate limiting, process supervision, live source probes,
live Internet Archive access, scraping, or production approval.

## Purpose

The wrapper gives a future supervised hosted-alpha operator one explicit local
entrypoint with safe defaults and startup validation:

```powershell
python scripts/run_public_alpha_server.py --check-config
python scripts/run_public_alpha_server.py --print-config-json
python scripts/run_public_alpha_server.py --host 127.0.0.1 --port 8781
```

By default it binds to `127.0.0.1:8781`, runs only in `public_alpha` mode, and
uses the existing public-alpha route policy. It refuses unsupported modes and
refuses nonlocal bind hosts unless the operator explicitly acknowledges that
choice.

## Safe Defaults

- mode: `public_alpha`
- bind host: `127.0.0.1`
- port: `8781`
- live source probes: disabled
- live Internet Archive access: disabled
- caller-provided local paths: disabled
- downloads, payload readback, and local export/readback controls: disabled or
  route-blocked
- user storage: disabled
- deployment approval: false
- production readiness: false

The status output exposes only safe capability flags and root configuration
states. It must not expose local private paths, credentials, host filesystem
details, or environment secrets.

## Configuration

The wrapper reads explicit flags plus these environment variables:

- `EUREKA_MODE`
- `EUREKA_BIND_HOST`
- `EUREKA_PORT`
- `EUREKA_ALLOW_NONLOCAL_BIND`
- `EUREKA_ALLOW_LIVE_PROBES`
- `EUREKA_ALLOW_LIVE_IA`
- `EUREKA_DISABLE_DOWNLOADS`
- `EUREKA_DISABLE_LOCAL_PATHS`
- `EUREKA_DISABLE_USER_STORAGE`
- `EUREKA_MAX_QUERY_LEN`
- `EUREKA_MAX_RESULTS_PER_SOURCE`
- `EUREKA_SOURCE_TIMEOUT_MS`
- `EUREKA_GLOBAL_TIMEOUT_MS`

Local root variables such as `EUREKA_WEB_INDEX_ROOT`,
`EUREKA_WEB_RUN_STORE_ROOT`, `EUREKA_WEB_TASK_STORE_ROOT`,
`EUREKA_WEB_MEMORY_STORE_ROOT`, and related `EUREKA_*_ROOT` values are refused
by the wrapper. Error summaries may name the configured environment variable,
but must not print its private value.

## Nonlocal Bind Guard

Binding to `0.0.0.0` or another nonlocal host is refused unless
`--allow-nonlocal-bind` or `EUREKA_ALLOW_NONLOCAL_BIND=1` is provided:

```powershell
python scripts/run_public_alpha_server.py --host 0.0.0.0 --check-config
python scripts/run_public_alpha_server.py --host 0.0.0.0 --allow-nonlocal-bind --check-config
```

Allowing a nonlocal bind is only an operator acknowledgement. It is not
deployment approval and does not approve production.

## Status And Smoke

Use these commands before any supervised rehearsal:

```powershell
python scripts/run_public_alpha_server.py --check-config
python scripts/run_public_alpha_server.py --print-config-json
python scripts/public_alpha_smoke.py
```

`/status` and `/api/status` report closed public-alpha capabilities:
`live_probes_enabled: false`, `live_internet_archive_enabled: false`,
`downloads_enabled: false`, `local_paths_enabled: false`,
`user_storage_enabled: false`, `deployment_approved: false`, and
`production_ready: false`, fixture-backed source posture, placeholder source
honesty, and pending/manual external baselines.

## Still Not Implemented

The wrapper deliberately does not provide:

- hosting provider configuration
- DNS or TLS ownership
- auth or accounts
- rate limiting or abuse controls
- process supervision
- production logging or monitoring
- live source probes
- live Internet Archive calls
- external baseline observations
- arbitrary local filesystem ingestion

Public Publication Plane Contracts v0 now defines the route, data, client,
base-path, deployment-target, redirect, and claim-traceability layer that sits
between this wrapper and any static deployment work. The next deployment-facing
step, GitHub Pages Deployment Enablement v0, now consumes those contracts as a
static-only workflow for `site/dist/`. It still keeps live probes closed
until a source-probe gateway contract and abuse-control posture exist. A later
deployment config pack may define provider-neutral backend deployment
configuration evidence, but it is not part of this wrapper.

Live Backend Handoff Contract v0 now reserves `/api/v1` as a future hosted
public-alpha handoff prefix. The wrapper's current local `/api` routes remain
local/prototype public-alpha routes; they are not the future `/api/v1`
contract and not a production API.

Live Probe Gateway Contract v0 now defines the future source-probe gateway
policy, but the wrapper still reports live probes and live Internet Archive
access as disabled by default. No external source probe, adapter, download, URL
fetch, or Internet Archive call is implemented here.
