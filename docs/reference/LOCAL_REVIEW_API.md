# Local Review API

The review API is served by the localhost local service.

Read-only routes:

- `GET /review`
- `GET /review/<review_item_id>`
- `GET /rebuild`
- `GET /api/v1/review`
- `GET /api/v1/review/<review_item_id>`
- `GET /api/v1/rebuild/status`

Operator-gated mutation routes:

- `POST /review/<review_item_id>/decision`
- `POST /rebuild`

Mutation requests require an operator token through form field
`operator_token` or header `X-Eureka-Operator-Token`.

Review decision fields:

- `decision`: `accept`, `reject`, `block`, `request_more_evidence`, or
  `note_only`
- `reason`: required for `reject`, `block`, and `request_more_evidence`
- `local_only_confirmed`: required for `accept`
- `operator_label`: optional local label

Rebuild includes accepted review items only and excludes rejected, blocked,
superseded, queued, needs-review, and needs-more-evidence items.
