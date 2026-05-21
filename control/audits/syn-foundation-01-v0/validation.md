# Validation

Final closeout commands:

```text
PASS python scripts/eureka_test_select.py --changed --failed-first --json
PASS python scripts/validate_syn_foundation.py
PASS python scripts/validate_search_need_seed_candidates.py
PASS python scripts/validate_workunit_seed_candidates.py
PASS python scripts/validate_ia_hunt_bridge.py
PASS python scripts/validate_workbench_result_lanes.py
PASS python scripts/validate_search_interaction_contract.py
PASS python scripts/validate_contract_taxonomy.py
PASS python scripts/validate_contract_taxonomy_plan.py
PASS python scripts/validate_test_lane_policy.py
PASS python scripts/validate_repo_structure_canon.py
PASS python -m unittest tests.scripts.test_validate_syn_foundation tests.operations.test_syn_foundation
PASS python -m unittest discover -s tests -t . (4814 tests, 2506.187s)
```
