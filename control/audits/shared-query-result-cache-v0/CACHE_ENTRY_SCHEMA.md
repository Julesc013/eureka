# Cache Entry Schema

The cache entry schema requires:

- `query_ref`
- `cache_key`
- `request_summary`
- `response_summary`
- `result_summaries`
- `absence_summary`
- `checked_scope`
- `index_refs`
- `source_status_summary`
- `freshness`
- `invalidation`
- `privacy`
- `retention_policy`
- `no_mutation_guarantees`

Hard no-mutation fields are required and false for master index, local index,
candidate index, query observation mutation, miss ledger mutation, search need
mutation, probe enqueue, telemetry export, and external calls.
