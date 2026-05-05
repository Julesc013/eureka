# Internet Archive Metadata Connector Runtime Planning v0

P87 plans a future bounded Internet Archive metadata connector runtime without implementing it.

Readiness decision: `blocked_connector_approval_pending`.

The P71 approval pack is present, but it explicitly keeps `connector_approved_now` false. Source policy review, User-Agent/contact configuration, rate-limit/timeout/retry/circuit-breaker values, source-cache runtime, evidence-ledger runtime, and operator approval remain gates.

P87 is planning-only. It does not implement the Internet Archive metadata connector runtime, does not call archive.org or Internet Archive APIs, does not run source sync jobs, does not write source-cache or evidence-ledger records, does not wire public search to live Internet Archive calls, does not enable downloads or mirroring, does not add credentials or telemetry, and does not mutate public, local, runtime, candidate, source-cache, evidence-ledger, or master indexes.
