# Workbench Review Flow

```text
EvidenceCandidate or SearchNeed
-> operator inspection
-> evidence/rationale check
-> review decision
-> ReviewEvent
-> ReviewedRecord or rejected/superseded/need state
-> index rebuild if needed
-> public-safe projection
```

Review decisions:

- promote
- reject
- supersede
- mark_near_miss
- mark_need
- mark_policy_blocked
- request_more_evidence

No review action may skip the review ledger.

