# Review Queue Store Summary

R0-07 adds `runtime/review_queue`, a standard-library SQLite store for local
review items and explicit decisions.

The store persists review items, links to evidence ledger records, links to
source-cache entries, append-only review events, and decision history.

The store does not write public indexes, master indexes, source registries, or
connector registries.
