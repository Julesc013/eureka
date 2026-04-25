# Decisions

## ADR-001: Use One Eureka Monorepo

- Status: accepted
- Decision: Eureka lives in one product monorepo.
- Why: the founding contracts, runtime components, and user surfaces need explicit shared boundaries from the start.

## ADR-002: Keep AIDE Separate from Product Runtime

- Status: accepted
- Decision: AIDE remains a separate project or repo and is used here only as a pinned repo operating layer.
- Why: repo operations, policy, and compatibility metadata must not become product runtime glue.

## ADR-003: Split the Repo into Control, Contracts, Runtime, and Surfaces

- Status: accepted
- Decision: the top-level product structure is `control/`, `contracts/`, `runtime/`, and `surfaces/`.
- Why: governance material, governed meaning, execution behavior, and user-facing surfaces need distinct ownership and dependency boundaries.

## ADR-004: Web Uses the Gateway Public API by Default

- Status: accepted
- Decision: the normal web path goes through `contracts/gateway/public_api` and gateway-facing contracts rather than engine internals.
- Why: web should consume product contracts, not runtime implementation detail.

## ADR-005: Schemas and Protocols Are Governed Assets

- Status: accepted
- Decision: schemas, protocols, public APIs, and shared UI contracts are treated as first-class governed assets.
- Why: Eureka depends on stable, inspectable meaning rather than implicit model drift.

## ADR-006: Version 1 Is Software-First

- Status: accepted
- Decision: v1 focuses on software resolution, preservation, compatibility, and reconstruction.
- Why: a narrower domain is needed before broader artifact classes can be governed well.

## ADR-007: Use Python Standard Library Only for the Bootstrap Execution Lane

- Status: accepted
- Decision: the first executable thin slice uses Python 3 standard library only.
- Why: the bootstrap lane should stay easy to inspect, dependency-light, and replaceable later without implying a final stack commitment.

## ADR-008: Keep the First Executable Slice Local, Deterministic, and Fixture-Backed

- Status: accepted
- Decision: the first executable slice resolves governed synthetic software fixtures through an engine service and an in-memory gateway bounded-job service.
- Why: this proves the core boundary model without prematurely committing to connectors, ranking, persistence, or async orchestration.

## ADR-009: Put Synthetic Fixture Access Behind a Connector-Shaped Boundary

- Status: accepted
- Decision: governed synthetic fixture access now lives under `runtime/connectors/synthetic_software/`, while the engine consumes only normalized records through `runtime/engine/interfaces/ingest/**`, `runtime/engine/interfaces/extract/**`, and `runtime/engine/interfaces/normalize/**`.
- Why: this proves the intended connector-to-engine boundary early without implying real external acquisition, connector-owned object truth, or finalized ingestion architecture.

## ADR-010: Keep the Gateway Public Boundary Separate from the In-Memory Job Service

- Status: accepted
- Decision: the bootstrap gateway now exposes a transport-neutral public submit and read boundary that translates in-memory job service state into public envelopes, while submit returns an accepted envelope and read returns the current job state.
- Why: this proves the declared public API boundary more honestly without introducing a real HTTP server, async workers, or persistence.

## ADR-011: Exercise Shared Surface Contracts Through a Workbench Session Mapping

- Status: accepted
- Decision: bootstrap now maps public gateway job envelopes into the shared `WorkbenchSession` view model without implementing browser-owned or native-owned UI behavior.
- Why: this proves the shared surface-contract boundary while keeping runtime behavior replaceable and keeping surface implementation decisions deferred.

## ADR-012: Keep the First Web Workbench Slice Server-Rendered and Public-Boundary-First

- Status: accepted
- Decision: the first `surfaces/web` slice renders compatibility-first HTML from the shared `WorkbenchSession` model and reaches runtime behavior only through the gateway public boundary.
- Why: this proves that web can consume governed public and shared-surface contracts without binding to engine internals, while keeping framework, JavaScript, routing, and deployment choices deferred.

## ADR-013: Keep the First Search Slice Deterministic, Small, and Absence-First

- Status: accepted
- Decision: the first search slice uses deterministic substring matching over a tiny governed synthetic corpus in stable catalog order, exposes results through a transport-neutral public search boundary, and emits a structured absence report when there are no matches.
- Why: this proves the next user-facing seam without prematurely committing to ranking, fuzzy matching, vector retrieval, or broader search architecture.

## ADR-014: Keep the First Action Slice Bounded to Manifest Export Through the Public Boundary

- Status: accepted
- Decision: the first action-oriented slice exposes exactly one bounded action, `export_resolution_manifest`, through a transport-neutral public gateway boundary and renders that action through a shared action-panel model in the exact-resolution web workbench.
- Why: this proves that resolved results can terminate in a useful local action without prematurely committing to installers, downloads, snapshot restore, persistence, or broader workflow orchestration.

## ADR-015: Keep the First Portable Offline Export Slice Bounded to a Deterministic Resolution Bundle

- Status: accepted
- Decision: the first portable offline export slice exposes exactly one additional bounded action, `export_resolution_bundle`, through the transport-neutral public gateway boundary and renders it alongside manifest export in the exact-resolution workbench.
- Why: this proves that resolved results can terminate in a small self-contained export artifact without prematurely committing to restore or import behavior, durable snapshot semantics, installers, or broader preservation workflows.

## ADR-016: Keep the First Bundle Readback Slice Local, Offline, and Inspection-Only

- Status: accepted
- Decision: the first bundle readback slice inspects previously exported deterministic bundles through a separate public inspection boundary and a compatibility-first web inspection page, using local bundle bytes or a local bundle path only.
- Why: this proves self-contained offline inspection without prematurely committing to upload, import, restore, runtime execution, or final snapshot verification semantics.

## ADR-017: Keep the First Local Export Store Slice Content-Addressed, Local-Only, and Surface-Visible

- Status: accepted
- Decision: the first local export store slice assigns stable `sha256:<hex>` artifact identities to deterministic manifest and bundle exports, stores them in a small local filesystem layout under a caller-provided store root, and exposes listing plus readback through a separate public stored-exports boundary.
- Why: this proves durable local artifact identity and reusable local retrieval without prematurely committing to databases, multi-user cache design, restore or import behavior, or broader preservation semantics.

## ADR-018: Use a Bootstrap Deterministic Resolved-Resource Identity Seam

- Status: accepted
- Decision: the current thin slice derives a deterministic bootstrap `resolved_resource_id` from already-normalized or already-resolved data and propagates it through exact resolution, deterministic search, public actions, portable exports, bundle inspection, local stored-export metadata, and compatibility-first web surfaces.
- Why: this hardens identity propagation beyond raw `target_ref` without prematurely committing to a final global identity registry, cross-source merge behavior, or broader object-model redesign.

## ADR-019: Prove the First Non-Web Surface Through a Public-Boundary-First CLI Slice

- Status: accepted
- Decision: the first `surfaces/native` implementation is a local stdlib-only CLI under `surfaces/native/cli/` that consumes the gateway public boundary and shared surface-neutral mappings instead of importing engine internals directly.
- Why: this proves real reuse across surface families without prematurely committing to a final native shell stack, TUI architecture, GUI runtime, packaging story, or offline-mode embedding strategy.

## ADR-020: Add a Narrow Repo-Local Architectural Boundary Checker

- Status: accepted
- Decision: Eureka now ships a stdlib-only repo-local checker at `scripts/check_architecture_boundaries.py` that inspects Python imports and enforces the currently proven layering: surfaces stay on the public side, `runtime/gateway/public_api` does not import surfaces, and engine/connectors do not import surfaces.
- Why: the current risk is silent layering erosion, and a small explicit checker hardens the proven architecture without pretending to be a universal policy engine or redesigning the repo policy model.

## ADR-021: Prove the First Machine-Readable HTTP API Slice Through the Existing Public Boundary

- Status: accepted
- Decision: Eureka now exposes a first local stdlib machine-readable HTTP API slice under `surfaces/web/server/` that serves JSON and ZIP responses for exact resolution, deterministic search, manifest export, bundle export, bundle inspection, and local stored-export flows by reusing `runtime/gateway/public_api/**` rather than duplicating runtime logic or importing engine internals directly.
- Why: this proves protocol-level reuse over the same transport-neutral public-boundary logic already consumed by the compatibility-first HTML workbench and the native CLI without prematurely committing to a production HTTP stack, auth model, HTTPS/TLS, deployment topology, or final durable route semantics.

## ADR-022: Prove the First Real External-Source Connector Through a Bounded GitHub Releases Slice

- Status: accepted
- Decision: Eureka now includes a bounded `runtime/connectors/github_releases/` connector family that loads small recorded GitHub Releases fixtures, passes them through the existing ingest, extract, and normalize seams, and exposes the resulting normalized records through the current engine, gateway public boundary, and web, CLI, plus HTTP API surfaces with minimal source-family visibility.
- Why: this proves the current architecture against one real source family without introducing live crawling, auth, download or installer behavior, new persistence architecture, or premature provenance and trust commitments.

## ADR-023: Carry the First Bounded Evidence Seam Without Forcing Silent Truth

- Status: accepted
- Decision: Eureka now carries compact source-backed evidence summaries from normalize through exact resolution, deterministic search, manifest export, portable bundle export and inspection, local stored-export metadata, and current web, CLI, plus HTTP API surfaces.
- Why: this proves the architecture can preserve bounded provenance and evidence visibility without prematurely introducing a provenance graph, trust scoring, cross-source merge engine, or a final claim ontology.

## ADR-024: Add a Bounded Side-by-Side Comparison Seam Without Merging Results

- Status: accepted
- Decision: Eureka now compares exactly two resolved targets side by side through a bounded engine comparison service and a transport-neutral public comparison boundary, preserving evidence summaries per side and surfacing explicit agreements plus disagreements through current web, CLI, and HTTP API surfaces.
- Why: this proves the architecture can keep multiple source-backed claims visible together without silently collapsing them into one answer or prematurely introducing merge logic, trust ranking, or global truth selection.

## ADR-025: Add a Bounded Subject-State Timeline Seam Without Finalizing Identity

- Status: accepted
- Decision: Eureka now groups multiple bounded states under one bootstrap `subject_key` through a deterministic engine state-listing service and a transport-neutral public subject/state boundary, preserving compact source and evidence summaries per state and surfacing the ordered listing through current web, CLI, and HTTP API surfaces.
- Why: this proves the architecture can expose temporal or release-oriented state listing without silently collapsing multiple states into one answer or prematurely introducing a final global object identity model, merge logic, trust scoring, or a broader temporal graph.

## ADR-026: Add a Bounded Miss-Explanation Seam Without Claiming Final Diagnostics

- Status: accepted
- Decision: Eureka now explains exact-resolution misses and deterministic search no-result cases through a bounded engine absence service and a transport-neutral public absence boundary, preserving checked source-family summaries plus compact near matches where the current corpus supports them and surfacing that explanation through current web, CLI, and HTTP API surfaces.
- Why: this proves the architecture can explain a miss in a source-aware and evidence-aware way without prematurely introducing ranking, fuzzy retrieval, trust scoring, merge logic, or a final diagnostic engine.

## ADR-027: Add a Bounded Representation and Access-Path Seam Without Choosing Final Actions

- Status: accepted
- Decision: Eureka now carries bounded representation and access-path summaries from normalize through exact resolution, a transport-neutral public representations boundary, and current web, CLI, plus HTTP API surfaces, while preserving multiple known source-backed paths for one resolved target side by side.
- Why: this proves the architecture can expose concrete known representations without silently turning them into final download, install, import, restore, or representation-selection semantics.

## ADR-028: Add a Bounded Compatibility Seam Without Claiming a Final Oracle

- Status: accepted
- Decision: Eureka now evaluates one resolved target against one small bootstrap host profile preset through a bounded engine compatibility service and a transport-neutral public compatibility boundary, surfacing compact reasons plus honest `unknown` outcomes through current web, CLI, and HTTP API surfaces.
- Why: this proves the architecture can expose practical compatibility guidance without prematurely introducing installer logic, runtime routing, trust scoring, or a final compatibility oracle.

## ADR-029: Add a Bounded Action-Routing Seam Without Introducing Execution

- Status: accepted
- Decision: Eureka now builds one bounded action plan for one resolved target by combining known representations and access paths, an optional bootstrap host-profile compatibility verdict, and bounded local export/store context into explicit recommended, available, and unavailable actions through a transport-neutral public boundary and current web, CLI, plus HTTP API surfaces.
- Why: this proves the architecture can expose first-class next-step guidance without silently hiding unavailable actions or prematurely introducing execution, installer, orchestration, or final policy-engine semantics.

## ADR-030: Add a Bounded User-Strategy Seam Without Mutating Underlying Truth

- Status: accepted
- Decision: Eureka now accepts one optional bootstrap strategy profile when building one bounded action plan for one resolved target, and uses that profile only to vary recommendation and presentation emphasis, rationale text, and next-step ordering through the transport-neutral public boundary plus current web, CLI, and HTTP API surfaces.
- Why: this proves the architecture can make user-goal emphasis explicit without silently baking one fixed recommendation posture into the product, while also avoiding personalization, ranking, persistence, or any mutation of the underlying resolved identity, evidence, compatibility, or representation data.

## ADR-031: Add a Bounded Representation-Selection Seam Without Performing the Handoff

- Status: accepted
- Decision: Eureka now selects one bounded preferred representation plus explicit available, unsuitable, and unknown alternatives for one resolved target by combining existing representation summaries with optional bootstrap host-profile compatibility and optional bootstrap strategy emphasis, then surfaces that recommendation through a transport-neutral public boundary plus current web, CLI, and HTTP API surfaces.
- Why: this proves the architecture can make handoff preference explicit without silently collapsing multiple representations into one hidden choice, while also avoiding downloads, installers, launches, runtime routing, orchestration, or a final policy engine.

## ADR-032: Add a Bounded Acquisition Seam Without Becoming a Downloader

- Status: accepted
- Decision: Eureka now retrieves tiny deterministic local payload bytes for one explicitly chosen bounded representation on one resolved target through a transport-neutral public acquisition boundary, and surfaces fetched, unavailable, and blocked outcomes through current web, CLI, and HTTP API surfaces.
- Why: this proves the architecture can move from representation discovery and bounded handoff recommendation into bounded payload retrieval without introducing live downloads, installers, restore/import flows, orchestration, or final acquisition semantics.

## ADR-033: Add a Bounded Decomposition Seam Without Becoming an Extractor Framework

- Status: accepted
- Decision: Eureka now inspects one explicitly chosen fetched bounded representation into a compact member listing through a transport-neutral public decomposition boundary, supporting ZIP only in this bootstrap slice and surfacing decomposed, unsupported, unavailable, and blocked outcomes through current web, CLI, and HTTP API surfaces.
- Why: this proves the architecture can move from bounded payload retrieval into bounded package-member inspection without introducing installers, import or restore behavior, extraction to disk, broad format coverage, or a final extractor or package-management model.

## ADR-034: Add a Bounded Member-Readback Seam Without Becoming a General Extractor

- Status: accepted
- Decision: Eureka now reads one explicitly chosen member from one explicitly chosen fetched representation through a transport-neutral public member-access boundary, supporting ZIP member readback only in this bootstrap slice and surfacing read, previewed, unsupported, unavailable, and blocked outcomes through current web, CLI, and HTTP API surfaces.
- Why: this proves the architecture can move from bounded package-member listing into bounded inside-the-package member access without introducing extraction-to-disk by default, installers, import or restore behavior, broad format coverage, or a final extraction or package-management model.

## ADR-035: Add an Archive-Resolution Eval Corpus Before Search Semantics Expansion

- Status: accepted
- Decision: Eureka now maintains a small repo-level archive-resolution benchmark corpus under `evals/archive_resolution/` that records hard software-resolution queries, explicit bad-result patterns, acceptable result shapes, minimum granularity expectations, expected future result lanes, and allowed absence outcomes.
- Why: future investigation, ranking, decomposition, source-expansion, and optional AI work need a governed benchmark before broader search or resolver claims are made.

## ADR-036: Treat Eureka as a Temporal Object Resolver Rather Than Flat Archive Search

- Status: accepted
- Decision: Eureka now treats its accepted product direction as a temporal object resolver that should find, verify, compare, explain, and route users toward the smallest useful actionable unit, rather than as a flat archive-search surface.
- Why: the bounded seams already proved by the repo point toward investigation, evidence, compatibility, actionability, and decomposition rather than toward a simple keyword-search product.

## ADR-037: Keep Python as the Reference Backend and Plan Rust as the Production Lane

- Status: accepted
- Decision: Eureka now treats the current Python stdlib implementation as the reference backend, oracle, tooling lane, and migration harness, while documenting Rust as the intended production backend lane for later work.
- Why: Python has already proven the architecture and behavior at bootstrap scale, while a later Rust backend remains better aligned with durable production runtime goals.

## ADR-038: Prioritize Backend Infrastructure Before Native Apps

- Status: accepted
- Decision: Eureka now prioritizes source registry, resolution runs, query planning, local indexing, worker models, and resolution memory ahead of native app shells or serious Visual Studio/Xcode work.
- Why: the repo has already completed most of the bounded seam-proof phase, and the next constraint is coherent backend operation rather than additional host shells.

## ADR-039: Gate Public Alpha on Source Registry, Resolution Runs, Query Planner, Local Index, and Safe Config

- Status: accepted
- Decision: Eureka now requires Source Registry v0, Resolution Run Model v0, Query Planner v0, Local Index v0, and public-alpha-safe configuration before public hosted alpha work can be treated as ready to start.
- Why: hosting the current local bootstrap behavior directly would overstate product maturity and would blur the boundary between local proof paths and safer public operation.

## ADR-040: Keep AI Optional, Evidence-Bounded, and Non-Authoritative

- Status: accepted
- Decision: Eureka now treats AI as optional helper capability only, bounded by evidence, typed outputs, and replaceable logic, and it forbids model output from becoming canonical truth or hidden trust authority.
- Why: the product must remain useful without LLMs and must keep source-backed truth, identity, and trust decisions inspectable.

## ADR-041: Add Source Registry v0 as the First Inventory-Backed Source Control Plane

- Status: accepted
- Decision: Eureka now maintains Source Registry v0 through draft governed source-registry schemas, explicit governed seed records under `control/inventory/sources/`, a stdlib-only runtime loader and filter layer under `runtime/source_registry/`, and a bounded public source-registry boundary reused by current web, CLI, and local HTTP API surfaces.
- Why: the repo already contains more than one source family, and future source growth needs an explicit, inspectable inventory and policy plane before broader connector work, resolution runs, local indexing, or hosted-alpha preparation continue.

## ADR-042: Add Resolution Run Model v0 as the First Durable Investigation Envelope

- Status: accepted
- Decision: Eureka now records synchronous exact-resolution and deterministic-search investigations as local JSON resolution-run records under `runtime/engine/resolution_runs/`, exposes them through a bounded public boundary reused by current web, CLI, and local HTTP API surfaces, and records checked source ids plus source families through Source Registry v0 where current implemented connectors are actually consulted.
- Why: the repo has now moved beyond isolated request/response seams, and later query-planner, indexing, worker, and resolution-memory work needs an explicit durable investigation envelope before broader backend infrastructure arrives.

## ADR-043: Add Query Planner v0 as the First Deterministic Raw-Query Compiler

- Status: accepted
- Decision: Eureka now compiles a bounded set of archive-resolution raw queries into structured `ResolutionTask` records through a deterministic stdlib-only Query Planner v0 under `runtime/engine/query_planner/`, projects those plans through a dedicated gateway public boundary reused by current web, CLI, and local HTTP API surfaces, and allows planned-search resolution runs to persist an optional plan summary without changing the underlying deterministic-search retrieval semantics.
- Why: Source Registry v0 and Resolution Run Model v0 established explicit source inventory plus a durable investigation envelope, and the next operational backend requirement is planner-owned structured intent without prematurely introducing LLM planning, vector search, fuzzy retrieval, ranking, worker queues, or full investigation planning.

## ADR-044: Add Local Index v0 as the First Durable Local Search Substrate

- Status: accepted
- Decision: Eureka now builds, inspects, and queries a caller-provided local SQLite index under `runtime/engine/index/`, preferring FTS5 when available and falling back to deterministic non-FTS query behavior otherwise, while indexing bounded records derived from the current synthetic and recorded GitHub Releases corpus plus Source Registry v0 records and projecting that capability through dedicated gateway public boundaries reused by current web, CLI, and local HTTP API surfaces.
- Why: Source Registry v0, Resolution Run Model v0, and Query Planner v0 established explicit source inventory, durable synchronous investigation records, and deterministic structured intent, and the next operational backend requirement is a durable local search substrate before worker models, resolution memory, public alpha work, or Rust parity planning continue.

## ADR-045: Add Local Worker and Task Model v0 as the First Synchronous Execution Substrate

- Status: accepted
- Decision: Eureka now creates, executes, persists, lists, and reads synchronous local task records under `runtime/engine/workers/`, using a caller-provided bootstrap `task_store_root`, wrapping existing Source Registry v0 validation, Local Index v0 build/query behavior, and archive-resolution eval validation through a dedicated gateway public boundary reused by current web, CLI, and local HTTP API surfaces.
- Why: Source Registry v0, Resolution Run Model v0, Query Planner v0, and Local Index v0 now exist as bounded backend infrastructure, and the next operational requirement is a deterministic local execution substrate before resolution memory, broader worker orchestration, or hosted-alpha safety work continue.

## ADR-046: Add Resolution Memory v0 as the First Explicit Local Reuse Layer

- Status: accepted
- Decision: Eureka now creates explicit local resolution-memory records from persisted completed resolution runs under `runtime/engine/memory/`, stores them as JSON under a caller-provided bootstrap `memory_store_root`, and exposes create, read, plus list behavior through a dedicated gateway public boundary reused by current web, CLI, and local HTTP API surfaces.
- Why: Source Registry v0, Resolution Run Model v0, Query Planner v0, Local Index v0, and Local Worker and Task Model v0 now exist as bounded backend infrastructure, and the next operational requirement is durable local reuse of successful and unsuccessful investigation outcomes without prematurely introducing cloud/shared memory, personalization, ranking, or an invalidation engine.

## ADR-047: Add Archive Resolution Eval Runner v0 as the First Executable Benchmark Harness

- Status: accepted
- Decision: Eureka now executes the governed archive-resolution hard-query packet through a bounded stdlib-only runner under `runtime/engine/evals/`, using Query Planner v0, Local Index v0 or deterministic search fallback, and bounded absence reasoning, then projecting stable JSON suite and task results through script, public gateway, CLI, local HTTP API, and compatibility-first web surfaces.
- Why: the eval packet already existed as schema and fixtures, but backend progress now needs an honest executable regression guardrail that can show planner satisfaction, absence partials, not-yet-evaluable expectations, and capability gaps without pretending the current corpus solves future-facing hard queries or introducing ranking, fuzzy retrieval, vector search, LLM planning, crawling, live sync, or production relevance evaluation.

## ADR-048: Add Public Alpha Safe Mode v0 as a Constrained Web/API Hosting Posture

- Status: accepted
- Decision: Eureka now gives the stdlib web/API backend explicit `local_dev` and `public_alpha` modes under `surfaces/web/server/`, with a route policy that blocks caller-provided local filesystem path controls in public-alpha mode, status/capability reporting at `/status` and `/api/status`, and script flags for starting or checking public-alpha behavior.
- Why: the local demo server intentionally supports trusted local path workflows, but a public demo needs an explicit constrained posture before any hosted-alpha experiment; this separates mode behavior without adding auth, HTTPS/TLS, accounts, production deployment, background workers, or new retrieval semantics.

## ADR-049: Add Public Alpha Deployment Readiness Review as an Auditable Gate

- Status: accepted
- Decision: Eureka now records a machine-readable public-alpha route inventory under `control/inventory/public_alpha_routes.json`, validates that inventory in tests, adds `scripts/public_alpha_smoke.py` for repeatable safe/blocked route smoke checks, and documents the readiness verdict plus operator checklist under `docs/operations/`.
- Why: `public_alpha` mode is useful only if its route posture can be audited and rechecked; the review makes safe routes, local-dev-only routes, blocked local-path variants, review-required routes, and unresolved hosting blockers explicit without deploying Eureka or adding auth, HTTPS/TLS, accounts, rate limiting, process management, or production infrastructure.

## ADR-050: Add Public Alpha Hosting Pack v0 as a Supervised Rehearsal Evidence Packet

- Status: accepted
- Decision: Eureka now groups Public Alpha Hosting Pack v0 under `docs/operations/public_alpha_hosting_pack/`, with a rehearsal runbook, route-safety summary, smoke evidence template, operator signoff template, blocker list, and manifest, plus `scripts/generate_public_alpha_hosting_pack.py` to keep the route summary aligned with the route inventory.
- Why: the readiness review established route posture evidence, but a human operator needs a bounded packet for supervised rehearsal decisions; the pack packages existing evidence and explicit blockers without deploying Eureka or adding Docker, nginx, systemd, cloud infrastructure, auth, HTTPS/TLS, accounts, rate limiting, production logging, production process management, live crawling, background workers, Rust code, or native app work.

## ADR-051: Add Rust Migration Skeleton and Parity Plan v0 Without Porting Behavior

- Status: accepted
- Decision: Eureka now contains a minimal Rust workspace under `crates/` plus `docs/architecture/RUST_BACKEND_LANE.md` and `tests/parity/` planning docs; Python remains the executable specification, reference backend, and oracle, and Rust cannot replace a seam until parity tests compare Python oracle outputs against Rust candidate outputs.
- Why: Rust is the intended later production backend lane, but the project needs a governed migration path before any rewrite; the skeleton reserves the first crate boundaries and parity discipline without porting runtime behavior, replacing Python, adding production services, adding FFI, or starting native app projects.
