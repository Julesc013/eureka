# Renderer Boundary

Implemented boundary:

```text
runtime/surface/dispatch.py
dispatch_surface_renderer(...)
```

The dispatch function receives a policy-filtered view model and passes a deep copy to an optional renderer callable.

Renderer dispatch records:

```text
renderer_called_source_provider = false
renderer_created_verified_state = false
renderer_mutated_reviewed_index = false
renderer_mutated_public_index = false
renderer_mutated_master_index = false
```

This task intentionally does not add full renderers. The default dispatch output is a renderer-ready payload.

`BASELINE-RENDERERS-00` should add:

```text
json_v0
text_v0
html_basic_v0
snapshot_v0
```

over this boundary.
