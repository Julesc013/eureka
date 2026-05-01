# Operator Deployment Steps

1. Choose a backend host.
2. Create a service from the repository or Dockerfile.
3. Set safe environment variables from `docs/operations/PUBLIC_SEARCH_ENVIRONMENT.md`.
4. Bind to `PORT` and `0.0.0.0` in the hosting environment.
5. Deploy.
6. Check `/healthz`.
7. Check `/api/v1/status`.
8. Check `/search?q=windows+7+apps`.
9. Verify `index_path`, `url`, `live_probe`, `download`, and `upload` are rejected.
10. Add edge/rate-limit controls before broader exposure.
11. Record deployment URL, commit, service revision or run ID, environment,
    route checks, and rollback evidence.
12. Update a later audit evidence pack.

These steps remain operator work; P54 did not perform them.
