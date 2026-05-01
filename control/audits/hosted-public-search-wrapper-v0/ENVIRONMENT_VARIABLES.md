# Environment Variables

`scripts/run_hosted_public_search.py --check-config` validates safe defaults:

| Variable | P54 value |
| --- | --- |
| `PORT` | `8080` default |
| `EUREKA_PUBLIC_MODE` | `1` |
| `EUREKA_SEARCH_MODE` | `local_index_only` |
| `EUREKA_ALLOW_LIVE_PROBES` | `0` |
| `EUREKA_ALLOW_DOWNLOADS` | `0` |
| `EUREKA_ALLOW_UPLOADS` | `0` |
| `EUREKA_ALLOW_LOCAL_PATHS` | `0` |
| `EUREKA_ALLOW_ARBITRARY_URL_FETCH` | `0` |
| `EUREKA_ALLOW_INSTALL_ACTIONS` | `0` |
| `EUREKA_ALLOW_TELEMETRY` | `0` |
| `EUREKA_MAX_QUERY_LEN` | `160` |
| `EUREKA_MAX_RESULTS` | `20` |
| `EUREKA_GLOBAL_TIMEOUT_MS` | `5000` |
| `EUREKA_OPERATOR_KILL_SWITCH` | `0` normally, `1` fails closed |

Local checks bind to `127.0.0.1`. Operator-hosted runs may bind to `0.0.0.0`
only as an explicit hosting bind choice.
