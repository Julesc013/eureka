# INDEXLESS-LIVE-SEARCH-FALLBACK-00

This package records the implementation of the first governed indexless live search fallback slice.

The fallback attaches to `runtime/engine/resolution_runs/service.py` through `LocalResolutionRunService._run_search`, as selected by the preflight decision. It keeps local reviewed lookup first, records fallback output on the resolution run, and lets gateway code project that run state without owning source calls.

This task does not create reviewed records, promote candidates, add downloads, add Wayback replay, rewrite canon, mutate queue state, or add new top-level roots.

Read:

- `IMPLEMENTATION_REPORT.md`
- `BEHAVIOR_SUMMARY.md`
- `POLICY_AND_SAFETY_REPORT.md`
- `TEST_REPORT.md`
- `VALIDATION_REPORT.md`
- `NEXT_TASK_HANDOFF.md`

Next recommended task: `REVIEW-LEDGER-00`.
