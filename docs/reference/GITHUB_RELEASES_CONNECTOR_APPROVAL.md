# GitHub Releases Connector Approval Pack v0

P73 defines the approval pack for a future GitHub Releases metadata connector. The live connector is not implemented. The pack makes no external calls, performs no GitHub API calls, clones no repositories, fetches no tags or releases, downloads no release assets or source archives, uses no tokens, and mutates no source cache, evidence ledger, candidate index, public index, local index, or master index.

## Scope

The scope is release metadata-only. Future capabilities may include repository release metadata, release tag metadata summaries, release asset metadata summaries, latest release metadata, release date/version summaries, and prerelease/draft status summaries. These are future-after-approval capabilities only. Existing recorded GitHub Releases fixtures remain fixture-only and do not imply live GitHub acquisition approval.

## Repository Identity And Privacy Policy

Repository owner/name review is required before any future connector can operate. Arbitrary public query repositories are forbidden, public search may not accept an arbitrary repository parameter for live fanout, raw repository URL publication is forbidden, private repositories are forbidden, credentialed repositories are forbidden, token-required repositories are forbidden for v0, local repository paths are forbidden, and sensitive repository inputs must be redacted or rejected. Example owner/repo values must be synthetic public-safe placeholders such as `example-org/example-project` and must not be fetched.

## Forbidden Behavior

Arbitrary repository fetch, direct public-query fanout, private repository access, token-required access, repository clone, tag fetch runtime now, release fetch runtime now, release asset download, source archive download, raw file fetch, blob fetch, tree fetch, org/user bulk crawl, account access, upload, install, execute, unbounded crawl, scraping, bypassing access restrictions, raw payload dumps, malware-safety decisions, and rights-clearance decisions are forbidden.

## Source Policy, User-Agent, Contact, And Token Gates

Official GitHub API/source policy, automated access policy, rate-limit, retry-after or abuse-limit, cache, rights/access, User-Agent, contact, repository identity, and token policy review are required before implementation approval. No User-Agent value, contact value, credential, or GitHub token is configured now; fake contact values and token use are forbidden.

## Rate Limits And Circuit Breakers

Future implementation must define source-policy-reviewed rate limits, timeouts, retry/backoff, retry-after or abuse-limit handling, and circuit breakers. P73 configures no runtime values and starts no workers.

## Cache-First And Evidence-First

Future GitHub Releases metadata must flow through approved source sync workers into source cache summaries and evidence ledger observations before public use. Source cache outputs are metadata summaries only and raw repository payloads, release asset payloads, and source archive payloads are forbidden. Evidence ledger outputs are observations, not accepted truth, and require review plus promotion policy before candidate or master-index use.

## Public Search Boundary

Public search must not call GitHub live. Public search must not accept arbitrary repository parameters for live fanout. A future public search path may read reviewed source cache output, but P73 does not implement that path and makes no static-site or hosted-backend live claim.

## Query Intelligence Boundary

Demand dashboard, search need, known absence, and probe queue records may reference this connector as future approval-gated work. P73 mutates no query observation, result cache, miss ledger, search need, probe queue, or candidate index records.

## Rights, Access, Risk, And Privacy

GitHub Releases metadata is not rights clearance and not malware safety. The approval pack is public-safe metadata policy only; it permits no private repositories, private data, credentials, account access, private paths, private URLs, tokens, release asset downloads, source archive downloads, repository clones, installs, or execution in examples.

## Future Path

Before live runtime work: complete official source-policy review, choose approved User-Agent/contact policy, confirm no token is required for v0, define rate/timeout/retry/circuit-breaker values, approve source sync worker output destinations, review source cache/evidence ledger integration, and approve the live connector implementation. P73 itself is not production readiness.

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
