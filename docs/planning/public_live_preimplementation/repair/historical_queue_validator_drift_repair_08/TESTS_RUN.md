# Tests Run

Focused compile:

```text
python -m py_compile tools\generators\hunt_queue_progress.py scripts\validate_public_alpha_launch_defer.py scripts\validate_dev_to_main_promotion_03.py scripts\validate_dev_to_main_promotion_04.py
```

Result: `PASS`

Representative focused bundle:

```text
python -m unittest tests.operations.test_hunt_main_promotion_gates tests.operations.test_search_hunt_track tests.operations.test_public_alpha_launch_defer tests.operations.test_dev_to_main_promotion_03 tests.operations.test_dev_to_main_promotion_04 tests.scripts.test_validate_dev_to_main_promotion_03 tests.scripts.test_validate_dev_to_main_promotion_04
```

Result:

```text
tests_run: 38
failures: 0
errors: 0
```

Exact rerun-08 failed modules:

```text
python -m unittest tests.operations.test_agent_research_scripts tests.operations.test_ai_escalation_scripts tests.operations.test_background_hunt_runner_scripts tests.operations.test_dev_to_main_promotion_03 tests.operations.test_dev_to_main_promotion_04 tests.operations.test_hunt_remediation tests.operations.test_hunt_remediation_continue tests.operations.test_hunt_replay_scripts tests.operations.test_need_to_workunit_scripts tests.operations.test_public_alpha_launch_defer tests.operations.test_search_hunt_closeout tests.operations.test_search_hunt_command_scripts tests.operations.test_search_hunt_exhaustion_scripts tests.operations.test_search_hunt_scripts tests.operations.test_search_hunt_track tests.operations.test_search_hunt_ui_scripts tests.operations.test_search_need_scripts tests.scripts.test_validate_dev_to_main_promotion_03 tests.scripts.test_validate_dev_to_main_promotion_04
```

Result:

```text
tests_run: 63
failures: 0
errors: 0
```

Standard validation is recorded in `VALIDATION_REPORT.md`.

