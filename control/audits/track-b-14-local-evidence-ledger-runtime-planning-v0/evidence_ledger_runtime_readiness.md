# Evidence Ledger Runtime Readiness

## Current Runtime Status

- Current phase: `phase_0_planning_only`
- Runtime status: `runtime_not_implemented`
- Source-cache bridge status: `source_cache_bridge_not_implemented`
- Evidence acceptance status: `evidence_acceptance_disabled`
- Local evidence-ledger state: not created

## Ready

- Planning inventory exists.
- Runtime, path, record, review, append, bridge, and rollout policies are
  defined.
- Append-style intent is explicit without append storage.
- Source-cache-to-evidence bridge phases and forbidden conversions are explicit.
- Public-safe examples exercise minimal, fixture-only, bridge, and blocked
  plans.
- Validator checks planning-only status, bridge-disabled status, review gates,
  append policy, truth/product boundaries, forbidden conversions, private paths,
  and credential patterns.

## Not Implemented

- Local evidence-ledger runtime.
- Source-cache-to-evidence bridge runtime.
- Authoritative evidence-ledger storage.
- Local private evidence-ledger roots.
- Evidence record writes.
- Evidence acceptance.
- Candidate promotion.
- Evidence pack export runtime.
- Review queue integration.
- Public index or master-index bridge.

## Approvals Required Before Fixture Runtime

- Explicit fixture-only evidence ledger runtime task.
- Output-root and private-root review.
- Append/correction/supersession policy review.
- Candidate-store and pack-export review gates.
- Validator proving no source-cache bridge runtime, evidence acceptance, public
  index use, or master-index mutation.

## Approvals Required Before Source-Cache Bridge Runtime

- Reviewed source-cache fixture or record inputs.
- Source-cache-to-evidence bridge plan acceptance.
- Review before bridge.
- Conflict preservation and provenance requirements.
- No truth conversion and no master-index mutation.

## Approvals Required Before Evidence Candidate Export

- Privacy/risk review.
- Rights/risk review.
- Review status records.
- Evidence pack export review.
- Public-safe or local-private labeling.
- No automatic public index use or master-index mutation.

## Must Remain Forbidden

- Evidence ledger runtime and source-cache bridge runtime in this task.
- Evidence record writes or evidence acceptance.
- Live probes, source sync, connectors, scraping, crawling, arbitrary URL fetch.
- Network/API/model/provider calls.
- Binary downloads, installer execution, uploads, accounts, telemetry.
- Rights-clearance, malware-safety, verified-installability, exhaustive-search,
  or production-readiness claims.
- Accepted public record creation or master-index mutation.

## Recommended Next Task

TRACK-B-15 - Local source cache runtime.
