# Public Private Action Audit

Task ID: `BASELINE-RENDERERS-00`

## Public Behavior

Public SurfaceKernel posture applies output policy before renderer dispatch.

Focused tests prove public renderer output excludes:

```text
review_candidate
promote
reject
rebuild_index
freeze_review
```

Public renderer output may include read-only actions such as:

```text
view
inspect_evidence
cite
```

## Private Behavior

Private/operator Workbench-shaped projections may retain supplied operator actions after SurfaceKernel policy application.

Focused tests prove `json_v0` can render private Workbench action ids including:

```text
review_candidate
promote
```

## Boundary Result

Renderers consume the action posture they receive. They do not add actions, classify permissions, or expose private actions in public posture.
