# PyPI Metadata Connector Approval Pack v0

P74 defines the approval pack for a future PyPI metadata connector. The live connector is not implemented. The pack makes no external calls, performs no PyPI API calls, invokes no package installer, installs no packages, resolves no dependencies, downloads no wheels, sdists, or package files, inspects no package archives, uses no tokens, and mutates no source cache, evidence ledger, candidate index, public index, local index, or master index.

## Scope

The scope is package metadata-only. Future capabilities may include project metadata, release metadata, file metadata summaries, `Requires-Python` metadata, classifier metadata, yanked status metadata, package summary/description metadata, and dependency metadata summaries. These are future-after-approval capabilities only. Existing package-registry recorded fixtures remain fixture-only and do not imply live PyPI acquisition approval.

## Package Identity And Privacy Policy

Package name review is required before any future connector can operate. Arbitrary public query packages are forbidden, public search may not accept an arbitrary package parameter for live fanout, raw package URL publication is forbidden, private packages are forbidden, credentialed package indexes are forbidden, token-required packages are forbidden for v0, alternate indexes are not allowed now, local package paths are forbidden, and sensitive package inputs must be redacted or rejected. Example package names must be synthetic public-safe placeholders such as `example-package` and must not be fetched.

## Dependency Metadata Caution

Dependency metadata caution is required. Dependency fields may be summarized as metadata only after approval. Dependency resolution, dependency graph expansion, installability claims, security/vulnerability claims, and dependency safety claims are forbidden by P74.

## Forbidden Behavior

Arbitrary package fetch, direct public-query fanout, private package index access, token-required access, package file download, wheel download, sdist download, package install, dependency resolution, dependency safety decisions, package archive inspection, setup.py execution, build script execution, raw file fetch, alternate index fetch, account access, upload, install, execute, unbounded crawl, scraping, bypassing access restrictions, raw payload dumps, malware-safety decisions, and rights-clearance decisions are forbidden.

## Source Policy, User-Agent, Contact, And Token Gates

Official PyPI API/source policy, automated access policy, rate-limit, retry-after or abuse-limit, cache, rights/access, User-Agent, contact, package identity, dependency metadata, and token policy review are required before implementation approval. No User-Agent value, contact value, credential, or PyPI token is configured now; fake contact values and token use are forbidden.

## Rate Limits And Circuit Breakers

Future implementation must define source-policy-reviewed rate limits, timeouts, retry/backoff, retry-after or abuse-limit handling, and circuit breakers. P74 configures no runtime values and starts no workers.

## Cache-First And Evidence-First

Future PyPI metadata must flow through approved source sync workers into source cache summaries and evidence ledger observations before public use. Source cache outputs are metadata summaries only and package payloads, wheel payloads, sdist payloads, and installation artifacts are forbidden. Evidence ledger outputs are observations, not accepted truth, and require review plus promotion policy before candidate or master-index use.

## Public Search Boundary

Public search must not call PyPI live. Public search must not accept arbitrary package parameters for live fanout. A future public search path may read reviewed source cache output, but P74 does not implement that path and makes no static-site or hosted-backend live claim.

## Query Intelligence Boundary

Demand dashboard, search need, known absence, and probe queue records may reference this connector as future approval-gated work. P74 mutates no query observation, result cache, miss ledger, search need, probe queue, or candidate index records.

## Rights, Access, Risk, And Privacy

PyPI metadata is not rights clearance, not malware safety, not dependency safety, and not installability proof. The approval pack is public-safe metadata policy only; it permits no private packages, private package indexes, private data, credentials, account access, private paths, private URLs, tokens, package file downloads, wheel downloads, sdist downloads, package installs, dependency resolution, package archive inspection, installs, or execution in examples.

## Future Path

Before live runtime work: complete official source-policy review, choose approved User-Agent/contact policy, confirm no token is required for v0, define rate/timeout/retry/circuit-breaker values, approve source sync worker output destinations, review source cache/evidence ledger integration, and approve the live connector implementation. P74 itself is not production readiness.

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

<!-- P81-COMPARISON-PAGE-CONTRACT-START -->
## P81 Comparison Page Contract v0

Comparison Page Contract v0 is contract-only and evidence-first. It defines future public comparison pages for subjects, criteria, matrices, identity/version/representation/source/evidence/compatibility/action comparisons, conflict preservation, scoped gaps, and future result-card/object/source projections.

Boundary notes:

- No runtime comparison pages, database, persistent comparison-page store, connector runtime, source sync runtime, source cache runtime, evidence ledger runtime, candidate promotion, public-index mutation, local-index mutation, master-index mutation, live source fanout, downloads, installs, execution, uploads, telemetry, accounts, rights clearance, malware safety claim, authoritative source trust claim, or winner without evidence are added.
- Public search may reference comparison links only after a future governed integration; P81 does not mutate public search result cards or the public index.
- Comparison pages explain evidence-backed similarity, difference, conflict, and gaps; they are not ranking authority, candidate promotion, source API proxies, download pages, installer pages, or production comparison services.
<!-- P81-COMPARISON-PAGE-CONTRACT-END -->
