# REVIEW-LEDGER-00

Goal: ensure review events are the only promotion path into reviewed truth.

Inputs to read first: `architecture/REVIEW_LEDGER_SPEC.md`, `contracts/review/**`,
`contracts/stores/review_event.v0.json`, `runtime/review/**`.

Allowed paths: review contracts/runtime/tests/docs/control evidence.

Protected paths: source adapters, public deployment, unrelated surfaces.

Deliverables: review event audit, promotion/rejection invariants, tests.

Non-goals: public mutation, automatic promotion, AI truth.

Validation: review queue, review batch, promotion preview, index rebuild tests.

Exit criteria: every reviewed record has review evidence and audit trail.

Impact statement: review/runtime/contract impact as applicable.

