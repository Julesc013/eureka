# Wrapper Summary

P54 adds `scripts/run_hosted_public_search.py` as a narrow public-search-only
entrypoint. It wraps the existing gateway public search API and exposes:

- `GET /healthz`
- `GET /status`
- `GET /search?q=...`
- `GET /api/v1/status`
- `GET /api/v1/search?q=...`
- `GET /api/v1/query-plan?q=...`
- `GET /api/v1/sources`
- `GET /api/v1/source/{source_id}`

The wrapper is read-only, local-index-only, and deployment-unverified. The
full local workbench remains separate.
