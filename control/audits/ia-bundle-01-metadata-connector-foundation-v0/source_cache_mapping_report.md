# Source Cache Mapping Report

Normalized IA fixture records can be mapped to source-cache candidate previews.
The mapping is fixture-only and does not write source cache runtime state.

Mapped fields:

- IA item identifier to `source_native_id`
- IA item locator to `source_locator`
- title, description, mediatype, creator, date, and collection to
  `source_metadata_summary`
- file list summary to `source_coverage_summary`
- limitations to `source_limitations`

The mapping preserves `accepted_source_truth: false`,
`source_cache_write_enabled: false`, and both public/master index mutation
booleans as false.
