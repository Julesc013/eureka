# Baseline

The baseline counts come from the committed Source Expansion v2 report:

```text
control/audits/search-usefulness-source-expansion-v2/source_expansion_v2_report.json
```

Baseline source type: `machine_derived_from_committed_p32_report`

Baseline counts before Source Expansion v2:

| Status | Count |
| --- | ---: |
| covered | 5 |
| partial | 22 |
| source_gap | 26 |
| capability_gap | 9 |
| unknown | 2 |

Limitations:

- The global status-count baseline is machine-readable and committed.
- Exact per-query baseline rows are not available as a standalone before-run JSON artifact.
- Query movement in this pack uses P32 selected targets plus current audit expected-status fields and is marked with that provenance.
- Exact before/after failure-mode counts are unavailable; this pack records current failure-mode counts and does not fabricate deltas.

