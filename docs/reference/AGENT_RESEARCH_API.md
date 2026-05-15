# Agent Research API

Read-only routes:

- `GET /hunt/<hunt_id>/agent-tasks`
- `GET /api/v1/hunt/<hunt_id>/agent-tasks`
- `GET /need/<need_id>/agent-tasks`
- `GET /api/v1/need/<need_id>/agent-tasks`
- `GET /api/v1/agent-research/report-schema`

Draft routes:

- `POST /hunt/<hunt_id>/agent-task-draft`
- `POST /api/v1/hunt/<hunt_id>/agent-task-draft`
- `POST /need/<need_id>/agent-task-draft`
- `POST /api/v1/need/<need_id>/agent-task-draft`

Draft routes require loopback client scope and an operator token. They create disabled local task records only.

There is no execution route.
