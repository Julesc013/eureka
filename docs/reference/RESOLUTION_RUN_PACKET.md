# Resolution Run Packet

`resolution_run.v0` records the state of a headless run.

Required concepts:

- `run_id`
- `request_id`
- `compiled_query_id`
- `state`
- `state_history`
- `active_lanes`
- `controls_available`
- `coverage_report_id`
- `dry_run`
- `accepted_truth: false`

The packet is operational state, not accepted evidence or reviewed truth.
