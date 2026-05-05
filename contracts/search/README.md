# Search Contracts

Search contracts define governed public-search presentation and future search behavior schemas. P83 adds result merge/deduplication contracts only; no runtime grouping or ranking changes are implemented.

<!-- P84-EVIDENCE-WEIGHTED-RANKING-START -->
## P84 Evidence-Weighted Ranking Contract v0

`evidence_weighted_ranking_assessment.v0.json`, `ranking_explanation.v0.json`, and `ranking_factor.v0.json` define future, contract-only evidence-weighted ranking semantics. They do not implement runtime ranking, change current public search ordering, suppress results, use popularity/telemetry/ad/user-profile signals, promote candidates, or mutate public/local/runtime/master indexes, source cache, evidence ledger, or candidate index.
<!-- P84-EVIDENCE-WEIGHTED-RANKING-END -->
