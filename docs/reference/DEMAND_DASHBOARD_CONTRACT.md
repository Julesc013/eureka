# Demand Dashboard Contract v0

Demand Dashboard v0 defines a contract-only aggregate visibility layer for future privacy-filtered aggregate demand. The dashboard is not runtime yet. The dashboard is not telemetry. The dashboard is not user tracking. It is not source trust, not candidate promotion, not rights clearance, not malware safety, and not public-search ranking authority.

The dashboard does not claim real demand in v0 examples. All committed examples are deterministic synthetic snapshots or stdout-only dry-run output. Raw query retention default none.

## Snapshot Shape

`contracts/query/demand_dashboard_snapshot.v0.json` records input summary, privacy guard summary, poisoning guard summary, dashboard scope, aggregate buckets, demand signals, source gap demand, capability gap demand, manual-observation demand, connector priorities, deep-extraction priorities, candidate-review priorities, known-absence patterns, priority summary, public visibility, freshness/invalidation, limitations, and hard no-runtime/no-mutation guarantees.

## Privacy Filtering Before Aggregation

Privacy filtering before aggregation is mandatory. Raw queries, private paths, secrets, credentials, private URLs, local identifiers, account identifiers, IP addresses, and protected private data are not dashboard aggregate fields.

## Poisoning and Fake-Demand Filtering Before Aggregation

Poisoning/fake-demand filtering before aggregation is mandatory. Fake demand, spam, source-stuffing, candidate-poisoning, rank manipulation attempts, live-probe forcing, arbitrary URL fetch forcing, and download/install/execute forcing must be excluded or quarantined before future aggregation.

## Aggregate Buckets

Aggregate buckets are coarse fields such as object kind, platform, artifact type, source family, source gap, capability gap, miss type, probe kind, candidate type, known absence status, manual-observation need, connector priority, and deep-extraction need. Example buckets use synthetic counts or count-not-available policies and never real public demand proof.

## Priority Signals

Priority signals can represent repeated needs, repeated misses, source gaps, capability gaps, compatibility gaps, member-access gaps, known-absence patterns, manual-observation needs, connector needs, deep-extraction needs, candidate-review needs, and policy-blocked patterns. Priority is a planning hint, not truth.

## Demand Models

Source, capability, manual-observation, connector, deep-extraction, candidate-review, and known-absence models stay future-facing. They do not run probes, sync sources, mutate caches, mutate ledgers, mutate candidates, promote candidates, or mutate indexes.

## Public Visibility Caveats

Public visibility requires caveats: contract-only, synthetic or future-filtered aggregate, no raw queries, no private data, no telemetry, no account/IP tracking, no production analytics, and no real demand counts unless separately evidenced by a governed future system.

## Relations

Demand Dashboard v0 relates to query observations, shared result cache entries, miss ledger entries, search need records, probe queue items, candidate index records, candidate promotion assessments, known absence pages, and query privacy/poisoning guard decisions as future inputs only. P68 reads no runtime logs and writes no query-intelligence objects.

Future source sync, source cache, evidence ledger, connector approvals, and any hosted dashboard require separate governed contracts and verification.

## Source Sync Worker v0 Relation

Source Sync Worker Contract v0 is future/contract-only. It may later consume probe queue and demand dashboard signals to plan approved, bounded source sync jobs, but P69 adds no connector runtime, source calls, public-query fanout, source cache mutation, evidence ledger mutation, candidate mutation, or index mutation.

## P70 Source Cache And Evidence Ledger Relation

Demand dashboard source and capability priorities may later inform approved source sync work whose outputs enter Source Cache Contract v0 and Evidence Ledger Contract v0. P70 adds no dashboard aggregation runtime, no source calls, no cache/ledger mutation, and no real demand claims.

<!-- P71-INTERNET-ARCHIVE-METADATA-CONNECTOR-APPROVAL-START -->
## P71 Internet Archive Metadata Connector Approval

`docs/reference/INTERNET_ARCHIVE_METADATA_CONNECTOR_APPROVAL.md` defines an approval-only, metadata-only future Internet Archive connector pack. It is not runtime, makes no external calls, enables no public-query fanout, performs no downloads/file retrieval/mirroring, and mutates no source cache, evidence ledger, candidate index, public/local/master index, telemetry, or credentials. Future work is blocked on official source policy review, User-Agent/contact policy, rate limits, timeouts, retry/backoff, circuit breakers, cache-first source cache output, and evidence ledger attribution.

This cross-reference keeps `docs/reference/DEMAND_DASHBOARD_CONTRACT.md` aligned with the source-ingestion boundary: IA metadata may become future reviewed cache/evidence input, never direct truth or live public search fanout.
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
