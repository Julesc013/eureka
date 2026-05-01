# Search Config Review

P56 adds governed static search configuration at:

- `control/inventory/publication/static_search_config.json`
- `site/dist/data/search_config.json`

Current generated status:

- `hosted_backend_status`: `backend_unconfigured`
- `hosted_backend_url`: `null`
- `hosted_backend_verified`: `false`
- `search_form_enabled`: `false`
- `mode`: `local_index_only`
- `max_query_length`: `160`
- `default_result_limit`: `10`
- `no_js_required`: `true`

Disabled hard flags:

- live probes
- downloads
- uploads
- local paths
- arbitrary URL fetch

The configuration is static handoff metadata only. A verified backend URL must
come from a later operator evidence record before hosted form submission is
enabled.
