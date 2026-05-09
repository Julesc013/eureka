# H1 Metadata Live Probe Summary

- source_id: `pypi`
- result: `blocked_by_missing_approval`
- request_count: `0`
- network_used: `false`
- public_index_mutated: `false`
- master_index_mutated: `false`

## Blocked Reasons
- allowed_requests.pypi.live_access_approved must be true
- allowed_requests.pypi.metadata_probe_approved must be true
- request key is not approved for live use: example_project_metadata
- endpoint class is not currently allowlisted: project_metadata_lookup_future
- rate_limit_policy decision is not approved
- User-Agent/contact posture is not approved or documented as not required
- cache policy decision is not approved
- cache TTL or no-cache decision must be approved
- kill switch blocks live call
