# Local Service Store Worker Boundary

The Local Appliance separates service, store, worker, workbench, and governance responsibilities.

- Service exposes local HTTP behavior and must default to read-only localhost.
- Stores own durable local state under an explicit instance root.
- Workers execute WorkUnits only and emit typed outputs.
- Workbench presents operator controls and review surfaces.
- Governance decides which effects are allowed and records evidence.

Workers cannot accept truth, mutate the public index directly, mutate the master index, crawl broadly by default, download packages, install packages, execute packages, or call model/provider agents until a future policy gate enables that behavior. All worker effects must pass through typed stores and review.

## LOCAL-03 Composition Rule

The local service, future workbench, future worker runtime, and tests must acquire local stores through `runtime/local/appliance.open_local_appliance(instance_path)`.

Direct store paths are not a service boundary. They skip instance root validation, schema support checks, store manifest validation, migration state checks, and disabled server/LAN/deployment flags.

LOCAL-03 composes only the current R0 stores:

- source cache
- evidence ledger
- review queue
- reviewed public index

It does not rebuild indexes or create review decisions. LOCAL-04 may add a read-only localhost service over this boundary.

## LOCAL-04 Service Rule

`runtime/local/service` is now the service adapter for read-only localhost HTTP access. It must receive an explicit instance path, open `LocalApplianceRuntime` in read-only mode, and route reads through that object.

The service boundary rejects write methods and LAN hosts. It does not run WorkUnits, source probes, review mutations, index rebuilds, deployment, or workbench UI behavior.

## LOCAL-07 Queue Rule

The local runtime now composes a fifth store, `workunit_queue`, from the instance manifest. The queue is the only durable place for proposed background/local work, but LOCAL-07 keeps it as records and transition history only.

Workers added later must consume WorkUnits through the runtime boundary and emit typed outputs through governed stores. A WorkUnit does not accept truth, mutate review decisions, mutate the public/master index, authorize downloads or installs, call providers, or start LAN/deployment behavior.

## LOCAL-09 Worker Rule

`runtime/local/worker` now executes only enabled deterministic worker kinds from queued WorkUnits. The runner records policy decisions, transition history, worker result references, and audit references.

The only LOCAL-09 worker allowed to mutate a product store is `reviewed_index_rebuild_worker`, and it is operator-token gated with mutation limited to the local reviewed `public_index`. Source probe, extraction, model/provider, download, install/execute, source sync, LAN, deployment, and master-index workers remain blocked.
