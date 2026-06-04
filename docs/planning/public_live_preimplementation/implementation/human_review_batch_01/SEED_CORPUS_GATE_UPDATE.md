# Seed Corpus Gate Update

Gate:

```text
FAIL_INSUFFICIENT_REVIEWED_CORPUS
```

Batch impact:

```text
reviewed_seed_records_created: 1
review_decision_backed_count: 12
hard_queries_with_review_decision: 6
hard_queries_with_promoted_or_reviewed_item_in_batch: 1
```

Cumulative after this batch:

```text
reviewed_count: 3
review_decision_backed_count: 18
hard_queries_with_promoted_or_reviewed_item: 2
```

The gate remains failed because public alpha still needs substantially more reviewed records and broader hard-query coverage.
