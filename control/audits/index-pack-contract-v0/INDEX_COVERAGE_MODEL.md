# Index Coverage Model

The index pack describes coverage without exporting a raw database.

`INDEX_PACK.json` records the index build:

- build id
- format
- producer tool
- input pack references
- source and record counts
- optional evidence, member, and compatibility counts
- deterministic flag
- explicit `private_data_included: false`
- explicit `raw_cache_included: false`
- explicit `database_included: false`

`index_summary.json` records the high-level build shape. `source_coverage.json`
records source-family and per-source counts. These files are meant for future
comparison and review tooling, not for direct runtime import.
