# Recovered Product Runtime Seams

R0 recovered a product-facing local runtime path:

1. `runtime/source_observation` models source records, metadata requests, metadata responses, source observations, normalized observations, evidence candidates, review items, health, and validation.
2. `runtime/source_cache` persists observations and normalized observations to explicit SQLite stores.
3. `runtime/evidence_ledger` persists evidence candidates, events, conflicts, and source-cache links.
4. `runtime/review_queue` persists review items and explicit local review decisions.
5. `runtime/public_index` rebuilds a local reviewed index from explicit source cache, evidence ledger, and review queue stores.
6. `runtime/source_observation/sources/pypi_json_metadata.py` proves one bounded metadata-only live source for `sampleproject`.

These seams are local and review-gated. They do not perform public launch, hosted search, master-index mutation, package downloads, package installation, broad source sync, or source truth acceptance.
