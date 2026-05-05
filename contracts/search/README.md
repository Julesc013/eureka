# Search Contracts

Search contracts define governed public-search presentation and future search behavior schemas. P83 adds result merge/deduplication contracts only; no runtime grouping or ranking changes are implemented.

<!-- P84-EVIDENCE-WEIGHTED-RANKING-START -->
## P84 Evidence-Weighted Ranking Contract v0

`evidence_weighted_ranking_assessment.v0.json`, `ranking_explanation.v0.json`, and `ranking_factor.v0.json` define future, contract-only evidence-weighted ranking semantics. They do not implement runtime ranking, change current public search ordering, suppress results, use popularity/telemetry/ad/user-profile signals, promote candidates, or mutate public/local/runtime/master indexes, source cache, evidence ledger, or candidate index.
<!-- P84-EVIDENCE-WEIGHTED-RANKING-END -->

<!-- P85-COMPATIBILITY-AWARE-RANKING-START -->
## P85 Compatibility-Aware Ranking Contract v0

- `compatibility_target_profile.v0.json` defines public-safe target environment profiles for future compatibility ranking.
- `compatibility_aware_ranking_assessment.v0.json` defines future compatibility-aware ranking assessments without runtime ranking or mutation.
- `compatibility_explanation.v0.json` defines cautious user-facing explanations for compatibility fit, unknowns, conflicts, and disabled actions.
- `compatibility_factor.v0.json` lists the compatibility factor item shape.
<!-- P85-COMPATIBILITY-AWARE-RANKING-END -->

<!-- P96-SEARCH-RESULT-EXPLANATION-CONTRACT-START -->
## P96 Search Result Explanation Contract v0

P96 adds contract-only search result explanation schemas for future result-level explanations. They define evidence-first, public-safe, user-readable and audit-readable explanation records, components, and policy gates. No runtime explanation generator, hidden score, result suppression, public search response change, ranking change, model call, telemetry, source/evidence/candidate/index mutation, or production search behavior is added.
<!-- P96-SEARCH-RESULT-EXPLANATION-CONTRACT-END -->
