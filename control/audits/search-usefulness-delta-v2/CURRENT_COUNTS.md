# Current Counts

Current command:

```text
python scripts/run_search_usefulness_audit.py --json
```

Current counts after Source Expansion v2:

| Status | Count |
| --- | ---: |
| covered | 5 |
| partial | 40 |
| source_gap | 10 |
| capability_gap | 7 |
| unknown | 2 |

Total query count: 64

Current top failure modes:

| Failure mode | Count |
| --- | ---: |
| external_baseline_pending | 64 |
| source_coverage_gap | 49 |
| compatibility_evidence_gap | 25 |
| planner_gap | 24 |
| query_interpretation_gap | 21 |
| identity_cluster_gap | 14 |
| representation_gap | 14 |
| decomposition_gap | 12 |
| member_access_gap | 12 |
| live_source_gap | 10 |
| ranking_gap | 9 |
| surface_ux_gap | 4 |

External baseline pending counts remain:

- Google web search: 64
- Internet Archive metadata search: 64
- Internet Archive full-text/OCR search: 64

