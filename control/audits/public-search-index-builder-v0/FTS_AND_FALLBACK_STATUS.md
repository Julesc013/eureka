# FTS And Fallback Status

Python `sqlite3` is available in the local verification environment, and FTS5
availability was detected as true.

P55 does not commit a SQLite artifact. Therefore:

- sqlite_available: true
- fts5_available: true
- fts5_enabled: false
- fallback_enabled: true

The runtime uses deterministic lexical matching over generated NDJSON-backed
`IndexRecord` values.
