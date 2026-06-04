# Surface Projection Report

Task ID: `MANUAL-OBSERVATION-BATCH-00`

Manual observations are projected through:

```text
evals.hard_queries.manual_observations.batch_00.project_observation
runtime.surface.SurfaceKernel
runtime.surface.renderers
```

Focused tests verify:

```text
candidate remains candidate
need remains need
near_miss remains near_miss
unavailable remains unavailable
policy_blocked degrades honestly when supplied
public posture strips operator-only actions
operator posture can retain review handoff actions
JSON/text/html_basic/snapshot renderers preserve status
HTML output escapes unsafe text
snapshot output is deterministic
no source/provider call or index mutation occurs
```
