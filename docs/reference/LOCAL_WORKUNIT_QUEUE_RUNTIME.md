# Local WorkUnit Queue Runtime

The runtime API lives in `runtime/workunit_queue`.

## Records

- `WorkUnit`
- `WorkUnitType`
- `WorkUnitState`
- `WorkUnitPriority`
- `WorkUnitTransition`
- `WorkUnitSummary`

`WorkUnit` fields include `id`, `kind`, `state`, `title`, `payload`, `priority`, `created_at`, `updated_at`, `idempotency_key`, `parent_id`, `blocked_reason`, `warnings`, and `limitations`.

## Store

`WorkUnitQueueStore.open(path)` opens an explicit SQLite path from the local instance manifest. Call `init()` to create the schema. `close()` is idempotent.

Supported operations:

- `create_workunit(workunit)`
- `get_workunit(workunit_id)`
- `list_workunits(state=None, kind=None, limit=100)`
- `transition_workunit(workunit_id, target_state, reason=None)`
- `pause_workunit(workunit_id, reason=None)`
- `resume_workunit(workunit_id, reason=None)`
- `cancel_workunit(workunit_id, reason=None)`
- `block_workunit(workunit_id, reason)`
- `complete_workunit(workunit_id, reason=None)`
- `fail_workunit(workunit_id, reason)`
- `list_transitions(workunit_id=None, limit=100)`
- `summarize()`
- `check_integrity()`

## Composition

`open_local_appliance(instance_path)` exposes `runtime.workunit_queue` alongside source cache, evidence ledger, review queue, and public index. Read-only runtime mode blocks queue mutation helpers.

The queue store may mutate only queue tables. It does not mutate review decisions or rebuild indexes.
