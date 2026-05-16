# AIDE File Quality Ledger

Schema family:

- top-level/index schema: `aide.file-quality-ledger.v0`
- shard schema: `aide.file-quality-ledger-shard.v0`

Top-level fields:

- `schema_version`
- `generated_by`
- `source_commit`
- `source_repo_intelligence`
- `summary`
- `record_storage`
- `record_count`
- `record_shards`
- `records`
- `regeneration_command`

When `record_storage` is `sharded`, the top-level `records` array is empty and
record data lives in shard files. AIDE quality commands hydrate the shards for
validation and `quality explain-file`.

Shard entries include:

- `shard_id`
- `path`
- `record_count`
- `size_bytes`
- `sha256`

Shard names are stable: `file-quality-ledger-0001.json`,
`file-quality-ledger-0002.json`, and so on.
