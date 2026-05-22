# Command Matrix

Implemented read commands:

- `create_run`
- `inspect_run`
- `list_events`
- `list_lanes`
- `list_workunits`
- `export_run_packet`

Reserved commands such as live source runs, review, promote, apply, and rebuild return policy-blocked responses and do not mutate state.
