# Internet Archive Metadata Connector Approval v0

P71 defines an approval pack for a future Internet Archive metadata connector. The connector is not implemented, no external calls are made, no public-query fanout is enabled, and no source cache, evidence ledger, candidate index, public index, local index, or master index is mutated.

## Scope

The allowed future scope is metadata-only: item metadata lookup, bounded item-search metadata summaries, file-listing metadata summaries, collection metadata summaries, and availability metadata. Every capability is disabled now and requires approval before implementation.

## Forbidden Capabilities

Downloads, file retrieval, mirroring, item bulk download, account access, uploads, installs, execution, arbitrary URL fetch, unbounded crawl, scraping, bypassing access restrictions, raw payload dumps, rights-clearance decisions, and malware-safety decisions are forbidden by this approval pack.

## Source Policy, User-Agent, And Contact

Official Internet Archive source policy and automated access review are required and remain pending. A descriptive User-Agent and contact policy are required later, but no User-Agent value or contact value is configured now. Fake contact values are forbidden.

## Rate Limits And Circuit Breakers

Future implementation must define source-policy-reviewed rate limits, timeouts, retry/backoff, retry-after handling, and circuit breakers. P71 configures no runtime values and starts no workers.

## Cache-First And Evidence Output

Future IA metadata must flow through approved source sync workers into source cache summaries and evidence ledger observations before public use. Source cache outputs are metadata summaries only and raw payloads are forbidden. Evidence ledger outputs are observations, not accepted truth, and require review plus promotion policy before candidate or master-index use.

## Public Search Boundary

Public search must not call Internet Archive live. A future public search path may read reviewed source cache output, but P71 does not implement that path and makes no static-site or hosted-backend live claim.

## Query Intelligence Boundary

Demand dashboard, search need, and probe queue records may reference this connector as future approval-gated work. P71 mutates no query observation, result cache, miss ledger, search need, probe queue, or candidate index records.

## Rights, Access, Risk, And Privacy

IA metadata is not rights clearance and not malware safety. The approval pack is public-safe metadata policy only; it permits no private data, credentials, account access, private paths, private URLs, or raw private queries in examples.

## Future Path

Before runtime work: complete official source-policy review, choose approved User-Agent/contact policy, define rate/timeout/retry/circuit-breaker values, approve source sync worker output destinations, and review source cache/evidence ledger integration. P71 itself is not production readiness.
