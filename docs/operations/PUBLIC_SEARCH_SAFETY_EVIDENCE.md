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

P60 Shared Query/Result Cache v0 remains contract-only. It adds no runtime
cache writes, telemetry, public query logging, miss ledger writes, search need
writes, probes, candidate-index mutation, local-index mutation, or master-index
mutation.

P61 Search Miss Ledger v0 remains contract-only. It adds no runtime ledger
writes, telemetry, public query logging, search need creation, probe
enqueueing, result-cache mutation, candidate-index mutation, local-index
mutation, or master-index mutation.

P62 Search Need Record v0 remains contract-only. It adds no runtime need store,
telemetry, public query logging, demand-count runtime, probe enqueueing,
candidate-index mutation, result-cache mutation, miss-ledger mutation,
local-index mutation, or master-index mutation.

P63 Probe Queue v0 remains contract-only. It adds no runtime probe queue, no
probe execution, no live source calls, no source-cache mutation, no
evidence-ledger mutation, no candidate-index mutation, no search-need mutation,
no result-cache mutation, no miss-ledger mutation, no local-index mutation, and
no master-index mutation.

Human or operator parallel work may deploy the wrapper, configure a real
backend URL, configure edge/rate limits, verify the static site, and execute
Manual Observation Batch 0, but those actions require separate evidence.
## P64 Candidate Index Note

Candidate Index v0 is contract-only. Public search safety evidence remains
local_index_only and does not write candidate records, rank with candidate
records, promote candidates, mutate source cache, mutate evidence ledger, call
external sources, or mutate the master index.

## P65 Candidate Promotion Safety Note

P65 adds Candidate Promotion Policy v0 as contract-only governance. Candidate promotion policy is not promotion runtime; candidate confidence is not truth; automatic promotion is forbidden; destructive merge is forbidden; future promotion assessment requires evidence, provenance, source policy, privacy, rights, risk, conflict, human, policy, and operator gates. No candidate, source, evidence, public index, local index, or master-index state is mutated.

## P66 Known Absence Page v0

Known Absence Page v0 is contract-only. It defines scoped absence, not global absence, for future no-result explanations with checked/not-checked scope, near misses, weak hits, gap explanations, safe next actions, privacy redaction, and no download/install/upload/live fetch. Known absence page is not a runtime page yet, not evidence acceptance, not candidate promotion, not master-index mutation, and not telemetry.

<!-- P67-QUERY-PRIVACY-AND-POISONING-GUARD-START -->
## P67 Query Privacy and Poisoning Guard

Query Privacy and Poisoning Guard v0 is future/contract-only. Public search docs reference it as a future privacy/poisoning decision layer only; no runtime guard, telemetry, account/IP tracking, demand dashboard, public search mutation, index mutation, or production abuse protection is claimed.
<!-- P67-QUERY-PRIVACY-AND-POISONING-GUARD-END -->
