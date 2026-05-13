# Local Service Store Worker Boundary

The Local Appliance separates service, store, worker, workbench, and governance responsibilities.

- Service exposes local HTTP behavior and must default to read-only localhost.
- Stores own durable local state under an explicit instance root.
- Workers execute WorkUnits only and emit typed outputs.
- Workbench presents operator controls and review surfaces.
- Governance decides which effects are allowed and records evidence.

Workers cannot accept truth, mutate the public index directly, mutate the master index, crawl broadly by default, download packages, install packages, execute packages, or call model/provider agents until a future policy gate enables that behavior. All worker effects must pass through typed stores and review.

## LOCAL-03 Composition Rule

The local service, future workbench, future worker runtime, and tests must acquire local stores through `runtime/local_appliance.open_local_appliance(instance_path)`.

Direct store paths are not a service boundary. They skip instance root validation, schema support checks, store manifest validation, migration state checks, and disabled server/LAN/deployment flags.

LOCAL-03 composes only the current R0 stores:

- source cache
- evidence ledger
- review queue
- reviewed public index

It does not rebuild indexes or create review decisions. LOCAL-04 may add a read-only localhost service over this boundary.
