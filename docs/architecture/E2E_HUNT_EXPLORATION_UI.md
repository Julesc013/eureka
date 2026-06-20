# E2E Hunt Exploration UI

`E2E-HUNT-EXPLORATION-UI-00` adds a private local `/explore` workspace over the existing E2E Reference Runner and E2E Preview Index.

The UI is a projection layer. It does not own search semantics, Hunt scheduling, Preview Index records, review decisions, reviewed records, or public service behavior.

## Architecture

- Discovery/run behavior stays in `runtime.resolution_run`.
- Preview search stays in `runtime.index.preview`.
- Local projection and bundle reading live in `runtime.local.e2e_hunt_exploration`.
- HTTP routing stays in `runtime.local.service.routes`.
- HTML rendering lives under `surfaces.web.workbench`.

## Routes

- `GET /explore`
- `GET /explore/runs`
- `GET /explore/run/<run-id>`
- `GET /explore/compare?left=<run-id>&right=<run-id>`
- `GET /api/v1/explore`
- `GET /api/v1/explore/runs`
- `GET /api/v1/explore/run/<run-id>`
- `GET /api/v1/explore/compare`
- `POST /explore/run/start`
- `POST /explore/run/<run-id>/pause`
- `POST /explore/run/<run-id>/resume`
- `POST /explore/run/<run-id>/cancel`
- `POST /explore/run/<run-id>/step`
- `POST /explore/run/<run-id>/replay`

The POST routes are loopback-only and operator-token gated. GET routes do not mutate state.

## Boundaries

Explore may write generated synthetic run bundles under `.eureka/e2e-reference/runs/`. It must not write Review Ledger decisions, reviewed records, reviewed/master indexes, public indexes, snapshots, source observations, candidate stores, or evidence-ledger stores.

The workspace may display candidates, evidence mentions, needs, near misses, absences, blocked states, unavailable states, unknowns, and reviewed records when those are already present in the Preview Index. Displaying a record does not change its authority.

## Non-Claims

- No reviewed IA truth is created.
- No public Workbench is exposed.
- No live provider/network calls are performed.
- No downloads, file payload fetches, Wayback replay, installs, execution, or public fanout are performed.
- No production-readiness or public-launch claim is made.
