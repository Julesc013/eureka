# Runtime

`runtime/` holds Eureka's Python reference runtime. Python remains the
executable reference backend and product-oracle lane for the current baseline.

Current families include:

- `engine/`: core resolution, planning, indexing, eval, memory, and interface
  boundaries
- `gateway/`: gateway-facing runtime and public API projections
- `connectors/`: bounded acquisition/metadata adapters
- `local/`: local appliance, service, worker, and foundry families
- `source/`: source cache, source registry, and source observation families
- `index/`: candidate and public-index runtime families
- `evidence/`: evidence ledger runtime family
- `review/`: review queue runtime family
- `search/`: search hunt, need, quality, and explanation families
- `worker/`: work-unit queue and worker families

## Taxonomy Closeout

`runtime/engine` remains the current engine/kernel boundary. The active
taxonomy uses canonical families such as `runtime/local/`, `runtime/source/`,
`runtime/index/`, `runtime/evidence/`, `runtime/review/`, `runtime/search/`,
and `runtime/worker/`.

Old first-level runtime package names remain compatibility shims for import
stability. They are not canonical implementation homes. New implementation
should move to the canonical family path instead.

## Current Runtime Boundaries

The runtime supports local/operator behavior and read-only public-alpha route
foundations. Public live source fanout, downloads, uploads, broad extraction,
model/provider calls, public mutation, deployment, native marketplace behavior,
and automatic master/public index mutation remain disabled or gated.
