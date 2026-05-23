# R0-05 Durable Source Cache Store

This audit pack records the first durable local source cache store.

R0-05 adds a SQLite-backed runtime package under `runtime/source/cache/` that persists source records, metadata responses, source observations, normalized observations, and cache entries produced from the R0-04 source observation seam.

Boundaries:

- no live calls
- no source sync
- no evidence ledger writes
- no review queue writes
- no public or master index mutation
- no connector rewrite
- no hidden local state root

F0 and dev-to-main promotion remain blocked.
