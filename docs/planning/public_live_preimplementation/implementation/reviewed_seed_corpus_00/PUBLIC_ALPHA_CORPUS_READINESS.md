# Public Alpha Corpus Readiness

Task ID: `REVIEWED-SEED-CORPUS-00`

Runnable readiness data:

```text
evals/hard_queries/seed_corpus/public_alpha_corpus_readiness.v0.json
```

## Gate

```text
FAIL_INSUFFICIENT_REVIEWED_CORPUS
```

## Current Counts

| Metric | Current | Target | Gap |
|---|---:|---:|---:|
| hard queries mapped | 6 | 50 | 44 |
| reviewed records | 0 | 200 | 200 |
| candidate/need/near_miss/bounded-absence items | 6 | 500 | 494 |

## Decision

Do not run `PUBLIC-ALPHA-READINESS-00` yet. The smallest honest next task is
`MANUAL-OBSERVATION-BATCH-00`, focused on source observations and review-ready
items for the six hard queries.
