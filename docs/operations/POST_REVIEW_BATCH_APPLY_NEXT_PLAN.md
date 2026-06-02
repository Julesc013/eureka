# Post Review Batch Apply Next Plan

Recommended next task:

```text
SNAPSHOT-REFRESH-06 - Refresh snapshots after review batch apply
```

Rationale:

- Review-batch apply grows limited reviewed records through a temp proof.
- Snapshot refresh is required before public alpha reassessment can see the new
  projection.
- Public launch remains deferred.
- Indexless fallback remains queued as the next resilience track after the
  review/apply/snapshot/reassess loop advances.

Planned after:

- `PUBLIC-ALPHA-REASSESS-06`
- `INDEXLESS-LIVE-SEARCH-FALLBACK-00`
- `SEARCH-USEFULNESS-EVAL-00`
- `DEV-TO-MAIN-PROMOTION-REVIEW-06`
