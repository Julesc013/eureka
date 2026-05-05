# Comparison Readiness Decision

Decision: `comparison_not_eligible`

Rationale:

- Valid observed records: 0
- Pending records: 39
- Invalid records: 0
- External baseline comparison runner eligibility: `no_observations`

Rules applied:

- If valid observations are 0, comparison is not eligible.
- If valid observations are greater than 0 but pending slots remain, comparison is partial only.
- If all batch records are valid observed records, comparison may be ready.
- If invalid records exist, comparison is blocked unless a comparison runner explicitly and safely ignores invalid records.

Batch 0 needs human manual observation before the external baseline comparison can make scoped comparison records.

