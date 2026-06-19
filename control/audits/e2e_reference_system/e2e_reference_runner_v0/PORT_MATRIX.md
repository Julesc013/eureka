# Port Matrix

The runner defines ports for nondeterministic and boundary-sensitive behavior:

- RunnerClock
- RunIdFactory
- RunStore
- RunEventStore
- WorkUnitScheduler
- WorkUnitExecutor
- RunPolicyEvaluator
- RunProjector
- RunBundleWriter
- ReplayReader

These ports isolate time, persistence, scheduling, execution, policy,
projection, bundles, and replay from the core lifecycle.
