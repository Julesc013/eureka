# Seed Batch Record

A seed batch record captures a curated discovery run and its review-only
outputs.

Required high-level fields include:

- `batch_id`
- `domain_id`
- `query_set`
- `source_plan_refs`
- `candidate_refs`
- `scout_refs`
- `review_batch_refs`
- `known_need_refs`
- `absence_refs`
- `snapshot_refresh_handoff_refs`
- `public_alpha_reassess_refs`

Boundary fields must remain false for this task:

- `accepted_truth_created`
- `reviewed_index_mutated`
- `master_index_mutated`
- `public_index_mutated`
- `download_performed`
- `extraction_executed`
- `install_execution_enabled`
- `model_provider_used`
- `deployment_performed`
