# Review Queue Runtime

## `ReviewQueueStore`

SQLite-backed store with explicit lifecycle:

- `open(path)`
- `init()`
- `close()`
- `enqueue_review_item(item)`
- `link_evidence(review_item_id, evidence_id)`
- `link_source_cache_entry(review_item_id, source_cache_entry_id)`
- `record_decision(review_item_id, decision)`
- `append_event(event)`
- `get_review_item(review_item_id)`
- `list_review_items(status=None, subject_kind=None, limit=100)`
- `list_events(review_item_id=None, limit=100)`
- `list_decisions(review_item_id=None, limit=100)`
- `summarize()`
- `check_integrity()`

## Records

`ReviewItemRecord` represents an item awaiting local review. It can be created
from an `EvidenceCandidateRecord` and optionally linked to a source-cache entry.

`ReviewDecision` records an explicit local decision. `reject`, `block`, and
`supersede` require a reason.

`ReviewEvent` records ordered event history for an item.

`ReviewQueueStatus` values are `queued`, `needs_review`, `accepted`, `rejected`,
`blocked`, `superseded`, and `needs_more_evidence`.

`ReviewQueueSummary` reports item, event, link, decision, status, and subject
counts.

## Migration API

`ReviewQueueMigration` defines deterministic migrations. The initial migration
creates the full SQLite schema and records migration history in
`review_queue_migrations`.
