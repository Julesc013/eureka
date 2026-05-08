# Source Cache Runtime Readiness

## Current Runtime Status

- Current phase: `phase_0_planning_only`
- Runtime status: `runtime_not_implemented`
- Source access status: `source_access_disabled`
- Local source-cache state: not created

## Ready

- Planning inventory exists.
- Runtime, source-access, path, record, review, and rollout policies are
  defined.
- Future metadata probe gates are explicit.
- Public-safe examples exercise minimal, fixture-only, future metadata probe,
  and policy-blocked plans.
- Validator checks planning-only status, disabled access, review gates,
  truth/product boundaries, forbidden claims, private paths, and credential
  patterns.

## Not Implemented

- Local source-cache runtime.
- Authoritative source-cache storage.
- Local private source-cache roots.
- Source sync.
- Connector runtime.
- Live probes or approved metadata probe execution.
- Evidence ledger bridge.
- Public index or master-index bridge.

## Approvals Required Before Fixture Runtime

- Explicit fixture-only runtime task.
- Output-root and private-root review.
- Candidate-store and evidence-ledger review gates.
- Validator proving no live source access, source sync, connector execution, or
  index mutation.

## Approvals Required Before Metadata Probes

- Explicit source policy approval.
- Operator approval.
- User-Agent/contact decision.
- Rate limit, timeout, retry policy, cache TTL, and kill switch.
- Terms/robots review.
- Privacy/risk review.
- Human review before downstream evidence use.

## Must Remain Forbidden

- Google result page scraping.
- Unapproved forum scraping.
- Bulk Reddit ingestion.
- Arbitrary URL fetch.
- Credentialed access without approval.
- Captcha, paywall, or access-control bypass.
- Binary download, installer execution, uploads, accounts, telemetry.
- Accepted evidence truth, accepted public record, public index mutation, or
  master-index mutation.

## Recommended Next Task

TRACK-B-14 - Local evidence ledger runtime planning.
