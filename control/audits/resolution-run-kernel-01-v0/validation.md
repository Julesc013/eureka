# Validation

Commands run:

```text
git diff --check
python scripts/eureka_test_select.py --changed --failed-first --json
python scripts/validate_resolution_run_kernel.py --json
python scripts/check_architecture_boundaries.py
python scripts/check_generated_artifact_cleanliness.py --check --json
python scripts/validate_contract_taxonomy.py
python scripts/validate_repo_structure_canon.py
python scripts/validate_test_lane_policy.py
python scripts/validate_ia_hunt_bridge.py
python scripts/validate_workbench_result_lanes.py
python scripts/validate_search_interaction_contract.py
python scripts/validate_workbench_foundation.py
python scripts/validate_g0_foundation.py
python scripts/validate_f0_foundation.py
python scripts/validate_scout_schema.py
python scripts/validate_domain_packs.py
python scripts/validate_syn_foundry.py
python -m unittest tests.runtime.test_resolution_run_kernel tests.runtime.test_resolution_run_projection tests.operations.test_resolution_run_scripts tests.scripts.test_validate_resolution_run_kernel
python -m unittest tests.operations.test_contract_taxonomy tests.operations.test_repo_structure_canon tests.scripts.test_validate_test_lane_policy tests.scripts.test_eureka_test_select tests.operations.test_test_lane_policy tests.operations.test_test_impact_map tests.operations.test_test_failure_ledger
python -m unittest tests.operations.test_hunt_remediation tests.operations.test_hunt_remediation_continue tests.operations.test_local_appliance_track tests.operations.test_search_hunt_closeout tests.operations.test_search_hunt_track
python scripts/validate_hunt_remediation.py
python scripts/validate_hunt_remediation_continue.py
python scripts/validate_local_appliance_track.py
python scripts/validate_search_hunt_track.py
python scripts/validate_search_hunt_closeout.py
python -m unittest discover -s tests -t .
```

The first full discovery found older HUNT/LOCAL validator allowlists that did
not recognize the run-kernel and Workbench live-run handoff. After a focused
allowlist repair, full discovery passed with 4880 tests.
