# Public Search Production Contract v0

Status: contract frozen; P54 hosted wrapper implemented for local rehearsal.

Public Search Production Contract v0 hardens Eureka's first production-facing
public search API shape while keeping current behavior local/prototype only.
The active v0 mode is `local_index_only`: future hosted search must query a
controlled Eureka index/cache first and must not fan out to arbitrary external
sources.

This contract does not deploy a backend, make hosted search available, enable
live probes, add telemetry, add accounts, accept uploads, expose downloads, or
mutate any index.

## Contract Files

- Request: `contracts/api/search_request.v0.json`
- Response: `contracts/api/search_response.v0.json`
- Error: `contracts/api/error_response.v0.json`
- Result card: `contracts/api/search_result_card.v0.json`
- Source status: `contracts/api/source_status.v0.json`
- Evidence summary: `contracts/api/evidence_summary.v0.json`
- Absence report: `contracts/api/absence_report.v0.json`
- Public status: `contracts/api/public_search_status.v0.json`

`error_response.v0.json` is the canonical error schema name in this repo. Any
future `search_error.v0.json` name should be treated as an alias unless a later
compatibility review changes that decision.

## Active Route Family

The production-facing route family for P54 is GET-only in v0:

- `GET /healthz`
- `GET /status`
- `GET /search?q=...`
- `GET /api/v1/status`
- `GET /api/v1/search?q=...`
- `GET /api/v1/query-plan?q=...`
- `GET /api/v1/sources`
- `GET /api/v1/source/{source_id}`

Future contract-only routes are `/api/v1/object/{id}`,
`/api/v1/result/{id}`, `/api/v1/absence/{need_id}`,
`/api/v1/compare`, and `/api/v1/capabilities`.

## Safety Defaults

Hosted wrapper defaults must keep these flags false:

- `hosted_search_implemented`
- `dynamic_backend_deployed`
- `live_probes_enabled`
- `downloads_enabled`
- `uploads_enabled`
- `installs_enabled`
- `local_paths_enabled`
- `arbitrary_url_fetch_enabled`
- `telemetry_enabled`

P54 implements a hosted wrapper for `local_index_only` only. P55 implements the
first controlled generated public search index under `data/public_index`; live
connectors, query intelligence, and public contribution intake remain later
milestones.

P54 now implements the wrapper entrypoint and local rehearsal check:

- `scripts/run_hosted_public_search.py`
- `scripts/check_hosted_public_search_wrapper.py`
- `scripts/validate_hosted_public_search_wrapper.py`

The wrapper remains deployment-unverified. It does not enable live probes,
downloads, uploads, installs, local paths, arbitrary URL fetch, telemetry,
accounts, source connectors, AI runtime, or index mutation.

The P55 generated public index is the current preferred corpus for local and
hosted-wrapper search rehearsal. It is built from governed source inventory
plus committed fixture/recorded metadata only, and it does not authorize
request-selected index paths, live source fanout, private local ingestion,
pack import, staging runtime, master-index mutation, or hosted deployment
claims.

P56 adds the static handoff layer for this contract. Static pages publish
`search_config.json` and `public_index_summary.json` with backend status
`backend_unconfigured`; the hosted search form stays disabled until a later
operator evidence pack records a verified backend URL.
