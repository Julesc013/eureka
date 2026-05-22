# Port Matrix

- `RunStore`: in-memory run packet store for deterministic local tests.
- `RunEventLog`: append/read event log.
- `PolicyGate`: blocks unsafe commands and actions.
- `WorkUnitScheduler`: plans IA-HUNT dry-run WorkUnits.
- `LaneProjector`: assembles projection-safe result lane snapshots.
- `ProjectionAdapter`: represented by projection profile handling in the lane projector.

Persistent stores, browser adapters, API adapters, relay adapters, and native
read-only adapters are deferred to later tasks.
