# Expected Artifacts

Return the compact artifacts first:

```text
../eureka-test-runs/source_foundry_preview_v0_post_historical_repair_02/full_unittest_summary.json
../eureka-test-runs/source_foundry_preview_v0_post_historical_repair_02/failed_tests.txt
../eureka-test-runs/source_foundry_preview_v0_post_historical_repair_02/failure_families.json
```

Raw stdout/stderr may remain in the external run directory unless a later ingest
task asks for targeted excerpts:

```text
../eureka-test-runs/source_foundry_preview_v0_post_historical_repair_02/full_unittest_stdout.txt
../eureka-test-runs/source_foundry_preview_v0_post_historical_repair_02/full_unittest_stderr.txt
```

Green criteria:

```text
failures: 0
errors: 0
exit_code: 0
```
