# Search Hunt Integration API

HUNT-08 smoke covers these JSON routes:

- `GET /api/v1/status`
- `GET /api/v1/hunts`
- `GET /api/v1/hunt/<hunt_id>`
- `GET /api/v1/hunt/<hunt_id>/exhaustion`
- `GET /api/v1/hunt/<hunt_id>/needs`
- `GET /api/v1/need/<need_id>`
- `GET /api/v1/need/<need_id>/workunits`
- `GET /api/v1/hunt/<hunt_id>/runner`

Mutating workflow routes remain localhost-only and operator-token-gated.
