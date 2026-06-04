# Baseline Renderers 00

Task ID: `BASELINE-RENDERERS-00`

Status: `PASS`.

This package records the first concrete renderer implementation over the checked-in `runtime/surface` SurfaceKernel boundary.

## What This Task Does

Adds built-in renderers for:

```text
json_v0
text_v0
html_basic_v0
snapshot_v0
```

The renderers consume SurfaceKernel policy-filtered view models through `runtime/surface/dispatch.py`.

## What This Task Does Not Do

This task does not rewire gateway routes, call source providers, create review decisions, promote candidates, mutate indexes, or launch public alpha behavior.

## Read Next

- `IMPLEMENTATION_REPORT.md`
- `RENDERER_CONTRACT_REPORT.md`
- `PROFILE_SUPPORT_MATRIX.md`
- `PUBLIC_PRIVATE_ACTION_AUDIT.md`
- `DEGRADATION_AND_COMPATIBILITY_REPORT.md`
- `VALIDATION_REPORT.md`

## Next Task

Recommended next task: `HARD-QUERY-EVAL-00`.
