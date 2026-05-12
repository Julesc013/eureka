# Schema Summary

The SQLite schema includes:

- `public_index_meta`
- `public_index_migrations`
- `public_index_records`
- `public_index_rebuilds`
- `public_index_search_terms`
- `public_index_source_refs`
- `public_index_evidence_refs`
- `public_index_review_refs`

Initialization is deterministic and idempotent. Migration metadata is stored locally in the reviewed-index database.
