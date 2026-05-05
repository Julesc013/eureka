# Software Heritage Review

Status summary: approval pack present, connector contract present, inventory
present, runtime planning present, approval pending, runtime planning-only.

Major gates:

- Software Heritage source-policy review is policy_gated.
- SWHID, origin URL, and repository identity review are required.
- Token/auth review is required; tokens are disabled now.
- Source-code content, blob fetch, archive download, and repository clone
  boundaries remain approval-gated.
- User-Agent/contact, rate-limit, timeout, retry/backoff, and circuit breaker are operator_gated.
- Source-cache/evidence-ledger authoritative destinations remain dependency_gated.

Forbidden capabilities: no Software Heritage API calls, no SWHID live
resolution, no origin lookup, no source-code/blob/content fetch, no repository
clone, no source archive download, no public-search fanout, no mutation, no
credentials, no telemetry.

Next safe action: human/operator SWHID/origin/repository policy review and
cache/evidence destination review.
