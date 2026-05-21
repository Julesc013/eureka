# Validation

Validation run for `TEST-LANE-ROUTER-01`:

- JSON parse checks for test-lane records: PASS
- `python scripts/eureka_test_select.py --changed --failed-first --json`: PASS
- `python scripts/eureka_test_select.py --promotion --json`: PASS
- `python scripts/eureka_test_select.py --task WORKBENCH-RESULT-LANES-01 --changed --json`: PASS
- `python scripts/validate_test_lane_policy.py`: PASS
- `python -m unittest tests.operations.test_test_lane_policy`: PASS
- `python -m unittest tests.operations.test_test_impact_map`: PASS
- `python -m unittest tests.operations.test_test_failure_ledger`: PASS
- `python -m unittest tests.scripts.test_eureka_test_select`: PASS
- `python -m unittest tests.scripts.test_validate_test_lane_policy`: PASS
- `python scripts/check_architecture_boundaries.py`: PASS
- `python .aide/scripts/aide_lite.py doctor`: PASS
- `python .aide/scripts/aide_lite.py validate`: PASS
- `python .aide/scripts/aide_lite.py test`: PASS
- `python .aide/scripts/aide_lite.py selftest`: PASS
- `python .aide/scripts/aide_lite.py verify`: PASS
- `python .aide/scripts/aide_lite.py review-pack`: PASS

`python scripts/check_generated_artifact_cleanliness.py --check --json`
was run before commit and reported the expected audit-generated drift for
`control/audits/test-lane-router-01-v0/`. It must be rerun after commit.

Full discovery is optional for this tooling/policy task and intentionally not
the per-commit default. Promotion mode still selects full discovery and refuses
promotion while the failure ledger contains fixed-pending-full promotion
blockers.
