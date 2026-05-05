# GitHub Releases Connector Runtime Plan

P89 is a planning-only runtime plan for a future GitHub Releases metadata connector.

## Approval Gate

The P73 approval pack is present, but `connector_approved_now` is false. Runtime implementation is blocked until approval, repository identity review, token/auth boundary review, source policy review, User-Agent/contact configuration, rate limits, timeouts, retry/circuit-breaker values, cache/evidence destinations, and operator approval are complete.

## Repository Identity Gate

Future owner/repository inputs must come from reviewed source records, reviewed search needs, source pack records, manual observation records, or fixture examples. Public query parameters, private repositories, credentialed repositories, local paths, uploaded files, and arbitrary URLs cannot choose live fetch.

## Token/Auth Boundary

GitHub Releases v0 is token-free by default. No token or credential is configured, and authenticated access remains blocked unless a future explicit policy approves it.

## Why Runtime Is Not Implemented Yet

No runtime is implemented because approval and operator gates are incomplete. P89 makes no external calls, adds no connector runtime, writes no source-cache or evidence-ledger records, enables no public-search live fanout, enables no arbitrary repository fetch, clones no repository, performs no asset/source download, fetches no raw blobs/files, uses no tokens, and performs no mutation.

## Runtime Architecture Plan

Future modules would include a bounded release metadata client, repository identity guard, token/auth policy guard, source policy guard, normalizer, evidence observation builder, bounded error model, and runtime README under `runtime/connectors/github_releases/`. P89 does not create those runtime files.

## Future Source Sync Job Flow

An approved source sync job would pass through connector approval, repository identity, token/auth, source policy, User-Agent/contact, rate-limit, timeout, retry, and circuit-breaker checks before any future metadata-only request. Normalized results would become source-cache candidates and evidence-ledger observation candidates. Review remains required before candidate or index effects.

## Future Source Cache Outputs

Future source-cache summaries may include repository release summaries, release metadata summaries, release asset metadata summaries, release tag/date summaries, and latest release summaries. They must be metadata-only, public-safe, attributed, repository-identity reviewed, bounded, and free of raw payloads, asset downloads, source archive downloads, repository clones, and raw file/blob fetches.

## Future Evidence Ledger Outputs

Future evidence outputs may include release metadata observations, package or release availability observations, version observations, asset metadata observations, repository source observations, and scoped absence observations. They are not truth, rights clearance, asset safety, installability, dependency safety, or malware safety.

## Public Search Boundary

Public search must not call GitHub live. Public search must not accept arbitrary repository parameters for live fetch. Future public cards may reference reviewed public-safe summaries only after separate runtime and review.

## Source Policy, User-Agent, Contact, And Rate-Limit Gates

Operator decisions are required for GitHub API/source policy, descriptive User-Agent, contact policy, rate limit, timeout, retry/backoff, circuit breaker, cache destination, evidence destination, and kill switch.

## Privacy, Rights, And Risk

The connector remains release-metadata-only. It does not access private repositories, use token-required access, clone repositories, download release assets or source archives, fetch raw files/blobs, mirror, retrieve files, install, execute, use credentials, access private accounts, claim rights clearance, claim asset safety, claim installability, claim dependency safety, or claim malware safety.

## Arbitrary Repository And Download Prohibitions

Arbitrary repository fetch, raw public query owner/repo fanout, repository clone, release asset download, source archive download, raw blob/file fetch, mirroring, and file retrieval remain forbidden.

## Failure, Retry, And Circuit Breaker

Future runtime must bound timeouts and retries, respect retry-after/backoff and abuse-limit signals, enforce per-source rate limits and circuit breakers, avoid retry storms, avoid raw error leaks, and never block public search.

## Implementation Phases

Phase 0 stays disabled and validates planning. Phase 1 is synthetic local dry-run only. Phase 2 allows local approved live metadata probes only after human/operator approval. Phase 3 integrates source sync worker candidate writes. Phase 4 rebuilds public index from reviewed cache/evidence only. Phase 5 adds a hosted connector worker with monitoring, rollback, quotas, and kill switch.

## Acceptance Criteria

Approval complete, repository identity policy reviewed, token/auth boundary reviewed, source policy reviewed, User-Agent/contact configured, rate limits and timeouts approved, retry/circuit breaker approved, source-sync/cache/evidence runtimes approved, cache and evidence destinations configured, evidence attribution required, public fanout disabled, arbitrary repository fetch disabled, repository clone disabled, asset/source download disabled, raw blob/file fetch disabled, kill switch present, no download/mirror/install/execute, no raw payload storage, no credentials for v0, blocked-public-param tests, and operator approval.

## Next Steps

Proceed to P90 PyPI Metadata Connector Runtime Planning v0 only after approval. Human/operator work remains hosted wrapper deployment, backend URL and edge/rate-limit configuration, static-site verification, Manual Observation Batch 0, GitHub API/source policy review, GitHub Releases User-Agent/contact decision, and token-free v0 policy decision.
