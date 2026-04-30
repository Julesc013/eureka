# Failure-Mode Delta

Exact P32-before failure-mode counts are unavailable as a committed machine-readable artifact. This audit therefore records current failure-mode counts and marks exact deltas as unavailable rather than inventing them.

Current failure modes:

| Failure mode | Current count | Delta |
| --- | ---: | --- |
| external_baseline_pending | 64 | unavailable |
| source_coverage_gap | 49 | unavailable |
| compatibility_evidence_gap | 25 | unavailable |
| planner_gap | 24 | unavailable |
| query_interpretation_gap | 21 | unavailable |
| identity_cluster_gap | 14 | unavailable |
| representation_gap | 14 | unavailable |
| decomposition_gap | 12 | unavailable |
| member_access_gap | 12 | unavailable |
| live_source_gap | 10 | unavailable |
| ranking_gap | 9 | unavailable |
| surface_ux_gap | 4 | unavailable |
| absence_reasoning_gap | 2 | unavailable |
| actionability_gap | 2 | unavailable |
| index_gap | 2 | unavailable |

What improved:

- More fixture-backed source families are now visible to selected queries.
- Several old-platform, manual/document, archive-page, and source-code/package rows now have enough local evidence to be partial.

What became more visible:

- Source coverage remains the largest current failure mode.
- Compatibility, planner/query interpretation, representation, member access, and identity clustering now stand out as next bounded improvements.

