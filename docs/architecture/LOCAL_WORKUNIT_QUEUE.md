# Local WorkUnit Queue

LOCAL-07 adds the durable local WorkUnit queue for the Local Appliance. It is an operator-gated record store, not a worker runner.

The queue lives in `runtime/workunit_queue` and is opened through `runtime/local_appliance`. The instance manifest owns the path `db/workunit_queue.sqlite`; product code must not invent a hidden queue path or open a separate database.

## Role

WorkUnits are the durable unit for proposed local/background work. Future source probes, extraction, review follow-up, index rebuilds, regression checks, Search Hunt Sessions, and agent-like delegated work route through this queue before anything executes.

A WorkUnit is not truth, not evidence acceptance, not permission to mutate the public index, and not permission to crawl, download, install, execute, or call a model/provider.

## Boundary

LOCAL-07 only records queue state:

- create and inspect WorkUnits
- list queue records
- record valid state transitions
- preserve transition history
- reject invalid transitions
- keep terminal transitions idempotent where practical

LOCAL-07 does not run workers, source probes, extraction, Search Hunt Sessions, review decisions, index rebuilds, LAN operations, deployments, downloads, installs, executable actions, or model/provider calls.

LOCAL-09 adds a separate deterministic runner over this queue. Queue records remain the durable coordination unit; execution is now explicit, policy-checked, and limited to enabled local worker kinds.

## Store

The queue store is SQLite-backed and manifest-defined:

- store id: `workunit_queue`
- relative path: `db/workunit_queue.sqlite`
- runtime API: `runtime.workunit_queue.WorkUnitQueueStore`

The local runtime status includes queue integrity and a queue summary. The HTTP service and HTML workbench stay read-only in LOCAL-07.

## Future Relationship

LOCAL-08 may add review/rebuild UI over the existing boundaries. LOCAL-09 adds the first worker relationship: workers consume queued records, emit typed results, and record audit references. HUNT, F, G, and H tracks should use WorkUnits as coordination records, not as truth acceptance.
