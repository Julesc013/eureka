# Local Review Queue Model

The Local Review Queue sits after candidate, source cache, evidence ledger, and source-cache-to-evidence bridge records. It gathers review intent without promoting anything.

## Position

Inputs flow into the queue as review subjects:

- candidate records
- source cache records
- evidence ledger candidates
- bridge results
- WorkUnit results
- node policy evaluations
- SearchNeeds and observation candidates

The output is a review entry or snapshot. It can prepare a later promotion dry-run, but it cannot accept truth or mutate an index.

## Entry Model

Each entry has a subject, status, decision, rationale, required evidence, missing evidence, duplicate/conflict summaries, policy summary, promotion readiness, related refs, review gates, limitations, truth boundary, and product boundary.

The `promotion_readiness.ready_for_promotion_dry_run` flag is true only when the decision is `approve_for_promotion_dry_run`. Its companion flags keep public acceptance, evidence acceptance, candidate acceptance, public index mutation, and master-index mutation false.

## Snapshot Model

A snapshot summarizes entry counts by status, subject type, and decision. It also records blocked, rejected, missing-evidence, and promotion-dry-run-ready counts. The snapshot is not a public queue, hosted moderation state, evidence database, or master index.

## No-Goals

No hosted moderation, candidate promotion, evidence acceptance, public truth acceptance, source access, live probing, accounts, telemetry, downloads, uploads, or master-index mutation are implemented.
