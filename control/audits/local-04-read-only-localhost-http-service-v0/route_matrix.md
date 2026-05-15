# Route Matrix

| Route | Method | Response | Read-only |
| --- | --- | --- | --- |
| `/` | GET | text | yes |
| `/status` | GET | JSON status | yes |
| `/health` | GET | JSON health | yes |
| `/api/v1/status` | GET | JSON status | yes |
| `/api/v1/health` | GET | JSON health | yes |
| `/api/v1/search` | GET | JSON reviewed-index search | yes |
| `/api/v1/object/<record_id>` | GET | JSON object or 404 | yes |
| `/api/v1/source/<source_id>` | GET | JSON source records | yes |
| `/api/v1/absence` | GET | JSON local absence report | yes |

No POST, PUT, PATCH, or DELETE routes are enabled.
