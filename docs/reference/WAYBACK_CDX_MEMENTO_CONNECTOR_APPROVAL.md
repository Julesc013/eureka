# Wayback/CDX/Memento Connector Approval Pack v0

P72 defines the approval pack for a future Wayback/CDX/Memento connector. The connector is not implemented. The pack makes no external calls, performs no Wayback/CDX/Memento calls, fetches no archived content, replays no captures, downloads no WARC records, and mutates no source cache, evidence ledger, candidate index, public index, local index, or master index.

## Scope

The scope is availability/capture metadata-only. Future capabilities may include URL availability metadata, CDX capture metadata summaries, Memento TimeMap/TimeGate metadata summaries, capture timestamp summaries, status-code/MIME/digest summaries, and nearest-capture metadata. These are future-after-approval capabilities only.

## URL/URI Privacy Policy

URI-R review is required before any future connector can operate. Arbitrary public query URLs are forbidden, public search may not accept an arbitrary URL parameter for live fanout, raw URL publication is forbidden, private URLs are forbidden, credentialed URLs are forbidden, local/localhost/file/data/javascript URLs are forbidden, and sensitive URI inputs must be redacted or rejected. Example URI-R values must be synthetic non-resolving placeholders such as `https://example.invalid/software` and must not be fetched.

## Forbidden Behavior

Arbitrary URL fetch, direct public-query fanout, archived page content fetch, capture replay, WARC download, file download, mirroring, screenshot capture, account access, upload, install, execute, unbounded crawl, scraping, bypassing access restrictions, raw payload dumps, malware-safety decisions, and rights-clearance decisions are forbidden.

## Source Policy and Operator Gates

Official source policy, Memento/CDX policy, automated access policy, source terms, rate-limit, retry-after, cache, rights/access, User-Agent, and contact policy review are required before implementation approval. No User-Agent value or contact value is configured now; fake contact values are forbidden.

## Cache-First and Evidence-First

Future outputs must go first to source cache and evidence ledger contracts. Public search must not call Wayback/CDX/Memento live. Future public search may only read reviewed cache/evidence outputs after governed runtime work exists. Evidence observations are not truth and require review plus candidate promotion policy before any index use.

## Relationships

Source sync workers may later request bounded jobs only after approval. Source cache may later hold metadata summaries only, never raw archived content. Evidence ledger may later hold availability/capture observations, never accepted truth by default. Query intelligence may prioritize future work but cannot mutate query observations, result cache, miss ledger, search needs, probe queue, or candidate index in P72.

## Remaining Future Work

The approval checklist, operator checklist, official source policy review, URI privacy filter, rate-limit/timeout/retry/circuit breaker values, User-Agent/contact decision, source sync runtime, source cache runtime, evidence ledger runtime, and connector implementation remain future/deferred.

<!-- P73-GITHUB-RELEASES-CONNECTOR-APPROVAL-START -->
## P73 GitHub Releases Connector Approval Pack v0

P73 defines a future release-metadata-only GitHub Releases connector approval pack. The live connector is not implemented, no external calls are made, no GitHub API calls are made, public queries do not fan out to GitHub, arbitrary repository fetch is forbidden, repository clone is forbidden, release asset download is forbidden, source archive download is forbidden, raw file/blob/tree fetch is forbidden, scraping/crawling is forbidden, token use is not allowed now, and future outputs must be cache-first/evidence-first after repository identity review and approval.
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

<!-- P80-SOURCE-PAGE-CONTRACT-START -->
## P80 Source Page Contract v0

Source Page Contract v0 is contract-only and evidence-first. It defines future public source pages for source identity, status, coverage, connector posture, source policy gates, source cache/evidence posture, public search projection, query-intelligence projection, limitations, provenance caution, and rights/risk posture.

Boundary notes:

- No runtime source routes, database, persistent source-page store, connector runtime, source sync runtime, source cache runtime, evidence ledger runtime, candidate promotion, public-index mutation, local-index mutation, master-index mutation, live source fanout, downloads, mirrors, installs, execution, uploads, telemetry, accounts, rights clearance, malware safety claim, or authoritative source trust claim are added.
- Public search may reference source page links or source badges only after a future governed integration; P80 does not mutate public search result cards or the public index.
- Source pages explain source posture and limitations; they are not source API proxies, scrapers, crawlers, download pages, mirrors, or connector health dashboards.
<!-- P80-SOURCE-PAGE-CONTRACT-END -->
