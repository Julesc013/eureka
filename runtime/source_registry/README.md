# Runtime Source Registry

`runtime/source_registry/` is the runtime-side loader for Source Registry v0.

Current scope:

- load governed source records from `control/inventory/sources/`
- validate required fields structurally with Python stdlib only
- expose typed runtime records for listing, lookup, and simple filtering

Out of scope here:

- live sync
- crawling
- source health scoring
- trust scoring
- auth
- async workers
- background scheduling
- production deployment semantics

Source Registry v0 is inventory metadata only. Placeholder and future records do
not imply implemented connectors.
