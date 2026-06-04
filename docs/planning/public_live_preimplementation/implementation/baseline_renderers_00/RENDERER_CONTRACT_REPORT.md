# Renderer Contract Report

Task ID: `BASELINE-RENDERERS-00`

## Contract

Renderer input:

```text
SurfaceKernel policy-filtered view model
representation profile
public/private posture already applied
```

Renderer output:

```text
schema_version
representation_profile
media_type
content_format
content
```

## Purity Rules

The renderer boundary preserves these rules:

```text
renderers do not query sources
renderers do not call source providers
renderers do not mutate the input view model
renderers do not create review decisions
renderers do not create reviewed records
renderers do not promote candidates
renderers do not mutate reviewed/public/master indexes
renderers do not decide policy
renderers do not re-add filtered public actions
```

## Dispatch Integration

`runtime/surface/dispatch.py` deep-copies the policy-filtered view model before rendering and records guard flags:

```text
renderer_input_mutated
renderer_called_source_provider
renderer_created_verified_state
renderer_mutated_reviewed_index
renderer_mutated_public_index
renderer_mutated_master_index
```

All focused tests assert the guard flags remain false for baseline renderer paths.

## Cache Posture

`runtime/surface/kernel.py` derives the effective renderer id before cache-key construction so the cache key distinguishes renderer/profile combinations.
