# Validation

Validation commands for INSTANCE-LAYOUT-01:

```text
git status --short
git diff --check
python -m json.tool control/policies/instance_layout_policy.json
python -m json.tool control/inventory/instance_layout_current_policy.json
python -m json.tool control/inventory/instance_layout_migration_plan.json
python -m json.tool control/inventory/instance_layout_result.json
python -m json.tool control/inventory/instance_layout_next_task_decision.json
python -m json.tool control/audits/instance-layout-01-v0/instance_layout_report.json
python scripts/eureka_resolve_paths.py --json
python scripts/eureka_list_instances.py --json
python scripts/eureka_migrate_instance_layout.py --from ../eureka-instance --to ../instances/default --dry-run --json
python scripts/validate_instance_layout_policy.py
python -m unittest tests.runtime.test_local_appliance_paths
python -m unittest tests.operations.test_instance_layout_policy
python -m unittest tests.operations.test_instance_layout_scripts
python scripts/check_architecture_boundaries.py
python scripts/check_generated_artifact_cleanliness.py --check --json
python -m unittest discover -s tests -t .
python .aide/scripts/aide_lite.py doctor
python .aide/scripts/aide_lite.py validate
python .aide/scripts/aide_lite.py test
python .aide/scripts/aide_lite.py selftest
python .aide/scripts/aide_lite.py verify
python .aide/scripts/aide_lite.py review-pack
```

Results are reported in the final task response. No validation command moves
or deletes the operator instance.

Full unittest discovery warning:

- `python -m unittest discover -s tests -t .` ran 4,557 tests and failed with
  21 failures. The task-focused tests passed. The broad failures were from
  legacy/current-task validators expecting SYN-00 or a clean uncommitted tree,
  plus clean-machine scripts that still create a repo-nested instance path
  outside this task's allowed edit scope.
