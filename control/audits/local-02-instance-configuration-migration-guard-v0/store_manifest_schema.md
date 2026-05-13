# Store Manifest Schema

`config/store_manifest.json` records required stores:

- `source_cache`
- `evidence_ledger`
- `review_queue`
- `public_index`

Each store records store id, kind, relative path, requiredness, initialization state, schema version, integrity support, migration support, and last checked timestamp.
