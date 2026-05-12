# Migration Summary

The initial migration is deterministic and idempotent. Re-running initialization
does not duplicate migration history or corrupt the store.

Migration history is recorded in `review_queue_migrations`.
