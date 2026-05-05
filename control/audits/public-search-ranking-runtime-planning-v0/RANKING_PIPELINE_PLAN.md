# Ranking Pipeline Plan

1. Public search validates a bounded request.
2. Local/public index returns candidate result set.
3. Result merge/dedup grouping may produce grouping metadata if enabled later.
4. Ranking feature extractor reads public-safe result fields only.
5. Evidence-weighted factors are computed.
6. Compatibility factors are computed if target profile exists and is public-safe.
7. Conflict/gap/action-safety cautions are attached.
8. Stable deterministic tie-break is applied.
9. Explanation records are generated or referenced.
10. Response includes user-visible ranking reasons if ranking is enabled.
11. Fallback returns current order if ranking fails.
12. No mutation occurs.
