# Status Delta

The status delta compares the committed P32 baseline counts with the current audit output.

| Status | Baseline | Current | Delta |
| --- | ---: | ---: | ---: |
| covered | 5 | 5 | 0 |
| partial | 22 | 40 | +18 |
| source_gap | 26 | 10 | -16 |
| capability_gap | 9 | 7 | -2 |
| unknown | 2 | 2 | 0 |

Interpretation:

- The expansion mostly moved selected rows into `partial`, not `covered`.
- No row is claimed as ready for hosted production use or globally useful.
- The source-gap reduction is fixture-backed and local-index-only.
- The capability-gap reduction indicates better bounded evidence visibility, not new runtime capabilities.
