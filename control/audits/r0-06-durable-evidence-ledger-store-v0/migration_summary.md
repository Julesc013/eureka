# Migration Summary

R0-06 defines one deterministic migration:

- `001_initial_evidence_ledger_store`

Initialization is idempotent. Repeated initialization does not duplicate migration records or delete stored evidence data.
