# Route Matrix

- `GET /review`: read-only HTML review queue.
- `GET /review/<review_item_id>`: read-only HTML review item detail.
- `GET /rebuild`: read-only HTML rebuild page.
- `GET /api/v1/review`: read-only JSON review queue.
- `GET /api/v1/review/<review_item_id>`: read-only JSON review item detail.
- `GET /api/v1/rebuild/status`: read-only JSON rebuild status.
- `POST /review/<review_item_id>/decision`: token-gated local review mutation.
- `POST /rebuild`: token-gated local reviewed-index rebuild.
