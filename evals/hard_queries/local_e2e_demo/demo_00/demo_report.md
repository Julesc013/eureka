# Local E2E Search Demo 00

This is a local product-proof demo over repo-local hard-query fixtures and SurfaceKernel baseline renderers.

It is not public-alpha readiness evidence and it is not artifact evidence.

## Gate Snapshot

```text
artifact gate: FAIL_INSUFFICIENT_REVIEWED_ARTIFACT_RECORDS
reviewed artifact records: 4/25
verified artifacts: 0
public alpha: blocked
dev -> main: blocked
external artifact evidence: absent
hardware details: absent
```

## Queries

| Query | Status | Concept |
| --- | --- | --- |
| Windows 7 apps | candidate | candidate |
| driver for Win98 | need | blocked_for_user_details |
| old blue FTP client for XP | near_miss | near_miss |
| manual for Sound Blaster CT1740 | candidate | candidate |
| latest Firefox before XP support ended | policy_blocked | policy_blocked |
| article about ray tracing in a 1994 magazine | unavailable | unavailable |

## Renderers

```text
json_v0
text_v0
html_basic_v0
snapshot_v0
```

## Truth Boundary

```text
live_source_calls: false
downloads_performed: false
reviewed_index_mutated: false
public_index_mutated: false
master_index_mutated: false
reviewed_artifact_records_created: 0
verified_artifacts_created: 0
```
