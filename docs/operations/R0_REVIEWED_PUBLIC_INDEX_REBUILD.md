# R0 Reviewed Public Index Rebuild

R0-08 adds the local reviewed public index seam. It rebuilds a local SQLite index from explicit source cache, evidence ledger, and review queue databases.

## Run

Initialize an index database:

```bash
python scripts/init_public_index_store.py --db tmp/public_index.sqlite --check --json
```

Run the full synthetic demo:

```bash
python scripts/demo_reviewed_public_index.py --source-cache-db tmp/source_cache.sqlite --evidence-db tmp/evidence.sqlite --review-db tmp/review.sqlite --public-index-db tmp/public_index.sqlite --json
```

Dry-run a rebuild:

```bash
python scripts/rebuild_reviewed_public_index.py --source-cache-db tmp/source_cache.sqlite --evidence-db tmp/evidence.sqlite --review-db tmp/review.sqlite --public-index-db tmp/public_index.sqlite --dry-run --json
```

Validate the seam:

```bash
python scripts/validate_reviewed_public_index.py
```

## Interpretation

Accepted local review decisions are projected into reviewed records. Rejected, blocked, superseded, queued, needs-review, and needs-more-evidence states are excluded. Search and absence reports are local to the reviewed index.

R0-08 does not call live sources, sync sources, mutate input stores, mutate site output, mutate a master index, deploy search, or claim production readiness. F0 and dev-to-main promotion remain blocked. R0-09 is next because one real source must be tested through the reviewed seams.
