# Remaining Risks

1. Dirty local state: Q56-Q61 artifacts and product/test files are cumulative
   and uncommitted. Normal product work should acknowledge this before editing.
2. AIDE eval is not fully green. Latest useful report records 127 pass / 9 fail,
   and current reruns can timeout or produce no stdout.
3. Release validation fails because Eureka does not carry target-local release
   dist artifacts. This is expected for a no-publish target but blocks release
   claims.
4. Refactor map validation fails because current move/salvage/path-alias maps
   are missing. This blocks refactor-map claims, not the fixture source slice.
5. Repo/quality surfaces retain many unknown classifications and orphan
   candidates.
6. The product slice remains fixture-only/local-only. It is not live-source,
   public-index, hosted API/UI, or production review readiness.
7. Duplicate limitation text remains cosmetic in some lower-level records,
   though Q60 packets deduplicate inspectable surface limitations.
8. Optional sibling Dominium is dirty; XCHECK should audit cross-repo state
   before global promotion decisions.

