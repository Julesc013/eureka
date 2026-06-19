# Targeted Validation Matrix

| Group | Command | Result | Classification | Next action |
| --- | --- | --- | --- | --- |
| runtime leakage | `python scripts/validate_runtime_architecture_leakage.py --json` | fail / invalid | `genuine_product_regression` | create separate runtime leakage repair task |
| runtime leakage | `python -m unittest tests.operations.test_legacy_runtime_leakage_remediation tests.operations.test_runtime_architecture_leakage -v` | fail, 29 tests, 2 failures | `genuine_product_regression` | create separate runtime leakage repair task |
| local worker | `python scripts/validate_local_worker_runner.py --json` | fail, queue-state errors only | `historical_queue_expectation_drift` | repair stale queue successor helper under proper authority |
| local worker | `python -m unittest tests.operations.test_local_worker_scripts -v` | fail, 3 tests, 1 failure | `historical_queue_expectation_drift` | repair stale queue successor helper under proper authority |

Historical HUNT, LOCAL, promotion, repo-layout/canon, public-alpha defer, IA
readiness, and staging assertion groups were not repaired in this pass because
the runtime leakage gate produced a material blocker requiring separate runtime
authority.

