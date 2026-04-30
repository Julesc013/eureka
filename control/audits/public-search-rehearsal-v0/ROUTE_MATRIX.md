# Route Matrix

| Route | Local runtime | Public-alpha safe | Static-host route | Requires backend | Mode | Rehearsal check |
| --- | --- | --- | --- | --- | --- | --- |
| `GET /search` | yes | yes | no | yes | `local_index_only` | `/search?q=windows+7+apps` returned server-rendered HTML |
| `GET /api/v1/search` | yes | yes | no | yes | `local_index_only` | safe queries and blocked requests passed |
| `GET /api/v1/query-plan` | yes | yes | no | yes | `local_index_only` | query plan returned `no_live_probe: true` |
| `GET /api/v1/status` | yes | yes | no | yes | `local_index_only` | status reported unsafe capabilities disabled |
| `GET /api/v1/sources` | yes | yes | no | yes | `local_index_only` | source summaries returned public-safe JSON |
| `GET /api/v1/source/{source_id}` | yes | yes | no | yes | `local_index_only` | `synthetic-fixtures` returned without private path leakage |

The static search entry point is `site/dist/search.html`, not `/search`.
GitHub Pages can serve that static file but cannot run the Python runtime.

All route checks were run by the local in-process smoke harness; no network
listener or external source call was required.
