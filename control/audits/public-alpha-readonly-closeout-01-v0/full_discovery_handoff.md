# Full Discovery Handoff

Run this outside the AI session from the repository root:

```powershell
python scripts/run_full_unittest_discovery.py --out ../eureka-test-runs/public_alpha_readonly_closeout
```

Paste back only:

```text
../eureka-test-runs/public_alpha_readonly_closeout/full_unittest_summary.json
../eureka-test-runs/public_alpha_readonly_closeout/failure_families.json
../eureka-test-runs/public_alpha_readonly_closeout/failed_tests.txt
git status --short --branch
```

Do not paste raw stdout/stderr unless the compact summary is insufficient.
