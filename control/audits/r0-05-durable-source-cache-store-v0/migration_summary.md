# Migration Summary

R0-05 adds one deterministic migration:

- `001_initial_source_cache_store`

The migration creates the source cache schema and indexes, records a checksum in `source_cache_migrations`, and writes `source_cache_store.v0` to `source_cache_meta`.

Repeated init is idempotent and does not delete data.
