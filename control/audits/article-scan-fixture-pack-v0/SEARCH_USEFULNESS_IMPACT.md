# Search Usefulness Impact

Baseline after More Source Coverage Expansion v1:

- `covered=5`
- `partial=21`
- `source_gap=27`
- `capability_gap=9`
- `unknown=2`

Current live audit output:

- `covered=5`
- `partial=22`
- `source_gap=26`
- `capability_gap=9`
- `unknown=2`

Delta:

- `partial +1`
- `source_gap -1`
- no change to `covered`, `capability_gap`, or `unknown`

The movement is attributable to the bounded article-scan fixture, especially
the `PC Magazine July 1994 ray tracing` search-usefulness query. External
baselines remain pending manual observation for all 64 queries.

