# Targeted Validation Matrix

All listed commands were targeted checks. Full unittest discovery was not run
inside this AI session.

| Group | Command | Result |
| --- | --- | --- |
| runtime leakage | `python scripts/validate_runtime_architecture_leakage.py --json` | PASS |
| runtime leakage | `python -m unittest tests.operations.test_legacy_runtime_leakage_remediation tests.operations.test_runtime_architecture_leakage -v` | PASS |
| local worker | `python scripts/validate_local_worker_runner.py --json` | PASS |
| local worker | `python -m unittest tests.operations.test_local_worker_scripts -v` | PASS |
| HUNT | `python -m unittest tests.operations.test_search_hunt_track tests.operations.test_search_hunt_scripts tests.operations.test_search_hunt_ui_scripts tests.operations.test_search_hunt_command_scripts tests.operations.test_search_hunt_exhaustion_scripts tests.operations.test_search_need_scripts tests.operations.test_need_to_workunit_scripts tests.operations.test_background_hunt_runner_scripts -v` | PASS |
| HUNT extras | `python -m unittest tests.operations.test_agent_research_scripts tests.operations.test_ai_escalation_scripts tests.operations.test_hunt_remediation tests.operations.test_hunt_remediation_continue tests.operations.test_hunt_replay_scripts tests.operations.test_search_hunt_closeout -v` | PASS |
| LOCAL split 1 | `python -m unittest tests.operations.test_local_appliance_track tests.operations.test_local_instance_policy tests.operations.test_local_instance_bootstrap -v` | PASS |
| LOCAL split 2 | `python -m unittest tests.operations.test_local_instance_migration_guard tests.operations.test_local_http_service_scripts tests.operations.test_local_runtime_composition_scripts -v` | PASS |
| LOCAL split 3 | `python -m unittest tests.operations.test_local_workbench_scripts tests.operations.test_local_lan_policy_scripts tests.operations.test_local_lan_smoke_scripts -v` | PASS |
| LOCAL split 4 | `python -m unittest tests.operations.test_clean_machine_smoke tests.operations.test_workunit_queue_scripts -v` | PASS |
| LOCAL extras | `python -m unittest tests.operations.test_local_auto_test_scripts -v` | PASS |
| LOCAL extras | `python -m unittest tests.operations.test_local_workbench_page_hardening_scripts -v` | PASS |
| LOCAL extras | `python -m unittest tests.operations.test_local_review_rebuild_smoke -v` | PASS |
| dev-to-main | `python -m unittest tests.operations.test_dev_to_main_promotion_03 tests.operations.test_dev_to_main_promotion_04 tests.scripts.test_validate_dev_to_main_promotion_03 tests.scripts.test_validate_dev_to_main_promotion_04 -v` | PASS |
| repo layout/canon | `python -m unittest tests.scripts.test_validate_repo_structure_canon tests.scripts.test_validate_repository_layout -v` | PASS |
| public alpha defer | `python scripts/validate_public_alpha_launch_defer.py --json` | PASS |
| public alpha defer | `python -m unittest tests.operations.test_public_alpha_launch_defer -v` | PASS |
| IA readiness | `python scripts/validate_ia_readiness_polish.py --json` | PASS |
| staging assertion | `python -m unittest tests.operations.test_local_quarantine_staging_model -v` | PASS |
| architecture | `python scripts/check_architecture_boundaries.py` | PASS |
| public-alpha readonly | `python scripts/validate_public_alpha_readonly.py` | PASS |
| snapshot relay | `python scripts/validate_snapshot_relay.py` | PASS |
| diff whitespace | `git diff --check` | PASS |

`python scripts/check_generated_artifact_cleanliness.py --check --json` reported
the intentional new audit directory before commit. It must be rerun after the
tracked repair commit.
