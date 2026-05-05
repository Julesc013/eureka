# Live Probe Policy

Live Probe Gateway Contract v0 is policy and validation only. It does not
enable live probes and it does not contact external sources.

## Operator Checklist

Before any future source can be enabled, an operator must:

- confirm the source is listed in `live_probe_gateway.json`
- review source terms, robots expectations, and abuse posture
- choose a user-agent policy with project identification
- confirm metadata-only scope
- confirm downloads remain disabled
- confirm arbitrary URL fetching remains disabled
- confirm no user credentials or private account data are used
- confirm per-source timeout and result caps
- confirm cache-first behavior
- confirm evidence records are written
- confirm retry/backoff and circuit breaker behavior
- confirm a per-source disable switch exists
- record explicit signoff

## Source Review

Each source review must record allowed modes, forbidden modes, default result
cap, timeout, cache requirement, evidence requirement, and rollback path.

## Disable Plan

Every future implementation must allow source disablement without code changes.
If a source fails, returns abusive-rate responses, or changes terms, the
operator must be able to turn it off and keep the backend functional.

## Current State

No live probe is implemented. Internet Archive, Wayback, GitHub, Software
Heritage, package registries, and Wikidata candidates are future-disabled.
Google remains manual-baseline only.
## P64 Candidate Index Note

Candidate records may later reference approved probe outputs, but P64 runs no
probes and calls no live sources. Any future live-probe-produced candidate
requires source policy approval, cache/evidence review, rights/risk review,
privacy review, and promotion policy before authoritative use.

## P65 Candidate Promotion Boundary

P65 adds Candidate Promotion Policy v0 as contract-only governance. Candidate promotion policy is not promotion runtime; candidate confidence is not truth; automatic promotion is forbidden; destructive merge is forbidden; future promotion assessment requires evidence, provenance, source policy, privacy, rights, risk, conflict, human, policy, and operator gates. No candidate, source, evidence, public index, local index, or master-index state is mutated.

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
