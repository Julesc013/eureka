# Run Event Log

`run_event.v0` records append-only operational events for a run:

- `run_created`
- `query_compiled`
- `command_applied`
- `command_blocked`
- `workunits_scheduled`
- `lane_snapshot_built`
- `coverage_report_built`

Events are useful for projection and debugging. They are not reviewed records
and cannot mutate stores.
