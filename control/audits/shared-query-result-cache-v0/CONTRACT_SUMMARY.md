# Contract Summary

P60 adds `contracts/query/search_result_cache_entry.v0.json` and
`contracts/query/cache_key.v0.json`.

The contract allows future reuse of safe public-search response summaries and
scoped absence/gap outcomes. It requires raw query retention default `none`,
non-reversible fingerprints, local_index_only mode, public index snapshot
references, freshness/invalidation fields, privacy flags, and hard
no-mutation guarantees.

Current status: `contract_only`. No public search runtime route reads or writes
cache entries in this milestone.
