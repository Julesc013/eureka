# Hosted Wrapper Requirements

P54 must implement only the P53 route contract in `local_index_only` mode.

Required routes:

- `GET /healthz`
- `GET /status`
- `GET /search`
- `GET /api/v1/status`
- `GET /api/v1/search`
- `GET /api/v1/query-plan`
- `GET /api/v1/sources`
- `GET /api/v1/source/{source_id}`

Required defaults:

- `EUREKA_PUBLIC_MODE=1`
- `EUREKA_SEARCH_MODE=local_index_only`
- `EUREKA_ALLOW_LIVE_PROBES=0`
- `EUREKA_ALLOW_DOWNLOADS=0`
- `EUREKA_ALLOW_UPLOADS=0`
- `EUREKA_ALLOW_LOCAL_PATHS=0`
- `EUREKA_ALLOW_ARBITRARY_URL_FETCH=0`
- `EUREKA_MAX_QUERY_LEN=160`
- `EUREKA_MAX_RESULTS=25`
- `EUREKA_GLOBAL_TIMEOUT_MS=5000`

P54 must reject forbidden parameters, enforce query/result limits, emit
public-safe errors, keep telemetry off by default, and require future
rate-limit, kill-switch, and deployment evidence gates.
