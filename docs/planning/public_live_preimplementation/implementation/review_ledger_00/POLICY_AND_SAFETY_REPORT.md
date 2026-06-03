# Policy And Safety Report

## Truth Boundary

The review ledger is now the explicit boundary between fallback/candidate/need input and reviewed decision state.

The implementation preserves:

- candidate cannot self-promote
- fallback summary cannot self-promote
- source observation cannot self-promote
- public projection cannot promote
- review event is required for promotion

## Mutation Boundary

Review-ledger decisions report:

- `reviewed_record_created: false`
- `reviewed_index_mutated: false`
- `public_index_mutated: false`
- `master_index_mutated: false`

Reviewed/public index projection still requires a separate rebuild operation.

## Audit Boundary

Each ledger decision writes:

- a durable review decision
- a durable review event with decision context and citations

Reject, supersede, policy-blocked, and request-more-evidence decisions require a rationale where appropriate.

## Public Surface

No public route or public UI action was added. Existing public run projection remains read-only and does not expose `review_candidate`, `promote`, `reject`, or `rebuild_index`.
