# View Model Matrix

| Payload | Source |
| --- | --- |
| workspace | Preview Index search plus durable run list |
| run list | `run_manifest.json` from durable bundles |
| run detail | `run_state.json`, `events.jsonl`, `workunits.jsonl`, `lane_snapshot.json`, `result.json` |
| run controls | run state and shared runner terminal-state rules |
| replay | `replay_run_bundle` |
| compare | two durable run details, read-only |

