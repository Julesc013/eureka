# Validation Matrix

|command|status|notes|
|---|---|---|
|python scripts/check_git_task_state.py --mode start-task --task-id EUREKA-FINAL-STATE-PROMOTION-PLAN-01|warn|Allowed branch-name warning on dev; working tree was clean.|
|git diff --check|pass||
|python -m unittest discover -s tests -t .|pass||
|python scripts/check_architecture_boundaries.py|pass||
|python scripts/check_generated_artifact_cleanliness.py --check --json|pass_after_commit_validation_required|Pre-commit check fails only because this final audit pack is uncommitted; rerun after commit is required.|
|python scripts/audit_runtime_architecture_leakage.py --check --json|pass_with_warnings||
|python scripts/validate_runtime_architecture_leakage.py|pass||
|LOCAL and R0 validator sweep|pass_with_warnings|All validators pass or pass_with_warnings; generated-artifact validator is expected to pass after commit.|
|py -3 .aide/scripts/aide_lite.py doctor|pass||
|py -3 .aide/scripts/aide_lite.py validate|pass_with_warnings||
|py -3 .aide/scripts/aide_lite.py test|pass||
|py -3 .aide/scripts/aide_lite.py selftest|pass||
|py -3 .aide/scripts/aide_lite.py verify|warn||
|py -3 .aide/scripts/aide_lite.py review-pack|pass_with_warnings||
