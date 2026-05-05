# PyPI Metadata Connector Runtime Plan

P90 is a planning-only runtime plan for a future PyPI metadata connector.

## Approval Gate

The P74 approval pack is present, but `connector_approved_now` is false. Runtime implementation is blocked until approval, package identity review, dependency metadata caution review, token/auth boundary review, source policy review, User-Agent/contact configuration, rate limits, timeouts, retry/circuit-breaker values, cache/evidence destinations, package download/install/dependency boundaries, and operator approval are complete.

## Package Identity Gate

Future package-name inputs must come from reviewed source records, reviewed search needs, source pack records, manual observation records, or fixture examples. Public query parameters, private packages, credentialed package indexes, alternate indexes without future approval, local paths, uploaded files, and arbitrary URLs cannot choose live fetch.

## Dependency Metadata Caution Gate

Dependency metadata may be summarized only when present in approved metadata. Dependency resolution, dependency graph expansion, package manager invocation, dependency safety claims, vulnerability/security claims, and installability claims remain disabled.

## Token/Auth Boundary

PyPI Metadata v0 is token-free by default. No token or credential is configured, and authenticated package index access remains blocked unless a future explicit policy approves it.

## Why Runtime Is Not Implemented Yet

No runtime is implemented because approval and operator gates are incomplete. P90 makes no external calls, adds no connector runtime, writes no source-cache or evidence-ledger records, enables no public-search live fanout, enables no arbitrary package fetch, downloads no wheels, sdists, or package files, installs no packages, resolves no dependencies, inspects no package archives, invokes no package manager, uses no tokens, and performs no mutation.

P90 explicitly provides no package download/install/dependency resolution behavior.

## Runtime Architecture Plan

Future modules would include a bounded metadata client, package identity guard, dependency metadata caution guard, token/auth policy guard, source policy guard, normalizer, evidence observation builder, bounded error model, and runtime README under `runtime/connectors/pypi_metadata/`. P90 does not create those runtime files.

## Future Source Sync Job Flow

An approved source sync job would pass through connector approval, package identity, dependency metadata caution, token/auth, source policy, User-Agent/contact, rate-limit, timeout, retry, and circuit-breaker checks before any future metadata-only request. Normalized results would become source-cache candidates and evidence-ledger observation candidates. Review remains required before candidate or index effects.

## Future Source Cache Outputs

Future source-cache summaries may include project metadata, release metadata, file metadata, requires-python, classifiers, yanked status, and dependency metadata. They must be metadata-only, public-safe, attributed, package-identity reviewed, dependency-caution reviewed, bounded, and free of raw payloads, wheel/sdist/package downloads, archive inspection, package installation, and dependency resolution.

## Future Evidence Ledger Outputs

Future evidence outputs may include package metadata observations, release observations, version observations, file metadata observations, requires-python observations, classifier observations, yanked status observations, dependency metadata observations, and scoped absence observations. They are not truth, rights clearance, file safety, installability, dependency safety, vulnerability status, or malware safety.

## Public Search Boundary

Public search must not call PyPI live. Public search must not accept arbitrary package parameters for live fetch. Future public cards may reference reviewed public-safe summaries only after separate runtime and review.

## Source Policy, User-Agent, Contact, And Rate-Limit Gates

Operator decisions are required for PyPI API/source policy, descriptive User-Agent, contact policy, rate limit, timeout, retry/backoff, circuit breaker, cache destination, evidence destination, and kill switch.

## Privacy, Rights, And Risk

The connector remains package-metadata-only. It does not access private packages or token-required indexes, use alternate indexes without future policy, download wheels/sdists/package files, inspect package archives, install packages, resolve dependencies, invoke package managers, mirror, retrieve files, install, execute, use credentials, access private accounts, claim rights clearance, claim file safety, claim installability, claim dependency safety, claim vulnerability status, or claim malware safety.

## Arbitrary Package And Download Prohibitions

Arbitrary package fetch, raw public query package fanout, wheel download, sdist download, package file download, package install, dependency resolution, package archive inspection, setup.py/build script execution, package manager invocation, mirroring, and file retrieval remain forbidden.

## Failure, Retry, And Circuit Breaker

Future runtime must bound timeouts and retries, respect retry-after/backoff and abuse-limit signals, enforce per-source rate limits and circuit breakers, avoid retry storms, avoid raw error leaks, and never block public search.

## Implementation Phases

Phase 0 stays disabled and validates planning. Phase 1 is synthetic local dry-run only. Phase 2 allows local approved live metadata probes only after human/operator approval. Phase 3 integrates source sync worker candidate writes. Phase 4 rebuilds public index from reviewed cache/evidence only. Phase 5 adds a hosted connector worker with monitoring, rollback, quotas, and kill switch.

## Acceptance Criteria

Approval complete, package identity policy reviewed, dependency metadata caution policy reviewed, token/auth boundary reviewed, source policy reviewed, User-Agent/contact configured, rate limits and timeouts approved, retry/circuit breaker approved, source-sync/cache/evidence runtimes approved, cache and evidence destinations configured, evidence attribution required, public fanout disabled, arbitrary package fetch disabled, wheel/sdist/package download disabled, package install disabled, dependency resolution disabled, package archive inspection disabled, package manager invocation disabled, kill switch present, no download/mirror/install/execute, no raw payload storage, no credentials for v0, blocked-public-param tests, and operator approval.

## Next Steps

Proceed to P91 npm Metadata Connector Runtime Planning v0 only after approval. Human/operator work remains hosted wrapper deployment, backend URL and edge/rate-limit configuration, static-site verification, Manual Observation Batch 0, PyPI API/source policy review, PyPI User-Agent/contact decision, and token-free v0 policy decision.
