# Ingest Report

## Status

`PASS_WITH_WARNINGS`

## Scope

This task ingested the compact external full-discovery artifacts for:

```text
run id: source_snapshot_baseline_closeout_01
```

External artifact paths inspected:

```text
../eureka-test-runs/source_snapshot_baseline_closeout_01/status.json
../eureka-test-runs/source_snapshot_baseline_closeout_01/full_unittest_summary.json
../eureka-test-runs/source_snapshot_baseline_closeout_01/failure_families.json
../eureka-test-runs/source_snapshot_baseline_closeout_01/failed_tests.txt
```

Raw stdout and stderr logs were not copied into the repo.

## Authority Findings

The summary is terminal and current to the checked-out `dev` `HEAD`:

```text
current HEAD: aad4517b8567aafad601bd1e8d22b40636d32433
summary HEAD: aad4517b8567aafad601bd1e8d22b40636d32433
summary branch: dev
summary working tree clean: true
```

The status is red:

```text
status: fail
exit_code: 1
tests_run: 5505
failures: 45
errors: 1
skipped: 0
```

The compact failure index contains 47 failed-test labels because the harness
includes synthetic validator-output labels in addition to unittest failure and
error counts.

## Summary

The run is valid evidence for the current branch, but it blocks public alpha,
source/snapshot release readiness, and `dev -> main` promotion.

Dominant failure categories:

| Family | Failed-test labels | Notes |
|---|---:|---|
| `queue_handoff_drift` | 39 | Stale queue, repo-health, latest-task-packet, HUNT/LOCAL/promotion expectations. |
| `architecture_boundary_drift` | 4 | Runtime/legacy leakage and repo-structure strict failures. |
| `source_snapshot_baseline_drift` | 2 | Source observation/local worker validation family. |
| `generated_artifact_drift` | 1 | Validator refuses forbidden output roots such as `site/dist`. |
| `contract_schema_drift` | 1 | TSIS validator CLI failure. |

## Warning

The run command in the handoff used the repo wrapper:

```text
python scripts/run_full_unittest_discovery.py --out ../eureka-test-runs/source_snapshot_baseline_closeout_01
```

The summary records the wrapped unittest command:

```text
python -m unittest discover -s tests -t .
```

This is acceptable because the wrapper generated the summary and the effective
test command is the approved discovery command.
