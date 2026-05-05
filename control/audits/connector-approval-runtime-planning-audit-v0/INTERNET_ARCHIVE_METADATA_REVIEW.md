# Internet Archive Metadata Review

Status summary: approval pack present, connector contract present, inventory
present, runtime planning present, approval pending, runtime planning-only.

Major gates:

- Source/API policy review is policy_gated.
- User-Agent/contact, rate-limit, timeout, retry/backoff, and circuit breaker are operator_gated.
- Token/auth is disabled for v0 unless a future policy changes.
- Item/source identifier privacy review is required.
- Source-cache/evidence-ledger authoritative destinations remain dependency_gated.

Forbidden capabilities: no live metadata calls, no downloads, no arbitrary URL
fetch, no public-search fanout, no source-cache/evidence-ledger writes, no index
mutation, no credentials, no telemetry.

Next safe action: human/operator source-policy and User-Agent/contact/rate-limit
review, then an explicit connector runtime approval decision pack.
