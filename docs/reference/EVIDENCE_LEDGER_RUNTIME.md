# Evidence Ledger Runtime

## EvidenceLedgerStore

SQLite-backed store opened with an explicit path or `:memory:`.

Public methods:

- `open(path)`
- `init()`
- `close()`
- `write_evidence_candidate(candidate)`
- `append_event(event)`
- `link_source_cache_entry(evidence_id, source_cache_entry_id)`
- `record_conflict(conflict)`
- `set_review_status(evidence_id, status, reason=None)`
- `get_evidence_candidate(evidence_id)`
- `list_evidence_candidates(source_id=None, status=None, claim_kind=None, limit=100)`
- `list_events(evidence_id=None, limit=100)`
- `list_conflicts(evidence_id=None, limit=100)`
- `summarize()`
- `check_integrity()`

## Records

`EvidenceCandidateRecord` stores claim candidates with source, observation, normalized observation, optional source-cache entry, claim kind, claim subject, claim payload, status, limitations, warnings, and timestamps.

`EvidenceEvent` stores append-only event history.

`EvidenceConflict` stores conflict candidates for later review.

`EvidenceReviewStatus` values:

- `candidate`
- `needs_review`
- `accepted`
- `rejected`
- `blocked`
- `superseded`

`EvidenceLedgerSummary` reports candidate, event, link, conflict, review status, status, and claim-kind counts.

## Migrations

`EvidenceLedgerMigration` records deterministic schema setup for `evidence_ledger_store.v0`.

Initialization is idempotent and records migration checksums.
