# Source Ingestion Plane

Source Ingestion Plane v0 begins with P69 Source Sync Worker Contract v0. Source sync workers are future bounded jobs for approved sources. They are not connector runtime yet, not crawlers, not scrapers, not public-query fanout, not source cache or evidence ledger mutation in v0, and not master-index mutation.

Future live source sync requires approval, source policy review, rate limits, timeouts, circuit breakers, User-Agent policy, source terms review, cache-first handling, evidence attribution, and operator controls. P69 adds no worker queue, database, deployment, credentials, telemetry, live source calls, downloads, uploads, installs, or arbitrary URL fetching.

## P70 Source Cache And Evidence Ledger v0

P70 adds Source Cache Contract v0 and Evidence Ledger Contract v0 as contract-only storage models. They are not runtime, not public-query fanout, not arbitrary URL cache, not raw payload store, not private data store, and not source/evidence/candidate/public/local/master index mutation. Future approved source sync workers may write cache-first, evidence-attributed metadata only after approval, source policy, rate limits, timeouts, circuit breakers, and descriptive User-Agent policy.

<!-- P71-INTERNET-ARCHIVE-METADATA-CONNECTOR-APPROVAL-START -->
## P71 Internet Archive Metadata Connector Approval Pack v0

P71 adds an approval pack for a future Internet Archive metadata connector. The connector is not implemented, no external calls occur, public queries do not fan out to Internet Archive, and source cache/evidence ledger/candidate/public/local/master indexes are not mutated. Scope is metadata-only after approval: item metadata, bounded metadata query summaries, collection summaries, file-listing metadata summaries, and availability metadata. Downloads, file retrieval, mirroring, arbitrary URL fetch, scraping, full-text scrape, access-restricted downloads, installs, execution, rights clearance, and malware safety decisions are forbidden.

Future implementation requires official source policy review, User-Agent/contact policy, rate limits, timeouts, retry/backoff, circuit breakers, cache-first output to source cache, evidence attribution to the evidence ledger, and operator approval.
<!-- P71-INTERNET-ARCHIVE-METADATA-CONNECTOR-APPROVAL-END -->

## P72 Wayback/CDX/Memento Connector Approval Pack v0

P72 defines a future availability/capture-metadata-only Wayback/CDX/Memento connector approval pack. The connector is not implemented, no external calls are made, public queries do not fan out to Wayback/CDX/Memento, arbitrary URL fetch is forbidden, archived content fetch/capture replay/WARC download are forbidden, and future outputs must be cache-first/evidence-first after URI privacy review and approval.

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

<!-- P79-OBJECT-PAGE-CONTRACT-START -->
## P79 Object Page Contract v0

Object Page Contract v0 is contract-only and evidence-first. It defines future public object pages that preserve provisional identity, source/evidence/provenance, compatibility, conflicts, scoped absence, and gaps without implementing runtime object pages.

Boundary notes:

- No runtime object routes, database, persistent object-page store, source connector runtime, source cache runtime, evidence ledger runtime, candidate promotion, public-index mutation, local-index mutation, master-index mutation, live source fanout, downloads, installs, execution, uploads, telemetry, accounts, rights clearance, or malware safety claim are added.
- Public search may reference object page links only after a future governed integration; P79 does not mutate public search result cards or the public index.
- Object pages are not app-store, downloader, installer, or execution surfaces.
<!-- P79-OBJECT-PAGE-CONTRACT-END -->
