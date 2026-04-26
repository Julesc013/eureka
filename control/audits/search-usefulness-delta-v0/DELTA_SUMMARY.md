# Delta Summary

## Status Delta

Baseline:
`historical_reported_baseline_before_source_planner_member_lane_compat_sequence`

Current:
`current_audit_after_compatibility_evidence_pack_v0`

| Status | Baseline | Current | Delta |
| --- | ---: | ---: | ---: |
| covered | 5 | 5 | 0 |
| partial | 1 | 5 | +4 |
| source_gap | 43 | 41 | -2 |
| capability_gap | 13 | 11 | -2 |
| unknown | 2 | 2 | 0 |

## Main Conclusion

The selected wedge improved, but the improvement is deliberately modest. The
audit now shows more evidence-backed partial answers, especially around
fixture-backed old-platform software and member-level discovery, while source
coverage remains the dominant blocker.

## What Improved

- Old-platform planner output is more structured and less generic.
- Recorded source fixtures give a few old-platform queries evidence-backed
  partial paths.
- Synthetic member records make selected inner bundle members visible.
- Result lanes and user-cost annotations explain member-vs-parent usefulness.
- Compatibility evidence is now visible where current fixture metadata, member
  paths, README text, or compatibility notes support it.

## What Did Not Change Enough

- Broad old-platform source coverage is still narrow.
- Many driver, manual, article-inside-scan, and latest-compatible release
  queries still lack source material.
- External baselines remain pending manual observations.
- Per-query historical movement cannot be proven from committed previous
  machine output.

## Bottom Line

The next implementation milestone should be:

`Old-Platform Source Coverage Expansion v0`

The reason is simple: `source_coverage_gap` remains the largest current failure
mode, and 41 of 64 current query statuses remain `source_gap`.
