# Workbench Live Run Routes

Routes added or projected:

| Route | Method | Purpose |
| --- | --- | --- |
| `/search` | GET | Existing search page shows a run-linked section when a query is present. |
| `/runs` | GET | Lists process-local runs or creates a dry-run when `q`/`query` is supplied. |
| `/runs/{run_id}` | GET | Renders run detail, lanes, events, planned WorkUnits, and blocked actions. |
| `/api/v1/resolution-runs` | GET | Lists runs or creates a local dry-run packet when `q`/`query` is supplied. |
| `/api/v1/resolution-runs/{run_id}` | GET | Returns the run packet envelope. |
| `/api/v1/resolution-runs/{run_id}/events` | GET | Returns event log envelope. |
| `/api/v1/resolution-runs/{run_id}/lanes` | GET | Returns lane snapshot envelope. |
| `/api/v1/resolution-runs/{run_id}/workunits` | GET | Returns planned dry-run WorkUnits. |
| `/api/v1/resolution-runs/{run_id}/commands` | GET | Returns safe read-command status or policy-blocked outcome. |

The local service stays GET-only for this foundation path. Future mutating commands require a separate policy gate.
