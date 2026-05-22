# Post Resolution Run Kernel Plan

Recommended sequence:

1. `WORKBENCH-LIVE-RUN-01` - project headless run creation and lane snapshots into the local Workbench.
2. `IA-LIVE-METADATA-LANE-01` - add explicit operator-approved live IA metadata lane policy.
3. `WORKBENCH-REVIEW-PROMOTE-01` - add browser review and promotion preview flow.
4. `LOCAL-APPLY-GATE-01` - add operator token, backup, audit, and rollback gate for explicit instance writes.
5. `SOURCE-WAVE-00` - add more source-family metadata waves through the same kernel.

Source expansion is intentionally deferred until Workbench/API projections use
the shared kernel.
