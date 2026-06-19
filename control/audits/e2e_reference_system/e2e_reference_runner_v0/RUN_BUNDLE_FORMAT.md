# Run Bundle Format

Generated local bundles are written under:

```text
.eureka/e2e-reference/runs/<run-id>/
```

Required files:

- run_manifest.json
- run_state.json
- events.jsonl
- workunits.jsonl
- result.json
- boundary_report.json
- lane_snapshot.json
- replay_report.json when replayed

The manifest records relative file names and hashes. `.eureka/` output remains
ignored local/private state.
