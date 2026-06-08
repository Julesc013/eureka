# Failure Labels Targeted

## Source

External run:

```text
../eureka-test-runs/source_snapshot_baseline_closeout_01/full_unittest_summary.json
```

Ingest package reported:

```text
queue_handoff_drift: 23 families, 39 failed-test labels
```

## Targeted Families

| Family ID | Count | Representative label | Planned repair |
|---|---:|---|---|
| `unittest-0f464fcd3956bacd` | 1 | `test_search_hunt_exhaustion_scripts` | HUNT advanced-task helper |
| `unittest-16f561ced3cd9735` | 1 | `test_workunit_queue_scripts` | LOCAL advanced-task helper |
| `unittest-17c94111c0f205a9` | 1 | `test_need_to_workunit_scripts` | HUNT advanced-task helper |
| `unittest-1d482963b26da899` | 1 | `test_search_hunt_ui_scripts` | HUNT advanced-task helper |
| `unittest-250024745e24b785` | 1 | `test_search_hunt_command_scripts` | HUNT advanced-task helper |
| `unittest-33a485f026ceb940` | 1 | `test_search_hunt_scripts` | HUNT advanced-task helper |
| `unittest-3a5d0577cb43afcc` | 1 | `test_local_http_service_scripts` | LOCAL advanced-task helper |
| `unittest-44fed5e5e2c36f1d` | 1 | `test_background_hunt_runner_scripts` | HUNT advanced-task helper |
| `unittest-59554bfe238d971c` | 1 | `test_local_instance_policy` | LOCAL advanced-task helper |
| `unittest-5a3e0f743b54d6d5` | 1 | `test_search_hunt_track` | HUNT advanced-task helper |
| `unittest-65e7bb3c030eb3a5` | 1 | `test_local_workbench_scripts` | LOCAL advanced-task helper |
| `unittest-6678b9a26758f460` | 9 | operations script validators | queue/handoff successor repair |
| `unittest-78460b8abd53bf01` | 1 | `test_public_alpha_launch_defer` | launch-defer validator successor repair |
| `unittest-93ea91e09d10ac2b` | 1 | `test_local_appliance_track` | local appliance successor repair |
| `unittest-a832b19b65e6f2ee` | 1 | `test_local_instance_bootstrap` | LOCAL advanced-task helper |
| `unittest-a9849bf9f45ccc73` | 1 | `test_search_need_scripts` | HUNT advanced-task helper |
| `unittest-b55dda8683d18f5f` | 5 | promotion/remediation/TSIS validators | repaired queue subset; TSIS reclassified |
| `unittest-c6c9edefc0b13811` | 1 | `test_local_appliance_track` | local appliance successor repair |
| `unittest-d405c651b4c28b43` | 1 | `test_local_runtime_composition_scripts` | LOCAL advanced-task helper |
| `unittest-eac7722c1dba20f2` | 1 | `test_search_hunt_track` | HUNT advanced-task helper |
| `unittest-eff3fd626dda7803` | 5 | clean/local LAN/workbench validators | LOCAL advanced-task helper |
| `unittest-f19c87e169c8e5c5` | 1 | `test_local_instance_migration_guard` | LOCAL advanced-task helper |
| `unittest-fb92c854e6cbd7ed` | 1 | `test_local_review_rebuild_smoke` | LOCAL advanced-task helper |

## Outcome

Queue-specific labels were repaired in focused split lanes. One label from the
original queue family, `ValidateTemporalSemanticInterfaceSystemTest.test_validator_passes`,
still fails for contract-schema/runtime-surface phase drift and is reclassified
as `contract_schema_drift`.
