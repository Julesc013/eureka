# Bootstrap Status

Current status: foundational scaffold plus thirty-five executable local deterministic thin slices, with draft contracts and concrete dependency boundary paths in place while broader product implementation remains intentionally deferred.

The executable lane should now be read as a Python reference backend and
architectural oracle rather than as a throwaway scaffold.

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
- first bounded representation-selection and handoff seam under `runtime/engine/handoff/` that lets one resolved target surface a preferred bounded representation plus explicit available, unsuitable, and unknown alternatives shaped by optional host and strategy input through the public boundary plus current surfaces without forcing downloads, installers, runtime launches, or final routing semantics
- first bounded acquisition and fetch seam under `runtime/engine/acquisition/` that lets one resolved target plus one explicit bounded representation retrieve tiny deterministic local payload bytes through the public boundary plus current surfaces, while preserving unavailable and blocked outcomes without forcing live downloads, installers, restore flows, or execution semantics
- first bounded decomposition and package-member seam under `runtime/engine/decomposition/` that lets one resolved target plus one explicit fetched bounded representation surface a compact ZIP member listing through the public boundary plus current surfaces, while returning explicit unsupported, unavailable, and blocked outcomes without forcing extraction, installers, import, or restore semantics
- first bounded member-readback and preview seam under `runtime/engine/members/` that lets one resolved target plus one explicit representation and member path surface compact text previews or bounded byte readback through the public boundary plus current surfaces, while returning explicit unsupported, unavailable, and blocked outcomes without forcing extraction to disk, installers, import, or restore semantics
- first repo-level archive-resolution eval corpus under `evals/archive_resolution/` that records hard software-resolution queries, explicit bad-result patterns, minimum granularity expectations, expected future result lanes, and allowed absence outcomes before broader investigation, ranking, decomposition, source-expansion, or optional AI claims are introduced
- first bounded Source Registry v0 seam under `contracts/source_registry/`, `control/inventory/sources/`, and `runtime/source_registry/` that records explicit governed source metadata, validates seed inventory records with stdlib-only runtime checks, and projects bounded source-registry listing plus detail views through the public boundary and current web, CLI, plus local HTTP API surfaces without implying live sync, crawling, health scoring, trust scoring, or implemented placeholder connectors
- first bounded Resolution Run Model v0 seam under `runtime/engine/resolution_runs/` that records synchronous exact-resolution, deterministic-search, and planned-search investigations as local JSON run records with checked source ids and families, current result summaries or bounded absence reports, and bounded public projection through current web, CLI, plus local HTTP API surfaces without implying worker queues, streaming phases, or async orchestration
- first bounded Query Planner v0 seam under `runtime/engine/query_planner/` that deterministically classifies a bounded set of archive-resolution eval query families into structured `ResolutionTask` records with compact platform, product, hardware, date, prefer/exclude, action-hint, and source-hint summaries, and projects those plans through current web, CLI, plus local HTTP API surfaces without implying LLM planning, vector search, fuzzy retrieval, ranking, or full investigation planning
- first bounded Local Index v0 seam under `runtime/engine/index/` that builds a caller-provided local SQLite index over the current bounded corpus, prefers FTS5 when available and falls back to deterministic non-FTS query behavior otherwise, preserves compact source ids, source families, representation and member text, evidence summaries, source-registry records, and bootstrap `resolved_resource_id` values where available, and projects build, status, plus query results through current web, CLI, plus local HTTP API surfaces without implying ranking, fuzzy retrieval, vector search, live source sync, incremental indexing, or final hosted search semantics
- first bounded Local Worker and Task Model v0 seam under `runtime/engine/workers/` that records synchronous local validation and indexing tasks as JSON task records under a caller-provided bootstrap `task_store_root`, wraps existing Source Registry v0, Local Index v0, and archive-resolution eval validation behavior through a transport-neutral public boundary reused by current web, CLI, plus local HTTP API surfaces, and does not imply background scheduling, retries, priorities, async orchestration, or distributed queue semantics
- first bounded Resolution Memory v0 seam under `runtime/engine/memory/` that derives explicit local reusable successful-resolution, successful-search, and absence-finding memory records from persisted completed resolution runs, stores them as JSON under a caller-provided bootstrap `memory_store_root`, and projects them through a transport-neutral public boundary reused by current web, CLI, plus local HTTP API surfaces without implying cloud memory, private user-history tracking, personalization, ranking, or an invalidation engine
- first bounded Archive Resolution Eval Runner v0 seam under `runtime/engine/evals/` that executes the governed hard-query packet through Query Planner v0, Local Index v0 or deterministic search fallback, and bounded absence reasoning, then reports stable JSON task and suite results with explicit satisfied, partial, not-satisfied, not-evaluable, and capability-gap checks without implying ranking, fuzzy retrieval, vector search, LLM planning, crawling, live sync, or production relevance evaluation
- first bounded Public Alpha Safe Mode v0 seam under `surfaces/web/server/` that separates trusted `local_dev` behavior from constrained `public_alpha` behavior, blocks caller-provided local path parameters in public-alpha mode, adds `/status` plus `/api/status`, and keeps safe read-only/search/eval routes available without implying production deployment, auth, accounts, HTTPS/TLS, or multi-user hosting
- first bounded Public Alpha Deployment Readiness Review seam through `control/inventory/public_alpha_routes.json`, `scripts/public_alpha_smoke.py`, and `docs/operations/` that inventories safe, blocked, local-dev-only, and review-required route groups, smoke-tests public-alpha allowed and blocked behavior, and records operator checklist guidance without deploying Eureka or adding auth, HTTPS/TLS, accounts, rate limiting, production process management, or hosting infrastructure
- first bounded Public Alpha Hosting Pack v0 seam under `docs/operations/public_alpha_hosting_pack/` plus `scripts/generate_public_alpha_hosting_pack.py` that packages route inventory status, smoke evidence templates, operator signoff, blockers, and a supervised rehearsal runbook without deploying Eureka or adding Docker, nginx, systemd, cloud infrastructure, auth, HTTPS/TLS, rate limiting, production logging, process management, live crawling, or background workers
- runtime component layout for engine, gateway, and connectors, including explicit engine interface boundaries
- surface layout for web and native
- component-local and root integration tests for the executable slices

## Accepted Doctrine

The repo now accepts doctrine that:

- Eureka is a temporal object resolver rather than flat archive search
- search is an investigation, not only a query
- the smallest actionable unit should outrank a bulky parent container when the
  evidence supports it
- deterministic identity outranks fuzzy similarity
- user strategy may shape recommendations but not objective truth
- AI is optional, evidence-bounded, and non-authoritative
- the backend should remain useful without LLMs
- eval-governed improvement is required for future search expansion

Accepted doctrine lives primarily under:

- `docs/vision/`
- `docs/architecture/`
- `docs/DECISIONS.md`

## Research Still Separate

The repo still keeps speculative or not-yet-accepted material under:

- `control/research/`

In particular, the temporal-object-resolution research note remains governed
research rather than a claim that the current repo already implements shared
evidence services, streaming run phases, hosted operation, or production
subsystem choices.

## Next Implementation Milestone

The next implementation milestone is:

> Rust Migration Skeleton and Parity Plan

Source Registry v0, Resolution Run Model v0, Query Planner v0, Local Index v0,
Local Worker and Task Model v0, Resolution Memory v0, and Archive Resolution
Eval Runner v0, Public Alpha Safe Mode v0, and Public Alpha Deployment
Readiness Review, and Public Alpha Hosting Pack v0 are now implemented as the first
inventory-backed source-control plane, synchronous durable investigation
envelope, deterministic raw-query compiler, durable local search substrate,
synchronous local execution substrate, explicit local reusable investigation
memory layer, executable eval guardrail, constrained public-demo posture, and
auditable public-alpha route/smoke checklist plus supervised rehearsal evidence packet.
The backend program should continue moving from bounded seam proof toward
operational backend infrastructure in this order:

1. Rust Migration Skeleton and Parity Plan
2. Native App Work Later

## Deferred Priorities

These are intentionally not the next milestone:

- Visual Studio app work
- Xcode app work
- full native app work
- public hosted alpha
- Rust production rewrite
- broad live federation
- installer or restore automation

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
- final action-routing, representation-selection, handoff, acquisition, decomposition, member-readback, strategy, execution, installer, workflow-policy, extraction, and personalization semantics beyond the current bounded recommendation seams
- mature search semantics, ranking, and broader retrieval architecture
- real web application structure, browser-side behavior, authentication, and deployment assumptions
- broader live external-source federation, live GitHub acquisition, ranking, retrieval, and broader provenance or trust semantics
- persistence beyond the local bootstrap filesystem store, background workers, and async orchestration
- richer web routing and page structure beyond the bootstrap compatibility-first workbench, search, subject-state, representations, manifest-export, bundle-export, stored-export, bundle-inspection, and local HTTP API slices, plus native runtime behavior
- final native CLI, TUI, GUI, and offline mode decisions
- serious Visual Studio/Xcode/native app shell work before backend infrastructure is stronger
- Rust production implementation work before parity planning and backend-roadmap prerequisites are met
- release automation and packaging implementation
