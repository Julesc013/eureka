# Surfaces

`surfaces/` contains Eureka's user-facing projections and adapters. Surfaces
should consume gateway public APIs and contracts rather than engine internals.

Current families:

- `web/`: local Workbench and read-only public-alpha HTML projections
- `cli/`: current local stdlib CLI surface
- `api/`: API projection notes; runtime service behavior stays in
  `runtime/gateway/`
- `text/`, `files/`, `lite/`: static projection families emitted under
  `site/dist/`
- `native/`: native projection adapters; canonical native client projects live
  under `native/`

The Workbench is a local operator cockpit, not a public mutation UI. Public
alpha surfaces are read-only and snapshot-backed. Native and marketplace
surfaces are not ready for distribution.
