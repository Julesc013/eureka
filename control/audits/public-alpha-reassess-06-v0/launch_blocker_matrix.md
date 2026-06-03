# Launch Blocker Matrix

```json
{
  "blockers": [
    {
      "blocker_id": "reviewed_record_count_below_threshold",
      "evidence": "Limited reviewed projection count 12 < threshold 25.",
      "launch_blocking": true,
      "public_explanation": "Limited reviewed projection count 12 < threshold 25.",
      "schema_version": "public_alpha_launch_blocker.v0",
      "severity": "launch_blocking"
    },
    {
      "blocker_id": "limited_reviewed_records_are_not_verified_artifacts",
      "evidence": "Limited metadata/source-lead records do not establish downloadable artifact verification.",
      "launch_blocking": true,
      "public_explanation": "Limited metadata/source-lead records do not establish downloadable artifact verification.",
      "schema_version": "public_alpha_launch_blocker.v0",
      "severity": "launch_blocking"
    },
    {
      "blocker_id": "candidate_heavy_snapshot",
      "evidence": "Candidate count is 60 versus 12 limited reviewed projections.",
      "launch_blocking": true,
      "public_explanation": "Candidate count is 60 versus 12 limited reviewed projections.",
      "schema_version": "public_alpha_launch_blocker.v0",
      "severity": "launch_blocking"
    },
    {
      "blocker_id": "indexless_live_fallback_missing",
      "evidence": "No indexless live metadata fallback exists for degraded search.",
      "launch_blocking": true,
      "public_explanation": "No indexless live metadata fallback exists for degraded search.",
      "schema_version": "public_alpha_launch_blocker.v0",
      "severity": "launch_blocking"
    },
    {
      "blocker_id": "search_usefulness_eval_missing",
      "evidence": "No search usefulness evaluation exists for hard public-alpha queries.",
      "launch_blocking": true,
      "public_explanation": "No search usefulness evaluation exists for hard public-alpha queries.",
      "schema_version": "public_alpha_launch_blocker.v0",
      "severity": "launch_blocking"
    },
    {
      "blocker_id": "no_external_full_discovery_after_current_dev_stack",
      "evidence": "No external full-discovery summary exists for the current dev stack.",
      "launch_blocking": true,
      "public_explanation": "No external full-discovery summary exists for the current dev stack.",
      "schema_version": "public_alpha_launch_blocker.v0",
      "severity": "launch_blocking"
    },
    {
      "blocker_id": "current_dev_not_promoted_to_main_after_discovery_ux_review_stack",
      "evidence": "Current dev stack has not been promoted to main after discovery, UX, and review-batch apply work.",
      "launch_blocking": true,
      "public_explanation": "Current dev stack has not been promoted to main after discovery, UX, and review-batch apply work.",
      "schema_version": "public_alpha_launch_blocker.v0",
      "severity": "launch_blocking"
    },
    {
      "blocker_id": "no_public_launch_approval",
      "evidence": "No explicit future manual approval exists for a public launch.",
      "launch_blocking": true,
      "public_explanation": "No explicit future manual approval exists for a public launch.",
      "schema_version": "public_alpha_launch_blocker.v0",
      "severity": "launch_blocking"
    },
    {
      "blocker_id": "no_snapshot_publication_rehearsal_after_current_snapshot",
      "evidence": "No publication rehearsal has run after the review-batch apply snapshot.",
      "launch_blocking": true,
      "public_explanation": "No publication rehearsal has run after the review-batch apply snapshot.",
      "schema_version": "public_alpha_launch_blocker.v0",
      "severity": "launch_blocking"
    }
  ],
  "blockers_count": 9,
  "created_at": "2026-06-03T00:00:00Z",
  "launch_blocked": true,
  "nonblocking_positives": [
    "reviewed_corpus_growth_confirmed",
    "review_batch_apply_loop_present",
    "public_search_ux_mvp_present",
    "no_js_search_present",
    "result_card_statuses_present",
    "four_domains_represented",
    "candidate_discovery_stack_present",
    "live_metadata_pilot_present",
    "local_apply_gate_present",
    "limited_reviewed_metadata_records_present",
    "reviewed_source_leads_present",
    "reviewed_known_needs_present",
    "reviewed_bounded_absences_present",
    "seed_batches_present",
    "snapshot_refresh_present"
  ],
  "reassess_id": "public_alpha_reassess_06",
  "schema_version": "public_alpha_launch_blocker_register.v0",
  "warnings": [
    "reviewed corpus grew materially but remains below threshold",
    "limited reviewed metadata/source-lead records are not verified artifacts",
    "candidate-heavy snapshots remain internal review material",
    "indexless fallback and search usefulness eval are missing",
    "external full discovery, main promotion, and launch approval remain future gates"
  ],
  "warnings_count": 5
}
```
