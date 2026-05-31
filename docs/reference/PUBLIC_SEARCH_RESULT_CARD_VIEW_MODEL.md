# Public Search Result Card View Model

Each result card records:

- title
- url
- status
- object type
- domain
- source family and label
- snippet
- match reasons
- evidence summary
- confidence, risk, rights, and compatibility labels
- action posture
- review-required flag
- accepted-truth flag
- limitations

The status field is one of:

```text
verified
candidate
near_miss
known_need
absence
source_lead
```

Only verified cards may be accepted truth. Candidate, near-miss, known-need,
absence, and source-lead cards remain review-required and must be visually and
semantically distinct from verified results.
