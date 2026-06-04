# SurfaceKernel Decisions

## Decision: Add Runtime Surface Boundary

`runtime/surface` already existed as an ignored cache footprint, but it had no checked-in source files. This task adds the real runtime modules there rather than creating a new top-level root.

## Decision: Adapt Existing Payloads

SurfaceKernel accepts already-built payloads and adapts them into canonical view models.

It does not call:

```text
source providers
review stores
fallback providers
gateway public APIs
Workbench routes
renderers that own policy
```

## Decision: Keep Gateway Imports Unchanged

The public gateway remains unchanged. Tests prove SurfaceKernel can wrap public run output, but gateway does not import the surface kernel in this task.

## Decision: Renderer Boundary Before Renderers

`runtime/surface/dispatch.py` provides the renderer boundary. Full JSON/text/basic HTML/snapshot renderers are left for `BASELINE-RENDERERS-00`.

## Remaining Gaps

Operator auth remains outside this task.

Real renderers are deferred.

Direct route integration into web/API/CLI surfaces is deferred until the baseline renderer and route-adapter work.
