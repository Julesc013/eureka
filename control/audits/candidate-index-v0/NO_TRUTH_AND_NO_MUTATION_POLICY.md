# No Truth And No Mutation Policy

P64 hard false guarantees:

- `accepted_as_truth`
- `promoted_to_master_index`
- `master_index_mutated`
- `local_index_mutated`
- `public_index_mutated`
- `source_registry_mutated`
- `source_cache_mutated`
- `evidence_ledger_mutated`
- `result_cache_mutated`
- `miss_ledger_mutated`
- `search_need_mutated`
- `probe_queue_mutated`
- `telemetry_exported`
- `external_calls_performed`
- `live_source_called`

Candidate records are provisional and review-gated. They cannot become
authoritative records in P64.
