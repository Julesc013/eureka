# Validation Matrix

```json
{
  "focused_test_modules": [
    "tests.runtime.test_snapshot_build",
    "tests.runtime.test_snapshot_manifest",
    "tests.runtime.test_snapshot_integrity",
    "tests.runtime.test_snapshot_records",
    "tests.runtime.test_relay_manifest",
    "tests.runtime.test_relay_projection",
    "tests.runtime.test_relay_read_only",
    "tests.runtime.test_capability_profile",
    "tests.operations.test_snapshot_relay_scripts",
    "tests.operations.test_snapshot_relay_smoke",
    "tests.scripts.test_validate_snapshot_relay"
  ],
  "full_discovery_deferred_reason": "Selector deferred full discovery for per-commit default; focused validators and tests passed, with existing known out-of-scope discovery debt deferred to a promotion/release gate.",
  "lanes": {
    "aide_checks": "pass_with_verify_warnings",
    "architecture_boundaries": "pass",
    "contract_taxonomy": "pass",
    "domain_packs": "pass",
    "f0_foundation": "pass",
    "focused_tests": "pass",
    "full_unittest_discovery": "not_run_deferred_known_out_of_scope_debt",
    "g0_foundation": "pass",
    "generated_artifact_cleanliness": "warn_audit_pack_classified_as_generated_drift",
    "ia_hunt_bridge": "pass",
    "ia_live_metadata_lane": "pass",
    "local_apply_gate": "pass",
    "repo_structure_canon": "pass",
    "resolution_run_kernel": "pass",
    "scout_schema": "pass",
    "search_interaction": "pass",
    "snapshot_relay": "pass",
    "source_action_kernel": "pass",
    "source_wave": "pass",
    "syn_foundry": "pass",
    "test_lane_policy": "pass",
    "test_selector": "pass",
    "workbench_foundation": "pass",
    "workbench_live_run": "pass",
    "workbench_local_loop_closeout": "pass",
    "workbench_result_lanes": "pass",
    "workbench_review_promote": "pass"
  },
  "schema_version": "snapshot_relay_validation_matrix.v0",
  "status": "pass_with_warnings",
  "task": "AIDE-BATCH-SNAPSHOT-RELAY-00",
  "warnings": [
    "AIDE verify returned warnings for context packet references but no errors.",
    "check_generated_artifact_cleanliness.py classifies the required new snapshot-relay audit pack as generated drift; global generated-artifact policy changes are outside this task scope."
  ]
}
```
