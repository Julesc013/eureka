# Review Ledger Proof

The scenario uses an isolated SQLite `ReviewQueueStore` under the generated `.eureka/test/...` scenario directory.

The canonical Review Ledger records one synthetic `promote` decision with actor `synthetic:e2e-reference-oracle`, source/evidence refs, and local-only confirmation. The decision step does not create a reviewed record or mutate an index.

