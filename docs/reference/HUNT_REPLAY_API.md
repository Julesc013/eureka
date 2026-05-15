# Hunt Replay API

Read-only:

- `GET /hunt/<hunt_id>/replay`
- `GET /api/v1/hunt/<hunt_id>/replay`

Operator-gated localhost-only:

- `POST /hunt/<hunt_id>/replay/plan`
- `POST /api/v1/hunt/<hunt_id>/replay/plan`
- `POST /hunt/<hunt_id>/replay/run`
- `POST /api/v1/hunt/<hunt_id>/replay/run`

Plan routes do not replay workflow steps. Run routes require an operator token and loopback client scope. LAN clients receive 403. Unknown hunts return 404. No route runs source probes, extraction, model/provider calls, or deployment.
