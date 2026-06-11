# Policy Report

## Policy Controls Exercised

```text
fallback disabled -> policy_blocked
source family disabled -> policy_blocked
source family not allowlisted -> policy_blocked
candidate limit -> bounded provider rows
malformed metadata -> unavailable
empty metadata -> need
near miss metadata -> near_miss
```

## Network Policy

Live network is not required for the smoke. The IA provider uses deterministic
fixture transport in tests.

## Forbidden Behavior

```text
downloads: forbidden
file_fetching: forbidden
Wayback_replay: forbidden
artifact_verification: forbidden
rights_clearance_claim: forbidden
malware_safety_claim: forbidden
reviewed_public_master_index_mutation: forbidden
public_route_direct_provider_call: forbidden
```

