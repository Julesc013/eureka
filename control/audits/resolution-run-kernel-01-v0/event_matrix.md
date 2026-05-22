# Event Matrix

Implemented events:

- `run_created`
- `command_received`
- `command_applied`
- `command_blocked`
- `workunits_planned`
- `lane_snapshot_built`
- `coverage_report_built`
- `run_completed`

Events are local in-memory records in this foundation. They do not write
operator instance state or public/master indexes.
