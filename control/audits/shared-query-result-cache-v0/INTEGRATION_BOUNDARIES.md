# Integration Boundaries

Allowed in P60:

- contract schemas
- synthetic examples
- validators
- stdout-only dry-run helper
- docs, audit, and metadata

Forbidden in P60:

- public search route cache writes
- database or persistent cache storage
- telemetry events
- miss ledger writes
- search need writes
- probe queue jobs
- candidate index mutation
- local index mutation
- master-index mutation
- external calls or live probes
