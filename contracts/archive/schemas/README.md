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
