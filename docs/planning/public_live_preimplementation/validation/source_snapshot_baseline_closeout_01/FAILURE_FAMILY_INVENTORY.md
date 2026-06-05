# Failure Family Inventory

No current-head full-discovery failure family is available yet.

## Current Evidence

External summaries were found under `../eureka-test-runs/`, but they are stale:

| Run | Status | Tests | Head | Current? |
|---|---|---:|---|---|
| `source_snapshot_closeout` | `pass` | 5008 | `994657d182caf288512a9b202d071152e2ca8f8f` | no |
| `promotion_gate` | `pass` | 5081 | `8f02824e0fb87431e104a63516af74089fbb461d` | no |

## Historical Families To Watch

Older closeout inventory recorded these historical blockers:

| Family | Historical Count | Status Now | Promotion Impact | Public Alpha Impact |
|---|---:|---|---|---|
| `checksum_manifest_drift` | 46 | `STALE_OR_UNVERIFIED` | blocks if repeated in current summary | blocks if repeated |
| `queue_handoff_drift` | 38 | `STALE_OR_UNVERIFIED` | blocks if repeated in current summary | blocks if repeated |
| `public_index_generated_drift` | 5 | `STALE_OR_UNVERIFIED` | blocks if repeated in current summary | blocks if repeated |
| `legacy_leakage_validator_drift` | 2 | `STALE_OR_UNVERIFIED` | blocks if repeated in current summary | blocks if repeated |
| `generated_artifact_cleanliness_drift` | 0 current safe-check evidence | `PASS_CURRENT` once validation reruns | monitor | monitor |
| `architecture_boundary_drift` | 0 current safe-check evidence | `PASS_CURRENT` once validation reruns | monitor | monitor |

## Rule

Do not start a targeted repair task from stale families alone. Run
`EXTERNAL-FULL-DISCOVERY-RUN-01` first.
