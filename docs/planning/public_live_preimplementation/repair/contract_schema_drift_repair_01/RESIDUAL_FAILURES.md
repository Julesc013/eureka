# Residual Failures

| Family | Status | Notes |
|---|---|---|
| `contract_schema_drift` | repaired in focused validation | TSIS validator now passes locally. |
| `generated_artifact_drift` | previously repaired | Fixed by `GENERATED-ARTIFACT-DRIFT-REPAIR-01`. |
| `source_snapshot_baseline_drift` | previously repaired | Fixed by `SOURCE-SNAPSHOT-BASELINE-DRIFT-REPAIR-01`. |
| `queue_handoff_drift` | previously repaired | Fixed by `QUEUE-HANDOFF-DRIFT-REPAIR-01`. |
| `architecture_boundary_drift` | previously repaired | Fixed by `ARCHITECTURE-BOUNDARY-DRIFT-REPAIR-01`. |

## Gates

| Gate | Status |
|---|---|
| public alpha | blocked |
| `dev -> main` | blocked |
| source/snapshot release gate | blocked pending external full-discovery rerun |

Do not claim release readiness until an external full-discovery rerun is current
to the repaired HEAD.

