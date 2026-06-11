# Validation Report

## Focused Demo Validation

```text
python -m unittest tests.evals.test_local_e2e_search_demo tests.runtime.test_surface_local_e2e_demo
```

Result: `PASS`

```text
tests_run: 12
failures: 0
errors: 0
```

## Demo Commands

```text
python scripts/run_local_e2e_search_demo.py --all --profile text_v0
python scripts/run_local_e2e_search_demo.py --query "driver for Win98" --profile snapshot_v0
python scripts/run_local_e2e_search_demo.py --write-fixtures
```

Result: `PASS`

## Standard Validation

```text
python -m py_compile scripts\run_local_e2e_search_demo.py
git diff --check
py -3 .aide/scripts/aide_lite.py doctor
py -3 .aide/scripts/aide_lite.py validate
python scripts/check_architecture_boundaries.py
python scripts/check_generated_artifact_cleanliness.py --check --json
py -3 scripts\eureka_test_select.py --changed --failed-first --json
```

Result: `PASS`

Selector-selected focused commands:

```text
python scripts/validate_test_lane_policy.py
python -m unittest tests.operations.test_test_lane_policy
python -m unittest tests.scripts.test_eureka_test_select
python -m unittest tests.scripts.test_validate_test_lane_policy
```

Result: `PASS`

Full unittest discovery was not run inside the AI session.
