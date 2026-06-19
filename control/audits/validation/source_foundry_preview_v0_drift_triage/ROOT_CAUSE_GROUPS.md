# Root Cause Groups

Groups: 9

## dev_to_main_promotion_state_expectations

- member tests: 13
- classifications: `{"historical_validator_drift": 13}`
- current authority: current queue: REVIEW-IA-CANDIDATES-BATCH-00; public exposure paused; dev-to-main promotion blocked until green external rerun
- proposed repair: update promotion validators to model blocked checkpoint state without weakening promotion gates
- targeted command: `python -m unittest tests.operations.test_dev_to_main_promotion_03 tests.operations.test_dev_to_main_promotion_04 tests.scripts.test_validate_dev_to_main_promotion_03 tests.scripts.test_validate_dev_to_main_promotion_04 -v`
- risk: Could hide a real boundary regression if queue or safety validators are broadened without precise successor-state evidence.

## hunt_historical_queue_expectation_drift

- member tests: 9
- classifications: `{"historical_queue_expectation_drift": 9}`
- current authority: current queue: REVIEW-IA-CANDIDATES-BATCH-00; public exposure paused; dev-to-main promotion blocked until green external rerun
- proposed repair: update historical validator successor handling or move to archival/nightly lane
- targeted command: `python -m unittest tests.operations.test_search_hunt_track tests.operations.test_search_hunt_scripts tests.operations.test_search_hunt_ui_scripts tests.operations.test_search_hunt_command_scripts tests.operations.test_search_hunt_exhaustion_scripts tests.operations.test_search_need_scripts tests.operations.test_need_to_workunit_scripts tests.operations.test_background_hunt_runner_scripts -v`
- risk: Could hide a real boundary regression if queue or safety validators are broadened without precise successor-state evidence.

## ia_historical_lane_expectation_drift

- member tests: 1
- classifications: `{"historical_queue_expectation_drift": 1}`
- current authority: current queue: REVIEW-IA-CANDIDATES-BATCH-00; public exposure paused; dev-to-main promotion blocked until green external rerun
- proposed repair: update or retire superseded IA-BUNDLE lane assertion
- targeted command: `python scripts/validate_ia_readiness_polish.py --json`
- risk: Could hide a real boundary regression if queue or safety validators are broadened without precise successor-state evidence.

## local_historical_queue_expectation_drift

- member tests: 15
- classifications: `{"historical_queue_expectation_drift": 15}`
- current authority: current queue: REVIEW-IA-CANDIDATES-BATCH-00; public exposure paused; dev-to-main promotion blocked until green external rerun
- proposed repair: update historical validator successor handling or move to archival/nightly lane
- targeted command: `python -m unittest tests.operations.test_local_appliance_track tests.operations.test_local_instance_policy tests.operations.test_local_instance_bootstrap tests.operations.test_local_instance_migration_guard tests.operations.test_local_http_service_scripts tests.operations.test_local_runtime_composition_scripts tests.operations.test_local_workbench_scripts tests.operations.test_local_lan_policy_scripts tests.operations.test_local_lan_smoke_scripts tests.operations.test_clean_machine_smoke tests.operations.test_workunit_queue_scripts -v`
- risk: Could hide a real boundary regression if queue or safety validators are broadened without precise successor-state evidence.

## local_quarantine_staging_obsolete_no_staging_assertion

- member tests: 1
- classifications: `{"obsolete_test_candidate": 1}`
- current authority: current queue: REVIEW-IA-CANDIDATES-BATCH-00; public exposure paused; dev-to-main promotion blocked until green external rerun
- proposed repair: retire or narrow the stale test assertion
- targeted command: `python -m unittest tests.operations.test_local_quarantine_staging_model -v`
- risk: Could hide a real boundary regression if queue or safety validators are broadened without precise successor-state evidence.

## local_worker_validator_unknown_or_slow

- member tests: 1
- classifications: `{"unknown_requires_investigation": 1}`
- current authority: current queue: REVIEW-IA-CANDIDATES-BATCH-00; public exposure paused; dev-to-main promotion blocked until green external rerun
- proposed repair: investigate harness/runtime duration before rerun
- targeted command: `python scripts/validate_local_worker_runner.py --json`
- risk: Could hide a real boundary regression if queue or safety validators are broadened without precise successor-state evidence.

## public_alpha_defer_queue_expectation_drift

- member tests: 1
- classifications: `{"historical_queue_expectation_drift": 1}`
- current authority: current queue: REVIEW-IA-CANDIDATES-BATCH-00; public exposure paused; dev-to-main promotion blocked until green external rerun
- proposed repair: update historical validator successor allowlist with current accepted source-wave chain
- targeted command: `python scripts/validate_public_alpha_launch_defer.py --json`
- risk: Could hide a real boundary regression if queue or safety validators are broadened without precise successor-state evidence.

## repo_layout_canon_historical_validator_drift

- member tests: 7
- classifications: `{"historical_validator_drift": 7}`
- current authority: current queue: REVIEW-IA-CANDIDATES-BATCH-00; public exposure paused; dev-to-main promotion blocked until green external rerun
- proposed repair: repair repo-layout validator expectations with dedicated layout authority
- targeted command: `python -m unittest tests.scripts.test_validate_repo_structure_canon tests.scripts.test_validate_repository_layout -v`
- risk: Could hide a real boundary regression if queue or safety validators are broadened without precise successor-state evidence.

## runtime_leakage_safety_unknown

- member tests: 2
- classifications: `{"unknown_requires_investigation": 2}`
- current authority: current queue: REVIEW-IA-CANDIDATES-BATCH-00; public exposure paused; dev-to-main promotion blocked until green external rerun
- proposed repair: investigate before rerun
- targeted command: `python scripts/validate_runtime_architecture_leakage.py --json`
- risk: Could hide a real boundary regression if queue or safety validators are broadened without precise successor-state evidence.
