# Post Dev IA Promotion Plan

After `DEV-AND-IA-PROMOTION-BLOCKER-01`, rerun the dev/IA promotion review and
promote `main` only if the repaired full-discovery gate remains green.

Required order:

1. `DEV-AND-IA-TO-MAIN-PROMOTION-REVIEW`
2. `REPO-LAYOUT-CANON-01` verification/re-run before layout-sensitive Workbench work
3. `WORKBENCH-FOUNDATION-00`
4. `SEARCH-INTERACTION-00`
5. `WORKBENCH-RESULT-LANES-01`
6. `IA-HUNT-BRIDGE-00`

The promoted baseline, if the next review passes, is still only:

```text
IA metadata-only local vertical slice plus repo layout canon baseline plus full-discovery blocker repair
```

It is not production readiness.
It is not public launch readiness.
It is not full Archive.org integration.
It is not marketplace or app-store readiness.
It is not public source fanout, downloads, extraction, or AI/model-provider use.
It is not a repo layout move or Workbench implementation task.
