# Public Alpha Launch Gates

`PUBLIC-ALPHA-HOSTING-READINESS-00` does not approve launch. A future launch
candidate must satisfy all gates below.

## Required Gates

- Public routes are read-only.
- API routes are read-only.
- No live source fanout is enabled.
- No public mutation is enabled.
- Downloads, uploads, extraction, and model/provider calls are disabled.
- Snapshot/relay validation passes.
- Public alpha read-only validation passes.
- Hosting-readiness validation passes.
- External full discovery passes before launch candidate approval.
- Security headers and CSP are configured for the hosting mode.
- Anonymous rate limits and request size limits are configured.
- Privacy, abuse, and takedown docs are present.
- Rollback plan is present and rehearsable.
- Deployment approval is explicit in a future reviewed task.

Until those gates pass, production readiness and public launch readiness remain
false.
