# Failure-Mode Delta

## Baseline Availability

The repo has historical reported aggregate status counts, but it does not have
a committed machine-derived historical failure-mode snapshot for every label.
For that reason, current failure-mode counts are reported exactly and prior
counts are marked unavailable unless a historical aggregate status maps
directly.

## Current Failure-Mode Counts

| Failure mode | Current count | Historical comparison |
| --- | ---: | --- |
| source_coverage_gap | 49 | No comparable machine count; historical `source_gap` status was 43. |
| planner_gap | 24 | No comparable machine count. |
| query_interpretation_gap | 21 | No comparable machine count. |
| compatibility_evidence_gap | 25 | No comparable machine count. |
| representation_gap | 14 | No comparable machine count. |
| decomposition_gap | 12 | No comparable machine count. |
| member_access_gap | 12 | No comparable machine count. |
| actionability_gap | 2 | No comparable machine count. |
| external_baseline_pending | 64 | External baselines remain pending/manual for all queries. |
| identity_cluster_gap | 12 | No comparable machine count. |
| live_source_gap | 10 | No comparable machine count. |
| ranking_gap | 4 | No comparable machine count. |
| surface_ux_gap | 4 | No comparable machine count. |
| index_gap | 3 | No comparable machine count. |
| absence_reasoning_gap | 2 | No comparable machine count. |

## Directly Comparable Aggregate Movement

| Aggregate | Baseline | Current | Delta |
| --- | ---: | ---: | ---: |
| source_gap status | 43 | 41 | -2 |
| capability_gap status | 13 | 11 | -2 |
| partial status | 1 | 5 | +4 |

## Interpretation

Source coverage remains the dominant usefulness failure. The recent sequence
reduced some capability/source statuses and made planner, member, lane, and
compatibility detail visible, but it did not provide enough old-platform source
material to change the suite shape dramatically.

Future failure-mode deltas should be machine-derived from committed reports
instead of inferred from aggregate historical notes.
