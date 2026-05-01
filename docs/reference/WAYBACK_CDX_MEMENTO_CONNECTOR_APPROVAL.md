# Wayback/CDX/Memento Connector Approval Pack v0

P72 defines the approval pack for a future Wayback/CDX/Memento connector. The connector is not implemented. The pack makes no external calls, performs no Wayback/CDX/Memento calls, fetches no archived content, replays no captures, downloads no WARC records, and mutates no source cache, evidence ledger, candidate index, public index, local index, or master index.

## Scope

The scope is availability/capture metadata-only. Future capabilities may include URL availability metadata, CDX capture metadata summaries, Memento TimeMap/TimeGate metadata summaries, capture timestamp summaries, status-code/MIME/digest summaries, and nearest-capture metadata. These are future-after-approval capabilities only.

## URL/URI Privacy Policy

URI-R review is required before any future connector can operate. Arbitrary public query URLs are forbidden, public search may not accept an arbitrary URL parameter for live fanout, raw URL publication is forbidden, private URLs are forbidden, credentialed URLs are forbidden, local/localhost/file/data/javascript URLs are forbidden, and sensitive URI inputs must be redacted or rejected. Example URI-R values must be synthetic non-resolving placeholders such as `https://example.invalid/software` and must not be fetched.

## Forbidden Behavior

Arbitrary URL fetch, direct public-query fanout, archived page content fetch, capture replay, WARC download, file download, mirroring, screenshot capture, account access, upload, install, execute, unbounded crawl, scraping, bypassing access restrictions, raw payload dumps, malware-safety decisions, and rights-clearance decisions are forbidden.

## Source Policy and Operator Gates

Official source policy, Memento/CDX policy, automated access policy, source terms, rate-limit, retry-after, cache, rights/access, User-Agent, and contact policy review are required before implementation approval. No User-Agent value or contact value is configured now; fake contact values are forbidden.

## Cache-First and Evidence-First

Future outputs must go first to source cache and evidence ledger contracts. Public search must not call Wayback/CDX/Memento live. Future public search may only read reviewed cache/evidence outputs after governed runtime work exists. Evidence observations are not truth and require review plus candidate promotion policy before any index use.

## Relationships

Source sync workers may later request bounded jobs only after approval. Source cache may later hold metadata summaries only, never raw archived content. Evidence ledger may later hold availability/capture observations, never accepted truth by default. Query intelligence may prioritize future work but cannot mutate query observations, result cache, miss ledger, search needs, probe queue, or candidate index in P72.

## Remaining Future Work

The approval checklist, operator checklist, official source policy review, URI privacy filter, rate-limit/timeout/retry/circuit breaker values, User-Agent/contact decision, source sync runtime, source cache runtime, evidence ledger runtime, and connector implementation remain future/deferred.
