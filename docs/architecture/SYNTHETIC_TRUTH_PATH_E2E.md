# Synthetic Truth Path E2E

`SYNTHETIC-TRUTH-PATH-E2E-00` proves Eureka's truth-changing mechanics inside an isolated synthetic namespace.

The path composes existing components:

- E2E reference runner for deterministic synthetic run input.
- `ReviewQueueStore` and `record_review_ledger_decision(...)` for canonical decision recording.
- Synthetic-only materialization under `.eureka/test/e2e-reference/synthetic-truth-path/`.
- Local lexical search index semantics for before/after/rollback proof.
- Snapshot manifest, envelope, fixity, and verification helpers for offline test snapshot proof.

The namespace is `synthetic:e2e-reference`. Records from this path are not production truth, not public truth, not verified artifacts, and not eligible for public projection.

Review decisions are append-only. Rollback restores active materialized truth and search-index pointers to earlier immutable generations; it does not delete the review decision or event history.

The production Preview Index rule remains unchanged: synthetic records cannot masquerade as production reviewed authority. The search proof uses a dedicated isolated synthetic test index.

Forbidden effects remain false:

- real candidate use
- production Review Ledger mutation
- reviewed/master/public index mutation
- public snapshot publication
- provider or network call
- public exposure
- downloads, file payload fetching, or execution

