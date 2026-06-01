# Query Coverage Matrix

```json
{
  "accepted_truth_created": false,
  "launch_sufficient": false,
  "queries_with_candidate_result": 36,
  "queries_with_need_or_absence": 28,
  "queries_with_review_preview": 3,
  "queries_with_reviewed_result": 0,
  "query_count": 36,
  "reassess_id": "public_alpha_reassess_02",
  "rows": [
    {
      "batch_id": "seed_batch_frontier_media_00",
      "candidate_source": "fixture_seed_batch",
      "coverage_note": "Seed queries have candidate/need coverage but no reviewed seed-result coverage yet.",
      "domain_key": "frontier_media",
      "queries_with_candidate_result": 12,
      "queries_with_need_or_absence": 12,
      "queries_with_review_preview": 0,
      "queries_with_reviewed_result": 0,
      "query_count": 12
    },
    {
      "batch_id": "seed_batch_legacy_software_00",
      "candidate_source": "fixture_seed_batch",
      "coverage_note": "Seed queries have candidate/need coverage but no reviewed seed-result coverage yet.",
      "domain_key": "legacy_software",
      "queries_with_candidate_result": 16,
      "queries_with_need_or_absence": 16,
      "queries_with_review_preview": 0,
      "queries_with_reviewed_result": 0,
      "query_count": 16
    },
    {
      "batch_id": "live_metadata_pilot_batch_00",
      "candidate_source": "redacted_live_metadata",
      "coverage_note": "Live metadata review produced previews, but local apply has not created reviewed records.",
      "domain_key": "live_metadata",
      "queries_with_candidate_result": 8,
      "queries_with_need_or_absence": 0,
      "queries_with_review_preview": 3,
      "queries_with_reviewed_result": 0,
      "query_count": 8
    }
  ],
  "schema_version": "public_alpha_reassess_query_coverage_matrix.v0",
  "seed_batches": [
    "seed_batch_frontier_media_00",
    "seed_batch_legacy_software_00"
  ]
}
```
