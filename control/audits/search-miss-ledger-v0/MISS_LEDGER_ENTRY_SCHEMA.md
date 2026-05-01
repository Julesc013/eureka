# Miss Ledger Entry Schema

Required top-level fields:

- `schema_version`
- `miss_entry_id`
- `miss_entry_kind`
- `status`
- `created_by_tool`
- `query_ref`
- `cache_ref`
- `miss_classification`
- `miss_causes`
- `checked_scope`
- `not_checked_scope`
- `near_misses`
- `weak_hits`
- `result_summary`
- `absence_summary`
- `suggested_next_steps`
- `privacy`
- `retention_policy`
- `aggregation_policy`
- `limitations`
- `no_mutation_guarantees`
- `notes`

No-mutation fields are hard false for master index, local index, candidate
index, search need creation, probe enqueueing, result cache mutation, query
observation mutation, telemetry export, and external calls.

