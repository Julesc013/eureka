# Smoke Results

## Cases

| Case | Query | Expected state |
| --- | --- | --- |
| `candidate_sound_blaster_manual` | manual for Sound Blaster CT1740 | candidate |
| `need_ray_tracing_magazine` | article about ray tracing in a 1994 magazine | need |
| `near_miss_blue_ftp_client` | old blue FTP client for XP | near_miss |
| `unavailable_firefox_malformed` | latest Firefox before XP support ended | unavailable |
| `policy_blocked_disabled` | manual for Sound Blaster CT1740 | policy_blocked |

## Renderers

```text
json_v0
text_v0
html_basic_v0
snapshot_v0
```

## Result

Focused smoke tests pass and prove the fallback states remain visible in all
baseline renderer outputs.

