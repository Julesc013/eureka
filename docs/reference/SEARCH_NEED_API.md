# SearchNeed API

Read-only routes:

- `GET /needs`
- `GET /need/<need_id>`
- `GET /api/v1/needs`
- `GET /api/v1/need/<need_id>`
- `GET /hunt/<hunt_id>/needs`
- `GET /api/v1/hunt/<hunt_id>/needs`

Operator-gated localhost mutation routes:

- `POST /hunt/<hunt_id>/search-need`
- `POST /api/v1/hunt/<hunt_id>/search-need`
- `POST /need/<need_id>/state`
- `POST /api/v1/need/<need_id>/state`

Mutation routes require an operator token. LAN clients receive 403. The routes mutate only local SearchNeed state and links.
