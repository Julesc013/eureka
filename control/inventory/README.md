# Inventory

`control/inventory/` holds governed inventory records that describe repo-known
assets without turning them into runtime truth by themselves.

Current inventory coverage:

- `sources/` for Source Registry v0 seed records
- `runtime/source_registry/` is the current stdlib-only runtime consumer of those records

Inventory records are:

- explicit
- inspectable
- honest about placeholder versus implemented status
- usable by bounded runtime loaders and future planning work

They are not:

- live sync state
- trust scores
- health scores
- auth configuration
- background scheduling metadata
- a substitute for connector implementation
