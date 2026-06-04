# Review Backlog

Task ID: `REVIEWED-SEED-CORPUS-00`

The runnable backlog is:

```text
evals/hard_queries/seed_corpus/review_backlog.v0.json
```

## Backlog Summary

| Seed item | Current state | Desired review decision | Next work |
|---|---|---|---|
| `seed_hq_windows_7_apps_candidate` | candidate | promote only after evidence | Manual observation and compatibility review |
| `seed_hq_driver_win98_need` | need | request_more_evidence | Identify vendor, model, architecture, OS edition |
| `seed_hq_blue_ftp_client_xp_near_miss` | near_miss | mark_near_miss | Collect identity and visual-clue observations |
| `seed_hq_sound_blaster_ct1740_manual_candidate` | candidate | request_more_evidence | Collect CT1740 document/source observation |
| `seed_hq_firefox_last_xp_policy_blocked` | policy_blocked | request_more_evidence | Collect support-window evidence |
| `seed_hq_ray_tracing_1994_magazine_unavailable` | unavailable | request_more_evidence | Narrow publication, issue, page, or OCR source |

## Truth Boundary

The backlog creates no review event and no reviewed record. It is only a queue
of manual observation and review work.
