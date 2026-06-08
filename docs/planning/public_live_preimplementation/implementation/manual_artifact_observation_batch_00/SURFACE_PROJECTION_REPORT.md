# Surface Projection Report

Surface projection fixtures were added for candidate, need, near-miss, and unavailable artifact-observation states.

The projection helper sends observations through `runtime.surface.SurfaceKernel` with already-bounded manual-observation payloads. It does not call source providers, expose public operator actions, create verified state, or mutate indexes.

Renderer expectations cover:

```text
json_v0
text_v0
html_basic_v0
snapshot_v0
```
