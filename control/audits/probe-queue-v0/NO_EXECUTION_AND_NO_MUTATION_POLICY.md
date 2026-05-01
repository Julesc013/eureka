# No Execution And No Mutation Policy

P63 hard false guarantees:

- `probe_executed`
- `live_source_called`
- `external_calls_performed`
- `source_cache_mutated`
- `evidence_ledger_mutated`
- `candidate_index_mutated`
- `master_index_mutated`
- `local_index_mutated`
- `result_cache_mutated`
- `miss_ledger_mutated`
- `search_need_mutated`
- `telemetry_exported`

These are contract invariants for examples and validators.
