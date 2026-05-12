# R0 Review Queue Store

R0-07 adds a durable local review queue. It proves the product runtime can
persist review items and explicit decisions without mutating public or master
indexes.

## Initialize

```bash
python scripts/init_review_queue_store.py --db control/audits/r0-07-review-queue-product-seam-v0/generated/review_queue_demo.sqlite --check --json
```

The script writes only to the explicit `--db` path.

## Demo

```bash
python scripts/demo_review_queue_store.py --source-cache-db control/audits/r0-07-review-queue-product-seam-v0/generated/source_cache_demo.sqlite --evidence-db control/audits/r0-07-review-queue-product-seam-v0/generated/evidence_ledger_demo.sqlite --review-db control/audits/r0-07-review-queue-product-seam-v0/generated/review_queue_demo.sqlite --decision accept --output control/audits/r0-07-review-queue-product-seam-v0/generated/sample_demo_output.json --json
```

The demo proves:

- source observation to source cache
- source cache to evidence ledger
- evidence ledger to review queue
- explicit local decision recording

## Validate

```bash
python scripts/validate_review_queue_store.py
python -m unittest tests.runtime.test_review_queue_store
python -m unittest tests.runtime.test_review_queue_migrations
python -m unittest tests.runtime.test_review_queue_integration
```

F0 remains blocked because the product loop still lacks a reviewed public index
rebuild. R0-08 is next.
