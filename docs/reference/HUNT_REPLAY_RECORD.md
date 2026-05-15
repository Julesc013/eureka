# Hunt Replay Record

`HuntReplayRecord` captures a deterministic local replay run.

Required fields include `replay_id`, `replay_source`, `hunt_id`, `query`, `instance_schema_version`, `index_snapshot_id`, `expected_steps`, `executed_steps`, `blocked_steps`, `skipped_steps`, `expected_outputs`, `actual_outputs`, `diff_summary`, `status`, `warnings`, `limitations`, `started_at`, and `finished_at`.

Replay records also carry explicit false boundary flags for source probes, extraction, external network, model/provider use, artifact acquisition or launch, master-index mutation, site output mutation, deployment, production readiness, and public launch readiness.
