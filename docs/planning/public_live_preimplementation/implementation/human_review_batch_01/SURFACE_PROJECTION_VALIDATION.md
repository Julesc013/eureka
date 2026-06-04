# Surface Projection Validation

The batch includes projection fixtures and renderer expectations for:

```text
json_v0
text_v0
html_basic_v0
snapshot_v0
```

Expected public statuses:

```text
verified
need
near_miss
superseded
```

Public projection must strip operator-only actions. Operator-private projection may retain review actions for private Workbench-style inspection.

Renderers consume SurfaceKernel view models and do not call sources or mutate indexes.
