# Baseline

Baseline label:

`historical_reported_baseline_before_source_planner_member_lane_compat_sequence`

## Source

No committed machine-derived per-query Search Usefulness Audit before snapshot
was found in the repo. This pack therefore uses a historical reported aggregate
baseline from:

- `control/audits/2026-04-25-comprehensive-test-eval-audit/CONTENT_COVERAGE_AUDIT.md`
- `control/audits/2026-04-25-comprehensive-test-eval-audit/findings.json`
- the prior milestone handoff values for Search Usefulness Audit v0

## Historical Reported Status Counts

| Status | Count |
| --- | ---: |
| covered | 5 |
| partial | 1 |
| source_gap | 43 |
| capability_gap | 13 |
| unknown | 2 |

Total query count: 64.

## Known Baseline Limitations

- The baseline is aggregate-level, not a committed per-query machine report.
- Per-query movement in this pack is therefore inferred from current output,
  current fixture evidence, and known milestone effects.
- The baseline is not external baseline data or external search observation
  data.
- The baseline does not include Google, Internet Archive metadata, or Internet
  Archive OCR/full-text observations.
- The baseline should be replaced by recurring machine-derived reports once
  future delta packs commit previous `--json` summaries.

## Baseline Interpretation

The historical baseline is still useful because it captures the shape of the
pre-sequence audit: covered sanity checks were stable, partial answers were
rare, and source/capability gaps dominated the suite.
