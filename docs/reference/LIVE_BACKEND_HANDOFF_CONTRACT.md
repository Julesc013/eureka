# Live Backend Handoff Contract

Live Backend Handoff Contract v0 reserves the future static-to-live backend
boundary for Eureka. It is not a production API and does not make `/api/v1/` live.

The current GitHub Pages publication target is static only. It publishes
`site/dist/`; it does not host Python, route requests to a backend, call live
sources, or enable live probes.

## Future Prefix

The reserved future public-alpha backend prefix is:

```text
/api/v1/
```

The current local stdlib helper routes under `/api` are local/prototype
public-alpha routes. They are useful for local smoke checks and wrapper
rehearsal, but they are not the stable public handoff contract.

Reserved endpoint families are recorded in:

```text
control/inventory/publication/live_backend_handoff.json
control/inventory/publication/live_backend_routes.json
```

## Required Client Behavior

Static clients and future native/API clients must treat live backend data as
experimental. They must:

- check capability flags before using live behavior
- tolerate live backend unavailability
- prefer static `/data/*.json` summaries when no backend is available
- avoid assuming live probes exist
- keep static demo routes under `/demo/` separate from live API routes

## Future Status Shape

A future `/api/v1/status` response should include enough capability state for
clients to decide whether live handoff is available:

```json
{
  "ok": true,
  "mode": "public_alpha",
  "production_ready": false,
  "capabilities": {
    "live_backend": true,
    "live_search": false,
    "live_probe_gateway": false,
    "internet_archive_live_probe": false
  }
}
```

This shape is a draft expectation only. It is not implemented by this task.

## Explicit Non-Guarantees

This contract does not add:

- backend hosting
- a stable production API
- live source probes
- live Internet Archive calls
- auth or accounts
- CORS policy
- rate limiting or abuse controls
- provider deployment configuration
- custom domain configuration

Live Probe Gateway Contract v0 now defines disabled-by-default source policy,
limits, cache/evidence expectations, and operator gates. It is policy only.
`/api/v1/live-probe` remains reserved and blocked for public alpha until a
later explicitly approved implementation exists.
