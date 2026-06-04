# Fixture Report

Task ID: `HARD-QUERY-EVAL-00`

## Fixture Source

Path:

```text
evals/hard_queries/fixtures_v0.py
```

## Fixture Disclaimer

```text
Synthetic hard-query fixtures are evaluation pressure only.
They are not evidence.
They are not reviewed records.
They do not promote corpus truth.
```

The disclaimer is stored with fixture/eval metadata, not injected into public renderer payloads.

## Covered States

| Query ID | Fixture State |
|---|---|
| `hq_windows_7_apps` | `candidate` |
| `hq_driver_win98` | `need` |
| `hq_blue_ftp_client_xp` | `near_miss` |
| `hq_sound_blaster_ct1740_manual` | `candidate` |
| `hq_firefox_last_xp` | `policy_blocked` |
| `hq_ray_tracing_1994_magazine` | `unavailable` |

Focused tests also create an unknown-status variant to prove unknown/degraded behavior remains honest.

## Fixture Boundary

Fixtures create synthetic `ResolutionRunRecord` objects with `fallback_summary` only. They do not write reviewed records, review decisions, source observations, public indexes, master indexes, or source provider outputs.
