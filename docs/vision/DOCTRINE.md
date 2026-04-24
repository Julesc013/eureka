# Doctrine

These principles are accepted doctrine for Eureka. They guide future contracts,
runtime work, evals, and surface behavior even when the current repo only
implements bounded slices of them.

1. Search is an investigation, not just a query.
2. Return the smallest actionable unit.
3. Never let outer-container metadata beat strong inner evidence.
4. Deterministic identity beats fuzzy similarity.
5. Preserve disagreement instead of merging it away.
6. Rank by usefulness, compatibility, provenance, risk, and user cost.
7. Show why each result was ranked.
8. Show what was checked when nothing was found.
9. Cache evidence, extraction work, and resolution memory, not just pages.
10. Share public evidence, not private user behavior.
11. Every long search should be resumable.
12. The model is never the source of truth.
13. Eureka must work without LLMs and improve with them when available.
14. Offline-first, online-enhanced.
15. CLI/API/core first; GUI is a shell over the core.
16. Eval-governed improvement or no improvement.

## How To Read This

Doctrine is stronger than research but weaker than a claim of implementation
completeness.

Accepted doctrine means:

- future work should align to these principles by default
- deviations should be explicit and justified
- the repo should not silently drift back toward flat archive search

Accepted doctrine does not mean:

- every principle is already fully implemented
- every detail is already a stable public contract
- research questions about storage, queues, or hosting are fully settled
