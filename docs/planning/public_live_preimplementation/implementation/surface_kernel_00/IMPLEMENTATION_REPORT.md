# Implementation Report

Task ID: `SURFACE-KERNEL-00`

Status: `PASS`.

## What Changed

Added the minimal checked-in SurfaceKernel foundation:

```text
runtime/surface/__init__.py
runtime/surface/kernel.py
runtime/surface/routes.py
runtime/surface/view_models.py
runtime/surface/capabilities.py
runtime/surface/profiles.py
runtime/surface/output_policy.py
runtime/surface/cache_key.py
runtime/surface/dispatch.py
runtime/surface/fallback.py
```

Added focused tests:

```text
tests/runtime/test_surface_kernel.py
tests/runtime/test_surface_output_policy.py
tests/runtime/test_surface_capability_negotiation.py
tests/runtime/test_surface_cache_key.py
```

## Existing Seams Used

The kernel adapts current payloads rather than calling source providers or stores:

```text
runtime.engine.interfaces.public.ResolutionRunRecord
runtime/gateway/public_api/resolution_runs_boundary.py output shape
runtime/gateway/public_api/public_search.py output shape
runtime/local/service/workbench_run_review_projection.py output shape
```

## Boundary Decision

Gateway modules were not changed to import `runtime.surface`. Current `AGENTS.md` dependency law limits gateway dependencies to public/service engine interfaces plus governed contract paths. SurfaceKernel can wrap gateway-shaped output without requiring gateway to depend on the broader runtime surface layer.

## Behavior

The new kernel coordinates:

```text
route resolution
profile negotiation
canonical view-model adaptation
public/private output policy filtering
cache key construction
renderer dispatch boundary
safe degraded-state projection
```

## Non-Behavior

No public route behavior changed.

No Workbench route behavior changed.

No renderer family was implemented beyond a renderer-ready dispatch boundary.

No source/provider call path was added.

No reviewed, public, or master index mutation was added.
