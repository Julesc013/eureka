# Validation Matrix

| Command | Status |
| --- | --- |
| `python scripts/validate_test_run_summary.py ../eureka-test-runs/source_snapshot_closeout/full_unittest_summary.json --json` | PASS |
| `python scripts/validate_source_snapshot_baseline_closeout.py` | PASS |
| `python scripts/validate_source_action_kernel.py` | PASS |
| `python scripts/validate_source_wave.py` | PASS |
| `python scripts/validate_snapshot_relay.py` | PASS |
| `python scripts/check_architecture_boundaries.py` | PASS |
| `python scripts/check_generated_artifact_cleanliness.py --check --json` | post_commit_required |
| `python scripts/validate_dev_to_main_promotion_03.py` | PASS |
| `python -m unittest tests.operations.test_dev_to_main_promotion_03` | PASS |
| `python -m unittest tests.scripts.test_validate_dev_to_main_promotion_03` | PASS |
| `python .aide/scripts/aide_lite.py doctor` | PASS |
| `python .aide/scripts/aide_lite.py validate` | PASS |
| `python .aide/scripts/aide_lite.py test` | PASS |
| `python .aide/scripts/aide_lite.py selftest` | PASS |
| `python .aide/scripts/aide_lite.py verify` | PASS_WITH_WARNINGS |
| `python .aide/scripts/aide_lite.py review-pack` | PASS |

Full unittest discovery was not rerun inside the AI session.
