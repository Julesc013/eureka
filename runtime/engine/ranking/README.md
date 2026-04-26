# Ranking

`runtime/engine/ranking/` owns bounded deterministic result-lane and user-cost
annotations for current Eureka result records.

Result Lanes + User-Cost Ranking v0 assigns compact lanes and cost explanations
from fields Eureka already has: record kind, source family, representation kind,
member path/kind, parent lineage, action hints, and evidence summaries.
Compatibility Evidence Pack v0 adds optional compatibility-evidence reasons
such as `compatibility_evidence_present`, `driver_platform_match`, and
`documentation_only_compatibility_evidence` when source-backed evidence is
available.

This is deliberately not final production ranking. It does not add fuzzy
retrieval, vector search, LLM scoring, live source behavior, crawling, source
federation, or new connectors. The goal is to explain why a member-level result
may be lower effort than a parent bundle while keeping parent context visible.
