# Refreshed Historical Drift Baseline

- total commands: 15
- pass: 2
- fail: 11
- timeout: 2

## Commands

- runtime_leakage_validator: pass (exit 0, 118.709s)
  - signature:   "status": "valid",
- runtime_leakage_tests: pass (exit 0, 236.755s)
- local_worker_validator: fail (exit 1, 121.372s)
  - signature:   "local_status_snapshot_worker_passed": true,
- local_worker_tests: fail (exit 1, 123.632s)
  - signature: FAIL: test_validator_passes (tests.operations.test_local_worker_scripts.LocalWorkerScriptTests.test_validator_passes)
- hunt_lane: fail (exit 1, 40.549s)
  - signature: FAIL: test_next_task_is_hunt_01_or_completed_post_hunt_task (tests.operations.test_search_hunt_track.SearchHuntTrackTests.test_next_task_is_hunt_01_or_completed_post_hunt_task)
- local_lane: timeout (exit 124, 300.022s)
  - signature: test_init_writes_config_and_status_with_safe_flags (tests.operations.test_local_instance_bootstrap.LocalInstanceBootstrapTests.test_init_writes_config_and_status_with_safe_flags) ... ok
- dev_to_main_lane: fail (exit 1, 3.052s)
  - signature: FAIL: test_validator_passes (tests.operations.test_dev_to_main_promotion_03.DevToMainPromotion03Tests.test_validator_passes)
- repo_layout_canon_lane: fail (exit 1, 9.74s)
  - signature: ERROR: test_validator_json_records_canon_and_resolved_debt (tests.scripts.test_validate_repo_structure_canon.RepoStructureCanonValidatorScriptTest.test_validator_json_records_canon_and_resolved_debt)
- public_alpha_defer_validator: fail (exit 1, 0.053s)
  - signature:   "status": "invalid",
- public_alpha_defer_tests: fail (exit 1, 0.129s)
  - signature: FAIL: test_defer_validator_passes (tests.operations.test_public_alpha_launch_defer.PublicAlphaLaunchDeferTests.test_defer_validator_passes)
- ia_readiness_validator: fail (exit 1, 0.063s)
  - signature:   "status": "invalid",
- ia_readiness_tests: fail (exit 1, 0.406s)
  - signature: FAIL: test_validator_passes_current_repo (tests.operations.test_ia_readiness_polish.IAReadinessPolishTest.test_validator_passes_current_repo)
- quarantine_staging_lane: fail (exit 1, 0.071s)
  - signature: FAIL: test_no_runtime_staging_tool_added (tests.operations.test_local_quarantine_staging_model.LocalQuarantineStagingModelOperationTestCase.test_no_runtime_staging_tool_added)
- dev_to_main_inventory_extras: fail (exit 1, 37.748s)
  - signature: FAIL: test_validator_demo_and_schema_cli_pass (tests.operations.test_agent_research_scripts.AgentResearchScriptsTests.test_validator_demo_and_schema_cli_pass)
- local_inventory_extras: timeout (exit 124, 240.012s)
