# Reviewed Public Index

The reviewed public index is a local projection of records that have passed the local review queue. It is separate from the source cache, evidence ledger, and review queue so indexing can be rebuilt without changing the stores that produced the reviewed inputs.

The index stores reviewed records, source-cache references, evidence references, review decision references, normalized fields, searchable text, limitations, warnings, and rebuild metadata. It is not a master index, hosted search system, deployment surface, rights clearance system, safety decision, or production-readiness claim.

## Schema Tables

- `public_index_meta` and `public_index_migrations` track deterministic schema initialization.
- `public_index_records` stores reviewed local records.
- `public_index_rebuilds` records rebuild metadata.
- `public_index_search_terms` stores deterministic local search terms.
- `public_index_source_refs`, `public_index_evidence_refs`, and `public_index_review_refs` preserve source, evidence, and decision links.

## Rebuild Model

`rebuild_reviewed_public_index` reads explicit source cache, evidence ledger, and review queue SQLite databases. It includes only locally accepted review decisions and excludes rejected, blocked, superseded, queued, needs-review, and needs-more-evidence states. Dry-run mode writes nothing.

The rebuild writes only to the explicit reviewed-index database in apply mode. It opens input stores read-only and does not mutate source cache, evidence ledger, review queue, site output, or any master index.

## Search And Absence

Search is local deterministic keyword matching over reviewed records. Absence reports are local-only reports: they say the reviewed index did not return a match for the query, not that no matching source exists.

## Runtime Boundaries

This package performs no live calls, source sync, downloads, provider calls, site generation, deployment, or connector expansion. It is a product runtime seam for local reviewed indexing only.
