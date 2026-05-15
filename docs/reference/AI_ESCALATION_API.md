# AI Escalation API

Read-only routes:

- `GET /hunt/<hunt_id>/ai-escalation`
- `GET /api/v1/hunt/<hunt_id>/ai-escalation`
- `GET /need/<need_id>/ai-escalation`
- `GET /api/v1/need/<need_id>/ai-escalation`

Local preflight routes:

- `POST /hunt/<hunt_id>/ai-escalation/preflight`
- `POST /api/v1/hunt/<hunt_id>/ai-escalation/preflight`
- `POST /need/<need_id>/ai-escalation/preflight`
- `POST /api/v1/need/<need_id>/ai-escalation/preflight`

Preflight routes require an operator token and loopback access. LAN clients are blocked. There is no execution route.

Responses include eligibility state, missing requirements, latest preflight, gate records, disabled provider flags, candidate-only output flags, and no-claim boundaries.
