# Validation

PASS:

- `python scripts/eureka_test_select.py --changed --failed-first --json`
- `python scripts/eureka_test_select.py --task WORKBENCH-RESULT-LANES-01 --changed --failed-first --json`
- `python scripts/eureka_test_select.py --promotion --json` ran and correctly refused promotion with active blockers.
- `python scripts/validate_test_lane_policy.py`
- `python scripts/validate_workbench_result_lanes.py`
- `python scripts/validate_workbench_foundation.py`
- `python scripts/validate_search_interaction_contract.py`
- `python scripts/validate_contract_taxonomy.py`
- `python scripts/validate_repo_structure_canon.py`
- Workbench result-lane projection smokes for operator, public web, and native read-only profiles.
- Focused Workbench/result-lane unit tests.
- `python scripts/check_architecture_boundaries.py`
- AIDE doctor, validate, test, selftest, verify, review-pack, and commit check.

FAIL:

- `python -m unittest discover -s tests -t .`

Full discovery failures:

- `tests.operations.test_contract_taxonomy_plan.ContractTaxonomyPlanTests.test_validator_confirms_no_contract_files_moved_and_recommends_r0_03b`
- `tests.operations.test_local_appliance_track.LocalApplianceTrackTests.test_validator_passes`

Post-full-discovery targeted status:

- Local appliance repo-health metadata was repaired and focused rerun passed.
- Contract taxonomy failure reproduced and remains blocked outside this task's allowed paths.
