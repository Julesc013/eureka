# Local Runtime Composition Boundary

LOCAL-03 adds `runtime/local_appliance` as the stable product-facing boundary for opening a local appliance instance.

## Purpose

The boundary composes an explicit instance root, versioned instance configuration, store manifest, migration state, and the four existing R0 SQLite stores into one `LocalApplianceRuntime` object. Future local service, workbench, worker, and test code should use this object instead of opening database files directly.

The composition boundary does not create product truth. It only opens initialized local stores, checks their integrity, and reports status.

## Boundary Contract

`open_local_appliance(instance_path, read_only=False)`:

- requires an explicit instance path
- rejects repo root, hidden local roots, private roots, generated site output roots, and forbidden product/runtime roots
- loads `config/instance.json`
- loads `config/store_manifest.json`
- loads `config/migration_state.json`
- fails closed for unsupported instance schema versions
- fails closed when migration state has blockers or requires destructive migration
- opens `source_cache`, `evidence_ledger`, `review_queue`, and `public_index` from manifest relative paths
- returns a `LocalApplianceRuntime`

`LocalApplianceRuntime` exposes:

- `instance_ref`
- `config`
- `store_manifest`
- `migration_state`
- `source_cache`
- `evidence_ledger`
- `review_queue`
- `public_index`
- `status()`
- `check_integrity()`
- `close()`

## Store Access

The store paths must come from `config/store_manifest.json`. Direct ad hoc paths are forbidden because they bypass instance validation, schema checks, migration state, and future service/workbench policy gates.

The current composed stores are:

- `source_cache` at `db/source_cache.sqlite`
- `evidence_ledger` at `db/evidence_ledger.sqlite`
- `review_queue` at `db/review_queue.sqlite`
- `public_index` at `db/public_index.sqlite`

LOCAL-03 performs only open, status, integrity, and close behavior. It does not create review decisions, rebuild indexes, run source probes, or mutate public/master index state.

## Non-Behavior

LOCAL-03 does not implement:

- HTTP server
- HTML workbench
- WorkUnit queue
- source probe runner
- index rebuild loop
- LAN mode
- deployment
- production readiness
- public launch readiness

## Handoff

LOCAL-04 can build the read-only localhost HTTP service over `LocalApplianceRuntime`. That service should receive an explicit instance path and call this boundary for status and reviewed-index reads.

LOCAL-04 implements that read-only service as `runtime/local_service`. Future workbench and worker routes should continue to use the composition boundary instead of opening store paths ad hoc.
