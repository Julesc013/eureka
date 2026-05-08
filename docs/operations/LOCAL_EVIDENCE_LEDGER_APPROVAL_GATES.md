# Local Evidence Ledger Approval Gates

B-14 keeps evidence ledger work behind explicit gates. Evidence candidates can
look persuasive, so the plan preserves review, provenance, and conflict
boundaries before any runtime exists.

## Current Gates

Current phase:

- `phase_0_planning_only`
- `runtime_not_implemented`
- `source_cache_bridge_not_implemented`
- `evidence_acceptance_disabled`

Current outputs are planning inventories, examples, docs, and validation
evidence only.

## Before Fixture Runtime

A future fixture-only runtime task needs:

- accepted B-14 planning artifacts
- explicit allowed input roots
- explicit output roots
- private-root review
- append/correction/supersession policy
- review before candidate store use
- review before pack export
- validator proving no source-cache bridge runtime, evidence acceptance, public
  index use, or master-index mutation

## Before Source-Cache Bridge Runtime

A future source-cache bridge task needs:

- reviewed source-cache records or fixtures
- source-cache-to-evidence bridge plan accepted
- review before bridge
- conflict preservation
- provenance and source locator requirements
- no truth conversion
- no evidence acceptance
- no master-index mutation

## Before Evidence Candidate Export

A future export task needs:

- privacy/risk review
- rights/risk review
- review status records
- evidence pack export review
- public-safe or local-private labeling
- no automatic public index use
- no automatic master-index mutation

## Always Forbidden Now

- evidence ledger runtime
- source-cache-to-evidence bridge runtime
- local evidence-ledger state creation
- evidence record writes
- evidence acceptance
- source cache runtime
- source sync
- connector runtime
- live probes
- scraping, crawling, arbitrary URL fetch
- network/API/model/provider calls
- binary download, installer execution, uploads, accounts, telemetry
- accepted public record creation
- master-index mutation

## Review Outcomes

Allowed review decisions may approve a future fixture-only runtime, source-cache
bridge, evidence candidate runtime, pack export, review queue integration,
request changes, reject, defer, block for policy/rights/risk, or preserve a
conflict.

Forbidden review outcomes include automatic evidence acceptance, automatic
public index use, automatic master-index mutation, automatic rights clearance,
automatic malware-safety claims, automatic installability verification, and
truth conversion without review.
