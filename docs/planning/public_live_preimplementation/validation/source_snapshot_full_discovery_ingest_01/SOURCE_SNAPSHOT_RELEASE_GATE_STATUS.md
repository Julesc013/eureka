# Source Snapshot Release Gate Status

## Status

```text
SOURCE_SNAPSHOT_RELEASE_BLOCKED
```

## Reasons

- Full discovery is current but red.
- `source_snapshot_baseline_drift` is present.
- `generated_artifact_drift` is present.
- Architecture/leakage validators are red.
- Queue handoff drift is widespread enough to make promotion evidence unstable.

## Decision

Do not treat source/snapshot baseline as release-clean. Repair focused failure
families and rerun focused validation before any new external full-discovery
handoff.
