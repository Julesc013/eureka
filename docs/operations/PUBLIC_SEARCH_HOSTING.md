# Public Search Hosting

Status: wrapper prepared; hosting remains operator-gated.

Eureka public search hosting begins with the P54 wrapper in
`local_index_only` mode. GitHub Pages remains static-only and cannot run this
Python backend.

Hosting guidance preserves no live probes, no downloads, no uploads, no
accounts, and no telemetry by default.

## Static And Dynamic Split

- `site/dist` is the static publication artifact.
- `scripts/run_hosted_public_search.py` is the backend wrapper entrypoint.
- Static pages may hand off to a configured backend only after a later evidence
  pack records the deployed URL and commit.
- The static site must not hardcode localhost as a public backend URL.
- Backend hosting does not enable live probes or source connectors.

## Operator Steps

1. Choose a backend host.
2. Create a service from the repository or Dockerfile.
3. Set the safe environment variables documented in
   `docs/operations/PUBLIC_SEARCH_ENVIRONMENT.md`.
4. Bind the service to `PORT` and `0.0.0.0` in the hosting environment.
5. Deploy.
6. Check `/healthz`.
7. Check `/api/v1/status`.
8. Check `/search?q=windows+7+apps`.
9. Verify forbidden parameters such as `index_path`, `url`, `live_probe`,
   `download`, and `upload` are rejected.
10. Add rate limits or edge controls before broader exposure.
11. Record deployed URL, commit, run ID or service revision, environment, and
    route evidence in a later audit pack.

These steps are instructions only. They have not been performed by P54.

## Deployment Templates

P54 adds a root `Dockerfile`, `.dockerignore`, `deploy/README.md`, and
`deploy/render/render.yaml` as inert templates. They contain no credentials and
do not call any hosting provider API.

## Still Required Later

- hosted deployment evidence
- rate-limit or abuse-control layer
- operator kill-switch procedure
- logging/privacy policy for hosted operation
- rollback evidence
- static-to-dynamic backend URL configuration
- hosted rehearsal evidence
