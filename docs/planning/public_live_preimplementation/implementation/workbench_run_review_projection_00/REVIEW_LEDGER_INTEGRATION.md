# Review Ledger Integration

## Integration Points

The Workbench projection reads durable review state from:

```text
runtime/review/queue/ReviewQueueStore
```

It uses the review ledger fallback handoff helper:

```text
runtime.review.build_review_item_from_fallback_summary(...)
```

It creates review queue items only through:

```text
runtime.review.enqueue_fallback_review_item(...)
```

Review decisions remain recorded by:

```text
runtime.review.record_review_ledger_decision(...)
```

## Projection Behavior

The Workbench projection shows:

```text
expected review item id
sanitized review item preview
stored review item if present
review decisions
audit events
allowed ledger decisions for operator profile
```

## Boundary Preserved

Projection does not create reviewed records.

Review-item creation does not promote fallback output.

Ledger decisions remain audit-visible and still require review item state plus ledger validation.

Promote decisions still do not rebuild indexes. The result records:

```text
reviewed_record_created = false
reviewed_index_mutated = false
public_index_mutated = false
master_index_mutated = false
```
