# Local Source Cache Approval Gates

B-13 keeps local source cache work behind explicit gates. These gates are
required because source-cache records can look useful while still being only
observations, not evidence truth.

## Current Gates

Current phase:

- `phase_0_planning_only`
- `runtime_not_implemented`
- `source_access_disabled`

Current allowed source access is limited to committed fixtures, repo-local
records, manual human descriptions, and no autonomous access.

## Before Fixture Runtime

A future fixture-only runtime task needs:

- accepted B-13 planning artifacts
- explicit allowed input roots
- explicit output roots
- review before candidate store use
- review before evidence ledger bridge
- rollback/deletion posture for any future private root
- validator proving no live source access, no source sync, and no index mutation

## Before Metadata Probes

A future metadata probe task needs:

- explicit source policy approval
- operator approval
- User-Agent/contact decision
- rate limit
- timeout
- retry policy
- cache TTL
- kill switch
- terms/robots review
- privacy/risk review
- human review before downstream evidence use

Without those gates, metadata probes remain disabled.

## Always Forbidden Now

- live probes
- source sync
- connector runtime
- Google result page scraping
- unapproved forum scraping
- bulk Reddit ingestion
- arbitrary URL fetch
- credentialed access without approval
- captcha, paywall, or access-control bypass
- binary download
- installer execution
- evidence acceptance
- public index use
- master-index mutation

## Review Outcomes

Allowed review decisions may approve a future fixture-only task, approve a
future metadata probe, approve a future static dump, approve a future evidence
bridge, request changes, reject, defer, or block for policy/rights/risk.

Forbidden review outcomes include automatic evidence acceptance, automatic
public index use, automatic connector enablement, automatic live probe
enablement, automatic source sync, and automatic master-index mutation.
