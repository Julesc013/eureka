# IA Review Integration Summary

- integration_status: `blocked_dry_run`
- source_cache_review_entry_created: `true`
- evidence_candidate_review_entry_created: `true`
- candidate_promotion_dry_run_created: `true`
- pack_draft_preview_created: `true`
- blocked_reason_count: `15`
- accepted_source_truth: `false`
- accepted_evidence_truth: `false`
- accepted_candidate_truth: `false`
- public_index_mutated: `false`
- master_index_mutated: `false`

## Blocked Reasons
- allowed identifier policy is not approved
- cache_policy.cache_ttl or no-cache decision must be approved
- endpoint_policy current behavior does not approve metadata read only
- endpoint_policy.current_network_calls_allowed must be true
- identifier is not approved: eureka-software-fixture
- kill_switch_policy does not allow this one probe
- live_probe_policy.approval_status is not approved
- live_probe_policy.live_probe_enabled must be true
- rate_limit_policy.contact_email is pending
- rate_limit_policy.max_requests_per_minute must be a positive number
- rate_limit_policy.proposed_user_agent is pending
- rate_limit_policy.retry_policy is pending
- rate_limit_policy.timeout_seconds must be a positive number
- source_policy.live_access_approved must be true
- source_policy.metadata_probe_approved must be true
