# Review Boundary Validation

Preserved:

```text
source_observation_self_promoted: false
candidate_self_promoted: false
fallback_summary_self_promoted: false
reviewable_item_self_promoted: false
synthetic_eval_fixture_used_as_evidence: false
ai_model_output_counted_as_truth: false
reviewed_index_mutated: false
public_index_mutated: false
master_index_mutated: false
product_runtime_live_source_calls_performed: false
downloads_performed: false
file_fetches_performed: false
wayback_replay_performed: false
```

Only explicit `promote` creates a reviewed seed record. `supersede`, `mark_need`, `mark_near_miss`, and `request_more_evidence` remain non-reviewed.
