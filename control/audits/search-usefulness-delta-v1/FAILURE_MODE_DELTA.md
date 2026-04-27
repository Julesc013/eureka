# Failure Mode Delta

Failure-mode counts compare the v0 delta current report with the current v1
audit output.

| Failure mode | Baseline | Current | Change |
| --- | ---: | ---: | ---: |
| source_coverage_gap | 49 | 49 | 0 |
| compatibility_evidence_gap | 25 | 25 | 0 |
| planner_gap | 24 | 24 | 0 |
| query_interpretation_gap | 21 | 21 | 0 |
| representation_gap | 14 | 14 | 0 |
| decomposition_gap | 12 | 12 | 0 |
| member_access_gap | 12 | 12 | 0 |
| identity_cluster_gap | 12 | 14 | +2 |
| live_source_gap | 10 | 10 | 0 |
| ranking_gap | 4 | 8 | +4 |
| surface_ux_gap | 4 | 4 | 0 |
| index_gap | 3 | 3 | 0 |
| absence_reasoning_gap | 2 | 2 | 0 |
| actionability_gap | 2 | 2 | 0 |
| external_baseline_pending | 64 | 64 | 0 |

## Interpretation

Failure-mode labels did not fall the way status counts did because many newly
partial queries still carry future-work labels. For example, a query can now
have source-backed partial results while still needing compatibility evidence,
identity clustering, result-lane refinement, or member-access improvements.

The dominant remaining blocker is still `source_coverage_gap`, but the hard
eval delta shows a new near-term bottleneck: source-backed candidates exist for
five hard tasks and are still `not_satisfied`.

External baselines remain pending/manual for all 64 queries.
