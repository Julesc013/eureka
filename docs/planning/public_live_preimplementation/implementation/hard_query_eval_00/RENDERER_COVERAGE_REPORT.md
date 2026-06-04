# Renderer Coverage Report

Task ID: `HARD-QUERY-EVAL-00`

## Profiles Covered

```text
json_v0
text_v0
html_basic_v0
snapshot_v0
```

## Coverage Checks

Focused tests verify:

```text
candidate remains candidate
need remains need
near_miss remains near_miss
policy_blocked remains policy_blocked
unavailable remains unavailable
unknown status degrades to unknown
json_v0 exposes machine-readable status
text_v0 exposes status and uncertainty/reason text
html_basic_v0 escapes unsafe fixture text
snapshot_v0 is deterministic for the same fixture
```

## Renderer Boundary

All renderer checks go through `SurfaceKernel` and `dispatch_surface_renderer(...)`. Renderers receive policy-filtered view models and do not call source providers or mutate indexes.
