# Targeted Validation Matrix

No targeted repairs were applied in this pass.

## Checks Run

- `python scripts/validate_search_hunt_track.py --json`: FAIL (hunt_historical_queue_expectation_drift)
- `python scripts/validate_local_appliance_track.py --json`: FAIL (local_historical_queue_expectation_drift)
- `python scripts/validate_dev_to_main_promotion_03.py --json`: FAIL (dev_to_main_promotion_state_expectations)
- `python scripts/validate_public_alpha_launch_defer.py --json`: FAIL (public_alpha_defer_queue_expectation_drift)
- `python scripts/validate_ia_readiness_polish.py --json`: FAIL (ia_historical_lane_expectation_drift)
- `python scripts/validate_repo_structure_canon.py --json`: FAIL (repo_layout_canon_historical_validator_drift)
- `python scripts/validate_repository_layout.py --json`: FAIL (repo_layout_canon_historical_validator_drift)
- `python scripts/validate_local_quarantine_staging_model.py --json`: PASS (local_quarantine_staging_obsolete_no_staging_assertion)
- `python scripts/validate_local_worker_runner.py --json`: TIMEOUT_60S (local_worker_validator_unknown_or_slow)
- `python -m unittest tests.operations.test_search_hunt_track tests.operations.test_local_appliance_track tests.operations.test_local_quarantine_staging_model tests.operations.test_dev_to_main_promotion_03 tests.scripts.test_validate_repo_structure_canon tests.scripts.test_validate_repository_layout -v`: FAIL_40_TESTS_6_FAILURES_7_ERRORS (representative_multigroup_targeted_lane)
  - Confirms HUNT/LOCAL queue drift, stale staging assertion, dev-to-main blocked posture, and repo layout/canon validator drift remain red before repairs.

Remaining failures: 50
Full rerun permitted: false
