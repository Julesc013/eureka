# Local Auto-Test Harness

LOCAL-10 adds a deterministic command-driven harness for the Local Appliance.
It measures the localhost service and server-rendered workbench with fixed
route, search, absence, safety, and latency checks.

The harness is intentionally local. It calls only `127.0.0.1` or `localhost`
HTTP routes and inspects the deterministic worker registry without executing
workers. It does not search the web, run source probes, run extraction, call
models, bind LAN, write `site/dist`, mutate a master index, or deploy.

## Runtime Boundary

The runtime package is `runtime/local/eval`. It contains suite definitions, a
localhost runner, report builders, latency helpers, and safety assertions. It
does not open ad hoc stores and does not mutate appliance state.

The service under test remains the existing `runtime/local/service` adapter.
The harness pressures only reviewed local index routes, workbench HTML routes,
operator-token rejection behavior, and worker-kind policy posture.

## Suites

- `service_health`: checks home, status, health, and JSON health routes.
- `json_search`: runs fixed JSON queries against the local reviewed index.
- `html_workbench`: checks the local workbench pages are available.
- `absence`: verifies local/current-index absence semantics.
- `read_only_safety`: verifies unsafe methods and missing-token mutations are rejected.
- `worker_queue_safety`: verifies risky workers remain blocked without running workers.
- `latency_smoke`: records elapsed milliseconds without a strict gate.
- `local_state_cleanliness`: verifies local-only status flags.

## Non-Claims

Passing the harness is not a production-readiness claim and not a public launch
claim. It is local regression evidence for the current reviewed local index and
localhost surface only.
