# Remaining Blockers

- Configured static URL https://julesc013.github.io/eureka/ returned HTTP 404 for root, search.html, search_config.json, and public_index_summary.json during P77 verification.
- No hosted backend URL is configured in environment variables, repo deployment inventory, live backend handoff, or site/dist search_config.json.
- Backend health/status/search/query-plan/source routes were not checked against a public backend because no backend URL exists.
- Safe-query and blocked-request verification against a public backend remains operator-gated.
- Rate-limit and edge evidence is unavailable; no rate-limit headers or provider evidence were recorded.
- CORS/TLS/cache evidence is partial for the failed static 404 responses and unavailable for backend routes.
- Logging retention and telemetry evidence from hosted status endpoints is unavailable because no hosted backend was verified.
- GitHub Actions/Pages status is unverified unless a later authenticated gh check is recorded.
- Manual Observation Batch 0 remains a human-operated prerequisite for P78 baseline comparison.
