# Search Hunt Exhaustion Report Record

The runtime record is `SearchHuntExhaustionReport`.

Required fields:

- `report_id`
- `hunt_id`
- `schema_version`
- `created_at`
- `state`
- `query_summary`
- `checked_layers`
- `result_state`
- `unchecked_or_deferred_layers`
- `blocked_by_policy`
- `recommended_next_actions`
- `limitations`
- `warnings`
- `non_claims`

Allowed states:

- `informative`
- `insufficient_local_index`
- `blocked_by_policy`
- `waiting_for_user`
- `waiting_for_policy`
- `complete_enough_locally`
- `failed_report_generation`

The record carries explicit false side-effect flags for WorkUnit creation, source probes, external network, model/provider use, review mutation, public index mutation, master index mutation, deployment, and production/public-launch claims.
