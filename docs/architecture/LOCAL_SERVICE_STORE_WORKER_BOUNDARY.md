# Local Service Store Worker Boundary

The Local Appliance separates service, store, worker, workbench, and governance responsibilities.

- Service exposes local HTTP behavior and must default to read-only localhost.
- Stores own durable local state under an explicit instance root.
- Workers execute WorkUnits only and emit typed outputs.
- Workbench presents operator controls and review surfaces.
- Governance decides which effects are allowed and records evidence.

Workers cannot accept truth, mutate the public index directly, mutate the master index, crawl broadly by default, download packages, install packages, execute packages, or call model/provider agents until a future policy gate enables that behavior. All worker effects must pass through typed stores and review.
