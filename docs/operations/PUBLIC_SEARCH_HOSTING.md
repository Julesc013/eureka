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
- `data/public_index` is the generated public-safe search index bundle used by
  the wrapper and local public-search runtime.
- `site/dist/data/search_config.json` records static search handoff status.
- `site/dist/data/public_index_summary.json` records the static summary of the
  generated public index.
- Static pages may hand off to a configured backend only after a later evidence
  pack records the deployed URL and commit.
- The static site must not hardcode localhost as a public backend URL.
- Backend hosting does not enable live probes or source connectors.

## Operator Steps

1. Choose a backend host.
2. Create a service from the repository or Dockerfile.
3. Validate the generated public index with
   `python scripts/build_public_search_index.py --check` and
   `python scripts/validate_public_search_index.py`.
4. Set the safe environment variables documented in
   `docs/operations/PUBLIC_SEARCH_ENVIRONMENT.md`.
5. Bind the service to `PORT` and `0.0.0.0` in the hosting environment.
6. Deploy.
7. Check `/healthz`.
8. Check `/api/v1/status`.
9. Check `/search?q=windows+7+apps`.
10. Verify forbidden parameters such as `index_path`, `url`, `live_probe`,
   `download`, and `upload` are rejected.
11. Add rate limits or edge controls before broader exposure.
12. Record deployed URL, commit, run ID or service revision, environment, and
    route evidence in a later audit pack.

These steps are instructions only. They have not been performed by P54 or P55.
P56 also does not perform them; it keeps static backend status unconfigured.

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
## P58 Local Hosted Rehearsal

P58 adds `scripts/run_hosted_public_search_rehearsal.py`, which starts the
hosted wrapper on `127.0.0.1` with safe hosted settings and checks the public
route surface over local HTTP. This is still no deployment evidence: backend
hosting, DNS/TLS, provider setup, edge rate limits, and hosted URL verification
remain operator-gated.
## P64 Candidate Index Note

Candidate Index v0 does not change hosting readiness. Future hosted candidate
behavior would require separate storage, privacy, poisoning, review, promotion,
rate-limit, timeout, circuit-breaker, and operator evidence before deployment.

## P77 Evidence Status

The repo-configured static URL was checked and returned 404 for required static routes. No hosted public search backend URL is configured. Hosting remains operator-gated; deploy and verify the backend separately before updating static handoff.
