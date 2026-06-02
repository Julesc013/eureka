# Review Batch Apply Decision

Review-batch apply decisions are limited to:

- `apply_limited_reviewed_metadata_record`
- `apply_limited_reviewed_source_lead`
- `not_applied`

Known needs and bounded absences are selected from existing need/absence
matrices and applied as reviewed unresolved state, not object truth.

Every non-applied candidate receives a reason and remains review-required.
