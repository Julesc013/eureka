# External Full Discovery Handoff

Run this outside the AI session from the repo root:

```powershell
python scripts/run_full_unittest_discovery.py --out ../eureka-test-runs/source_snapshot_baseline_closeout_01
```

Return these compact artifacts:

- `../eureka-test-runs/source_snapshot_baseline_closeout_01/full_unittest_summary.json`
- `../eureka-test-runs/source_snapshot_baseline_closeout_01/failure_families.json`
- `../eureka-test-runs/source_snapshot_baseline_closeout_01/failed_tests.txt`
- `git status --short --branch`

Do not paste raw stdout or stderr. Do not commit `.aide.local/**` or raw
external run logs.

The returned summary must match the operator's current checkout:

- branch: `dev`
- head: the output of `git rev-parse HEAD` at run time
- working tree clean: `true`

The batch 02 base observed by this closeout was
`3868150d89830256655a8c7d8ff3b1b7f3bebd82`, but the docs-only closeout commit
will naturally advance `HEAD`.
