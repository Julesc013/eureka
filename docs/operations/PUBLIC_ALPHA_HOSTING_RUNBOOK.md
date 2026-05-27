# Public Alpha Hosting Runbook

This runbook is a pre-launch readiness reference. It must not be read as
deployment approval.

## Prerequisites

- Reviewed snapshot manifest is present and validated.
- Relay manifest is present and validated.
- `python scripts/validate_public_alpha_readonly.py` passes.
- `python scripts/validate_public_alpha_hosting_readiness.py` passes.
- Security headers, rate limits, privacy, abuse, takedown, observability, and
  rollback documents are present.
- External full discovery passes before any launch-candidate task.
- Deployment approval is explicit in a future reviewed task.

## Environment

Expected non-secret environment values are documented in
`docs/reference/PUBLIC_ALPHA_ENVIRONMENT.md`. No credentials, provider tokens, or
operator secrets are required for the read-only alpha baseline.

## Smoke Checks

- Status route responds from reviewed snapshot/relay data.
- Search route returns reviewed-index-only results.
- Object, source, evidence, absence, and needs pages render without write
  affordances.
- Attempts to request downloads or other disabled behavior are refused.

No deployment or publication is performed by this task.
