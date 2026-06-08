# File Change Plan

| Path | Classification | Reason | Risk | Rollback |
|---|---|---|---|---|
| `runtime/source/observation/internet_archive_live_transport.py` | expected modify | Remove alternate shell fallback that violates the source-observation seam baseline. | Low to medium; IA TLS failures now degrade instead of trying shell fallback. | Restore previous fallback only with explicit source policy and validator update. |
| `tests/runtime/test_ia_live_transport.py` | expected modify | Add regression coverage for TLS failure degraded state. | Low. | Remove the added test if the runtime policy changes through a later approved task. |
| `.aide/queue/index.yaml` | expected modify | Move this repair into completed state and recommend the next drift family. | Low; operating metadata only. | Restore prior queue state if a later external run supersedes this repair. |
| `docs/planning/public_live_preimplementation/repair/source_snapshot_baseline_drift_repair_01/**` | expected add | Required repair package and validation handoff. | Low; docs/evidence only. | Delete package if superseded by a rerun-specific package. |
| `snapshots/**` | avoid | No targeted snapshot artifact change was required. | High if hand-edited. | Use generators in a future task only. |
| `site/**` | avoid | No public/generated site artifact change was required. | High if hand-edited. | Use repo-approved generators in a future task only. |
| `contracts/**` | avoid | Contract/schema drift is a separate family. | High if broadened here. | Defer to `CONTRACT-SCHEMA-DRIFT-REPAIR-01`. |

