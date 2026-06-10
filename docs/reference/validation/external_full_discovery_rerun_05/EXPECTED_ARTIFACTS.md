# Expected Artifacts

Return compact artifacts only:

- `../eureka-test-runs/source_snapshot_full_discovery_rerun_05/status.json`
- `../eureka-test-runs/source_snapshot_full_discovery_rerun_05/full_unittest_summary.json`
- `../eureka-test-runs/source_snapshot_full_discovery_rerun_05/failure_families.json`
- `../eureka-test-runs/source_snapshot_full_discovery_rerun_05/failed_tests.txt`
- `git status --short --branch`
- `git rev-parse HEAD`

Do not paste:

- `full_unittest_stdout.txt`
- `full_unittest_stderr.txt`
- raw traceback logs unless a compact failure summary is insufficient

Do not commit:

- `.aide.local/**`
- `../eureka-test-runs/**`
- raw external run logs

The returned summary must be terminal and must match the operator checkout used
for the run.
