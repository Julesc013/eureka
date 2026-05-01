# Hosted Public Search Wrapper

Status: local wrapper implemented; hosted backend not deployed.

P54 adds a stdlib-only hosted public search wrapper around Eureka's existing
`local_index_only` public search API. The wrapper is deployable by an operator,
but this repository state does not prove a running hosted backend.

## Purpose

The wrapper gives operators one narrow backend entrypoint for future public
alpha hosting:

```powershell
python scripts/run_hosted_public_search.py --check-config
python scripts/check_hosted_public_search_wrapper.py
python scripts/run_hosted_public_search.py --host 127.0.0.1 --port 8080
python scripts/run_hosted_public_search.py --public-mode --host 0.0.0.0 --port 8080
```

It serves only:

- `GET /healthz`
- `GET /status`
- `GET /search?q=...`
- `GET /api/v1/status`
- `GET /api/v1/search?q=...`
- `GET /api/v1/query-plan?q=...`
- `GET /api/v1/sources`
- `GET /api/v1/source/{source_id}`

The full local workbench server remains separate and is not the P54 hosted
public-search wrapper.

P55 adds a generated public search index under `data/public_index`. The wrapper
configuration check now requires that bundle to exist, and status/search
responses report `public_index_present: true` and
`index_status: generated_public_search_index` in this checkout. Operators
should rebuild or validate that index before deployment:

```powershell
python scripts/build_public_search_index.py --check
python scripts/validate_public_search_index.py
```

P56 adds static search integration for the publication site. The static site
now publishes `data/search_config.json` and
`data/public_index_summary.json`, but the hosted backend remains unconfigured
and no verified backend URL is written into `site/dist`.

P57 adds local safety evidence for the wrapper before hosted rehearsal. The
evidence runner uses the wrapper in-process, verifies safe routes and 32 blocked
request cases, checks static handoff and public index safety, and records
edge/rate-limit evidence as operator-gated. It does not deploy the wrapper or
claim hosted availability.

## Safety Posture

The wrapper is read-only and keeps these disabled:

- no live probes or live source fanout
- arbitrary URL fetch
- downloads, install actions, execution, mirrors, and uploads
- caller-provided index paths, store roots, local paths, directories, files, and
  source credentials
- accounts, sessions, telemetry, external calls, and AI runtime
- local index mutation, runtime index mutation, master-index mutation, pack
  import, and staging runtime

Forbidden request parameters are rejected by the same public-search safety
layer used by Local Public Search Runtime v0.

## Local Rehearsal

Use the in-process rehearsal command before operator deployment:

```powershell
python scripts/check_hosted_public_search_wrapper.py
python scripts/check_hosted_public_search_wrapper.py --json
```

The rehearsal checks status routes, HTML search, JSON search, query planning,
source listing, and blocked unsafe parameters without opening a public listener.

## Deployment Evidence

Committing the wrapper, Dockerfile, or Render template is not deployment
evidence. A later operator evidence pack must record the host, deployed URL,
commit SHA, environment, route checks, and rollback plan before public claims
change.
