# Source Cache Store Summary

R0-05 adds a durable SQLite store for source observations.

The store persists:

- source records
- metadata responses
- source observations
- normalized observations
- cache entries

It supports get/list/summarize/integrity behavior and requires the caller to provide an explicit database path or `:memory:`.

It does not write evidence ledger records, review queue records, public index data, master index data, source registry data, or connector registry data.
