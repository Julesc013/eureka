# Storage And Retention Plan

storage_status: planned_only
Candidate storage backends: append-only local development file store, SQLite local development store, managed Postgres hosted store.
Recommended first runtime: append-only local development store or SQLite only if explicitly approved.
Hosted production prerequisite: managed DB with migrations, retention, deletion, backup, and access control.
raw_query_retention_default: none
Retained fields: normalized query fingerprint, query intent, public-safe target kind, public-safe platform/artifact hints, result count bucket, miss/gap class, safety decision.
Forbidden fields: raw private query, IP address, account ID, private path, secret, private URL, credential, local machine fingerprint.
