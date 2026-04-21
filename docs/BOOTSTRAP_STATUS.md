# Bootstrap Status

Current status: foundational scaffold plus eleven executable local deterministic thin slices, with draft contracts and concrete dependency boundary paths in place while broader product implementation remains intentionally deferred.

## Established

- repo identity and founding docs
- minimal AIDE repo-operating profile and policies
- concrete advisory dependency policy that points to real engine interface boundary paths
- governed archive draft schema skeletons using one consistent JSON Schema style
- draft gateway public API and shared UI contracts aligned to the normal online path
- governed synthetic software fixture set for one exact-match local resolution path
- Python 3 standard library bootstrap execution lane for the current executable slices
- connector-shaped local source loading for governed synthetic software fixtures
- ingest, extract, and normalize boundary types for the bootstrap execution lane
- exact-match engine resolution over normalized records plus bounded object-summary mapping
- transport-neutral gateway submit and read boundary over an in-memory job service
- transport-neutral public search boundary over the governed synthetic software corpus
- shared workbench-session view-model mapping exercised without implementing web or native shells
- shared search-results view-model mapping exercised without implementing web or native shells
- shared resolution-actions view-model mapping exercised without implementing web or native shells
- local demo command that shows submit, read, and optional shared view-model output over the connector-shaped path
- first server-rendered web workbench slice under `surfaces/web/` that consumes the public gateway boundary and shared workbench session without engine coupling
- tiny stdlib local server entrypoint for the compatibility-first web workbench page
- first deterministic search-and-absence web slice that renders result lists and no-match reports and links back into exact resolution flow
- first bounded action/export slice that exposes a manifest-export action through the public boundary and returns deterministic JSON for known synthetic targets
- first portable bundle/export slice that exposes a deterministic self-contained resolution bundle through the public boundary and returns ZIP content for known synthetic targets
- first portable bundle inspection/readback slice that inspects a previously exported bundle through a public boundary and renders a compatibility-first HTML inspection page without live fixture dependence
- first deterministic local store/cache seam that assigns stable artifact identity, stores exported manifest and bundle artifacts in a local content-addressed store, and reads them back through the public boundary
- first stable resolved-resource identity seam that derives a deterministic bootstrap `resolved_resource_id` and propagates it across resolution, search, action, export, store, inspection, and compatibility-first surface projection
- first non-web local CLI surface under `surfaces/native/cli/` that reuses the same gateway public boundary and shared surface-neutral mappings already proven by the web surface for exact resolution, deterministic search, export, inspection, and stored-export flows
- first repo-local architectural-boundary checker under `scripts/check_architecture_boundaries.py` that enforces the current Python import layering between surfaces, `runtime/gateway/public_api`, connectors, and engine
- runtime component layout for engine, gateway, and connectors, including explicit engine interface boundaries
- surface layout for web and native
- component-local and root integration tests for the executable slices

## Intentionally Deferred

- finalized archive schema meaning
- broader automated dependency-policy enforcement tooling beyond the current narrow Python import checker
- mature gateway API semantics, wider public read coverage, and durable submit versus read guarantees
- final action semantics, installer behavior, download handling, restore/import handling, and durable manifest, bundle, inspection, or store guarantees
- final global identity semantics, cross-source merge behavior, and any durable resource-identity guarantees beyond the current bootstrap seam
- mature search semantics, ranking, and broader retrieval architecture
- real web application structure, browser-side behavior, authentication, and deployment assumptions
- real external connectors, ranking, retrieval, and broader provenance or trust semantics
- persistence beyond the local bootstrap filesystem store, background workers, and async orchestration
- richer web routing and page structure beyond the bootstrap compatibility-first workbench, search, manifest-export, bundle-export, stored-export, and bundle-inspection pages, plus native runtime behavior
- final native CLI, TUI, GUI, and offline mode decisions
- release automation and packaging implementation
