# Integration Boundaries

P59 does not wire query observation into public search runtime.

Allowed in P59:

- contract schema
- policy inventory
- synthetic example
- validator scripts
- stdout-only dry-run helper
- documentation and audit evidence

Not allowed in P59:

- persistent query logging
- telemetry
- database tables
- runtime files under local state
- result cache writes
- miss ledger writes
- search need records
- probe enqueueing
- candidate index mutation
- local/public/runtime index mutation
- master-index mutation
- external source calls
