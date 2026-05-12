# Review Queue Store

`runtime/review_queue` is the durable local review queue for Eureka's recovery runtime.
It records review items, review links, explicit local decisions, and append-only
review events in SQLite.

The review queue is not the evidence ledger. Evidence candidates and evidence
events live in `runtime/evidence_ledger`; the review queue links to those records
when an operator-facing item needs a local decision.

The review queue is not the public index. Recording `accept`, `reject`, `block`,
`supersede`, `request_more_evidence`, or `note_only` changes only local review
state. It does not write public or master index data.

## Schema

The SQLite store contains:

- `review_queue_meta`
- `review_queue_migrations`
- `review_items`
- `review_events`
- `review_evidence_links`
- `review_source_cache_links`
- `review_decisions`

`review_events` is append-only. Decisions are stored separately in
`review_decisions` and mirrored by review events so history can be inspected in
order.

## Runtime Relationships

`runtime/source_observation` creates source observations and evidence candidates.
`runtime/source_cache` persists source observations and normalized observations.
`runtime/evidence_ledger` persists evidence candidate records and event history.
`runtime/review_queue` enqueues those candidate records for explicit review.

R0-08 may consume accepted local review items to build a reviewed public index
candidate, but that is deliberately outside R0-07.

## Boundaries

- Standard library only.
- Explicit SQLite path or `:memory:` only.
- No hidden default local state root.
- No live source calls.
- No connector registry writes.
- No public or master index mutation.
- No task-shaped runtime naming.
