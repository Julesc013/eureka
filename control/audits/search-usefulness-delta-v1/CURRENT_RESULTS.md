# Current Results

Current command sources:

```bash
python scripts/run_search_usefulness_audit.py --json
python scripts/run_archive_resolution_evals.py --json
```

Normalized run date: 2026-04-27.

## Search Usefulness Audit

| Status | Count |
| --- | ---: |
| covered | 5 |
| partial | 20 |
| source_gap | 28 |
| capability_gap | 9 |
| unknown | 2 |

Query count: 64.

External baseline pending counts:

| Baseline | Count |
| --- | ---: |
| google | 64 |
| internet_archive_metadata | 64 |
| internet_archive_full_text | 64 |

## Failure Modes

| Failure mode | Count |
| --- | ---: |
| source_coverage_gap | 49 |
| compatibility_evidence_gap | 25 |
| planner_gap | 24 |
| query_interpretation_gap | 21 |
| representation_gap | 14 |
| identity_cluster_gap | 14 |
| decomposition_gap | 12 |
| member_access_gap | 12 |
| live_source_gap | 10 |
| ranking_gap | 8 |
| surface_ux_gap | 4 |
| index_gap | 3 |
| absence_reasoning_gap | 2 |
| actionability_gap | 2 |
| external_baseline_pending | 64 |

Failure-mode counts are label occurrences. A query moving to `partial` can
still carry source, compatibility, identity, ranking, or member-access labels
because the result is useful but not fully satisfying.

## Archive Resolution Evals

| Status | Count |
| --- | ---: |
| capability_gap | 1 |
| not_satisfied | 5 |

Current task outcomes:

| Task | Status | Local results |
| --- | --- | ---: |
| `article_inside_magazine_scan` | capability_gap | 0 |
| `driver_inside_support_cd` | not_satisfied | 28 |
| `latest_firefox_before_xp_drop` | not_satisfied | 16 |
| `old_blue_ftp_client_xp` | not_satisfied | 3 |
| `win98_registry_repair` | not_satisfied | 8 |
| `windows_7_apps` | not_satisfied | 11 |

`not_satisfied` is not success. It means the runner found source-backed local
results but the exact hard expected-result checks still failed.
