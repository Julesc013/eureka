# Observation Schema Status

Status classification: `complete`

Schema file:

- `evals/search_usefulness/external_baselines/observation.schema.json`

The schema describes manual, human-recorded external baseline observations. It is documentation; stdlib validation is implemented by `scripts/validate_external_baseline_observations.py`.

Required fields:

- `observation_id`
- `query_id`
- `query_text`
- `system_id`
- `observation_status`
- `top_results`
- `failure_modes`
- `next_eureka_work`
- `evidence_limitations`
- `created_by`
- `schema_version`

Important optional/manual fields for observed records:

- `operator`
- `observed_at`
- `browser_or_tool`
- `location_context_optional`
- `exact_query_submitted`
- `filters_or_scope`
- `result_count_visible_optional`
- `collection_method`
- `first_useful_result_rank`
- `first_useful_result_reason`
- `usefulness_scores`
- `comparison_notes`
- `staleness_notes`

Valid source/system labels in current Batch 0:

- `google_web_search`
- `internet_archive_metadata_search`
- `internet_archive_full_text_search`

Valid observation states:

- `observed`
- `pending_manual_observation`
- `not_applicable`
- `blocked`
- `stale`

Result quality is currently represented through structured `top_results`, `first_useful_result_rank`, `failure_modes`, and 0-3 `usefulness_scores`; this follow-up worksheet adds human-facing quality labels for operator convenience, but committed records must still satisfy the existing schema.

Missing schema elements: none blocking for Batch 0 follow-up. A future schema revision could add an explicit `observed_result_quality` enum, but P102 does not change the existing observation schema.

