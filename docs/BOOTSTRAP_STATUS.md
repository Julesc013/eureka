# Bootstrap Status

Current status: foundational scaffold plus twenty-one executable local deterministic thin slices, with draft contracts and concrete dependency boundary paths in place while broader product implementation remains intentionally deferred.

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
- first local stdlib machine-readable HTTP API slice under `surfaces/web/server/` that exposes exact resolution, deterministic search, manifest export, bundle export, bundle inspection, and local stored-export flows as JSON or ZIP responses over the same transport-neutral public boundary already consumed by the HTML and CLI surfaces
- first bounded real external-source connector slice under `runtime/connectors/github_releases/` that loads small recorded GitHub Releases fixtures, normalizes them into the existing engine path, and exposes source-family visibility through the public boundary plus current web, CLI, and HTTP API surfaces
- first bounded provenance and evidence seam under `runtime/engine/provenance/` that carries compact source-backed evidence summaries from normalize through exact resolution, deterministic search, export, storage, bundle inspection, and current surfaces without forcing a final truth, trust, or merge model
- first bounded comparison and disagreement seam under `runtime/engine/compare/` that compares exactly two resolved targets side by side, preserves evidence per side, and surfaces explicit agreements and disagreements through the public boundary plus current surfaces without forcing merge or trust-selection behavior
- first bounded object/state timeline seam under `runtime/engine/states/` that groups multiple bounded states under one bootstrap `subject_key`, orders them deterministically, and surfaces compact source plus evidence summaries through the public boundary plus current surfaces without forcing a final object identity or temporal graph model
- first bounded absence-reasoning seam under `runtime/engine/absence/` that explains exact-resolution misses and deterministic search no-result cases with checked source-family summaries, compact near matches, and bounded next steps through the public boundary plus current surfaces without forcing ranking, trust, or final diagnostic behavior
- first bounded representation/access-path seam under `runtime/engine/representations/` that carries multiple known source-backed representation and access-path summaries for one resolved target through normalize, exact resolution, public boundaries, and current surfaces without forcing final download, install, import, restore, or representation-selection semantics
- first bounded compatibility and host-profile seam under `runtime/engine/compatibility/` that evaluates one resolved target against one bootstrap host profile preset, returns compact reasons plus honest `unknown` outcomes, and surfaces the verdict through the public boundary plus current surfaces without forcing installer logic, runtime routing, or a final compatibility oracle
- first bounded action-routing and recommendation seam under `runtime/engine/action_routing/` that combines one resolved target, bounded representations, optional host-profile compatibility, and bounded local export/store context into explicit recommended, available, and unavailable actions through the public boundary plus current surfaces without forcing execution, installer, or workflow-policy behavior
- first bounded user-strategy and intent-profile seam under `runtime/engine/strategy/` plus `runtime/engine/action_routing/` that lets the same resolved target produce different bounded recommendation emphasis under explicit strategy profiles while preserving underlying identity, evidence, and representation truth through the public boundary plus current surfaces
- runtime component layout for engine, gateway, and connectors, including explicit engine interface boundaries
- surface layout for web and native
- component-local and root integration tests for the executable slices

## Intentionally Deferred

- finalized archive schema meaning
- broader automated dependency-policy enforcement tooling beyond the current narrow Python import checker
- mature gateway API semantics, wider public read coverage, and durable submit versus read guarantees
- final HTTP API route naming, auth, HTTPS/TLS, deployment topology, and multi-user semantics beyond the current local bootstrap slice
- final action semantics, installer behavior, download handling, restore/import handling, and durable manifest, bundle, inspection, or store guarantees
- final global identity semantics, cross-source merge behavior, and any durable resource-identity guarantees beyond the current bootstrap seam
- final provenance graph semantics, trust scoring, and broader evidence or claim ontology work beyond the current bounded summary seam
- final comparison semantics, merge behavior, and truth-selection behavior beyond the current bounded disagreement seam
- final object, subject, and state identity plus ordering semantics beyond the current bounded timeline seam
- final diagnostic and absence-reasoning semantics beyond the current bounded miss-explanation seam
- final representation, access-path, download, install, import, and restore semantics beyond the current bounded representation seam
- final compatibility, host-profile, installer, and runtime-routing semantics beyond the current bounded compatibility seam
- final action-routing, strategy, execution, installer, workflow-policy, and personalization semantics beyond the current bounded recommendation seam
- mature search semantics, ranking, and broader retrieval architecture
- real web application structure, browser-side behavior, authentication, and deployment assumptions
- broader live external-source federation, live GitHub acquisition, ranking, retrieval, and broader provenance or trust semantics
- persistence beyond the local bootstrap filesystem store, background workers, and async orchestration
- richer web routing and page structure beyond the bootstrap compatibility-first workbench, search, subject-state, representations, manifest-export, bundle-export, stored-export, bundle-inspection, and local HTTP API slices, plus native runtime behavior
- final native CLI, TUI, GUI, and offline mode decisions
- release automation and packaging implementation
