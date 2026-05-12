# R0-08 Reviewed Public Index Rebuild

This audit pack records the local reviewed public index seam added in R0-08.

The seam reads explicit source cache, evidence ledger, and review queue SQLite stores, then writes a separate reviewed-index SQLite database only when apply mode is requested. It does not call live sources, mutate input stores, mutate site output, mutate a master index, or claim production readiness.
