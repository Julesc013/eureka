# Preflight

## Existing Seams Found

```text
runtime/engine/resolution_runs/service.py
runtime/source/observation/archive_org_public_metadata.py
runtime/source/observation/internet_archive_live_transport.py
runtime/surface/kernel.py
runtime/surface/view_models.py
runtime/surface/renderers/
runtime/gateway/public_api/resolution_runs_boundary.py
```

## Existing Controls Found

```text
fallback enabled/disabled
source allowlist
source-family disable
max request budget
candidate limit
timeout budget
public/private SurfaceKernel posture
renderer no-source-call flags
mutation flags
```

## Decision

```text
DECISION: WIRE_EXISTING_IA_TRANSPORT_THROUGH_ENGINE_FALLBACK
```

No safe reason was found to create a broad new provider framework.

