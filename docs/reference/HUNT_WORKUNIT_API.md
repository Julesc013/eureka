# Hunt WorkUnit API

Read routes:

- `GET /need/<need_id>/workunits`
- `GET /api/v1/need/<need_id>/workunits`
- `GET /hunt/<hunt_id>/workunits`
- `GET /api/v1/hunt/<hunt_id>/workunits`

Operator-gated localhost routes:

- `POST /need/<need_id>/workunits/plan`
- `POST /api/v1/need/<need_id>/workunits/plan`
- `POST /need/<need_id>/workunits`
- `POST /api/v1/need/<need_id>/workunits`

The POST routes require an operator token and are blocked for LAN clients.
