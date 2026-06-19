# E2E Reference State Transitions

## State Machines

ResolutionRun:

```text
created -> planned -> running -> paused -> running -> completed
created -> planned -> running -> failed
created -> planned -> cancelled
completed -> replayed
```

WorkUnit:

```text
queued -> leased/running -> succeeded
queued -> leased/running -> failed -> retryable -> queued
queued -> blocked
queued -> cancelled
```

Candidate:

```text
provisional -> pending_review -> near_miss
provisional -> pending_review -> need
provisional -> pending_review -> policy_blocked
provisional -> pending_review -> rejected
provisional -> pending_review -> superseded
pending_review -> promotion_eligible
```

ReviewItem:

```text
pending -> decided
pending -> superseded
pending -> blocked
```

ReviewDecision:

```text
recorded -> superseded_or_amended
recorded -> current_valid
```

ReviewedRecord:

```text
materialized -> active
active -> superseded
active -> withdrawn
active -> invalidated_or_re_review_required
```

PreviewRecord derives status from its source object and does not create its own
truth lifecycle.

## Forbidden Transitions

- SourceObservation -> ReviewedRecord directly
- EvidenceSummary -> ReviewedRecord directly
- Candidate -> ReviewedRecord without explicit ReviewDecision and materialization
- PreviewRecord -> ReviewedRecord
- synthetic object -> production reviewed record
- public projection -> master/store authority
- rejected candidate -> promoted candidate without a new explicit review path
- stale or superseded ReviewDecision -> materialization without current validity

