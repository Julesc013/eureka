# Search Hunt Command API

HUNT-03 adds these read-only routes:

- `GET /hunt/<hunt_id>/commands`
- `GET /api/v1/hunt/<hunt_id>/commands`
- `GET /hunt/<hunt_id>/steering`
- `GET /api/v1/hunt/<hunt_id>/steering`

HUNT-03 adds these operator-gated localhost-only routes:

- `POST /hunt/<hunt_id>/pause`
- `POST /hunt/<hunt_id>/resume`
- `POST /hunt/<hunt_id>/cancel`
- `POST /hunt/<hunt_id>/block`
- `POST /hunt/<hunt_id>/wait-for-user`
- `POST /hunt/<hunt_id>/wait-for-policy`
- `POST /hunt/<hunt_id>/steer`

Mutating routes require `operator_token` in the submitted form body or an `X-Eureka-Operator-Token` header. Missing and invalid tokens are rejected. LAN mutation attempts are rejected.

All route responses keep the boundary flags explicit: no WorkUnit creation, no source probes, no model/provider calls, no review mutation, no public index mutation, no master index mutation, and no deployment.
