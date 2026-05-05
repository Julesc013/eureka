# Wayback/CDX/Memento Connector Runtime Plan

P88 is a planning-only runtime plan for a future Wayback/CDX/Memento metadata connector.

## Approval Gate

The P72 approval pack is present, but `connector_approved_now` is false. Runtime implementation is blocked until approval, URI privacy review, source policy review, User-Agent/contact configuration, rate limits, timeouts, retry/circuit-breaker values, cache/evidence destinations, and operator approval are complete.

## URI Privacy Gate

URI-R inputs must come from reviewed source records, reviewed search needs, source pack records, manual observation records, or fixture examples. Raw public query URL parameters, private URLs, credentialed URLs, localhost URLs, file URLs, data URLs, javascript URLs, uploaded files, and local paths are forbidden for live fetch.

## Why Runtime Is Not Implemented Yet

No runtime is implemented because the approval, URI privacy, and operator gates are incomplete. P88 makes no external calls, adds no connector runtime, writes no source-cache or evidence-ledger records, enables no public-search live fanout, enables no arbitrary URL fetch, fetches no archived content, replays no captures, downloads no WARC records, and performs no mutation.

## Runtime Architecture Plan

Future modules would include a bounded availability/capture metadata client, URI privacy guard, source policy guard, normalizer, evidence observation builder, bounded error model, and runtime README under `runtime/connectors/wayback_cdx_memento/`. P88 does not create those runtime files.

## Future Source Sync Job Flow

An approved source sync job would pass through connector approval, URI privacy, source policy, User-Agent/contact, rate-limit, timeout, retry, and circuit-breaker checks before any future metadata-only request. Normalized results would become source-cache candidates and evidence-ledger observation candidates. Review remains required before candidate or index effects.

## Future Source Cache Outputs

Future source-cache summaries may include URL availability, CDX capture metadata, Memento timemap metadata, capture timestamp distributions, status/MIME/digest summaries, and nearest capture metadata. They must be metadata-only, public-safe, attributed, URI-privacy reviewed, bounded, and free of raw payloads or archived content.

## Future Evidence Ledger Outputs

Future evidence outputs may include availability observations, capture presence or absence observations, capture metadata observations, historical access path observations, and scoped absence observations. They are not truth, rights clearance, content safety, or malware safety.

## Public Search Boundary

Public search must not call Wayback/CDX/Memento live and must not accept arbitrary URL parameters or URI-R values for live fetch. Future public cards may reference reviewed public-safe summaries only after separate runtime and review.

## Source Policy, User-Agent, Contact, And Rate-Limit Gates

Operator decisions are required for source policy, descriptive User-Agent, contact policy, rate limit, timeout, retry/backoff, circuit breaker, cache destination, evidence destination, and kill switch.

## Privacy, Rights, And Risk

The connector remains availability-and-capture-metadata-only. It does not fetch archived content, replay captures, download WARC records, take screenshots, download, mirror, retrieve files, install, execute, use credentials, access private accounts, claim rights clearance, claim archived content safety, or claim malware safety.

## Arbitrary URL, Capture, And WARC Prohibitions

Arbitrary URL fetch, raw public query URL fanout, archived content fetch, capture replay, WARC download, screenshots, mirroring, and file retrieval remain forbidden.

## Failure, Retry, And Circuit Breaker

Future runtime must bound timeouts and retries, respect retry-after/backoff, enforce per-source rate limits and circuit breakers, avoid retry storms, avoid raw error leaks, and never block public search.

## Implementation Phases

Phase 0 stays disabled and validates planning. Phase 1 is synthetic local dry-run only. Phase 2 allows local approved live metadata probes only after human/operator approval. Phase 3 integrates source sync worker candidate writes. Phase 4 rebuilds public index from reviewed cache/evidence only. Phase 5 adds a hosted connector worker with monitoring, rollback, quotas, and kill switch.

## Acceptance Criteria

Approval complete, URI privacy policy reviewed, source policy reviewed, User-Agent/contact configured, rate limits and timeouts approved, retry/circuit breaker approved, source-sync/cache/evidence runtimes approved, cache and evidence destinations configured, evidence attribution required, public fanout disabled, arbitrary URL fetch disabled, archived content fetch disabled, capture replay disabled, WARC download disabled, kill switch present, no download/mirror/install/execute, no raw payload storage, no credentials, blocked-public-param tests, and operator approval.

## Next Steps

Proceed to P89 GitHub Releases Connector Runtime Planning v0 only after approval. Human/operator work remains hosted wrapper deployment, backend URL and edge/rate-limit configuration, static-site verification, Manual Observation Batch 0, Wayback/CDX/Memento source policy review, and User-Agent/contact decision.
