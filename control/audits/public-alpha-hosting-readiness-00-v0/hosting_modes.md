# Hosting Modes

| Mode | Status | Notes |
| --- | --- | --- |
| `static_snapshot_site` | preferred | Snapshot/relay artifact only; no server-side mutation. |
| `read_only_relay_service` | preferred | Serves reviewed snapshot data through read-only relay routes. |
| `local_preview_server` | allowed | Local operator preview only. |
| `future_dynamic_gateway` | blocked | Requires a future reviewed task before use. |

All modes keep live source fanout, downloads, extraction, public mutation,
accounts, model/provider calls, deployment, production readiness claims, and
public launch readiness claims disabled in this task.
