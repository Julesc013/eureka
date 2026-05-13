# Local LAN Route Matrix

## LAN Read-Only Allowed

| Method | Route |
| --- | --- |
| GET | `/` |
| GET | `/status` |
| GET | `/health` |
| GET | `/search` |
| GET | `/object/<record_id>` |
| GET | `/source/<source_id>` |
| GET | `/absence` |
| GET | `/api/v1/status` |
| GET | `/api/v1/health` |
| GET | `/api/v1/search` |
| GET | `/api/v1/object/<record_id>` |
| GET | `/api/v1/source/<source_id>` |
| GET | `/api/v1/absence` |

## Localhost-Only

| Method | Route |
| --- | --- |
| GET | `/review` |
| GET | `/review/<review_item_id>` |
| GET | `/rebuild` |
| GET | `/api/v1/review` |
| GET | `/api/v1/rebuild/status` |
| POST | `/review/<review_item_id>/decision` |
| POST | `/rebuild` |

Future route classes for source probes, WorkUnit execution, extraction, agents,
config mutation, uploads, downloads, and install/execute actions remain blocked
from LAN clients.
