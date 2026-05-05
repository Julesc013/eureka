# Internet Archive Metadata Connector Runtime Plan

P87 is a planning-only runtime plan for a future Internet Archive metadata connector.

## Approval Gate

The P71 approval pack is present, but `connector_approved_now` is false. Runtime implementation is blocked until approval, source policy review, User-Agent/contact configuration, rate limits, timeouts, retry/circuit-breaker values, cache/evidence destinations, and operator approval are complete.

## Why Runtime Is Not Implemented Yet

No runtime is implemented because the approval and operator gates are incomplete. P87 makes no external calls, adds no connector runtime, writes no source-cache or evidence-ledger records, enables no public-search live fanout, and performs no mutation.

## Runtime Architecture Plan

Future modules would include a bounded metadata-only client, policy guard, normalizer, evidence observation builder, bounded error model, and runtime README under `runtime/connectors/internet_archive_metadata/`. P87 does not create those runtime files.

## Future Source Sync Job Flow

An approved source sync job would pass through connector approval, source policy, User-Agent/contact, rate-limit, timeout, retry, and circuit-breaker checks before any future metadata-only request. Normalized results would become source-cache candidates and evidence-ledger observation candidates. Review remains required before candidate or index effects.

## Future Source Cache Outputs

Future source-cache summaries may include item metadata, file-listing metadata, collection metadata, and availability metadata. They must be metadata-only, public-safe, attributed, bounded, and free of raw payload dumps or executable payloads.

## Future Evidence Ledger Outputs

Future evidence outputs may include source metadata observations, availability observations, file-listing observations, release or item metadata observations, and scoped absence observations. They are not truth, rights clearance, or malware safety.

## Public Search Boundary

Public search must not call Internet Archive live. Public query parameters must not select live connector mode, source-cache paths, evidence-ledger paths, item identifiers for live fetch, URLs, or filesystem roots. Future public cards may reference reviewed public-safe summaries only after separate runtime and review.

## Source Policy, User-Agent, Contact, And Rate-Limit Gates

Operator decisions are required for source policy, descriptive User-Agent, contact policy, rate limit, timeout, retry/backoff, circuit breaker, cache destination, evidence destination, and kill switch.

## Privacy, Rights, And Risk

The connector remains metadata-only. It does not download, mirror, retrieve files, install, execute, use credentials, access private accounts, claim rights clearance, or claim malware safety.

## Failure, Retry, And Circuit Breaker

Future runtime must bound timeouts and retries, respect retry-after/backoff, enforce per-source rate limits and circuit breakers, avoid retry storms, avoid raw error leaks, and never block public search.

## Implementation Phases

Phase 0 stays disabled and validates planning. Phase 1 is synthetic local dry-run only. Phase 2 allows local approved live metadata probes only after human/operator approval. Phase 3 integrates source sync worker candidate writes. Phase 4 rebuilds public index from reviewed cache/evidence only. Phase 5 adds a hosted connector worker with monitoring, rollback, quotas, and kill switch.

## Acceptance Criteria

Approval complete, source policy reviewed, User-Agent/contact configured, rate limits and timeouts approved, retry/circuit breaker approved, source-sync/cache/evidence runtimes approved, cache and evidence destinations configured, evidence attribution required, public fanout disabled, kill switch present, no download/mirror/install/execute, no raw payload storage, no credentials, blocked-public-param tests, and operator approval.

## Next Steps

Proceed to P88 Wayback/CDX/Memento Connector Runtime Planning v0 only after approval. Human/operator work remains hosted wrapper deployment, backend URL and edge/rate-limit configuration, static-site verification, Manual Observation Batch 0, IA source policy review, and IA User-Agent/contact decision.
