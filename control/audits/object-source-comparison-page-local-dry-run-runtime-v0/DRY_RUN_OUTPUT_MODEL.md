# Dry-Run Output Model

The CLI emits a JSON report with:

- `report_id`
- `mode: local_dry_run`
- `input_roots`
- `pages_seen`
- `pages_valid`
- `pages_invalid`
- `page_summaries`
- `page_kinds`
- `page_statuses`
- `lane_counts`
- `privacy_status_counts`
- `public_safety_status_counts`
- `action_status_counts`
- `conflict_gap_counts`
- `preview_outputs`
- `mutation_summary`
- `warnings`
- `errors`
- `hard_booleans`

Hard booleans:

- `local_dry_run: true`
- `hosted_runtime_enabled: false`
- `public_routes_added: false`
- `api_routes_added: false`
- `public_search_runtime_mutated: false`
- `public_search_response_changed: false`
- `live_source_called: false`
- `external_calls_performed: false`
- `connector_runtime_executed: false`
- `source_cache_read: false`
- `source_cache_mutated: false`
- `evidence_ledger_read: false`
- `evidence_ledger_mutated: false`
- `candidate_index_mutated: false`
- `candidate_promotion_performed: false`
- `public_index_mutated: false`
- `local_index_mutated: false`
- `master_index_mutated: false`
- `telemetry_exported: false`
- `credentials_used: false`
- `downloads_enabled: false`
- `uploads_enabled: false`
- `installs_enabled: false`
- `execution_enabled: false`
