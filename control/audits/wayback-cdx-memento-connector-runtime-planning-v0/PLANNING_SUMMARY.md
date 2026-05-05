# Planning Summary

The future connector would be source-sync-worker driven, availability-and-capture-metadata-only, URI-privacy guarded, cache-first, evidence-first, and disabled by default.

It would fetch bounded capture availability, CDX metadata, or Memento summary metadata only after approval and operator configuration, normalize it into source-cache record candidates, and emit evidence-ledger observation candidates. It would never directly mutate the master index, candidate index, public index, local index, or public search runtime.

P88 adds only planning docs, an inventory record, an operations reference, a validator, and tests.
