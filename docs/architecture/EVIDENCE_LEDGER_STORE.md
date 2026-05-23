# Evidence Ledger Store

`runtime/evidence/ledger` is the durable local claim and event store created for R0-06.

The ledger records evidence candidates, event history, source-cache links, conflict candidates, review status, limitations, and warnings. It does not decide whether a claim is true, accepted, safe, rights-cleared, or eligible for a public index.

## Role

The evidence ledger sits after `runtime/source/observation` and `runtime/source/cache`:

1. a source observation is normalized,
2. an evidence candidate is built,
3. the source observation can be cached in `runtime/source/cache`,
4. the evidence candidate is persisted in `runtime/evidence/ledger`,
5. future review-queue work can turn ledger records into reviewable queue items.

The ledger is not the source cache. Source cache stores observations and normalized source material. Evidence ledger stores claim candidates and event history derived from those observations.

The ledger is not the review queue. It can hold a review status value, but it does not create a review workflow, assign reviewers, or approve claims.

The ledger is not the public index. It never writes public records, search results, or master index state.

## SQLite Tables

- `evidence_ledger_meta`
- `evidence_ledger_migrations`
- `evidence_candidates`
- `evidence_events`
- `evidence_source_cache_links`
- `evidence_conflicts`
- `evidence_review_status`

## Event Model

`evidence_events` is append-only. Store operations append events for candidate creation, source-cache linking, conflict recording, notes, and explicit status changes. Event ordering is preserved with the table sequence.

## Conflict Model

Conflicts are stored as candidates for review. A conflict row records the evidence item, optional conflicting evidence item, conflict kind, payload, status, limitations, and warnings.

## Migration Model

Migrations are deterministic and idempotent. Re-running initialization records no duplicate migration and does not delete data.

## Boundaries

- no live source calls
- no network or provider calls
- no hidden local state root
- no connector rewrite
- no review queue write
- no public or master index mutation
- no automatic evidence acceptance

R0-07 is expected to build the review queue seam that consumes these records.
