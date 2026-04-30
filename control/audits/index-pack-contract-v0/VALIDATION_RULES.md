# Validation Rules

`scripts/validate_index_pack.py` validates:

- manifest parse and required fields
- schema version, status, index mode, and index format
- no private data, raw cache, or database included
- required docs and pack files
- JSON and JSONL parse
- source coverage source ids
- record id uniqueness
- record kind allowlist
- record source references
- privacy/status consistency
- checksum coverage and SHA-256 values
- privacy/rights doc language
- prohibited credential fields
- private absolute paths
- raw database extensions
- executable payload extensions
- no live network authority

The validator does not import, merge, upload, index, fetch, scrape, execute, or
accept records into a master index.
