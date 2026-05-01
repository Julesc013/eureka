# Integration Boundaries

P63 does not wire public search routes to write probe queue items. It does not
add a database, queue processor, connector runtime, source cache runtime,
evidence ledger runtime, candidate index runtime, telemetry, uploads,
downloads, installers, model calls, or deployment.

Future integration must pass source policy, privacy, poisoning, approval,
rate-limit, timeout, circuit-breaker, cache, evidence, candidate, and
promotion-policy gates.
