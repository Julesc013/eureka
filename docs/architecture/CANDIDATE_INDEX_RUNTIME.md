# Candidate Index Runtime

`CANDIDATE-INDEX-RUNTIME-00` adds local candidate memory for source-action
results. It sits after query planning and source observations, and before any
review or snapshot refresh.

Flow:

```text
QueryPlan -> SourceAction -> CandidateRecord -> CandidateFingerprint
-> CandidateIndex -> CandidateLane -> ReviewHandoff
```

Candidates are not truth. The candidate index is not the reviewed index. Public
views may show read-only candidate summaries, but public users cannot mutate
candidate state, accept candidates, reject candidates, promote records, download
payloads, run extraction, or trigger model/provider calls.

Persistence is explicit. The default CLI path emits dry-run write plans and the
runtime can apply those plans only to a caller-provided temp store. Operator
local persistence is a planned gate, not a default side effect.
