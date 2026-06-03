# Surface Kernel Spec

## Purpose

The SurfaceKernel projects canonical view models into public web, API, text,
snapshot, Workbench, and future client representations.

## Responsibilities

- route resolution
- view-model loading
- capability negotiation
- representation selection
- renderer dispatch
- cache key generation
- output policy enforcement
- fallback generation
- public/private visibility filtering

## Pure Renderer Contract

```text
view_model + representation_profile + skin + policy_context
-> representation
```

Renderers must not query sources, mutate records, promote candidates, infer
facts, change policy, hide status, or expose forbidden actions.

## Current State

TSIS-00 documented future `runtime/surface/**` placement. Runtime SurfaceKernel
implementation remains deferred unless a later task authorizes it.

