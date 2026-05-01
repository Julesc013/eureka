# Hosted Public Search Rehearsal

P58 records a local-only hosted-mode rehearsal for Eureka public search. It
starts `scripts/run_hosted_public_search.py` on `127.0.0.1` with hosted-safe
environment variables, checks health/status/search routes over HTTP, rejects
blocked requests, and shuts the local process down.

This is no deployment evidence. It does not call a provider API, configure DNS,
claim a hosted URL, or prove production readiness.

## Safe Environment

The rehearsal uses:

- `EUREKA_PUBLIC_MODE=1`
- `EUREKA_SEARCH_MODE=local_index_only`
- `EUREKA_ALLOW_LIVE_PROBES=0`
- `EUREKA_ALLOW_DOWNLOADS=0`
- `EUREKA_ALLOW_UPLOADS=0`
- `EUREKA_ALLOW_LOCAL_PATHS=0`
- `EUREKA_ALLOW_ARBITRARY_URL_FETCH=0`
- `EUREKA_ALLOW_INSTALL_ACTIONS=0`
- `EUREKA_ALLOW_TELEMETRY=0`
- `EUREKA_MAX_QUERY_LEN=160`
- `EUREKA_MAX_RESULTS=20`
- `EUREKA_GLOBAL_TIMEOUT_MS=5000`
- `EUREKA_OPERATOR_KILL_SWITCH=0`

## Covered Checks

The rehearsal checks `/healthz`, `/status`, `/api/v1/status`,
`/api/v1/sources`, `/api/v1/search`, `/api/v1/query-plan`, and `/search`.

Safe query checks include `windows 7 apps`, `driver.inf`,
`pc magazine ray tracing`, `firefox xp`, and an intentional no-result query.
Blocked request checks cover local paths, store roots, index paths, URL fetch
parameters, credentials, live probes, live source selectors, downloads,
uploads, install/execute requests, raw payload expansion, and invalid limits.

## Compatibility Checks

P58 also checks that the static search handoff remains backend-unconfigured,
that the public index is present and public-safe, and that Docker/Render
templates keep safe defaults. Non-local base URLs are rejected by default.

## Operator-Gated Work

Edge rate limits, DNS/TLS, provider deployment, CORS verification, log
redaction evidence, rollback evidence, and hosted URL verification remain
operator-gated. Operators must record the deployed URL, commit SHA, host,
environment, route checks, blocked-request checks, and edge/rate-limit evidence
before static search config can point to a hosted backend.

## Non-Goals

P58 adds no live probes, no downloads, no uploads, no accounts, no telemetry, no
arbitrary URL fetch, no AI runtime, no source connector runtime, no index
mutation, no pack import, no staging runtime, and no production claim.

## Next Step

The next Codex-safe branch is P59 Query Observation Contract v0. Operator
parallel work may deploy and verify the hosted wrapper, but public claims must
not change until evidence exists.
