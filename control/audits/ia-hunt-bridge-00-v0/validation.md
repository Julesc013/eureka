# Validation

Selected lane validation was used during development:

```text
python scripts/eureka_test_select.py --changed --failed-first --json
```

Focused validators and tests passed:

```text
python scripts/validate_ia_hunt_bridge.py
python scripts/validate_workbench_result_lanes.py
python scripts/validate_search_interaction_contract.py
python scripts/validate_workbench_foundation.py
python scripts/validate_test_lane_policy.py
python scripts/validate_contract_taxonomy.py
python scripts/validate_repo_structure_canon.py
python -m unittest tests.runtime.test_ia_hunt_bridge tests.runtime.test_ia_hunt_workunits tests.runtime.test_ia_hunt_result_lanes
python -m unittest tests.operations.test_ia_hunt_bridge_scripts tests.operations.test_ia_hunt_bridge_smoke tests.scripts.test_validate_ia_hunt_bridge
```

Full discovery passed after repairing the import cycle:

```text
python -m unittest discover -s tests -t .
Ran 4809 tests in 2915.768s
OK
```
