# Replay And Compare

Replay uses `runtime.resolution_run.replay_run_bundle` and writes only a generated `replay_report.json` inside the durable run bundle.

Compare is read-only. It loads two durable run details and reports query/state equality, event count delta, WorkUnit count delta, result count delta, and lane differences.

