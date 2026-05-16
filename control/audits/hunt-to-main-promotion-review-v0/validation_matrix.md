# Validation Matrix

| validation_id | status | command |
| --- | --- | --- |
| git_diff_check | pass | git diff --check |
| aide_task_inspect | pass | py -3 .aide/scripts/aide_lite.py task inspect |
| aide_git_plan | pass | py -3 .aide/scripts/aide_lite.py git plan |
| aide_doctor | pass | py -3 .aide/scripts/aide_lite.py doctor |
| aide_validate | pass | py -3 .aide/scripts/aide_lite.py validate |
| aide_test | pass | py -3 .aide/scripts/aide_lite.py test |
| aide_selftest | pass | py -3 .aide/scripts/aide_lite.py selftest |
| aide_verify | pass | py -3 .aide/scripts/aide_lite.py verify |
| aide_review_pack | pass | py -3 .aide/scripts/aide_lite.py review-pack |
| aide_eval_run | pass | py -3 .aide/scripts/aide_lite.py eval run |
| hunt_validators | pass | all HUNT validators listed in task |
| local_dependency_validators | pass | all LOCAL dependency validators listed in task |
| full_unittest_discovery | pass | python -m unittest discover -s tests -t . |
| architecture_boundaries | pass | python scripts/check_architecture_boundaries.py |
| generated_artifact_cleanliness | pass | python scripts/check_generated_artifact_cleanliness.py --check --json |
| runtime_leakage | pass | python scripts/audit_runtime_architecture_leakage.py --check --json |
| runtime_leakage_validator | pass | python scripts/validate_runtime_architecture_leakage.py |
| report_size_validator | pass | python scripts/validate_aide_report_sizes.py --json |
