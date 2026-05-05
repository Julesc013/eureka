# Wayback/CDX/Memento Connector Runtime Planning v0

P88 plans a future bounded Wayback/CDX/Memento connector runtime without implementing it.

Readiness decision: `blocked_connector_approval_pending`.

The P72 approval pack is present, but it explicitly keeps `connector_approved_now` false. URI privacy review, source policy review, User-Agent/contact configuration, rate-limit/timeout/retry/circuit-breaker values, source-cache runtime, evidence-ledger runtime, and operator approval remain gates.

P88 is planning-only. It does not implement the Wayback/CDX/Memento connector runtime, does not call Wayback, CDX, Memento, Internet Archive, or archive.org endpoints, does not fetch archived pages, does not replay captures, does not download WARC records, does not run source sync jobs, does not write source-cache or evidence-ledger records, does not wire public search to live calls, does not enable arbitrary URL fetch, downloads, mirroring, screenshots, credentials, or telemetry, and does not mutate public, local, runtime, candidate, source-cache, evidence-ledger, or master indexes.
