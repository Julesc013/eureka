# Health And Status Endpoints

`GET /healthz` returns public-safe JSON with no private paths, secrets, local
filesystem roots, stack traces, deployment URL, or provider status.

`GET /status` and `GET /api/v1/status` return the public search status envelope
plus P54 wrapper flags:

- `hosted_wrapper_configured: true`
- `hosted_backend_deployed: false`
- `hosted_deployment_verified: false`
- `dynamic_backend_deployed: false`
- disabled live probes, downloads, uploads, local paths, arbitrary URL fetch,
  telemetry, accounts, external calls, and AI runtime

Status confirms wrapper availability for local rehearsal only.
