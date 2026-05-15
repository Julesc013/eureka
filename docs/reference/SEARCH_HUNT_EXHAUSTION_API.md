# Search Hunt Exhaustion API

Read-only routes:

- `GET /hunt/<hunt_id>/exhaustion`
- `GET /api/v1/hunt/<hunt_id>/exhaustion`

Generation routes:

- `POST /hunt/<hunt_id>/exhaustion`
- `POST /api/v1/hunt/<hunt_id>/exhaustion`

Generation requires an operator token and loopback client scope. LAN clients receive `403`. Missing or invalid tokens receive `401`. Unknown hunt IDs receive `404`.

POST generation attaches a deterministic report to the local Search Hunt store and records local command history. It does not create WorkUnits, run source probes, call model providers, mutate review state, rebuild indexes, or mutate public/master indexes.
