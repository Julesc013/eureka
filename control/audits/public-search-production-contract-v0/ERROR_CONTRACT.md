# Error Contract

Canonical schema: `contracts/api/error_response.v0.json`.

Errors must include `ok: false`, schema/contract IDs, `mode`, a public-safe
`error` object, `limitations`, and `request_limits`.

Required error codes include:

- `query_required`
- `query_too_long`
- `limit_too_large`
- `unsupported_mode`
- `unsupported_profile`
- `unsupported_include`
- `forbidden_parameter`
- `local_paths_forbidden`
- `arbitrary_url_fetch_forbidden`
- `downloads_disabled`
- `installs_disabled`
- `uploads_disabled`
- `live_probes_disabled`
- `live_backend_unavailable`
- `rate_limited`
- `timeout`
- `bad_request`
- `internal_error_public_safe`

Errors must not include stack traces, private paths, secrets, or raw suspicious
query material.
