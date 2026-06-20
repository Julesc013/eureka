# Validation Report

Status: PREPARATION_VALIDATION_PASS_WITH_POSTCOMMIT_CLEANLINESS_REQUIRED

## Completed Preflight

| Command | Result |
| --- | --- |
| `git fetch origin` | PASS |
| `git status --short --branch` | PASS, clean `dev...origin/dev` |
| `git rev-list --left-right --count origin/main...origin/dev` | PASS, `0 16` |
| `python scripts/check_git_task_state.py --mode start-task --task-id HUMAN-END-TO-END-ACCEPTANCE-00` | WARN, only long-lived branch/task-ID warning |
| `python scripts/eureka.py --instance ../instances/eureka-e2e-acceptance-v0 bootstrap --json` | PASS |
| repeated bootstrap | PASS |
| `python scripts/eureka.py --instance ../instances/eureka-e2e-acceptance-v0 doctor --strict --json` | PASS |
| `python scripts/eureka.py --instance ../instances/eureka-e2e-acceptance-v0 test --suite core --json` | PASS |
| `python scripts/eureka.py --instance ../instances/eureka-e2e-acceptance-v0 status --json` | PASS |
| `python scripts/eureka.py --instance ../instances/eureka-e2e-acceptance-v0 serve --mode exploration --host 127.0.0.1 --port 0 --smoke --json` | PASS |

## Focused Validation

| Command | Result |
| --- | --- |
| `python -m unittest tests.e2e.test_portable_eureka_clean_machine tests.e2e.test_portable_eureka_instance tests.e2e.test_e2e_hunt_exploration_ui -v` | PASS, 5 tests |
| `python scripts/check_architecture_boundaries.py` | PASS |
| `python scripts/validate_runtime_architecture_leakage.py --json` | PASS, status valid |
| `python scripts/validate_public_alpha_readonly.py` | PASS, valid |
| `python scripts/validate_snapshot_relay.py` | PASS |
| `python scripts/eureka_test_select.py --changed --failed-first --json` | PASS, selected L0 static preflight only |
| `git diff --check` | PASS |
| `py -3 .aide/scripts/aide_lite.py doctor` | PASS |
| `py -3 .aide/scripts/aide_lite.py validate` | PASS |

## Generated Artifact Cleanliness

`python scripts/check_generated_artifact_cleanliness.py --check --json` reported the new audit packet as generated drift before commit:

```text
control/audits/e2e_reference_system/human_end_to_end_acceptance_v0/
```

This is expected for an intentional new tracked audit packet. Rerun the check after the preparation commit.

Full unittest discovery is not run inside this acceptance preparation task.
