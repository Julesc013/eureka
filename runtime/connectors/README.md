# Connectors

`runtime/connectors/` contains bounded acquisition adapters.

Boundary notes:

- connectors may depend only on `runtime/engine/interfaces/ingest/**`, `runtime/engine/interfaces/extract/**`, `runtime/engine/interfaces/normalize/**`, and governed archive contracts
- connectors must not define their own canonical object model
- connectors must not own trust semantics

Current bootstrap slice:

- `synthetic_software/` is a local-only connector-shaped adapter over governed synthetic software fixtures
- connectors own source loading only in this slice
- extract and normalize steps remain engine-owned boundary logic
