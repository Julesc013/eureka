# Schema Summary

SQLite tables:

- `source_cache_meta`
- `source_cache_migrations`
- `source_records`
- `metadata_responses`
- `source_observations`
- `normalized_observations`
- `cache_entries`

The row payloads are stored as JSON text. Limitations and warnings are stored as JSON arrays. Cache entries include source id, source family, trust lane, request id, response id, observation id, normalized observation id, response fingerprint, status, and timestamps.
