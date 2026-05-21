# IA Hunt WorkUnit Schema

The bridge defines IA metadata WorkUnits for `internet_archive_metadata` source-family work.

Required WorkUnit types:

- `ia_metadata_search`
- `ia_item_metadata_read`
- `ia_file_manifest_metadata`
- `ia_source_cache_write`
- `ia_evidence_candidate_write`
- `ia_candidate_index_write`
- `ia_review_queue_write`
- `ia_promotion_dry_run`
- `ia_reviewed_index_rebuild`
- `ia_result_lane_project`

Required states:

- `created`
- `queued`
- `running`
- `waiting_for_policy`
- `waiting_for_source_quota`
- `completed`
- `failed`
- `blocked`
- `cancelled`

Every WorkUnit carries hunt/source identity, input/output refs, policy refs, dry-run posture, write scope, blocked actions, timestamps, and limitations.
