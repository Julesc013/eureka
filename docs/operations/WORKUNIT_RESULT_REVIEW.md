# WorkUnit Result Review

WorkUnit results are review envelopes. They can help a human or future review
system decide whether a proposed output should become a source lead,
SearchNeed seed, WorkUnit seed, candidate draft, evidence draft, or pack draft.

## Review Gates

Result envelopes preserve human, source-policy, evidence, candidate, pack,
master-index, rights, risk, privacy, operator-network, operator-hosted, and
legal/rights gates.

Outputs that propose candidates, evidence, source leads, packs, or review items
must require review. Approval of a result envelope does not itself create
accepted public truth.

## Noop, Resume, And Quarantine

- Noop: a repeated or already-complete WorkUnit validated without changes.
- Resume: partial work remains and can be resumed from missing acceptance.
- Quarantine: conflicting output must be isolated for review.
- Blocked: required policy, operator, legal, privacy, rights, or source
  decisions are absent.

## No-Goals

Do not use WorkUnit results to perform observations, fetch sources, run
WorkUnits, create local state, call providers, create review runtime, import
packs, claim rights or safety status, or mutate the master-index.
