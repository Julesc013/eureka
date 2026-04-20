# Connectors

`runtime/connectors/` contains bounded acquisition adapters.

Boundary notes:

- connectors may depend on narrow ingest, extract, and normalize interfaces plus governed contracts
- connectors must not define their own canonical object model
- connectors must not own trust semantics

