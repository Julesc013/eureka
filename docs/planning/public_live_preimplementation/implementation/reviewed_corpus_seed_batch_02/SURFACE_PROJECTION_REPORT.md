# Surface Projection Report

Batch 02 adds SurfaceKernel fixtures and renderer expectations for:

- `verified`
- `need`
- `near_miss`
- `superseded`

Expected behavior:

- Public projection strips operator-only actions.
- Operator-private projection may retain review actions.
- HTML output escapes unsafe text.
- Snapshot output is deterministic.
- Renderers do not create truth.
- Renderers do not call source providers.
- Renderers do not mutate reviewed, public, or master indexes.
