# Hosted Mode Requirements

Hosted mode must run `local_index_only` search against Eureka-controlled local
public search records. Public callers must not provide filesystem roots, local
paths, URLs, credentials, source controls, uploads, downloads, install actions,
live probes, or network fanout controls.

Required defaults:

- `EUREKA_PUBLIC_MODE=1`
- `EUREKA_SEARCH_MODE=local_index_only`
- `EUREKA_ALLOW_LIVE_PROBES=0`
- `EUREKA_ALLOW_DOWNLOADS=0`
- `EUREKA_ALLOW_UPLOADS=0`
- `EUREKA_ALLOW_LOCAL_PATHS=0`
- `EUREKA_ALLOW_ARBITRARY_URL_FETCH=0`
- `EUREKA_ALLOW_INSTALL_ACTIONS=0`
- `EUREKA_ALLOW_TELEMETRY=0`
- `EUREKA_MAX_QUERY_LEN=160`
- `EUREKA_MAX_RESULTS=20`
- `EUREKA_GLOBAL_TIMEOUT_MS=5000`

`--check-config` fails closed if prohibited behavior is enabled.
