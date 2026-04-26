# Current Results

Current results were captured from:

```bash
python scripts/run_search_usefulness_audit.py --json
```

The committed summary normalizes the current run date as
`current_run_normalized_2026-04-27` so this pack does not depend on volatile
local timestamps.

## Current Status Counts

| Status | Count |
| --- | ---: |
| covered | 5 |
| partial | 5 |
| source_gap | 41 |
| capability_gap | 11 |
| unknown | 2 |

Total query count: 64.

## External Baseline Status

| Baseline | Pending manual observations |
| --- | ---: |
| Google | 64 |
| Internet Archive metadata | 64 |
| Internet Archive full text/OCR | 64 |

No external baseline observations are recorded by this audit pack.

## Current Failure-Mode Counts

| Failure mode | Count |
| --- | ---: |
| source_coverage_gap | 49 |
| compatibility_evidence_gap | 25 |
| planner_gap | 24 |
| query_interpretation_gap | 21 |
| representation_gap | 14 |
| decomposition_gap | 12 |
| member_access_gap | 12 |
| identity_cluster_gap | 12 |
| live_source_gap | 10 |
| ranking_gap | 4 |
| surface_ux_gap | 4 |
| index_gap | 3 |
| absence_reasoning_gap | 2 |
| actionability_gap | 2 |
| external_baseline_pending | 64 |

## Current Interpretation

The recent usefulness sequence produced a small but measurable movement:
partial results increased, source gaps decreased, and capability gaps
decreased. Source coverage is still the dominant blocker, followed by
compatibility evidence, planner/query interpretation, representation,
decomposition, and member access gaps.
