# Next Work Matrix

```json
{
  "created_at": "2026-06-01T00:00:00Z",
  "deployment_performed": false,
  "needs_live_candidate_review": true,
  "needs_more_reviewed_records": true,
  "needs_more_seed_batches": true,
  "needs_snapshot_refresh_after_review": true,
  "public_launch_performed": false,
  "reassess_id": "public_alpha_reassess_01",
  "recommendations": [
    {
      "priority": 1,
      "reason": "Review real source-backed candidates and promote only if evidence supports local acceptance.",
      "task": "REVIEW-LIVE-METADATA-CANDIDATES-00"
    },
    {
      "priority": 2,
      "reason": "Refresh snapshots after any reviewed live metadata promotions.",
      "task": "SNAPSHOT-REFRESH-02"
    },
    {
      "priority": 3,
      "reason": "Reassess public usefulness after reviewed-record count changes.",
      "task": "PUBLIC-ALPHA-REASSESS-02"
    },
    {
      "priority": 4,
      "reason": "Add another discovery wedge while reviewed corpus grows.",
      "task": "SEED-BATCH-MANUALS-SCANS-00"
    }
  ],
  "recommended_next_task": "REVIEW-LIVE-METADATA-CANDIDATES-00 - Review live metadata candidates for possible local promotion",
  "schema_version": "public_alpha_next_work_recommendation.v0"
}
```
