# Review Boundary Validation

Task ID: `HUMAN-REVIEW-BATCH-00`

## Preserved

```text
manual observations were not treated as reviewed truth by themselves
source observations did not self-promote
candidates did not self-promote
fallback summaries did not self-promote
synthetic eval fixtures were not treated as evidence
AI/model output was not treated as truth
reviewed/master/public indexes were not mutated
```

## Promoted Records

Only `promote` decisions with source references, rationale,
`local_only_confirmed=true`, and review event IDs created reviewed seed records.

Non-promote decisions remain need or near_miss states.
