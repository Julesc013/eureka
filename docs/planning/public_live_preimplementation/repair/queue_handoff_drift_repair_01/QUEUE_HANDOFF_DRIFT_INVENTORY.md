# Queue Handoff Drift Inventory

| Category | Evidence | Repair |
|---|---|---|
| `stale_queue_index` | `.aide/queue/index.yaml` pointed to `INDEXLESS-LIVE-SEARCH-FALLBACK-00` | Updated current task to `QUEUE-HANDOFF-DRIFT-REPAIR-01` |
| `stale_latest_task_packet` | `.aide/context/latest-task-packet.md` pointed to `SOURCE-SNAPSHOT-BASELINE-CLOSEOUT-01` | Refreshed through AIDE Lite pack |
| `stale_next_implementation_handoff` | Handoff recommended fallback preflight | Replaced with queue-handoff repair handoff |
| `stale_readme_roadmap` | README roadmap listed deploy/launch as next | Replaced with validation repair sequence |
| `stale_public_live_queue_docs` | Execution queue/DAG named fallback as current | Updated to completed/current repair posture |
| `validator_expectation_drift` | HUNT/LOCAL validators required old successor tasks | Extended advanced-task checks to current repair chain |
| `stale_launch_gate_state` | Launch-defer validator required old active-discovery queue forever | Allowed later blocked repair/readiness tasks |
| `stale_commit_head_reference` | External ingest remains current to `aad4517b`; repo is now later | Recorded as expected after repairs; rerun external discovery later |

## Reclassified Residual

`ValidateTemporalSemanticInterfaceSystemTest.test_validator_passes` reports:

```text
TSIS-00 must not add runtime phase file: runtime/surface/cache_key.py
TSIS-00 must not add runtime phase file: runtime/surface/fallback.py
TSIS-00 must not add runtime phase file: runtime/surface/kernel.py
TSIS-00 must not add runtime phase file: runtime/surface/output_policy.py
```

This is contract/schema phase drift, not queue-handoff drift.
