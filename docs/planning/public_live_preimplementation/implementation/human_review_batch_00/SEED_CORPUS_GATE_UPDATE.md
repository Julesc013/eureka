# Seed Corpus Gate Update

Task ID: `HUMAN-REVIEW-BATCH-00`

Runnable gate:

```text
evals/hard_queries/human_reviews/batch_00/corpus_gate_update.json
```

## Counts

| Metric | Count |
|---|---:|
| reviewed | 2 |
| review_decision_backed | 6 |
| candidate | 0 |
| need | 3 |
| near_miss | 1 |
| policy_blocked | 0 |
| unavailable | 0 |
| request_more_evidence | 2 |
| blocked_for_user_details | 1 |

## Gate

```text
FAIL_INSUFFICIENT_REVIEWED_CORPUS
```

The gate remains failed because two reviewed seed records are not enough for
public alpha.
