# Post Driver Support Seed Batch Plan

The next recommended task is:

```text
SNAPSHOT-REFRESH-04 - Refresh snapshots after manuals/scans and driver/support batches
```

Rationale:

- Manuals/scans and driver/support now add third-domain and high-risk support
  media discovery coverage.
- The new driver/support candidates are review-only and metadata-only.
- Snapshot refresh is the next boundary for packaging these candidates without
  accepting truth or mutating public/master/reviewed indexes.
- Public alpha reassessment should follow only after the snapshot layer reflects
  the new seed batches.
