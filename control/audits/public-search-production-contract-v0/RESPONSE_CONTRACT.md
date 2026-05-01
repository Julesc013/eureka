# Response Contract

Canonical schema: `contracts/api/search_response.v0.json`.

The P54 hosted wrapper must emit a public-safe response envelope with:

- `schema_version`, `contract_id`, `ok`, `mode`, and `stability`
- `query`
- `result_count`
- `results`
- `checked` and compatibility alias `checked_sources`
- `gaps`
- `warnings`
- `limitations`
- `absence` and compatibility alias `absence_summary`
- `source_status`
- `timing`
- `request_limits`
- `next_actions`

Safety flags must remain false in `local_index_only`: live probes, downloads,
uploads, installs, local paths, arbitrary URL fetch, and telemetry.

Results are public search result cards aligned with
`contracts/api/search_result_card.v0.json`.
