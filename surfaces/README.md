# Surfaces

`surfaces/` contains Eureka's user-facing applications and projection notes.
Bootstrap keeps each surface family separate so dependency rules stay explicit.

- `web/` uses gateway public APIs and contracts in the normal online path
- `cli/` is the current local stdlib CLI surface
- `api/` records API projection ownership; runtime service behavior remains in `runtime/gateway/`
- `text/`, `files/`, and `lite/` record static projection families emitted under `site/dist/`
- `native/` uses contracts and gateway public APIs in the normal path, with any future engine SDK use explicitly gated to offline or local mode

Current bootstrap proof points:

- `web/` contains the compatibility-first HTML workbench slice
- `cli/` contains the first non-web surface slice, proving reuse across surface families without direct engine imports from the surface layer
