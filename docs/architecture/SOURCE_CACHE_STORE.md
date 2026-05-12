# Source Cache Store

R0-05 adds a durable local SQLite store for source observations produced by `runtime/source_observation/`.

The source cache records supplied metadata observations. It is not an evidence ledger, review queue, public index, source registry, connector registry, or live acquisition runtime.

## Role

The store persists:

- source records
- metadata responses supplied by callers
- source observations
- normalized observations
- cache entries linking those records

It records what was observed and cached. It does not accept evidence, decide review outcomes, include records in public search, claim rights clearance, claim safety, or claim production readiness.

## Tables

The SQLite schema contains:

- `source_cache_meta`
- `source_cache_migrations`
- `source_records`
- `metadata_responses`
- `source_observations`
- `normalized_observations`
- `cache_entries`

Every runtime payload is stored as explicit JSON in `payload_json`, with limitations and warnings stored separately as JSON arrays.

## Migration Model

`runtime/source_cache/migrations.py` defines deterministic migrations with checksums. Initialization is idempotent: repeated init applies no duplicate migration rows and does not delete data.

## Runtime Relationship

R0-04 creates source observation objects in memory. R0-05 persists those objects in a caller-provided SQLite database.

The store accepts explicit inputs only. It does not call a source, fetch a URL, read private roots, sync source registries, or write hidden local state.

## Future Relationship

R0-06 can read cached observations and create durable evidence ledger candidates. R0-07 can create review queue records from evidence candidates. R0-08 can rebuild a reviewed public index only after explicit review decisions exist.

## Local State Boundary

The caller must provide the database path. The store supports `:memory:` for tests and explicit file paths for local operation. It refuses hidden private roots and product/runtime output roots.
