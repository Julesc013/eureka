# IA Metadata Live Probe Summary

- identifier: `eureka-software-fixture`
- result: `blocked`
- attempted: `false`
- request_count: `0`
- network_used: `false`
- public_index_mutated: `false`
- master_index_mutated: `false`

## Blocked Reasons
- source_policy.live_access_approved must be true
- source_policy.metadata_probe_approved must be true
- live_probe_policy.live_probe_enabled must be true
- live_probe_policy.approval_status is not approved
- endpoint_policy current behavior does not approve metadata read only
- endpoint_policy.current_network_calls_allowed must be true
- rate_limit_policy.proposed_user_agent is pending
- rate_limit_policy.contact_email is pending
- rate_limit_policy.timeout_seconds must be a positive number
- rate_limit_policy.max_requests_per_minute must be a positive number
- rate_limit_policy.retry_policy is pending
- cache_policy.cache_ttl or no-cache decision must be approved
- kill_switch_policy does not allow this one probe
- allowed identifier policy is not approved
- identifier is not approved: eureka-software-fixture
