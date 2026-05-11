# H13 Local/Private Boundary Dry-Run Summary

- source_id: `local_folder_metadata`
- result: `blocked_by_missing_approval`
- operation_count: `0`
- local_access_used: `false`
- network_used: `false`
- boundary_dry_run_only: `true`
- local_access: `false`
- private_source_access: `false`
- user_supplied_url_fetch: `false`
- authenticated_access: `false`
- restricted_source_access: `false`
- cas_import: `false`
- pack_export_import: `false`
- source_cache_writes: `false`
- public_index_writes: `false`
- private_publication: `false`

## Blocked Reasons
- source approval_status is not approved_for_boundary_dry_run
- boundary_dry_run_approved is missing or false
- request key is not approved for this source
- request budget is not approved
- boundary dry-run kill switch is enabled
