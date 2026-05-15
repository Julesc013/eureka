# Background Hunt API

Read-only routes:

- `GET /hunt/<hunt_id>/runner`
- `GET /api/v1/hunt/<hunt_id>/runner`
- `GET /hunt/<hunt_id>/workunits`
- `GET /api/v1/hunt/<hunt_id>/workunits`

Operator-gated localhost routes:

- `POST /hunt/<hunt_id>/runner/plan`
- `POST /api/v1/hunt/<hunt_id>/runner/plan`
- `POST /hunt/<hunt_id>/runner/run-next`
- `POST /api/v1/hunt/<hunt_id>/runner/run-next`
- `POST /hunt/<hunt_id>/runner/run-batch`
- `POST /api/v1/hunt/<hunt_id>/runner/run-batch`

`/runner/plan` is a preview route and records no worker result. `run-next` and `run-batch` require an operator token and loopback client scope.

Responses use `background_hunt_runner_response.v0` and include explicit false flags for source probes, extraction, external network use, model/provider use, acquisition actions, review mutation, master index mutation, deployment, production readiness, and public launch readiness.

