# Source Cache Local Dry-Run Runtime

`runtime/source_cache/` contains the P98 local dry-run runtime. It loads
approved repo-local synthetic source-cache candidate examples, validates their
shape, classifies them, and emits deterministic reports.

It does not call live sources, execute connectors or source-sync workers, write
authoritative source-cache state, mutate the evidence ledger or indexes, alter
public search, export telemetry, use credentials, enable downloads, enable
installs, or execute payloads.

It does not alter public search.
