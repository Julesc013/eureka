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

## Demand Dashboard v0 Relation

Demand Dashboard v0 is future/contract-only. It can later summarize privacy-filtered and poisoning-guarded aggregate demand, but P68 adds no telemetry, public query logging, account/IP tracking, real demand claims, runtime dashboard, candidate promotion, source sync, source cache/evidence ledger mutation, public-search ranking change, or index mutation.

## Source Sync Worker v0 Relation

Source Sync Worker Contract v0 is future/contract-only. It may later consume probe queue and demand dashboard signals to plan approved, bounded source sync jobs, but P69 adds no connector runtime, source calls, public-query fanout, source cache mutation, evidence ledger mutation, candidate mutation, or index mutation.

## P70 Source Cache And Evidence Ledger Relation

P70 adds contract-only source cache and evidence ledger models. It adds no live source calls, arbitrary URL cache, raw payload storage, telemetry, credentials, downloads, installs, or public-search mutation.

<!-- P71-INTERNET-ARCHIVE-METADATA-CONNECTOR-APPROVAL-START -->
## P71 Internet Archive Metadata Connector Approval

`docs/reference/INTERNET_ARCHIVE_METADATA_CONNECTOR_APPROVAL.md` defines an approval-only, metadata-only future Internet Archive connector pack. It is not runtime, makes no external calls, enables no public-query fanout, performs no downloads/file retrieval/mirroring, and mutates no source cache, evidence ledger, candidate index, public/local/master index, telemetry, or credentials. Future work is blocked on official source policy review, User-Agent/contact policy, rate limits, timeouts, retry/backoff, circuit breakers, cache-first source cache output, and evidence ledger attribution.

This cross-reference keeps `docs/operations/PUBLIC_SEARCH_SAFETY_EVIDENCE.md` aligned with the source-ingestion boundary: IA metadata may become future reviewed cache/evidence input, never direct truth or live public search fanout.
<!-- P71-INTERNET-ARCHIVE-METADATA-CONNECTOR-APPROVAL-END -->

## P72 Wayback/CDX/Memento Connector Approval Pack v0

P72 defines a future availability/capture-metadata-only Wayback/CDX/Memento connector approval pack. The connector is not implemented, no external calls are made, public queries do not fan out to Wayback/CDX/Memento, arbitrary URL fetch is forbidden, archived content fetch/capture replay/WARC download are forbidden, and future outputs must be cache-first/evidence-first after URI privacy review and approval.

<!-- P73-GITHUB-RELEASES-CONNECTOR-APPROVAL-START -->
## P73 GitHub Releases Connector Approval Pack v0

P73 defines a future release-metadata-only GitHub Releases connector approval pack. The live connector is not implemented, no external calls or GitHub API calls are made, public queries do not fan out to GitHub, arbitrary repository fetch is forbidden, repository clone/release asset download/source archive download are forbidden, token use is not allowed now, and future outputs must be cache-first/evidence-first after repository identity review and approval.
<!-- P73-GITHUB-RELEASES-CONNECTOR-APPROVAL-END -->

<!-- P74-PYPI-METADATA-CONNECTOR-APPROVAL-START -->
## P74 PyPI Metadata Connector Approval Pack v0

P74 adds an approval-only, package metadata-only PyPI connector pack. It adds no live PyPI connector runtime, no external calls, no PyPI API calls, no package metadata fetch, no release fetch, no wheel/sdist/package file download, no package install, no dependency resolution, no package archive inspection, no public-query fanout, no telemetry, no credentials or tokens, and no source cache/evidence ledger/candidate/index mutation. Package identity review, dependency metadata caution, source policy review, User-Agent/contact, token policy, rate limits, timeouts, retry/backoff, circuit breaker, cache-first output, and evidence attribution remain approval gates.
<!-- P74-PYPI-METADATA-CONNECTOR-APPROVAL-END -->
