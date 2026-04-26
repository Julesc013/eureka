# Local Index v0

`runtime/engine/index/` holds Eureka's first durable local index slice.

Scope:

- build a local SQLite-backed index from the current bounded corpus
- prefer SQLite FTS5 when available
- fall back to deterministic LIKE-based search when FTS5 is unavailable
- expose bounded build, status, and query behavior through engine service interfaces
- annotate records with bounded result lanes and user-cost explanations where
  current evidence supports them
- treat caller-provided index paths as bootstrap local inputs only, not final
  hosted or multi-user storage semantics

Non-goals:

- production ranking engines
- fuzzy retrieval
- vector search
- LLM search
- live source sync
- incremental indexing
- worker queues or background indexing

Current corpus inputs:

- synthetic fixture records
- GitHub Releases recorded-fixture records
- bounded representation summaries
- bounded member summaries when cheap local ZIP inspection is available
- deterministic `synthetic_member` records derived from committed local bundle
  fixtures, including parent target refs, member paths, member kind, hash/size
  metadata when available, and action hints
- bounded evidence summaries
- source-registry records

Member-level records are fixture-derived and deterministic. They do not imply
production ranking, broad archive extraction, arbitrary local filesystem ingestion,
incremental indexing, live source sync, or a final hosted search service.

Result Lanes + User-Cost Ranking v0 adds deterministic lane and cost metadata
to index records so a member with source evidence and parent lineage can be
explained as lower user cost than a bulky parent bundle. This is an annotation
and small-result ordering seam only; it is not fuzzy, vector, LLM, semantic, or
production relevance ranking.
