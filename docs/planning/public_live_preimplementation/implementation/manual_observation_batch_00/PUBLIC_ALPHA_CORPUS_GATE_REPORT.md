# Public Alpha Corpus Gate Report

Task ID: `MANUAL-OBSERVATION-BATCH-00`

Runnable gate:

```text
evals/hard_queries/manual_observations/batch_00/corpus_gate_status.json
```

## Gate

```text
FAIL_INSUFFICIENT_REVIEWED_CORPUS
```

## Counts

| Metric | Count |
|---|---:|
| reviewed | 0 |
| candidate | 3 |
| need | 1 |
| near_miss | 1 |
| mention_only | 0 |
| policy_blocked | 0 |
| unavailable | 1 |
| unknown | 0 |
| review_queue_items | 5 |
| manual_followup_items | 1 |
| hard_queries_with_any_observation | 6 |
| hard_queries_with_reviewable_item | 5 |
| hard_queries_with_reviewed_record | 0 |

## Recommendation

Run `HUMAN-REVIEW-BATCH-00` next. Do not run public alpha readiness yet.
