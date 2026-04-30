# Blocked Request Results

The rehearsal checked representative unsafe or invalid requests against
`/api/v1/search`. Each response used the governed error envelope, avoided stack
traces, and did not leak private paths.

| Case | Expected code | Actual code | Status |
| --- | --- | --- | --- |
| missing `q` | `query_required` | `query_required` | pass |
| query too long | `query_too_long` | `query_too_long` | pass |
| limit too large | `limit_too_large` | `limit_too_large` | pass |
| unsupported `mode=live_probe` | `live_probes_disabled` | `live_probes_disabled` | pass |
| `index_path` parameter | `local_paths_forbidden` | `local_paths_forbidden` | pass |
| `store_root` parameter | `local_paths_forbidden` | `local_paths_forbidden` | pass |
| `url` parameter | `forbidden_parameter` | `forbidden_parameter` | pass |
| `fetch_url` parameter | `forbidden_parameter` | `forbidden_parameter` | pass |
| `download=true` | `downloads_disabled` | `downloads_disabled` | pass |
| `install=true` | `installs_disabled` | `installs_disabled` | pass |
| `upload=true` | `uploads_disabled` | `uploads_disabled` | pass |
| `source_credentials` parameter | `forbidden_parameter` | `forbidden_parameter` | pass |
| `api_key` parameter | `forbidden_parameter` | `forbidden_parameter` | pass |
| `live_source` parameter | `live_probes_disabled` | `live_probes_disabled` | pass |

This is request safety evidence only. It does not add hosted rate limiting,
accounts, telemetry, or production abuse protection.
