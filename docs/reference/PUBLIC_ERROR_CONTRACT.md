# Public Error Contract

Status: governed by `contracts/api/error_response.v0.json`.

Public search errors must be public-safe. They must not expose stack traces,
private local paths, credentials, secret values, provider internals, or raw
suspicious query material.

Required fields are:

- `ok: false`
- `schema_version`
- `contract_id`
- `mode`
- `error.code`
- `error.message`
- `error.status`
- `error.retryable`
- `error.severity`
- `limitations`
- `request_limits`

Required error codes include `query_required`, `query_too_long`,
`limit_too_large`, `unsupported_mode`, `unsupported_profile`,
`unsupported_include`, `forbidden_parameter`, `local_paths_forbidden`,
`arbitrary_url_fetch_forbidden`, `downloads_disabled`, `installs_disabled`,
`uploads_disabled`, `live_probes_disabled`, `live_backend_unavailable`,
`rate_limited`, `timeout`, `bad_request`, and
`internal_error_public_safe`.

The legacy `internal_error` code remains present for old local/prototype
clients, but P54 should prefer `internal_error_public_safe`.
