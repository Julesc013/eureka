# Connectors

`runtime/connectors/` contains bounded acquisition adapters.

Boundary notes:

- connectors may depend only on `runtime/engine/interfaces/ingest/**`, `runtime/engine/interfaces/extract/**`, `runtime/engine/interfaces/normalize/**`, and governed archive contracts
- connectors must not define their own canonical object model
- connectors must not own trust semantics
