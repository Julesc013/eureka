# Runner Architecture

The E2E reference runner is an extension of `runtime/resolution_run`, not a new
engine.

Architecture:

```text
E2EReferenceRunner
  -> RunStore
  -> RunEventStore
  -> WorkUnitScheduler
  -> WorkUnitExecutor
  -> RunProjector
  -> LocalRunBundleStore
  -> Replay validator
```

The runner is step-oriented and deterministic for tests. CLI and Workbench keep
using the same compatibility facade.
