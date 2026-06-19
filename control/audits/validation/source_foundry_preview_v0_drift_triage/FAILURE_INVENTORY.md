# Failure Inventory

Total records: 50

## Classification Counts

- historical_queue_expectation_drift: 26
- historical_validator_drift: 20
- obsolete_test_candidate: 1
- unknown_requires_investigation: 3

## Records

### test_validator_passes (tests.operations.test_search_hunt_exhaustion_scripts.SearchHuntExhaustionScriptTests.test_validator_passes)

- classification: `historical_queue_expectation_drift`
- group: `hunt_historical_queue_expectation_drift`
- signature: `0 != 1 : HUNT-04 Search Hunt exhaustion validation`
- targeted command: `python -m unittest tests.operations.test_search_hunt_track tests.operations.test_search_hunt_scripts tests.operations.test_search_hunt_ui_scripts tests.operations.test_search_hunt_command_scripts tests.operations.test_search_hunt_exhaustion_scripts tests.operations.test_search_need_scripts tests.operations.test_need_to_workunit_scripts tests.operations.test_background_hunt_runner_scripts -v`
- repair disposition: update historical validator successor handling or move to archival/nightly lane
- safety relevance: `low`

### test_validator_passes (tests.operations.test_workunit_queue_scripts.WorkUnitQueueScriptTests.test_validator_passes)

- classification: `historical_queue_expectation_drift`
- group: `local_historical_queue_expectation_drift`
- signature: `0 != 1 : LOCAL-07 workunit queue validation`
- targeted command: `python -m unittest tests.operations.test_local_appliance_track tests.operations.test_local_instance_policy tests.operations.test_local_instance_bootstrap tests.operations.test_local_instance_migration_guard tests.operations.test_local_http_service_scripts tests.operations.test_local_runtime_composition_scripts tests.operations.test_local_workbench_scripts tests.operations.test_local_lan_policy_scripts tests.operations.test_local_lan_smoke_scripts tests.operations.test_clean_machine_smoke tests.operations.test_workunit_queue_scripts -v`
- repair disposition: update historical validator successor handling or move to archival/nightly lane
- safety relevance: `low`

### test_validator_passes (tests.operations.test_need_to_workunit_scripts.NeedToWorkUnitScriptTests.test_validator_passes)

- classification: `historical_queue_expectation_drift`
- group: `hunt_historical_queue_expectation_drift`
- signature: `0 != 1 : HUNT-06 Hunt-to-WorkUnit validation`
- targeted command: `python -m unittest tests.operations.test_search_hunt_track tests.operations.test_search_hunt_scripts tests.operations.test_search_hunt_ui_scripts tests.operations.test_search_hunt_command_scripts tests.operations.test_search_hunt_exhaustion_scripts tests.operations.test_search_need_scripts tests.operations.test_need_to_workunit_scripts tests.operations.test_background_hunt_runner_scripts -v`
- repair disposition: update historical validator successor handling or move to archival/nightly lane
- safety relevance: `low`

### test_validator_passes (tests.operations.test_search_hunt_ui_scripts.SearchHuntUiScriptTests.test_validator_passes)

- classification: `historical_queue_expectation_drift`
- group: `hunt_historical_queue_expectation_drift`
- signature: `0 != 1 : HUNT-02 Search Hunt UI validation`
- targeted command: `python -m unittest tests.operations.test_search_hunt_track tests.operations.test_search_hunt_scripts tests.operations.test_search_hunt_ui_scripts tests.operations.test_search_hunt_command_scripts tests.operations.test_search_hunt_exhaustion_scripts tests.operations.test_search_need_scripts tests.operations.test_need_to_workunit_scripts tests.operations.test_background_hunt_runner_scripts -v`
- repair disposition: update historical validator successor handling or move to archival/nightly lane
- safety relevance: `low`

### test_no_runtime_staging_tool_added (tests.operations.test_local_quarantine_staging_model.LocalQuarantineStagingModelOperationTestCase.test_no_runtime_staging_tool_added)

- classification: `obsolete_test_candidate`
- group: `local_quarantine_staging_obsolete_no_staging_assertion`
- signature: `Lists differ: ['eureka_external_staging.py', 'eureka_loc[39 chars].py'] != []`
- targeted command: `python -m unittest tests.operations.test_local_quarantine_staging_model -v`
- repair disposition: retire or narrow the stale test assertion
- safety relevance: `low`

### test_validator_passes (tests.operations.test_search_hunt_command_scripts.SearchHuntCommandScriptTests.test_validator_passes)

- classification: `historical_queue_expectation_drift`
- group: `hunt_historical_queue_expectation_drift`
- signature: `0 != 1 : HUNT-03 Search Hunt command validation`
- targeted command: `python -m unittest tests.operations.test_search_hunt_track tests.operations.test_search_hunt_scripts tests.operations.test_search_hunt_ui_scripts tests.operations.test_search_hunt_command_scripts tests.operations.test_search_hunt_exhaustion_scripts tests.operations.test_search_need_scripts tests.operations.test_need_to_workunit_scripts tests.operations.test_background_hunt_runner_scripts -v`
- repair disposition: update historical validator successor handling or move to archival/nightly lane
- safety relevance: `low`

### test_validator_passes (tests.operations.test_search_hunt_scripts.SearchHuntScriptTests.test_validator_passes)

- classification: `historical_queue_expectation_drift`
- group: `hunt_historical_queue_expectation_drift`
- signature: `0 != 1 : HUNT-01 Search Hunt runtime validation`
- targeted command: `python -m unittest tests.operations.test_search_hunt_track tests.operations.test_search_hunt_scripts tests.operations.test_search_hunt_ui_scripts tests.operations.test_search_hunt_command_scripts tests.operations.test_search_hunt_exhaustion_scripts tests.operations.test_search_need_scripts tests.operations.test_need_to_workunit_scripts tests.operations.test_background_hunt_runner_scripts -v`
- repair disposition: update historical validator successor handling or move to archival/nightly lane
- safety relevance: `low`

### test_validator_passes (tests.operations.test_local_http_service_scripts.LocalHTTPServiceScriptTests.test_validator_passes)

- classification: `historical_queue_expectation_drift`
- group: `local_historical_queue_expectation_drift`
- signature: `0 != 1 : LOCAL-04 local HTTP service validation`
- targeted command: `python -m unittest tests.operations.test_local_appliance_track tests.operations.test_local_instance_policy tests.operations.test_local_instance_bootstrap tests.operations.test_local_instance_migration_guard tests.operations.test_local_http_service_scripts tests.operations.test_local_runtime_composition_scripts tests.operations.test_local_workbench_scripts tests.operations.test_local_lan_policy_scripts tests.operations.test_local_lan_smoke_scripts tests.operations.test_clean_machine_smoke tests.operations.test_workunit_queue_scripts -v`
- repair disposition: update historical validator successor handling or move to archival/nightly lane
- safety relevance: `low`

### test_validator_passes (tests.operations.test_background_hunt_runner_scripts.BackgroundHuntRunnerScriptTests.test_validator_passes)

- classification: `historical_queue_expectation_drift`
- group: `hunt_historical_queue_expectation_drift`
- signature: `0 != 1 : HUNT-07 background hunt runner validation`
- targeted command: `python -m unittest tests.operations.test_search_hunt_track tests.operations.test_search_hunt_scripts tests.operations.test_search_hunt_ui_scripts tests.operations.test_search_hunt_command_scripts tests.operations.test_search_hunt_exhaustion_scripts tests.operations.test_search_need_scripts tests.operations.test_need_to_workunit_scripts tests.operations.test_background_hunt_runner_scripts -v`
- repair disposition: update historical validator successor handling or move to archival/nightly lane
- safety relevance: `low`

### test_validator_passes_current_repo (tests.operations.test_legacy_runtime_leakage_remediation.LegacyRuntimeLeakageRemediationTests.test_validator_passes_current_repo)

- classification: `unknown_requires_investigation`
- group: `runtime_leakage_safety_unknown`
- signature: `0 != 1 : R0 legacy runtime leakage remediation validation`
- targeted command: `python scripts/validate_runtime_architecture_leakage.py --json`
- repair disposition: investigate before rerun
- safety relevance: `high`

### test_validator_passes (tests.operations.test_local_workbench_scripts.LocalWorkbenchScriptTests.test_validator_passes)

- classification: `historical_queue_expectation_drift`
- group: `local_historical_queue_expectation_drift`
- signature: `0 != 1 : LOCAL-05 local HTML workbench validation`
- targeted command: `python -m unittest tests.operations.test_local_appliance_track tests.operations.test_local_instance_policy tests.operations.test_local_instance_bootstrap tests.operations.test_local_instance_migration_guard tests.operations.test_local_http_service_scripts tests.operations.test_local_runtime_composition_scripts tests.operations.test_local_workbench_scripts tests.operations.test_local_lan_policy_scripts tests.operations.test_local_lan_smoke_scripts tests.operations.test_clean_machine_smoke tests.operations.test_workunit_queue_scripts -v`
- repair disposition: update historical validator successor handling or move to archival/nightly lane
- safety relevance: `low`

### test_validator_demo_and_schema_cli_pass (tests.operations.test_agent_research_scripts.AgentResearchScriptsTests.test_validator_demo_and_schema_cli_pass)

- classification: `historical_validator_drift`
- group: `dev_to_main_promotion_state_expectations`
- signature: `1 != 0 : {`
- targeted command: `python -m unittest tests.operations.test_dev_to_main_promotion_03 tests.operations.test_dev_to_main_promotion_04 tests.scripts.test_validate_dev_to_main_promotion_03 tests.scripts.test_validate_dev_to_main_promotion_04 -v`
- repair disposition: update promotion validators to model blocked checkpoint state without weakening promotion gates
- safety relevance: `medium`

### test_validator_demo_and_cli_pass (tests.operations.test_ai_escalation_scripts.AIEscalationScriptsTests.test_validator_demo_and_cli_pass)

- classification: `historical_validator_drift`
- group: `dev_to_main_promotion_state_expectations`
- signature: `1 != 0 : {`
- targeted command: `python -m unittest tests.operations.test_dev_to_main_promotion_03 tests.operations.test_dev_to_main_promotion_04 tests.scripts.test_validate_dev_to_main_promotion_03 tests.scripts.test_validate_dev_to_main_promotion_04 -v`
- repair disposition: update promotion validators to model blocked checkpoint state without weakening promotion gates
- safety relevance: `medium`

### test_script_entrypoint_passes (tests.operations.test_hunt_remediation.HuntRemediationTests.test_script_entrypoint_passes)

- classification: `historical_validator_drift`
- group: `dev_to_main_promotion_state_expectations`
- signature: `1 != 0 : {`
- targeted command: `python -m unittest tests.operations.test_dev_to_main_promotion_03 tests.operations.test_dev_to_main_promotion_04 tests.scripts.test_validate_dev_to_main_promotion_03 tests.scripts.test_validate_dev_to_main_promotion_04 -v`
- repair disposition: update promotion validators to model blocked checkpoint state without weakening promotion gates
- safety relevance: `medium`

### test_script_entrypoint_passes (tests.operations.test_hunt_remediation_continue.HuntRemediationContinueTests.test_script_entrypoint_passes)

- classification: `historical_validator_drift`
- group: `dev_to_main_promotion_state_expectations`
- signature: `1 != 0 : {`
- targeted command: `python -m unittest tests.operations.test_dev_to_main_promotion_03 tests.operations.test_dev_to_main_promotion_04 tests.scripts.test_validate_dev_to_main_promotion_03 tests.scripts.test_validate_dev_to_main_promotion_04 -v`
- repair disposition: update promotion validators to model blocked checkpoint state without weakening promotion gates
- safety relevance: `medium`

### test_validator_demo_and_cli_pass (tests.operations.test_hunt_replay_scripts.HuntReplayScriptsTests.test_validator_demo_and_cli_pass)

- classification: `historical_validator_drift`
- group: `dev_to_main_promotion_state_expectations`
- signature: `1 != 0 : {`
- targeted command: `python -m unittest tests.operations.test_dev_to_main_promotion_03 tests.operations.test_dev_to_main_promotion_04 tests.scripts.test_validate_dev_to_main_promotion_03 tests.scripts.test_validate_dev_to_main_promotion_04 -v`
- repair disposition: update promotion validators to model blocked checkpoint state without weakening promotion gates
- safety relevance: `medium`

### test_defer_validator_script_passes_json_mode (tests.operations.test_public_alpha_launch_defer.PublicAlphaLaunchDeferTests.test_defer_validator_script_passes_json_mode)

- classification: `historical_validator_drift`
- group: `dev_to_main_promotion_state_expectations`
- signature: `1 != 0 : {`
- targeted command: `python -m unittest tests.operations.test_dev_to_main_promotion_03 tests.operations.test_dev_to_main_promotion_04 tests.scripts.test_validate_dev_to_main_promotion_03 tests.scripts.test_validate_dev_to_main_promotion_04 -v`
- repair disposition: update promotion validators to model blocked checkpoint state without weakening promotion gates
- safety relevance: `medium`

### test_validator_script_passes_with_disposed_warnings (tests.operations.test_search_hunt_closeout.SearchHuntCloseoutTests.test_validator_script_passes_with_disposed_warnings)

- classification: `historical_validator_drift`
- group: `dev_to_main_promotion_state_expectations`
- signature: `1 != 0 : {`
- targeted command: `python -m unittest tests.operations.test_dev_to_main_promotion_03 tests.operations.test_dev_to_main_promotion_04 tests.scripts.test_validate_dev_to_main_promotion_03 tests.scripts.test_validate_dev_to_main_promotion_04 -v`
- repair disposition: update promotion validators to model blocked checkpoint state without weakening promotion gates
- safety relevance: `medium`

### test_validator_script_json_passes (tests.scripts.test_validate_dev_to_main_promotion_03.ValidateDevToMainPromotion03ScriptTests.test_validator_script_json_passes)

- classification: `historical_validator_drift`
- group: `dev_to_main_promotion_state_expectations`
- signature: `1 != 0 : {`
- targeted command: `python -m unittest tests.operations.test_dev_to_main_promotion_03 tests.operations.test_dev_to_main_promotion_04 tests.scripts.test_validate_dev_to_main_promotion_03 tests.scripts.test_validate_dev_to_main_promotion_04 -v`
- repair disposition: update promotion validators to model blocked checkpoint state without weakening promotion gates
- safety relevance: `medium`

### test_validator_script_json_passes (tests.scripts.test_validate_dev_to_main_promotion_04.ValidateDevToMainPromotion04ScriptTests.test_validator_script_json_passes)

- classification: `historical_validator_drift`
- group: `dev_to_main_promotion_state_expectations`
- signature: `1 != 0 : {`
- targeted command: `python -m unittest tests.operations.test_dev_to_main_promotion_03 tests.operations.test_dev_to_main_promotion_04 tests.scripts.test_validate_dev_to_main_promotion_03 tests.scripts.test_validate_dev_to_main_promotion_04 -v`
- repair disposition: update promotion validators to model blocked checkpoint state without weakening promotion gates
- safety relevance: `medium`

### test_validator_passes_current_repo_or_reports_only_known_allowlisted (tests.operations.test_runtime_architecture_leakage.RuntimeArchitectureLeakageTests.test_validator_passes_current_repo_or_reports_only_known_allowlisted)

- classification: `unknown_requires_investigation`
- group: `runtime_leakage_safety_unknown`
- signature: `0 != 1 : R0-02 runtime architecture leakage validation`
- targeted command: `python scripts/validate_runtime_architecture_leakage.py --json`
- repair disposition: investigate before rerun
- safety relevance: `high`

### test_defer_validator_passes (tests.operations.test_public_alpha_launch_defer.PublicAlphaLaunchDeferTests.test_defer_validator_passes)

- classification: `historical_queue_expectation_drift`
- group: `public_alpha_defer_queue_expectation_drift`
- signature: `'invalid' != 'pass'`
- targeted command: `python scripts/validate_public_alpha_launch_defer.py --json`
- repair disposition: update historical validator successor allowlist with current accepted source-wave chain
- safety relevance: `medium`

### test_next_task_is_hunt_01_or_completed_post_hunt_task (tests.operations.test_search_hunt_track.SearchHuntTrackTests.test_next_task_is_hunt_01_or_completed_post_hunt_task)

- classification: `historical_queue_expectation_drift`
- group: `hunt_historical_queue_expectation_drift`
- signature: `Regex didn't match: 'current_recommended_task: (HUNT-(0[1-9]|1[0-2])|SYN-00|DOMAIN-00|SCOUT-SCHEMA-00|F0-00|G0|HUNT-REMEDIATION|HUNT-TO-MAIN-PROMOTION-REVIEW|DEV-AND-IA-[A-Z0-9-]+|REPO-LAYOUT-[A-Z0-9-]+|IA-HUNT-BRIDGE-00|RESOLUTION-RUN-KERNEL-00|WORKBENCH-LIVE-RUN-01)\\b' not found in 'current_recommended_task: REVIEW-IA-CANDIDATES-BATCH-00 - Prepare governed IA candidate<path> review batch material; operator decisions are explicit and review-ledger-only; reviewed records, index rebuilds, public`
- targeted command: `python -m unittest tests.operations.test_search_hunt_track tests.operations.test_search_hunt_scripts tests.operations.test_search_hunt_ui_scripts tests.operations.test_search_hunt_command_scripts tests.operations.test_search_hunt_exhaustion_scripts tests.operations.test_search_need_scripts tests.operations.test_need_to_workunit_scripts tests.operations.test_background_hunt_runner_scripts -v`
- repair disposition: update historical validator successor handling or move to archival/nightly lane
- safety relevance: `low`

### test_queue_points_to_local_track_successor (tests.operations.test_local_appliance_track.LocalApplianceTrackTests.test_queue_points_to_local_track_successor)

- classification: `historical_queue_expectation_drift`
- group: `local_historical_queue_expectation_drift`
- signature: `False is not true : current_recommended_task: REVIEW-IA-CANDIDATES-BATCH-00 - Prepare governed IA candidate<path> review batch material; operator decisions are explicit and review-ledger-only; reviewed records, index rebuilds, public exposure, external artifact evidence, and hardware details remain gated`
- targeted command: `python -m unittest tests.operations.test_local_appliance_track tests.operations.test_local_instance_policy tests.operations.test_local_instance_bootstrap tests.operations.test_local_instance_migration_guard tests.operations.test_local_http_service_scripts tests.operations.test_local_runtime_composition_scripts tests.operations.test_local_workbench_scripts tests.operations.test_local_lan_policy_scripts tests.operations.test_local_lan_smoke_scripts tests.operations.test_clean_machine_smoke tests.operations.test_workunit_queue_scripts -v`
- repair disposition: update historical validator successor handling or move to archival/nightly lane
- safety relevance: `low`

### test_validator_passes_focused_tests (tests.operations.test_local_instance_bootstrap.LocalInstanceBootstrapTests.test_validator_passes_focused_tests)

- classification: `historical_queue_expectation_drift`
- group: `local_historical_queue_expectation_drift`
- signature: `0 != 1 : LOCAL-01 local instance bootstrap validation`
- targeted command: `python -m unittest tests.operations.test_local_appliance_track tests.operations.test_local_instance_policy tests.operations.test_local_instance_bootstrap tests.operations.test_local_instance_migration_guard tests.operations.test_local_http_service_scripts tests.operations.test_local_runtime_composition_scripts tests.operations.test_local_workbench_scripts tests.operations.test_local_lan_policy_scripts tests.operations.test_local_lan_smoke_scripts tests.operations.test_clean_machine_smoke tests.operations.test_workunit_queue_scripts -v`
- repair disposition: update historical validator successor handling or move to archival/nightly lane
- safety relevance: `low`

### test_validator_passes (tests.operations.test_search_need_scripts.SearchNeedScriptTests.test_validator_passes)

- classification: `historical_queue_expectation_drift`
- group: `hunt_historical_queue_expectation_drift`
- signature: `0 != 1 : HUNT-05 hunt-to-SearchNeed validation`
- targeted command: `python -m unittest tests.operations.test_search_hunt_track tests.operations.test_search_hunt_scripts tests.operations.test_search_hunt_ui_scripts tests.operations.test_search_hunt_command_scripts tests.operations.test_search_hunt_exhaustion_scripts tests.operations.test_search_need_scripts tests.operations.test_need_to_workunit_scripts tests.operations.test_background_hunt_runner_scripts -v`
- repair disposition: update historical validator successor handling or move to archival/nightly lane
- safety relevance: `low`

### test_validator_passes (tests.operations.test_dev_to_main_promotion_03.DevToMainPromotion03Tests.test_validator_passes)

- classification: `historical_validator_drift`
- group: `dev_to_main_promotion_state_expectations`
- signature: `'fail' != 'pass'`
- targeted command: `python -m unittest tests.operations.test_dev_to_main_promotion_03 tests.operations.test_dev_to_main_promotion_04 tests.scripts.test_validate_dev_to_main_promotion_03 tests.scripts.test_validate_dev_to_main_promotion_04 -v`
- repair disposition: update promotion validators to model blocked checkpoint state without weakening promotion gates
- safety relevance: `medium`

### test_validator_passes (tests.operations.test_dev_to_main_promotion_04.DevToMainPromotion04Tests.test_validator_passes)

- classification: `historical_validator_drift`
- group: `dev_to_main_promotion_state_expectations`
- signature: `'fail' != 'pass'`
- targeted command: `python -m unittest tests.operations.test_dev_to_main_promotion_03 tests.operations.test_dev_to_main_promotion_04 tests.scripts.test_validate_dev_to_main_promotion_03 tests.scripts.test_validate_dev_to_main_promotion_04 -v`
- repair disposition: update promotion validators to model blocked checkpoint state without weakening promotion gates
- safety relevance: `medium`

### test_remediation_validator_passes (tests.operations.test_hunt_remediation.HuntRemediationTests.test_remediation_validator_passes)

- classification: `historical_validator_drift`
- group: `dev_to_main_promotion_state_expectations`
- signature: `'fail' != 'pass'`
- targeted command: `python -m unittest tests.operations.test_dev_to_main_promotion_03 tests.operations.test_dev_to_main_promotion_04 tests.scripts.test_validate_dev_to_main_promotion_03 tests.scripts.test_validate_dev_to_main_promotion_04 -v`
- repair disposition: update promotion validators to model blocked checkpoint state without weakening promotion gates
- safety relevance: `medium`

### test_continuation_validator_passes (tests.operations.test_hunt_remediation_continue.HuntRemediationContinueTests.test_continuation_validator_passes)

- classification: `historical_validator_drift`
- group: `dev_to_main_promotion_state_expectations`
- signature: `'fail' != 'pass'`
- targeted command: `python -m unittest tests.operations.test_dev_to_main_promotion_03 tests.operations.test_dev_to_main_promotion_04 tests.scripts.test_validate_dev_to_main_promotion_03 tests.scripts.test_validate_dev_to_main_promotion_04 -v`
- repair disposition: update promotion validators to model blocked checkpoint state without weakening promotion gates
- safety relevance: `medium`

### test_validator_plain_passes (tests.scripts.test_validate_repo_structure_canon.RepoStructureCanonValidatorScriptTest.test_validator_plain_passes)

- classification: `historical_validator_drift`
- group: `repo_layout_canon_historical_validator_drift`
- signature: `Command '['<path> '<path> returned non-zero exit status 1.`
- targeted command: `python -m unittest tests.scripts.test_validate_repo_structure_canon tests.scripts.test_validate_repository_layout -v`
- repair disposition: repair repo-layout validator expectations with dedicated layout authority
- safety relevance: `low`

### test_validator_plain_passes (tests.scripts.test_validate_repository_layout.RepositoryLayoutValidatorScriptTest.test_validator_plain_passes)

- classification: `historical_validator_drift`
- group: `repo_layout_canon_historical_validator_drift`
- signature: `Command '['<path> '<path> returned non-zero exit status 1.`
- targeted command: `python -m unittest tests.scripts.test_validate_repo_structure_canon tests.scripts.test_validate_repository_layout -v`
- repair disposition: repair repo-layout validator expectations with dedicated layout authority
- safety relevance: `low`

### test_validator_strict_passes_after_reconcile (tests.scripts.test_validate_repo_structure_canon.RepoStructureCanonValidatorScriptTest.test_validator_strict_passes_after_reconcile)

- classification: `historical_validator_drift`
- group: `repo_layout_canon_historical_validator_drift`
- signature: `Command '['<path> '<path> '--strict', '--json']' returned non-zero exit status 1.`
- targeted command: `python -m unittest tests.scripts.test_validate_repo_structure_canon tests.scripts.test_validate_repository_layout -v`
- repair disposition: repair repo-layout validator expectations with dedicated layout authority
- safety relevance: `low`

### test_validator_strict_passes (tests.scripts.test_validate_repository_layout.RepositoryLayoutValidatorScriptTest.test_validator_strict_passes)

- classification: `historical_validator_drift`
- group: `repo_layout_canon_historical_validator_drift`
- signature: `Command '['<path> '<path> '--strict', '--json']' returned non-zero exit status 1.`
- targeted command: `python -m unittest tests.scripts.test_validate_repo_structure_canon tests.scripts.test_validate_repository_layout -v`
- repair disposition: repair repo-layout validator expectations with dedicated layout authority
- safety relevance: `low`

### test_validator_json_records_canon_and_resolved_debt (tests.scripts.test_validate_repo_structure_canon.RepoStructureCanonValidatorScriptTest.test_validator_json_records_canon_and_resolved_debt)

- classification: `historical_validator_drift`
- group: `repo_layout_canon_historical_validator_drift`
- signature: `Command '['<path> '<path> '--json']' returned non-zero exit status 1.`
- targeted command: `python -m unittest tests.scripts.test_validate_repo_structure_canon tests.scripts.test_validate_repository_layout -v`
- repair disposition: repair repo-layout validator expectations with dedicated layout authority
- safety relevance: `low`

### test_validator_rejects_unclassified_src (tests.scripts.test_validate_repo_structure_canon.RepoStructureCanonValidatorScriptTest.test_validator_rejects_unclassified_src)

- classification: `historical_validator_drift`
- group: `repo_layout_canon_historical_validator_drift`
- signature: `Command '['<path> '<path> '--json']' returned non-zero exit status 1.`
- targeted command: `python -m unittest tests.scripts.test_validate_repo_structure_canon tests.scripts.test_validate_repository_layout -v`
- repair disposition: repair repo-layout validator expectations with dedicated layout authority
- safety relevance: `low`

### test_validator_json_parses (tests.scripts.test_validate_repository_layout.RepositoryLayoutValidatorScriptTest.test_validator_json_parses)

- classification: `historical_validator_drift`
- group: `repo_layout_canon_historical_validator_drift`
- signature: `Command '['<path> '<path> '--json']' returned non-zero exit status 1.`
- targeted command: `python -m unittest tests.scripts.test_validate_repo_structure_canon tests.scripts.test_validate_repository_layout -v`
- repair disposition: repair repo-layout validator expectations with dedicated layout authority
- safety relevance: `low`

### test_validator_passes (tests.operations.test_local_appliance_track.LocalApplianceTrackTests.test_validator_passes)

- classification: `historical_queue_expectation_drift`
- group: `local_historical_queue_expectation_drift`
- signature: `'pass' != 'fail'`
- targeted command: `python -m unittest tests.operations.test_local_appliance_track tests.operations.test_local_instance_policy tests.operations.test_local_instance_bootstrap tests.operations.test_local_instance_migration_guard tests.operations.test_local_http_service_scripts tests.operations.test_local_runtime_composition_scripts tests.operations.test_local_workbench_scripts tests.operations.test_local_lan_policy_scripts tests.operations.test_local_lan_smoke_scripts tests.operations.test_clean_machine_smoke tests.operations.test_workunit_queue_scripts -v`
- repair disposition: update historical validator successor handling or move to archival/nightly lane
- safety relevance: `low`

### test_validator_passes (tests.operations.test_local_runtime_composition_scripts.LocalRuntimeCompositionScriptTests.test_validator_passes)

- classification: `historical_queue_expectation_drift`
- group: `local_historical_queue_expectation_drift`
- signature: `0 != 1 : LOCAL-03 local runtime composition validation`
- targeted command: `python -m unittest tests.operations.test_local_appliance_track tests.operations.test_local_instance_policy tests.operations.test_local_instance_bootstrap tests.operations.test_local_instance_migration_guard tests.operations.test_local_http_service_scripts tests.operations.test_local_runtime_composition_scripts tests.operations.test_local_workbench_scripts tests.operations.test_local_lan_policy_scripts tests.operations.test_local_lan_smoke_scripts tests.operations.test_clean_machine_smoke tests.operations.test_workunit_queue_scripts -v`
- repair disposition: update historical validator successor handling or move to archival/nightly lane
- safety relevance: `low`

### test_queue_points_to_local_02 (tests.operations.test_local_instance_policy.LocalInstancePolicyTests.test_queue_points_to_local_02)

- classification: `historical_queue_expectation_drift`
- group: `local_historical_queue_expectation_drift`
- signature: `'current_recommended_task: LOCAL-02' not found in 'current_recommended_task: REVIEW-IA-CANDIDATES-BATCH-00 - Prepare governed IA candidate<path> review batch material; operator decisions are explicit and review-ledger-only; reviewed records, index rebuilds, public exposure, external artifact evidence, and hardware details remain gated\ncomplete<path> - SOURCE-ACTION-KERNEL-00\n - SOURCE-WAVE-00\n - SNAPSHOT-RELAY-00\n - CI-FULL-DISCOVERY-HARNESS-00\n - SOURCE-SNAPSHOT-BASELINE-CLOSEOUT-01\n - DE`
- targeted command: `python -m unittest tests.operations.test_local_appliance_track tests.operations.test_local_instance_policy tests.operations.test_local_instance_bootstrap tests.operations.test_local_instance_migration_guard tests.operations.test_local_http_service_scripts tests.operations.test_local_runtime_composition_scripts tests.operations.test_local_workbench_scripts tests.operations.test_local_lan_policy_scripts tests.operations.test_local_lan_smoke_scripts tests.operations.test_clean_machine_smoke tests.operations.test_workunit_queue_scripts -v`
- repair disposition: update historical validator successor handling or move to archival/nightly lane
- safety relevance: `low`

### test_validator_passes (tests.operations.test_local_worker_scripts.LocalWorkerScriptTests.test_validator_passes)

- classification: `unknown_requires_investigation`
- group: `local_worker_validator_unknown_or_slow`
- signature: `'fail' not found in {'pass', 'pass_with_warnings'}`
- targeted command: `python scripts/validate_local_worker_runner.py --json`
- repair disposition: investigate harness/runtime duration before rerun
- safety relevance: `low`

### test_validator_passes_with_disposed_warnings (tests.operations.test_search_hunt_track.SearchHuntTrackTests.test_validator_passes_with_disposed_warnings)

- classification: `historical_queue_expectation_drift`
- group: `hunt_historical_queue_expectation_drift`
- signature: `'fail' not found in {'pass', 'pass_with_warnings'} : {'schema_version': 'search_hunt_track_validation.v0', 'task': 'HUNT-00', 'status': 'fail', 'errors': ['queue must point to HUNT-01 or a later HUNT task', 'queue must mark HUNT-00 completed', 'queue must include HUNT-01', 'latest task packet must point to HUNT-01 or a later HUNT task'], 'warnings': ['HUNT-00 carries final baseline warning disposition forward'], 'next_task': 'HUNT-01', 'runtime_modified': False, 'contracts_modified': False, 'sou`
- targeted command: `python -m unittest tests.operations.test_search_hunt_track tests.operations.test_search_hunt_scripts tests.operations.test_search_hunt_ui_scripts tests.operations.test_search_hunt_command_scripts tests.operations.test_search_hunt_exhaustion_scripts tests.operations.test_search_need_scripts tests.operations.test_need_to_workunit_scripts tests.operations.test_background_hunt_runner_scripts -v`
- repair disposition: update historical validator successor handling or move to archival/nightly lane
- safety relevance: `low`

### test_validator_passes_with_known_warning (tests.operations.test_clean_machine_smoke.CleanMachineSmokeScriptTests.test_validator_passes_with_known_warning)

- classification: `historical_queue_expectation_drift`
- group: `local_historical_queue_expectation_drift`
- signature: `0 != 1 : {`
- targeted command: `python -m unittest tests.operations.test_local_appliance_track tests.operations.test_local_instance_policy tests.operations.test_local_instance_bootstrap tests.operations.test_local_instance_migration_guard tests.operations.test_local_http_service_scripts tests.operations.test_local_runtime_composition_scripts tests.operations.test_local_workbench_scripts tests.operations.test_local_lan_policy_scripts tests.operations.test_local_lan_smoke_scripts tests.operations.test_clean_machine_smoke tests.operations.test_workunit_queue_scripts -v`
- repair disposition: update historical validator successor handling or move to archival/nightly lane
- safety relevance: `low`

### test_validator_passes (tests.operations.test_local_auto_test_scripts.LocalAutoTestScriptTests.test_validator_passes)

- classification: `historical_queue_expectation_drift`
- group: `local_historical_queue_expectation_drift`
- signature: `0 != 1 : {`
- targeted command: `python -m unittest tests.operations.test_local_appliance_track tests.operations.test_local_instance_policy tests.operations.test_local_instance_bootstrap tests.operations.test_local_instance_migration_guard tests.operations.test_local_http_service_scripts tests.operations.test_local_runtime_composition_scripts tests.operations.test_local_workbench_scripts tests.operations.test_local_lan_policy_scripts tests.operations.test_local_lan_smoke_scripts tests.operations.test_clean_machine_smoke tests.operations.test_workunit_queue_scripts -v`
- repair disposition: update historical validator successor handling or move to archival/nightly lane
- safety relevance: `low`

### test_validator_passes (tests.operations.test_local_lan_policy_scripts.LocalLanPolicyScriptTests.test_validator_passes)

- classification: `historical_queue_expectation_drift`
- group: `local_historical_queue_expectation_drift`
- signature: `0 != 1 : {`
- targeted command: `python -m unittest tests.operations.test_local_appliance_track tests.operations.test_local_instance_policy tests.operations.test_local_instance_bootstrap tests.operations.test_local_instance_migration_guard tests.operations.test_local_http_service_scripts tests.operations.test_local_runtime_composition_scripts tests.operations.test_local_workbench_scripts tests.operations.test_local_lan_policy_scripts tests.operations.test_local_lan_smoke_scripts tests.operations.test_clean_machine_smoke tests.operations.test_workunit_queue_scripts -v`
- repair disposition: update historical validator successor handling or move to archival/nightly lane
- safety relevance: `low`

### test_validator_passes (tests.operations.test_local_lan_smoke_scripts.LocalLanSmokeScriptTests.test_validator_passes)

- classification: `historical_queue_expectation_drift`
- group: `local_historical_queue_expectation_drift`
- signature: `0 != 1 : {`
- targeted command: `python -m unittest tests.operations.test_local_appliance_track tests.operations.test_local_instance_policy tests.operations.test_local_instance_bootstrap tests.operations.test_local_instance_migration_guard tests.operations.test_local_http_service_scripts tests.operations.test_local_runtime_composition_scripts tests.operations.test_local_workbench_scripts tests.operations.test_local_lan_policy_scripts tests.operations.test_local_lan_smoke_scripts tests.operations.test_clean_machine_smoke tests.operations.test_workunit_queue_scripts -v`
- repair disposition: update historical validator successor handling or move to archival/nightly lane
- safety relevance: `low`

### test_page_hardening_validator_passes (tests.operations.test_local_workbench_page_hardening_scripts.LocalWorkbenchPageHardeningScriptTests.test_page_hardening_validator_passes)

- classification: `historical_queue_expectation_drift`
- group: `local_historical_queue_expectation_drift`
- signature: `0 != 1 : {`
- targeted command: `python -m unittest tests.operations.test_local_appliance_track tests.operations.test_local_instance_policy tests.operations.test_local_instance_bootstrap tests.operations.test_local_instance_migration_guard tests.operations.test_local_http_service_scripts tests.operations.test_local_runtime_composition_scripts tests.operations.test_local_workbench_scripts tests.operations.test_local_lan_policy_scripts tests.operations.test_local_lan_smoke_scripts tests.operations.test_clean_machine_smoke tests.operations.test_workunit_queue_scripts -v`
- repair disposition: update historical validator successor handling or move to archival/nightly lane
- safety relevance: `low`

### test_validator_passes_focused_tests (tests.operations.test_local_instance_migration_guard.LocalInstanceMigrationGuardTests.test_validator_passes_focused_tests)

- classification: `historical_queue_expectation_drift`
- group: `local_historical_queue_expectation_drift`
- signature: `0 != 1 : LOCAL-02 local instance migration guard validation`
- targeted command: `python -m unittest tests.operations.test_local_appliance_track tests.operations.test_local_instance_policy tests.operations.test_local_instance_bootstrap tests.operations.test_local_instance_migration_guard tests.operations.test_local_http_service_scripts tests.operations.test_local_runtime_composition_scripts tests.operations.test_local_workbench_scripts tests.operations.test_local_lan_policy_scripts tests.operations.test_local_lan_smoke_scripts tests.operations.test_clean_machine_smoke tests.operations.test_workunit_queue_scripts -v`
- repair disposition: update historical validator successor handling or move to archival/nightly lane
- safety relevance: `low`

### test_validator_passes_current_repo (tests.operations.test_ia_readiness_polish.IAReadinessPolishTest.test_validator_passes_current_repo)

- classification: `historical_queue_expectation_drift`
- group: `ia_historical_lane_expectation_drift`
- signature: `'invalid' != 'valid'`
- targeted command: `python scripts/validate_ia_readiness_polish.py --json`
- repair disposition: update or retire superseded IA-BUNDLE lane assertion
- safety relevance: `low`

### test_validator_passes (tests.operations.test_local_review_rebuild_smoke.LocalReviewRebuildSmokeTests.test_validator_passes)

- classification: `historical_queue_expectation_drift`
- group: `local_historical_queue_expectation_drift`
- signature: `'fail' not found in {'pass', 'pass_with_warnings'} : ['queue index must point to LOCAL-09', 'queue index must mark LOCAL-08 completed', 'queue index must include queued LOCAL-09', 'queue index must keep F0 deferred until LOCAL-14']`
- targeted command: `python -m unittest tests.operations.test_local_appliance_track tests.operations.test_local_instance_policy tests.operations.test_local_instance_bootstrap tests.operations.test_local_instance_migration_guard tests.operations.test_local_http_service_scripts tests.operations.test_local_runtime_composition_scripts tests.operations.test_local_workbench_scripts tests.operations.test_local_lan_policy_scripts tests.operations.test_local_lan_smoke_scripts tests.operations.test_clean_machine_smoke tests.operations.test_workunit_queue_scripts -v`
- repair disposition: update historical validator successor handling or move to archival/nightly lane
- safety relevance: `low`
