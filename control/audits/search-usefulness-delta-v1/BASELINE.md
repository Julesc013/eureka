# Baseline

Baseline label:
`search_usefulness_delta_v0_current_after_compatibility_evidence_pack_v0`

Primary baseline source:
`control/audits/search-usefulness-delta-v0/delta_report.json`

This is a committed machine-readable aggregate baseline for the Search
Usefulness Audit status counts and failure-mode counts.

## Search Usefulness Baseline

| Status | Count |
| --- | ---: |
| covered | 5 |
| partial | 5 |
| source_gap | 41 |
| capability_gap | 11 |
| unknown | 2 |

Query count: 64.

## Failure-Mode Baseline

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

## Archive Eval Baseline

The v0 delta pack did not commit archive-resolution eval counts. For archive
eval comparison, this pack uses the previously reported handoff baseline:

| Status | Count |
| --- | ---: |
| capability_gap | 5 |
| not_satisfied | 1 |

That archive baseline is historical/reported, not a committed machine-derived
per-task report. It is included only to explain the observed movement from
missing capability toward source-backed but still unsatisfied hard evals.

## Limitations

- The search-usefulness baseline is aggregate-level.
- The v0 pack does not provide a full committed per-query historical output.
- Per-query movement in this pack is inferred from current output plus
  committed expected-current-status fields and aggregate baseline movement.
- The baseline is not external baseline data.
- Google and Internet Archive baselines remain pending/manual.
