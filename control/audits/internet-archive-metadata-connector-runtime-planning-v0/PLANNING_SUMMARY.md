# Planning Summary

The future connector would be source-sync-worker driven, metadata-only, cache-first, evidence-first, and disabled by default.

It would fetch bounded Internet Archive item/search/file-listing metadata only after approval and operator configuration, normalize it into source-cache record candidates, and emit evidence-ledger observation candidates. It would never directly mutate the master index, candidate index, public index, local index, or public search runtime.

P87 adds only planning docs, an inventory record, an operations reference, a validator, and tests.
