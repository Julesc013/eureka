# Wayback CDX Memento Review

Status summary: approval pack present, connector contract present, inventory
present, runtime planning present, approval pending, runtime planning-only.

Major gates:

- CDX/Memento source-policy review is policy_gated.
- URI-R privacy review is required before any live or recorded public output.
- User-Agent/contact, rate-limit, timeout, retry/backoff, and circuit breaker are operator_gated.
- Token/auth is disabled for v0 unless future policy changes.
- Source-cache/evidence-ledger authoritative destinations remain dependency_gated.

Forbidden capabilities: no CDX/Memento calls, no arbitrary URL fetch, no capture
replay, no WARC download, no archived content fetch, no public-search fanout, no
mutation, no credentials, no telemetry.

Next safe action: human/operator URI privacy and source-policy review, then an
explicit connector runtime approval decision pack.
