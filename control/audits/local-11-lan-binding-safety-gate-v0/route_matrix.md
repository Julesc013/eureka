# Route Matrix

Read-only LAN-allowed routes:

- `GET /`
- `GET /status`
- `GET /health`
- `GET /search`
- `GET /object/<record_id>`
- `GET /source/<source_id>`
- `GET /absence`
- `GET /api/v1/status`
- `GET /api/v1/health`
- `GET /api/v1/search`
- `GET /api/v1/object/<record_id>`
- `GET /api/v1/source/<source_id>`
- `GET /api/v1/absence`

Localhost-only routes:

- `GET /review`
- `GET /review/<review_item_id>`
- `GET /rebuild`
- `GET /api/v1/review`
- `GET /api/v1/review/<review_item_id>`
- `GET /api/v1/rebuild/status`
- `POST /review/<review_item_id>/decision`
- `POST /rebuild`
