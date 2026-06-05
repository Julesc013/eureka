# Failure Family Inventory

## Taxonomy Summary

| Family | Families | Failed-test labels | Representative evidence |
|---|---:|---:|---|
| `queue_handoff_drift` | 23 | 39 | HUNT/LOCAL/promotion validators expect old queue or latest-packet state. |
| `architecture_boundary_drift` | 4 | 4 | Runtime/legacy leakage validators and strict repo-structure validator fail. |
| `source_snapshot_baseline_drift` | 1 | 2 | Source observation/local worker validation family reports `fail`. |
| `generated_artifact_drift` | 1 | 1 | Validator refuses forbidden output roots including `site/dist`. |
| `contract_schema_drift` | 1 | 1 | TSIS validator CLI returns non-zero. |

## Families

| Family ID | Taxonomy | Count | Representative test |
|---|---|---:|---|
| `unittest-0f464fcd3956bacd` | `queue_handoff_drift` | 1 | `tests.operations.test_search_hunt_exhaustion_scripts` |
| `unittest-16f561ced3cd9735` | `queue_handoff_drift` | 1 | `tests.operations.test_workunit_queue_scripts` |
| `unittest-17c94111c0f205a9` | `queue_handoff_drift` | 1 | `tests.operations.test_need_to_workunit_scripts` |
| `unittest-1d482963b26da899` | `queue_handoff_drift` | 1 | `tests.operations.test_search_hunt_ui_scripts` |
| `unittest-250024745e24b785` | `queue_handoff_drift` | 1 | `tests.operations.test_search_hunt_command_scripts` |
| `unittest-33a485f026ceb940` | `queue_handoff_drift` | 1 | `tests.operations.test_search_hunt_scripts` |
| `unittest-3a5d0577cb43afcc` | `queue_handoff_drift` | 1 | `tests.operations.test_local_http_service_scripts` |
| `unittest-44fed5e5e2c36f1d` | `queue_handoff_drift` | 1 | `tests.operations.test_background_hunt_runner_scripts` |
| `unittest-4d9516d5c8f96943` | `architecture_boundary_drift` | 1 | `tests.operations.test_legacy_runtime_leakage_remediation` |
| `unittest-59554bfe238d971c` | `queue_handoff_drift` | 1 | `tests.operations.test_local_instance_policy` |
| `unittest-5a3e0f743b54d6d5` | `queue_handoff_drift` | 1 | `tests.operations.test_search_hunt_track` |
| `unittest-65e7bb3c030eb3a5` | `queue_handoff_drift` | 1 | `tests.operations.test_local_workbench_scripts` |
| `unittest-6678b9a26758f460` | `queue_handoff_drift` | 9 | Operations script validators expecting old queue state. |
| `unittest-6e4a64768ed369aa` | `architecture_boundary_drift` | 1 | `tests.operations.test_runtime_architecture_leakage` |
| `unittest-78460b8abd53bf01` | `queue_handoff_drift` | 1 | `tests.operations.test_public_alpha_launch_defer` |
| `unittest-93ea91e09d10ac2b` | `queue_handoff_drift` | 1 | `tests.operations.test_local_appliance_track` |
| `unittest-a832b19b65e6f2ee` | `queue_handoff_drift` | 1 | `tests.operations.test_local_instance_bootstrap` |
| `unittest-a9849bf9f45ccc73` | `queue_handoff_drift` | 1 | `tests.operations.test_search_need_scripts` |
| `unittest-af0abc3ea9a15727` | `contract_schema_drift` | 1 | `tests.scripts.test_validate_temporal_semantic_interface_system` |
| `unittest-b55dda8683d18f5f` | `queue_handoff_drift` | 5 | Promotion, remediation, and TSIS validators with shared `fail` result. |
| `unittest-bb58d69e1df56823` | `architecture_boundary_drift` | 1 | Strict repo-structure validator subprocess error. |
| `unittest-c6c9edefc0b13811` | `queue_handoff_drift` | 1 | `tests.operations.test_local_appliance_track` |
| `unittest-cb1ded72f5fc441c` | `generated_artifact_drift` | 1 | `refusing forbidden output root: site/dist` |
| `unittest-d405c651b4c28b43` | `queue_handoff_drift` | 1 | `tests.operations.test_local_runtime_composition_scripts` |
| `unittest-e31dd26eed981165` | `source_snapshot_baseline_drift` | 2 | Local worker and source observation validation report `fail`. |
| `unittest-e63c0d0556f2cd2c` | `architecture_boundary_drift` | 1 | Repo structure canon reports `scripts` as unresolved debt. |
| `unittest-eac7722c1dba20f2` | `queue_handoff_drift` | 1 | HUNT track validator expects older current task. |
| `unittest-eff3fd626dda7803` | `queue_handoff_drift` | 5 | Clean-machine/local auto/local LAN/workbench validators expect LOCAL queue state. |
| `unittest-f19c87e169c8e5c5` | `queue_handoff_drift` | 1 | `tests.operations.test_local_instance_migration_guard` |
| `unittest-fb92c854e6cbd7ed` | `queue_handoff_drift` | 1 | `tests.operations.test_local_review_rebuild_smoke` |

## Notes

The external summary has one unittest error. It is classified here as
`architecture_boundary_drift` because the error is a strict repo-structure
validator subprocess failure, not Python unittest discovery failure.
