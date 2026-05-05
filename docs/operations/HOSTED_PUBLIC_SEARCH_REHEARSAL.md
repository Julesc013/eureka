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

The next completed query-intelligence steps are P59 Query Observation Contract
v0, P60 Shared Query/Result Cache v0, P61 Search Miss Ledger v0, and P62 Search
Need Record v0. They define privacy-filtered observation, shared cache, scoped
miss, and scoped unresolved-need contracts only: no telemetry, no persistent
query logging, no public query observation feed, no cache writes, no runtime
ledger writes, no runtime need store, no demand-count runtime, no probe
enqueueing, no candidate-index mutation, and no master-index mutation.

P63 Probe Queue v0 extends that chain with contract-only future probe items. It
does not create a runtime queue, execute probes, call live sources, mutate
source caches or evidence ledgers, mutate candidate indexes, or change the
hosted-wrapper rehearsal behavior.

Operator parallel work may deploy and verify the hosted wrapper, but public
claims must not change until evidence exists.
## P64 Candidate Index Note

Hosted public search rehearsal remains local-only and local_index_only. The P64
candidate index contract adds no runtime candidate index, no public search
candidate injection, no candidate promotion runtime, no source-cache mutation,
no evidence-ledger mutation, no external calls, and no hosted query
intelligence runtime.

## P65 Candidate Promotion Rehearsal Boundary

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

Hosted rehearsal remains separate from Source Cache Contract v0 and Evidence Ledger Contract v0. P70 does not deploy, host cache/ledger runtime, or claim source ingestion is live.

<!-- P71-INTERNET-ARCHIVE-METADATA-CONNECTOR-APPROVAL-START -->
## P71 Internet Archive Metadata Connector Approval

`docs/reference/INTERNET_ARCHIVE_METADATA_CONNECTOR_APPROVAL.md` defines an approval-only, metadata-only future Internet Archive connector pack. It is not runtime, makes no external calls, enables no public-query fanout, performs no downloads/file retrieval/mirroring, and mutates no source cache, evidence ledger, candidate index, public/local/master index, telemetry, or credentials. Future work is blocked on official source policy review, User-Agent/contact policy, rate limits, timeouts, retry/backoff, circuit breakers, cache-first source cache output, and evidence ledger attribution.

This cross-reference keeps `docs/operations/HOSTED_PUBLIC_SEARCH_REHEARSAL.md` aligned with the source-ingestion boundary: IA metadata may become future reviewed cache/evidence input, never direct truth or live public search fanout.
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

<!-- P75-NPM-METADATA-SUMMARY-START -->
## P75 npm Metadata Connector Approval Pack v0

Completed as an approval-only package metadata connector pack. It adds no live npm connector runtime, no external calls, no npm registry API calls, no npm/yarn/pnpm CLI calls, no package metadata fetch, no version fetch, no dist-tag fetch, no tarball metadata fetch, no tarball download, no package file download, no package install, no dependency resolution, no package archive inspection, no lifecycle script execution, no npm audit, no public-query fanout, no telemetry, no credentials or tokens, and no source cache/evidence ledger/candidate/index mutation. It requires package identity review, scoped package review, dependency metadata caution, lifecycle script risk policy, source policy review, User-Agent/contact decisions, and cache-first evidence outputs. Next recommended branch: P76 Software Heritage Connector Approval Pack v0.
<!-- P75-NPM-METADATA-SUMMARY-END -->

<!-- P76-SOFTWARE-HERITAGE-SUMMARY-START -->
## P76 Software Heritage Connector Approval Pack v0

Completed as an approval-only software identity/archive metadata connector pack. It adds no live Software Heritage connector runtime, no external calls, no Software Heritage API calls, no SWHID resolution, no origin/visit/snapshot/release/revision/directory/content lookup, no source code download, no repository clone, no source archive download, no source file retrieval, no public-query fanout, no telemetry, no credentials or tokens, and no source cache/evidence ledger/candidate/index mutation. It requires SWHID/origin/repository identity review, source-code-content risk policy, source policy review, User-Agent/contact decisions, and cache-first evidence outputs. Next recommended branch: P77 Public Hosted Deployment Evidence v0.
<!-- P76-SOFTWARE-HERITAGE-SUMMARY-END -->

## P77 Public Hosted Deployment Evidence

P77 confirms that P58 remains localhost rehearsal evidence only. The configured public static URL failed required checks with 404 responses, and no hosted backend URL is configured for route, safe-query, blocked-request, telemetry, or rate-limit verification.

<!-- P79-OBJECT-PAGE-CONTRACT-START -->
## P79 Object Page Contract v0

Object Page Contract v0 is contract-only and evidence-first. It defines future public object pages that preserve provisional identity, source/evidence/provenance, compatibility, conflicts, scoped absence, and gaps without implementing runtime object pages.

Boundary notes:

- No runtime object routes, database, persistent object-page store, source connector runtime, source cache runtime, evidence ledger runtime, candidate promotion, public-index mutation, local-index mutation, master-index mutation, live source fanout, downloads, installs, execution, uploads, telemetry, accounts, rights clearance, or malware safety claim are added.
- Public search may reference object page links only after a future governed integration; P79 does not mutate public search result cards or the public index.
- Object pages are not app-store, downloader, installer, or execution surfaces.
<!-- P79-OBJECT-PAGE-CONTRACT-END -->

<!-- P80-SOURCE-PAGE-CONTRACT-START -->
## P80 Source Page Contract v0

Source Page Contract v0 is contract-only and evidence-first. It defines future public source pages for source identity, status, coverage, connector posture, source policy gates, source cache/evidence posture, public search projection, query-intelligence projection, limitations, provenance caution, and rights/risk posture.

Boundary notes:

- No runtime source routes, database, persistent source-page store, connector runtime, source sync runtime, source cache runtime, evidence ledger runtime, candidate promotion, public-index mutation, local-index mutation, master-index mutation, live source fanout, downloads, mirrors, installs, execution, uploads, telemetry, accounts, rights clearance, malware safety claim, or authoritative source trust claim are added.
- Public search may reference source page links or source badges only after a future governed integration; P80 does not mutate public search result cards or the public index.
- Source pages explain source posture and limitations; they are not source API proxies, scrapers, crawlers, download pages, mirrors, or connector health dashboards.
<!-- P80-SOURCE-PAGE-CONTRACT-END -->
