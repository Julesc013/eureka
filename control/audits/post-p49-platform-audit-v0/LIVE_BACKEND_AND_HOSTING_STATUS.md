# Live Backend And Hosting Status

| Area | Evidence | Classification | Notes |
|---|---|---|---|
| Hosted backend | no provider/runtime evidence | `operator_gated` | GitHub Pages is static-only. |
| Deployment config | no `Dockerfile`, `render.yaml`, `fly.toml`, backend host config | `operator_gated` | Static Pages workflow exists only for `site/dist`. |
| Health endpoint | local public-alpha/status routes only | `implemented_local_prototype` | No hosted health endpoint. |
| Production env vars | no production env config | `operator_gated` | No credentials added. |
| Rate limits | policy only | `contract_only` | No hosted middleware. |
| TLS/auth/CORS | unresolved in live backend handoff | `operator_gated` | No deployment. |
| Process supervision | absent | `operator_gated` | No service process. |
| Logging/privacy | local privacy policy only | `contract_only` | No production logging stack. |
| Kill switch/rollback | absent | `operator_gated` | Needs host/operator design. |
| Observability | absent | `operator_gated` | No monitoring. |
| Database/object storage/worker plane | absent | `operator_gated` | No production data plane. |
| Deployment evidence | recorded Pages run failed | `blocked` | No successful Pages deployment evidence for current static artifact. |
