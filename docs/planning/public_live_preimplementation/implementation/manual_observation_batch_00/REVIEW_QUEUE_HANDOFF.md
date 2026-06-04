# Review Queue Handoff

Task ID: `MANUAL-OBSERVATION-BATCH-00`

Runnable handoff data:

```text
evals/hard_queries/manual_observations/batch_00/reviewable_items.json
evals/hard_queries/review_backlog/batch_00/review_backlog.json
```

## Reviewable Items

| Reviewable item | Status | Recommended decision |
|---|---|---|
| `reviewable_obs_hq_windows_7_firefox_115_candidate` | candidate | request_more_evidence |
| `reviewable_obs_hq_blue_ftp_flashfxp_near_miss` | near_miss | mark_near_miss |
| `reviewable_obs_hq_sound_blaster_ct1740_manual_unavailable` | unavailable | request_more_evidence |
| `reviewable_obs_hq_firefox_xp_52_9_candidate` | candidate | promote |
| `reviewable_obs_hq_ray_tracing_byte_parallel_course_candidate` | candidate | request_more_evidence |

The promote recommendation is a review queue recommendation only. It did not
create a review-ledger decision or reviewed record.
