# Source Cache Runtime Reference

## SourceCacheStore

`SourceCacheStore.open(path)` opens a SQLite store at an explicit path or `:memory:`.

Public methods:

- `init()`
- `close()`
- `write_source_record(record)`
- `write_metadata_response(response)`
- `write_source_observation(observation)`
- `write_normalized_observation(observation)`
- `write_cache_entry(entry)`
- `get_cache_entry(entry_id)`
- `get_source_record(source_id)`
- `list_cache_entries(source_id=None, status=None, limit=100)`
- `summarize()`
- `check_integrity()`

Writes are transactional and limited to the provided SQLite database.

## SourceCacheEntry

`SourceCacheEntry` links a source record, metadata response, source observation, and normalized observation into one durable cache row.

Fields include:

- `entry_id`
- `source_id`
- `source_family`
- `trust_lane`
- `request_id`
- `response_id`
- `observation_id`
- `normalized_observation_id`
- `response_fingerprint`
- `status`
- `payload`
- `limitations`
- `warnings`
- `created_at`
- `updated_at`

## SourceCacheStatus

Supported statuses:

- `cached`
- `stale`
- `superseded`
- `blocked`
- `invalid`
- `not_evaluable`

## SourceCacheWrite

`SourceCacheWrite` summarizes a write operation with table, record id, status, and row count.

## SourceCacheRead

`SourceCacheRead` is a serializable read summary for simple callers.

## SourceCacheSummary

`SourceCacheSummary` reports table counts and cache-entry status counts.

## Migrations

`SourceCacheMigration` records migration id, schema version, statement count, and checksum. `apply_migrations(connection)` is idempotent.
