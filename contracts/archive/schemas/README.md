# Archive Schemas

These files are draft JSON Schema 2020-12 skeletons for canonical archive contracts. They are intentionally incomplete, provisional, and not yet stable compatibility promises.

Conventions used here:

- each file declares `$schema` and `$id`
- each file sets `x-eureka-status: draft`
- each file uses `additionalProperties: false`
- only minimal fields that are genuinely useful in the bootstrap phase are modeled

Connectors must adapt to these governed concepts over time. They do not get to define replacements for them.

Member-Level Synthetic Records v0 adds draft schemas for deterministic records
derived from bounded fixture-backed bundle members. These schemas describe
member lineage and evidence only; they do not introduce broad archive
extraction, arbitrary local filesystem ingestion, or new source truth.

Result Lanes + User-Cost Ranking v0 adds draft schemas for bounded lane and
user-cost annotations on existing result records. These annotations explain
current deterministic usefulness hints; they are not final production ranking,
fuzzy retrieval, vector search, LLM scoring, or live source behavior.

Compatibility Evidence Pack v0 adds a draft schema for compact source-backed
compatibility evidence records derived from committed fixture metadata, member
paths, readmes, and compatibility notes. The schema preserves evidence and
confidence; it is not a universal compatibility oracle, runtime execution
proof, installer behavior, or live-source claim.
