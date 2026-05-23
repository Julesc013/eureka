# Evidence Ledger Store Summary

R0-06 adds `runtime/evidence/ledger` as a durable SQLite store for local evidence candidate records and event history.

The store persists:

- evidence candidates
- append-only evidence events
- source-cache entry links
- conflict candidates
- review status values

The store does not perform live access, connector execution, evidence acceptance, review queue persistence, public index writes, or master index writes.
