# Public Search Safety Evidence v0

P57 records local/public-alpha safety evidence for Eureka public search before
hosted rehearsal. It proves the current public search path can answer safe query
checks and reject blocked request checks while staying in `local_index_only`
mode.

The evidence runner uses the P54 hosted wrapper through an in-process WSGI
harness. It does not deploy a backend, bind a public service, call external
source APIs, scrape, browse, call models, use credentials, or mutate indexes.

## Covered Checks

- Safe query checks for `windows 7 apps`, `driver.inf`, `pc magazine ray tracing`,
  and an intentional no-result query.
- Blocked request checks for missing query, too-long query, excessive limits,
  live modes, raw source payload expansion, local path/root controls, arbitrary
  URL or network controls, downloads, installs, execute, uploads, user files,
  credentials, API keys, live probes, and live sources.
- Query/result limit checks for length 160, length 161, limit 25, limit 26,
  negative limit, and non-integer limit.
- Status endpoint honesty for `/healthz`, `/status`, and `/api/v1/status`.
- Static handoff safety for `search.html`, lite/text/files projections, and
  `search_config.json`.
- Public index safety for `data/public_index` and the static
  `public_index_summary.json`.
- Hosted wrapper safety through local rehearsal only.

## Rate-Limit And Edge Status

Rate-limit and edge evidence remains operator-gated. P57 does not claim
Cloudflare, provider, TLS, DNS, hosted service, edge rate-limit, or production
deployment evidence. App-level rate-limit behavior remains contract-only for
this checkpoint. P58 Hosted Public Search Rehearsal v0 records a localhost HTTP
rehearsal of the wrapper, but edge and provider rate-limit evidence remains
operator-gated until real deployment evidence exists.

## Hard Non-Goals

P57 adds no live probes, no downloads, no uploads, no installs, no accounts, no
telemetry, no arbitrary URL fetch, no source connector runtime, no AI runtime,
no public contribution intake, no local index mutation, no runtime index
mutation, no master-index mutation, and no production claim.

## Next Step

P58 Hosted Public Search Rehearsal v0 is the local hosted-mode evidence gate
after P57. P59 Query Observation Contract v0 is the next Codex-safe query
intelligence contract step. It defines privacy-filtered query observations as
contract-only records and does not add telemetry, persistent query logging,
cache mutation, miss-ledger mutation, probe enqueueing, or master-index
mutation.

Human or operator parallel work may deploy the wrapper, configure a real
backend URL, configure edge/rate limits, verify the static site, and execute
Manual Observation Batch 0, but those actions require separate evidence.
