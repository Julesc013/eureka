# External Run Status

## Run

| Field | Value |
|---|---|
| Run ID | `source_snapshot_baseline_closeout_01` |
| Status | `fail` |
| Terminal | yes |
| Exit code | `1` |
| Started | `2026-06-05T03:27:35Z` |
| Finished | `2026-06-05T04:16:33Z` |
| Status updated | `2026-06-05T04:16:34Z` |
| Elapsed seconds | `2939.438` |

## Paths

| Artifact | Path |
|---|---|
| Status | `../eureka-test-runs/source_snapshot_baseline_closeout_01/status.json` |
| Summary | `../eureka-test-runs/source_snapshot_baseline_closeout_01/full_unittest_summary.json` |
| Failure families | `../eureka-test-runs/source_snapshot_baseline_closeout_01/failure_families.json` |
| Failed tests | `../eureka-test-runs/source_snapshot_baseline_closeout_01/failed_tests.txt` |
| Stdout | not copied; external only |
| Stderr | not copied; external only |

## Command

The external harness summary records:

```text
python -m unittest discover -s tests -t .
```

This command was run outside the AI session through the detached harness.
