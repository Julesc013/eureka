# Rebuild Summary

`rebuild_reviewed_public_index` reads explicit source cache, evidence ledger, and review queue databases through read-only SQLite connections.

Accepted local review decisions are included. Rejected, blocked, superseded, queued, needs-review, and needs-more-evidence states are excluded. Apply mode writes only the explicit reviewed-index database; dry-run mode writes nothing.
