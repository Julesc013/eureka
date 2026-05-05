# Public Search Environment

Status: safe hosted-wrapper defaults defined.

`scripts/run_hosted_public_search.py --check-config` validates the wrapper
environment before startup. Missing variables use safe defaults.

The environment contract preserves `local_index_only`, no live probes, no
downloads, no uploads, no local paths, no arbitrary URL fetch, no accounts, and
no telemetry by default.

## Safe Defaults

| Variable | Default | Meaning |
| --- | --- | --- |
| `PORT` | `8080` | Bind port. |
| `EUREKA_PUBLIC_MODE` | `1` | Hosted wrapper public posture. |
| `EUREKA_SEARCH_MODE` | `local_index_only` | Only active search mode. |
| `EUREKA_ALLOW_LIVE_PROBES` | `0` | Live probes disabled. |
| `EUREKA_ALLOW_DOWNLOADS` | `0` | Downloads disabled. |
| `EUREKA_ALLOW_UPLOADS` | `0` | Uploads disabled. |
| `EUREKA_ALLOW_LOCAL_PATHS` | `0` | Caller local paths disabled. |
| `EUREKA_ALLOW_ARBITRARY_URL_FETCH` | `0` | URL fetching disabled. |
| `EUREKA_ALLOW_INSTALL_ACTIONS` | `0` | Install and execute actions disabled. |
| `EUREKA_ALLOW_TELEMETRY` | `0` | Telemetry disabled. |
| `EUREKA_MAX_QUERY_LEN` | `160` | Public query character limit. |
| `EUREKA_MAX_RESULTS` | `20` | Hosted wrapper default cap, bounded by the contract max of 25. |
| `EUREKA_GLOBAL_TIMEOUT_MS` | `5000` | Hosted wrapper timeout budget. |
| `EUREKA_OPERATOR_KILL_SWITCH` | `0` | Set to `1` to fail closed before startup. |

`EUREKA_HOSTED_DEPLOYMENT_VERIFIED` and `EUREKA_DYNAMIC_BACKEND_DEPLOYED` must
not be set to true by local configuration. Deployment evidence belongs in a
later audit pack.

## Refused Settings

The config check fails if any of these are enabled:

- `EUREKA_ALLOW_LIVE_PROBES=1`
- `EUREKA_ALLOW_DOWNLOADS=1`
- `EUREKA_ALLOW_UPLOADS=1`
- `EUREKA_ALLOW_LOCAL_PATHS=1`
- `EUREKA_ALLOW_ARBITRARY_URL_FETCH=1`
- `EUREKA_ALLOW_INSTALL_ACTIONS=1`
- `EUREKA_ALLOW_TELEMETRY=1`
- `EUREKA_OPERATOR_KILL_SWITCH=1`

`EUREKA_SEARCH_MODE` must remain `local_index_only`.

The P55 generated public index must also be present at
`data/public_index/search_documents.ndjson`. This is not controlled by an
environment variable because public requests must never choose index paths or
source roots. If the bundle is missing, rebuild or validate it locally:

```powershell
python scripts/build_public_search_index.py --check
python scripts/validate_public_search_index.py
```

## Binding

Local checks bind to `127.0.0.1` by default. Operator-hosted runs may use:

```powershell
python scripts/run_hosted_public_search.py --public-mode --host 0.0.0.0
```

Binding to `0.0.0.0` is only a hosting bind choice. It is not deployment
evidence or approval for live probes, downloads, uploads, accounts, telemetry,
or source connectors.
## P58 Rehearsal Environment

The P58 hosted rehearsal uses the same safe environment expected for future
operator deployment: `EUREKA_PUBLIC_MODE=1`, `EUREKA_SEARCH_MODE=local_index_only`,
live probes/downloads/uploads/local paths/arbitrary URL fetch/install actions
and telemetry set to `0`, max query length `160`, max results `20`, timeout
budget `5000`, and kill switch `0`. The rehearsal binds only to localhost.
## P64 Candidate Index Note

No P64 environment variable enables candidate storage, candidate paths, source
roots, external sources, live probes, public search candidate injection, or
master-index mutation. Candidate index work remains contract-only.

## P77 URL Evidence Variables

`EUREKA_PUBLIC_STATIC_URL`, `EUREKA_STATIC_SITE_URL`, `EUREKA_PUBLIC_BACKEND_URL`, and `EUREKA_HOSTED_BACKEND_URL` are evidence inputs for the verifier only. They do not deploy services, enable live probes, or authorize index/cache/ledger mutation.
