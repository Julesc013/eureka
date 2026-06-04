# Hard Query Seed Map

Task ID: `REVIEWED-SEED-CORPUS-00`

The runnable map is:

```text
evals/hard_queries/seed_corpus/query_seed_map.v0.json
```

## Map

| Hard query | Seed item | Current state | Reviewed records | Alpha posture |
|---|---|---|---:|---|
| Windows 7 apps | `seed_hq_windows_7_apps_candidate` | candidate | 0 | not_ready |
| driver for Win98 | `seed_hq_driver_win98_need` | need | 0 | not_ready |
| old blue FTP client for XP | `seed_hq_blue_ftp_client_xp_near_miss` | near_miss | 0 | not_ready |
| manual for Sound Blaster CT1740 | `seed_hq_sound_blaster_ct1740_manual_candidate` | candidate | 0 | not_ready |
| latest Firefox before XP support ended | `seed_hq_firefox_last_xp_policy_blocked` | policy_blocked | 0 | not_ready |
| article about ray tracing in a 1994 magazine | `seed_hq_ray_tracing_1994_magazine_unavailable` | unavailable | 0 | not_ready |

## Boundary Notes

Every seed item is public-safe only as a non-truth state. None has a
`review_event_ref`, none is `verified`, and none mutates reviewed, public, or
master indexes.
