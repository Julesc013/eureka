# Public Surface Report

## Public Route Boundary

The public gateway route does not import or own the IA provider.

```text
runtime/gateway/public_api/resolution_runs_boundary.py imports IA provider: false
public route direct source call: false
```

## SurfaceKernel Boundary

SurfaceKernel receives a completed resolution run and projects it into
renderer-ready view models. It does not call source providers.

```text
surface_kernel_called_source_provider: false
renderer_called_source_provider: false
renderer_mutated_reviewed_index: false
renderer_mutated_public_index: false
renderer_mutated_master_index: false
```

Public posture strips operator-only actions from nested fallback action fields.

