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

## ADR-052: Add Rust Parity Fixture Pack v0 as Python-Oracle Golden Evidence

- Status: accepted
- Decision: Eureka now commits the first Python-oracle golden fixture pack under `tests/parity/golden/python_oracle/v0/`, generated by `scripts/generate_python_oracle_golden.py`, covering source registry, query planner, resolution runs, local index, resolution memory, and archive-resolution eval outputs with explicit normalization of unstable fields.
- Why: future Rust seams need concrete Python reference outputs before any replacement can be judged safe; the fixture pack creates reviewable parity evidence without porting runtime behavior to Rust, changing Python behavior, adding a Rust parity runner, adding native app work, or implying a production Rust backend.

## ADR-053: Add Rust Source Registry Parity Candidate v0 as the First Rust Behavior Seam

- Status: accepted
- Decision: Eureka now implements an isolated Rust source-registry candidate under `crates/eureka-core/` that loads governed `.source.json` inventory records, validates bounded required fields, detects duplicate `source_id` values, and compares generated source-registry public envelopes against the committed Python-oracle golden outputs.
- Why: source-registry loading is the smallest useful first Rust parity seam and can be checked without replacing Python behavior; the candidate proves one Rust behavior path while keeping Python authoritative and avoiding Rust gateway, CLI, FFI, resolver, query-planner, index, memory, worker, app, network, or production-service scope.

## ADR-054: Add Search Usefulness Audit v0 as an Honest Backlog Generator

- Status: accepted
- Decision: Eureka now maintains Search Usefulness Audit v0 under `evals/search_usefulness/`, with a 64-query archive-resolution-style pack, JSON-subset YAML schemas, a stdlib runner, a manual baseline-observation helper, and reports that aggregate current Eureka statuses, pending external baselines, failure modes, and future-work labels.
- Why: archive-resolution progress needs a broad usefulness audit that can show where Eureka's structure helps and where corpus, planner, index, decomposition, representation, compatibility, or UX gaps dominate; external systems must remain pending manual observations unless a human records them, so the repo does not fabricate Google or Internet Archive results or introduce scraping.

## ADR-055: Add Test/Eval Operating Layer and Comprehensive Repo Audit v0

- Status: accepted
- Decision: Eureka now records a repo-native test/eval operating layer under `control/inventory/tests/`, structured audit finding schemas under `control/audits/schemas/`, a dated comprehensive audit pack under `control/audits/2026-04-25-comprehensive-test-eval-audit/`, and AIDE task/report scaffolding under `.aide/tasks/` and `.aide/reports/`.
- Why: future backend, eval, public-alpha, and Rust parity work needs modular verification lanes, structured findings, hard-test proposals, and evidence-backed backlog recommendations before implementation broadens; this is governance metadata only and does not add product runtime behavior, source connectors, deployment infrastructure, external scraping, or production-readiness claims.

## ADR-056: Add Hard Test Pack v0 as a High-Risk Regression Guard Lane

- Status: accepted
- Decision: Eureka now maintains Hard Test Pack v0 under `tests/hardening/`, with stdlib-only guards for hard eval truth, external baseline honesty, public-alpha local path safety, route inventory drift, README command drift, documentation link drift, Python-oracle golden drift, Rust parity structure, source placeholder honesty, resolution-memory path/privacy scope, and AIDE/test registry consistency.
- Why: the comprehensive audit identified risks that should fail loudly before future work broadens the repo; hardening those risks as tests improves regression discipline without adding product runtime behavior, source connectors, Rust behavior ports, deployment infrastructure, external scraping, native apps, or production-readiness claims.

## ADR-057: Select Old-Platform Software and Member-Level Discovery as the Next Usefulness Wedges

- Status: accepted
- Decision: Eureka now records Search Usefulness Backlog Triage v0 under `control/backlog/search_usefulness_triage/`, selecting old-platform-compatible software search as the primary usefulness wedge, member-level discovery inside bundles as the secondary wedge, and the initial Source Coverage and Capability Model v0 milestone before later source, planner, member, and compatibility slices.
- Why: Search Usefulness Audit v0 shows source coverage, query interpretation, planner, compatibility evidence, representation, decomposition, and member-access gaps dominate current usefulness failures; the selected wedges produce the clearest user value while preserving hard eval honesty, external baseline pending/manual status, Python-oracle authority, and the deferral of live crawling, scraping, ranking/fuzzy/vector/LLM retrieval, Rust behavior ports, native apps, and production hosting.

## ADR-058: Add Source Coverage and Capability Model v0 Without Adding Connectors

- Status: accepted
- Decision: Eureka now extends Source Registry v0 with explicit source capability booleans, source posture, connector-mode metadata, a six-level coverage-depth ladder, current limitations, and next coverage steps across governed source records, runtime loading/filtering, gateway projection, CLI, local HTTP API, and compatibility-first web source pages.
- Why: Search Usefulness Backlog Triage v0 selected old-platform-compatible software search and member-level discovery, but those wedges need an honest source-capability plane before recorded fixtures or planner changes can improve results. This milestone makes source coverage depth visible while keeping Internet Archive, Wayback/Memento, Software Heritage, and local-files records as placeholders or local/private future sources. It does not add source connectors, live source probing, crawling, scraping, acquisition behavior, ranking, fuzzy/vector retrieval, LLM planning, Rust runtime behavior, native apps, or production deployment.

## ADR-059: Add Real Source Coverage Pack v0 as Recorded Fixtures Only

- Status: accepted
- Decision: Eureka now adds separate active fixture-backed records for `internet-archive-recorded-fixtures` and `local-bundle-fixtures`, with tiny committed Internet Archive-like metadata/file-list fixtures plus committed ZIP bundle fixtures flowing through existing ingest, extract, normalize, index, eval, and public projection paths.
- Why: Old-platform-compatible software search and member-level discovery need more realistic source-shaped evidence before planner and member-target work can improve usefulness. This milestone keeps `internet-archive-placeholder` and `local-files-placeholder` as unimplemented planning anchors, adds no live Internet Archive API calls, scraping, crawling, broad source federation, arbitrary local filesystem ingestion, ranking, fuzzy/vector retrieval, LLM planning, Rust runtime behavior, native apps, or production deployment, and preserves hard eval honesty.

## ADR-060: Add Old-Platform Software Planner Pack v0 as Deterministic Interpretation Only

- Status: accepted
- Decision: Eureka now extends Query Planner v0 with deterministic old-platform software planning rules for OS/platform aliases, platform-as-constraint handling, app-vs-OS-media suppression hints, latest-compatible release intent, driver/hardware/OS intent, vague identity uncertainty, documentation intent, and member-discovery hints.
- Why: Search Usefulness Audit v0 still shows old-platform software and member-discovery usefulness blocked by interpretation, member, representation, compatibility, and source gaps. This milestone reduces planner/query-interpretation gaps while preserving source/capability gap honesty. It does not add ranking, fuzzy/vector retrieval, LLM planning, live source calls, crawling, scraping, new connectors, Rust runtime behavior, native apps, or production deployment.

## ADR-061: Add Member-Level Synthetic Records v0 for Bounded Fixture Members

- Status: accepted
- Decision: Eureka now derives deterministic `member:sha256:<digest>` synthetic member records from committed local bundle fixtures, preserving parent target refs, parent representation ids, source provenance, member paths, inferred member kind, content metadata, evidence summaries, and action hints. These records flow through the normalized catalog, exact resolution, deterministic search, local index, gateway public envelopes, CLI, web, and local HTTP API projections.
- Why: The old-platform software and member-level discovery wedges need Eureka to identify the useful inner file, not only the parent ZIP or support bundle. This milestone adds that first bounded seam without adding new source connectors, live source calls, crawling, scraping, broad archive extraction, arbitrary local filesystem ingestion, ranking, fuzzy/vector retrieval, LLM planning, Rust runtime behavior, native apps, or production deployment.

## ADR-062: Add Result Lanes and User-Cost Hints Without Production Ranking

- Status: accepted
- Decision: Eureka now assigns deterministic result lanes and user-cost explanations to current result records under `runtime/engine/ranking/`, then projects those annotations through exact resolution, deterministic search, local index, eval summaries, gateway public envelopes, CLI, web, and local HTTP API output.
- Why: The old-platform software and member-level discovery wedges need the system to explain why a source-backed inner member can be more actionable than a parent bundle while keeping parent context visible. This milestone adds bounded explanation and small-result ordering only; it does not add fuzzy/vector retrieval, LLM scoring, live source behavior, source connectors, broad source federation, Rust runtime behavior, native apps, production deployment, or final production ranking.

## ADR-063: Add Compatibility Evidence Records Without Creating an Oracle

- Status: accepted
- Decision: Eureka now derives compact compatibility evidence records from committed fixture metadata, member paths, README text, and compatibility notes under `runtime/engine/compatibility/`, then projects those records through exact resolution, deterministic search, local index, compatibility evaluation, eval summaries, gateway public envelopes, CLI, web, and local HTTP API output.
- Why: The old-platform software wedge needs source-backed compatibility signals for platforms such as Windows 7, Windows XP, and Windows 2000 while preserving unknown outcomes. This milestone adds evidence records only; it does not execute software, verify installers, scrape external systems, call live sources, add fuzzy/vector retrieval or LLM behavior, introduce source connectors, port Rust behavior, start native app work, add deployment infrastructure, or claim a universal compatibility oracle.

## ADR-064: Record Search Usefulness Audit Delta v0 Before Expanding Sources Again

- Status: accepted
- Decision: Eureka now records Search Usefulness Audit Delta v0 under `control/audits/search-usefulness-delta-v0/`, comparing current local Search Usefulness Audit output against a historical reported aggregate baseline after source coverage, old-platform planning, member records, result lanes/user-cost, and compatibility evidence landed.
- Why: The recent usefulness sequence produced a modest measured movement: partial results increased from 1 to 5, `source_gap` decreased from 43 to 41, and `capability_gap` decreased from 13 to 11. The delta pack keeps baseline limitations explicit, leaves external baselines pending/manual, and recommends Old-Platform Source Coverage Expansion v0 because source coverage remains dominant. It does not change retrieval behavior, add source connectors, call live sources, scrape external systems, add fuzzy/vector retrieval or LLM behavior, weaken hard evals, port Rust behavior, start native app work, or add deployment infrastructure.

## ADR-065: Expand Old-Platform Source Coverage With Committed Fixtures Only

- Status: accepted
- Decision: Eureka now expands the existing `internet-archive-recorded-fixtures` and `local-bundle-fixtures` source families with tiny committed old-platform utility, browser-note, registry-repair, and driver/support-media fixture records.
- Why: Search Usefulness Audit Delta v0 showed source coverage remained the dominant usefulness blocker. The expansion moves current local audit counts to 5 covered, 20 partial, 28 source gaps, 9 capability gaps, and 2 unknowns while keeping placeholder sources unimplemented and external baselines pending/manual. It does not add live Internet Archive calls, scraping, crawling, arbitrary local filesystem ingestion, real software binaries, fuzzy/vector retrieval, LLM behavior, Rust behavior ports, native apps, deployment infrastructure, hard-eval weakening, or production-readiness claims.

## ADR-066: Record Search Usefulness Audit Delta v1 Before Hard Eval Satisfaction Work

- Status: accepted
- Decision: Eureka now records Search Usefulness Audit Delta v1 under `control/audits/search-usefulness-delta-v1/`, comparing current local Search Usefulness Audit output against the committed v0 delta aggregate baseline and recording archive eval movement after Old-Platform Source Coverage Expansion v0.
- Why: The source expansion produced meaningful measured movement: partial results increased from 5 to 20, `source_gap` decreased from 41 to 28, `capability_gap` decreased from 11 to 9, and archive evals moved to `capability_gap=1` plus `not_satisfied=5`. The next selected milestone is Hard Eval Satisfaction Pack v0 because source-backed candidates now exist for five hard tasks but exact expected-result checks still fail. This is reporting only; it does not change retrieval behavior, weaken hard evals, fabricate external baselines, add live sources, scrape external systems, add fuzzy/vector retrieval or LLM behavior, port Rust behavior, start native app work, add deployment infrastructure, or make production-readiness claims.

## ADR-067: Map Source-Backed Hard Eval Evidence Before Result Refinement

- Status: accepted
- Decision: Eureka now records Hard Eval Satisfaction Pack v0 under `control/audits/hard-eval-satisfaction-v0/` and updates Archive Resolution Eval Runner v0 so hard expected-result checks can inspect source-backed member paths, representation locators, compatibility evidence, result lanes, source ids, and source families already present in bounded local results.
- Why: Delta v1 showed five archive hard tasks with local source-backed candidates but `not_satisfied` status. The new mapping moves those five tasks to `partial` without changing task definitions, removing expected fields, fabricating evidence, or marking any task overall satisfied. The next selected milestone is Old-Platform Result Refinement Pack v0 because expected lanes and bad-result pattern checks remain not evaluable.

## ADR-068: Score Result Shape Before Expanding Old-Platform Evidence Again

- Status: accepted
- Decision: Eureka now records Old-Platform Result Refinement Pack v0 under `control/audits/old-platform-result-refinement-v0/` and updates Archive Resolution Eval Runner v0 to score deterministic primary-candidate shape, expected lanes, and bad-result pattern avoidance for the current old-platform hard eval partials.
- Why: Hard Eval Satisfaction Pack v0 proved source-backed candidates exist but did not score lane or bad-result expectations. The refinement moves `driver_inside_support_cd` to `satisfied` while keeping four old-platform tasks `partial` and `article_inside_magazine_scan` as `capability_gap`. The next selected milestone is More Source Coverage Expansion v1 because the remaining partials need exact-release, concrete-identity, direct-artifact, or source-evidence breadth. This does not weaken hard evals, add retrieval behavior, fabricate evidence, add live sources, scrape external systems, port Rust behavior, start native app work, or add deployment infrastructure.

## ADR-069: Target Old-Platform Fixture Evidence Before Article/Scan Work

- Status: accepted
- Decision: Eureka now records More Source Coverage Expansion v1 under `control/audits/more-source-coverage-expansion-v1/` and extends existing active fixture families with tiny Firefox XP, blue FTP-client XP, Windows 98 registry repair, and Windows 7 utility/app evidence.
- Why: Old-Platform Result Refinement Pack v0 left four old-platform hard tasks partial because the exact release, concrete identity, direct artifact, and source-evidence breadth checks needed more fixture-backed evidence. This targeted expansion moves archive evals to `capability_gap=1` and `satisfied=5`, while Search Usefulness Audit now reports 5 covered, 21 partial, 27 source gaps, 9 capability gaps, and 2 unknowns. The next selected milestone is Article/Scan Fixture Pack v0 because `article_inside_magazine_scan` remains the only archive hard capability gap. This does not weaken hard evals, add live source calls, scrape external systems, add arbitrary local ingestion, add real binaries, fabricate external baselines, port Rust behavior, start native app work, or add deployment infrastructure.

## ADR-070: Add Article/Scan Fixture Evidence Without OCR or Real Scans

- Status: accepted
- Decision: Eureka now records Article/Scan Fixture Pack v0 under `control/audits/article-scan-fixture-pack-v0/` and adds `article-scan-recorded-fixtures` as a tiny active recorded-fixture source with one synthetic article segment, parent issue lineage, page-range metadata, and OCR-like fixture text.
- Why: More Source Coverage Expansion v1 left `article_inside_magazine_scan` as the only archive hard capability gap. The new fixture moves archive evals to `satisfied=6`, while Search Usefulness Audit now reports 5 covered, 22 partial, 26 source gaps, 9 capability gaps, and 2 unknowns. The next selected milestone is Manual External Baseline Observation Pack v0 because all current archive hard evals are satisfied under strict fixture-backed checks and external baselines remain pending/manual. This does not add OCR engines, PDF/image parsing, real magazine scans, copyrighted article text, live source calls, scraping, arbitrary local ingestion, fuzzy/vector/LLM retrieval, Rust behavior ports, native app work, production deployment, or external baseline claims.

## ADR-071: Define Manual External Baseline Observation Protocol

- Status: accepted
- Decision: Eureka now records Manual External Baseline Observation Pack v0 under `evals/search_usefulness/external_baselines/` with manual-only baseline systems, a JSON observation schema, a fillable template, operator instructions, a pending observation manifest, and stdlib validation/status-report scripts.
- Why: Archive hard evals are now satisfied internally, but all Google and Internet Archive baselines remain pending/manual. The pack creates a repeatable way for a human operator to record Google web search, Internet Archive metadata search, and Internet Archive full-text/OCR observations for the 64-query audit corpus without scraping, automated external searches, live APIs, or fabricated results. It seeds 192 pending slots and recommends Manual Observation Batch 0 as the next milestone. It changes no retrieval behavior, records no observed external baselines, and makes no global Google/Internet Archive comparison claim.

## ADR-072: Prepare Manual Observation Batch 0 Without Filling Results

- Status: accepted
- Decision: Eureka now records Manual Observation Batch 0 under `evals/search_usefulness/external_baselines/batches/batch_0/`, selecting 13 existing high-value query IDs across Google web search, Internet Archive metadata search, and Internet Archive full-text/OCR search for 39 pending query/system slots.
- Why: The manual external baseline protocol exists, but a human operator still needs a manageable first batch before any comparison report. Batch 0 narrows the work to old-platform software, member-level discovery, driver/support-media, and article/scan queries where external comparison is most useful. It creates templates, instructions, validation, and reporting support only; it does not perform observations, scrape or automate external systems, call APIs, fabricate top results, or treat one future manual observation as global truth. The next selected milestone is Manual Observation Batch 0 Execution.

## ADR-073: Add Manual Observation Entry Helpers Without Performing Observations

- Status: accepted
- Decision: Eureka now adds Manual Observation Entry Helper v0 through stdlib-only scripts for listing manual external-baseline slots, creating one fillable pending observation file from a Batch 0 slot, validating one file or the full observation area, and reporting Batch 0 progress.
- Why: Batch 0 exists, but human entry needs a safer local workflow before any observations are manually filled. The helpers reduce friction while preserving the boundary that Codex and scripts do not perform observations: they do not fetch URLs, open browsers, scrape Google or Internet Archive, automate external searches, call APIs, populate top results, mark pending records observed, fabricate external baselines, or claim global Google/Internet Archive truth. The next milestone remains Manual Observation Batch 0 Execution by a human operator.

## ADR-074: Add LIVE_ALPHA_00 Static Public Site Pack Without Deployment

- Status: accepted
- Decision: Eureka now records LIVE_ALPHA_00 Static Public Site Pack under `site/dist/` with plain static HTML/CSS pages for identity, status, source matrix, eval/audit state, demo queries, limitations, roadmap, and local quickstart, plus a stdlib validator at `scripts/validate_public_static_site.py`.
- Why: live-alpha preparation needs honest public-facing material before backend hosting. This pack is static documentation only: it does not deploy Eureka, add hosting infrastructure, add DNS or cloud configuration, start a server, add live source probes, scrape Google or Internet Archive, automate external searches, fabricate external baselines, weaken evals, or claim production readiness. The next Codex-side milestone is Public Alpha Rehearsal Evidence v0, while Manual Observation Batch 0 Execution remains human-operated parallel work.

## ADR-075: Record Public Alpha Rehearsal Evidence Without Deploying

- Status: accepted
- Decision: Eureka now records Public Alpha Rehearsal Evidence v0 under `docs/operations/public_alpha_rehearsal_evidence_v0/` with a stdlib generator/check script at `scripts/generate_public_alpha_rehearsal_evidence.py`.
- Why: the static site, safe mode, hosting pack, smoke checks, route inventory, evals, and manual baseline status need one supervised local evidence packet before wrapper or deployment-config work. The pack records static-site validation, public-alpha smoke status, route classification counts, archive/search eval status, external-baseline pending counts, blockers, next deployment requirements, and unsigned operator signoff. It does not deploy Eureka, approve production, add hosting infrastructure, add live probes, scrape external systems, call external APIs, fabricate external observations, weaken evals, or claim a public deployment happened.

## ADR-076: Add Public Alpha Wrapper Without Deployment

- Status: accepted
- Decision: Eureka now adds LIVE_ALPHA_01 Production Public-Alpha Wrapper through `scripts/run_public_alpha_server.py` and `surfaces/web/server/public_alpha_config.py`.
- Why: public-alpha rehearsal evidence showed the repo has safe-mode behavior, static-site validation, route inventory, smoke checks, eval evidence, and pending manual baselines, but future supervised hosting still needs one explicit process/config guard before deployment config. The wrapper defaults to localhost, requires `public_alpha`, rejects unsupported modes, guards nonlocal binds, reports safe capability flags, disables live probes and live Internet Archive access, blocks local path root configuration, keeps downloads/readback and user storage closed, and exposes no deployment approval or production-readiness claim. It does not deploy Eureka, add DNS or provider configuration, add auth/TLS/rate limiting/process management, enable live probes, scrape external systems, fabricate external baselines, weaken evals, or port Rust behavior.

## ADR-077: Add Public Publication Plane Contracts Before Deployment

- Status: accepted
- Decision: Eureka now adds Public Publication Plane Contracts v0 under `control/inventory/publication/` with reference documentation and `scripts/validate_publication_inventory.py`.
- Why: public routes, status vocabulary, public JSON fields, client profiles, base-path behavior, redirect policy, and claim traceability are harder to change than deployment mechanics. The publication plane defines `site/dist/` as the current static artifact, reserves `site/` and `site/dist/` for later generation work, records GitHub Pages project-path semantics at `/eureka/`, keeps custom-domain and backend targets future, and validates that reserved `/lite/`, `/text/`, `/files/`, `/data/`, `/api/`, and `/snapshots/` route families are not implemented by claim alone. It does not deploy Eureka, add a GitHub Pages workflow, add DNS or provider configuration, create a generator, enable live backend behavior, add live probes, record external observations, weaken evals, or port Rust behavior. The next Codex-side milestone becomes GitHub Pages Deployment Enablement v0 using these contracts.

## ADR-078: Enable Static GitHub Pages Deployment Path Without Backend Hosting

- Status: accepted
- Decision: Eureka now adds GitHub Pages Deployment Enablement v0 through `.github/workflows/pages.yml`, `docs/operations/GITHUB_PAGES_DEPLOYMENT.md`, `scripts/check_github_pages_static_artifact.py`, and workflow/artifact safety tests.
- Why: after the publication plane defined the public route, data, client, base-path, and deployment target contracts, GitHub Pages can be a small static publishing layer over `site/dist/`. The workflow validates the publication inventory, validates the static site, checks the artifact for runtime/secrets/local-store leakage and base-path unsafe links, uploads only `site/dist/`, and deploys through GitHub's Pages artifact actions. It does not deploy the Python backend, enable live probes or live Internet Archive access, add custom-domain configuration, add a generator or Node/npm chain, add secrets, add auth/TLS/rate limiting/process management, fabricate external observations, weaken hard evals, or claim a public deployment succeeded without GitHub Actions evidence. The next Codex-side milestone becomes Static Site Generation Migration v0.

## ADR-079: Add Stdlib Static Site Generator Without Replacing Public Site Artifact

- Status: accepted
- Decision: Eureka now adds Static Site Generation Migration v0 through `site/`, `site/build.py`, `site/validate.py`, page JSON, templates, copied static assets, generated `site/dist/`, and generated-site tests.
- Why: after the publication plane and GitHub Pages workflow made `site/dist/` governable and deployable as a static artifact, the next risk is hand-authored public pages drifting from repo inventories and contracts. The v0 generator renders the current no-JS pages from governed source files and source inventory reads into `site/dist/` for validation, while keeping `site/dist/` as the GitHub Pages artifact. It adds no Node/npm, frontend framework, custom domain, deployment workflow change, live backend behavior, live probes, external baseline observations, fuzzy/vector/LLM retrieval, Rust behavior port, native app project, or production-readiness claim. The next Codex-side milestone becomes Generated Public Data Summaries v0.

## ADR-080: Generate Static Public Data Summaries Without Creating a Live API

- Status: accepted
- Decision: Eureka now adds Generated Public Data Summaries v0 through `scripts/generate_public_data_summaries.py`, static JSON files under `site/dist/data/`, generated copies under `site/dist/data/`, updated publication data contracts, validator checks, static-page links, and public-data tests.
- Why: after the publication contracts, Pages workflow, and stdlib site generator established a safe static publication plane, the then-future lite/text/files surfaces, snapshots, relays, API handoff planning, and native clients needed machine-readable summaries that traced back to governed repo sources. The v0 summaries project page registry, source posture, eval/audit counts, public-alpha route posture, site summary, and build provenance from local inventories and deterministic scripts while keeping `site/dist/` as the deployable artifact. They are static data summaries, not a live API or production JSON stability promise, and they add no deployment behavior, live backend, live probes, live Internet Archive calls, external searches, fabricated external observations, Node/npm chain, Rust behavior port, native app project, or production-readiness claim. The next Codex-side milestone became Lite/Text/Files Seed Surfaces v0.

## ADR-081: Seed Lite, Text, and Files Surfaces Without Live Search or Downloads

- Status: accepted
- Decision: Eureka now adds Lite/Text/Files Seed Surfaces v0 through `scripts/generate_compatibility_surfaces.py`, static seed surfaces under `site/dist/lite/`, `site/dist/text/`, and `site/dist/files/`, generated copies under `site/dist/`, checksum metadata for public data files, publication inventory updates, validator checks, and surface tests.
- Why: after generated public data summaries landed, old-browser, text-browser, simple file-tree, snapshot, relay, and future native-client consumption paths need static compatibility surfaces before any snapshot bundle or live handoff contract. The v0 surfaces consume committed public data summaries and keep `site/dist/` as the GitHub Pages artifact. They add no live search, executable downloads, software mirror, signed snapshot, relay runtime, native-client runtime, live backend behavior, live probes, external observations, Node/npm chain, Rust behavior port, deployment change, or production-readiness claim. The next Codex-side milestone becomes Static Resolver Demo Snapshots v0.

## ADR-082: Add Static Resolver Demo Snapshots Without Live Search or API Semantics

- Status: accepted
- Decision: Eureka now adds Static Resolver Demo Snapshots v0 through `scripts/generate_static_resolver_demos.py`, static no-JS demo pages under `site/dist/demo/`, generated validation copies under `site/dist/demo/`, a static demo manifest at `site/dist/demo/data/demo_snapshots.json`, publication inventory updates, validator checks, and demo snapshot tests.
- Why: after generated public data summaries and lite/text/files seed surfaces made the publication plane consumable by compatibility-first clients, Eureka needed representative static examples of current resolver behavior before snapshots, domain readiness, or live backend handoff. The v0 demos show fixture-backed query planning, member-level results, compatibility evidence, result lane/user-cost explanation, absence reasoning, comparison/disagreement, source detail, article/scan fixture results, and eval summaries while keeping `site/dist/` as the GitHub Pages artifact. They add no live search, live API semantics, backend hosting, external observations, signed snapshots, relay/native runtime, Node/npm chain, Rust behavior port, deployment change, or production-readiness claim. The next Codex-side milestone becomes Custom Domain / Alternate Host Readiness v0.

## ADR-083: Record Host Readiness Without Configuring Domains Or Alternate Providers

- Status: accepted
- Decision: Eureka now adds Custom Domain / Alternate Host Readiness v0 through `control/inventory/publication/domain_plan.json`, `control/inventory/publication/static_hosting_targets.json`, `docs/operations/CUSTOM_DOMAIN_AND_ALTERNATE_HOST_READINESS.md`, `docs/operations/CUSTOM_DOMAIN_OPERATOR_CHECKLIST.md`, `docs/reference/BASE_PATH_PORTABILITY.md`, `scripts/validate_static_host_readiness.py`, and readiness tests.
- Why: after static Pages deployment enablement, generated public data, compatibility seed surfaces, and static demo snapshots, the hardest remaining publication-plane risk is host portability and accidental public claims. The readiness layer records `/eureka/` versus `/` base-path expectations, future custom-domain prerequisites, takeover-risk language, prohibited claims, alternate-static-host candidates, and an unsigned operator checklist while preserving `site/dist/` as the current artifact. It adds no DNS records, `CNAME`, provider config, alternate-host deployment, backend hosting, live probes, custom-domain claim, deployment-success claim, Node/npm chain, Rust behavior port, native app project, or production-readiness claim. The next Codex-side milestone becomes Live Backend Handoff Contract v0.

## ADR-084: Reserve Live Backend Handoff Without Making An API Live

- Status: accepted
- Decision: Eureka now adds Live Backend Handoff Contract v0 through `control/inventory/publication/live_backend_handoff.json`, `control/inventory/publication/live_backend_routes.json`, `control/inventory/publication/surface_capabilities.json`, `docs/architecture/LIVE_BACKEND_HANDOFF.md`, `docs/reference/LIVE_BACKEND_HANDOFF_CONTRACT.md`, `docs/reference/LIVE_BACKEND_ERROR_ENVELOPE.md`, `scripts/validate_live_backend_handoff.py`, and handoff tests.
- Why: after static host readiness, Eureka needs to define how the static publication plane may later hand off to a hosted public-alpha backend before any hosted backend claim or live route appears. The v0 contract reserves future `/api/v1` status, search, query-plan, source, evidence, object, result, absence, comparison, and live-probe endpoint families; records disabled live capability flags; and documents error-envelope expectations. It adds no backend hosting, live `/api/v1` route, live source probe, Internet Archive access, CORS/auth/rate-limit implementation, provider config, custom domain, external observation, Rust behavior port, native app project, or production API guarantee. The next Codex-side milestone becomes Live Probe Gateway Contract v0.

## ADR-085: Define Live Probe Gateway Policy Before External Probes

- Status: accepted
- Decision: Eureka now adds Live Probe Gateway Contract v0 through `control/inventory/publication/live_probe_gateway.json`, `docs/reference/LIVE_PROBE_GATEWAY_CONTRACT.md`, `docs/architecture/LIVE_PROBE_GATEWAY.md`, `docs/operations/LIVE_PROBE_POLICY.md`, `scripts/validate_live_probe_gateway.py`, and live-probe gateway tests.
- Why: after reserving future `/api/v1` handoff routes, Eureka needs a disabled-by-default source-probe policy before any Internet Archive, Wayback, GitHub, Software Heritage, package registry, Wikidata, or other external metadata probe can be considered. The v0 contract defines candidate sources, caps, cache/evidence requirements, retry and circuit-breaker posture, no-download/no-arbitrary-URL-fetch rules, operator gates, and Google-as-manual-baseline-only posture. It adds no live probe adapters, network calls, URL fetching, scraping, crawling, downloads, live Internet Archive behavior, provider config, backend hosting, Rust behavior port, native app project, or production source claim. The next unattended Codex-side milestone becomes Rust Query Planner Parity Candidate v0; Internet Archive Live Probe v0 requires explicit human approval after separate review.

## ADR-086: Add Isolated Rust Query Planner Parity Candidate Without Runtime Wiring

- Status: accepted
- Decision: Eureka now adds Rust Query Planner Parity Candidate v0 through `crates/eureka-core/src/query_planner.rs`, expanded Python-oracle query-planner goldens, `tests/parity/rust_query_planner_cases.json`, `scripts/check_rust_query_planner_parity.py`, and parity structure tests.
- Why: after source-registry parity and the live-probe gateway contract, the next safe Rust step is a non-network deterministic planner candidate that follows the Python oracle instead of changing runtime behavior. The candidate covers the current old-platform planner families, including platform aliases, platform-as-constraint, latest-compatible release intent, driver/hardware intent, vague software identity uncertainty, documentation intent, member/container discovery, article/scan intent, and generic fallback. It adds no Python planner replacement, web/CLI/HTTP API wiring, worker integration, public-alpha route behavior, production Rust backend, live probes, external API calls, scraping, crawling, downloads, native app project, deployment behavior, or production-readiness claim. Cargo checks remain optional when the local Rust toolchain is unavailable. The next unattended Codex-side milestone should be Compatibility Surface Strategy v0 or Signed Snapshot Format v0; Internet Archive Live Probe v0 still requires explicit human approval.

## ADR-087: Govern Compatibility Surfaces Before Snapshot, Relay, Or Native Work

- Status: accepted
- Decision: Eureka now adds Compatibility Surface Strategy v0 through `docs/architecture/COMPATIBILITY_SURFACES.md`, expanded `control/inventory/publication/surface_capabilities.json`, `control/inventory/publication/surface_route_matrix.json`, old-client degradation policy, native-client readiness policy, snapshot/relay readiness notes, `scripts/validate_compatibility_surfaces.py`, and tests.
- Why: the publication plane now has static pages, public data, lite/text/files seed surfaces, static demos, future `/api/v1` reservations, and disabled live-probe policy. The next durable contract is a clear same-resolver-truth/multiple-projection strategy so old browsers, text clients, file-tree clients, snapshots, relays, API clients, CLI, web, and future native clients do not drift into different truth models. This adds no new runtime behavior, snapshots, relay services, native app project, live API, live backend deployment, live probes, external API calls, scraping, crawling, downloads, frontend framework, provider config, or production-readiness claim. The next non-network milestone should be Signed Snapshot Format v0; Manual Observation Batch 0 remains human-operated parallel work.

## ADR-088: Define Signed Snapshot Format Without Real Keys Or Downloads

- Status: accepted
- Decision: Eureka now adds Signed Snapshot Format v0 through `control/inventory/publication/snapshot_contract.json`, `docs/reference/SNAPSHOT_FORMAT_CONTRACT.md`, `docs/reference/SNAPSHOT_SIGNATURE_POLICY.md`, `snapshots/schema/`, `scripts/generate_static_snapshot.py`, `scripts/validate_static_snapshot.py`, and a deterministic seed example under `snapshots/examples/static_snapshot_v0/`.
- Why: after the compatibility surface strategy, Eureka needs an offline/static snapshot contract before relay designs, native clients, or future downloadable snapshot surfaces can safely consume publication-plane data. The v0 format records required manifests, public data projections, checksums, and signature-placeholder documentation while keeping `site/dist/` as the current GitHub Pages artifact. It adds no real signing keys, production signatures, executable downloads, real software binaries, public `/snapshots/` route, relay service, native-client runtime, live backend behavior, live probes, external API calls, scraping, crawling, provider config, or production-authentic release claim. The next non-network milestone should be Relay Surface Design v0.

## ADR-089: Record Post-Queue State Checkpoint As Audit Metadata

Status: accepted

Post-Queue State Checkpoint v0 is recorded under
`control/audits/post-queue-state-checkpoint-v0/` as durable repo-state evidence
and planning metadata after the publication/static/live-alpha/Rust/snapshot
queue. It does not add product runtime behavior, live probes, deployment
behavior, external observations, production signing, relay services, or native
clients. Relay Surface Design v0 is the next recommended Codex-safe milestone;
Manual Observation Batch 0 remains human-operated parallel work.

## ADR-090: Define Relay Surface Design Without Relay Runtime

Status: accepted

Relay Surface Design v0 is recorded through
`control/inventory/publication/relay_surface.json`,
`docs/architecture/RELAY_SURFACE.md`,
`docs/reference/RELAY_SURFACE_CONTRACT.md`,
`docs/reference/RELAY_SECURITY_AND_PRIVACY.md`,
`docs/operations/RELAY_OPERATOR_CHECKLIST.md`,
`scripts/validate_relay_surface_design.py`, and tests.

The decision keeps future relay work local/LAN, operator-controlled, read-only
by default, public-data-only by default, and dependent on snapshots, public
data summaries, lite/text/files surfaces, and later explicit policy. It adds no
relay runtime, network socket, local HTTP relay, FTP, SMB, WebDAV, AFP, NFS,
Gopher, protocol proxy, native sidecar, private data exposure, write/admin
route, live-probe passthrough, backend hosting, external call, deployment
behavior, or production relay claim. The next Codex-safe milestone should be
Rust Source Registry Parity Catch-up v0; Manual Observation Batch 0 remains
human-operated parallel work.

## ADR-091: Catch Up Rust Source Registry Candidate To Current Python Shape

Status: accepted

Rust Source Registry Parity Catch-up v0 updates the isolated Rust
source-registry candidate through `crates/eureka-core/src/source_registry.rs`,
expanded Python-oracle source-registry goldens,
`tests/parity/rust_source_registry_cases.json`,
`scripts/check_rust_source_registry_parity.py`, and parity structure tests.

The decision makes the Rust candidate preserve the current Python
source-registry shape, including capability booleans, coverage depth/status,
connector mode, current limitations, next coverage step, placeholder warnings,
recorded fixture flags, local/private future source posture, and article-scan
source records. It keeps Python as the oracle, treats Cargo as optional where
the toolchain is unavailable, and adds no Rust runtime wiring, Python source
registry replacement, web/CLI/HTTP API integration, public-alpha route
behavior, live probes, external API calls, scraping, crawling, provider config,
deployment behavior, native app project, or production Rust backend claim. The
next Codex-safe milestone should be Rust Local Index Parity Planning v0;
Manual Observation Batch 0 remains human-operated parallel work.

## ADR-092: Plan Rust Local Index Parity Before Implementing It

Status: accepted

Rust Local Index Parity Planning v0 adds
`tests/parity/RUST_LOCAL_INDEX_PARITY_PLAN.md`,
`tests/parity/rust_local_index_cases.json`,
`tests/parity/local_index_acceptance.schema.json`,
`scripts/validate_rust_local_index_parity_plan.py`, and structure tests.

The decision is to define the future local-index parity target before writing
Rust index behavior. The plan names the current Python-oracle local-index
goldens, the 489-record bounded build status, required record kinds,
source/member/article/compatibility/lane/user-cost fields, current and future
query cases, deterministic ordering, FTS/fallback normalization, path privacy,
and allowed/forbidden divergences. Python remains the oracle, Rust remains
unwired, and this adds no Rust local-index implementation, SQLite/indexing
behavior, Python runtime replacement, web/CLI/HTTP API integration, worker or
gateway behavior, public-alpha route change, live probes, external API calls,
scraping, crawling, provider config, deployment behavior, native app project,
or production Rust backend claim. The next Codex-safe milestone should be
Signed Snapshot Consumer Contract v0; Manual Observation Batch 0 remains
human-operated parallel work.

## ADR-093: Define Snapshot Consumer Contract Before Native Or Relay Runtime

Status: accepted

Signed Snapshot Consumer Contract v0 adds
`control/inventory/publication/snapshot_consumer_contract.json`,
`control/inventory/publication/snapshot_consumer_profiles.json`,
`docs/reference/SNAPSHOT_CONSUMER_CONTRACT.md`,
`scripts/validate_snapshot_consumer_contract.py`, and focused operations/script
tests.

The decision is to define how future file-tree, text, lite HTML, relay, native,
and audit-tool consumers read and validate static snapshots before any consumer
runtime exists. The contract fixes the required read order, checksum semantics,
v0 signature-placeholder handling, missing optional file behavior, unsupported
feature posture, and consumer profile limits. It keeps Signed Snapshot Format
v0 as a static/experimental seed, keeps relay/native consumption future, and
adds no snapshot reader runtime, relay service, native client, production
signing, real signing keys, executable downloads, live backend behavior, live
probes, external API calls, scraping, crawling, deployment behavior, or
production authenticity claim. The next Codex-safe milestone should be Native
Client Contract v0; Manual Observation Batch 0 remains human-operated parallel
work.

## ADR-094: Define Native Client Contract Before App Projects

Status: accepted

Native Client Contract v0 adds
`control/inventory/publication/native_client_contract.json`,
`control/inventory/publication/native_client_lanes.json`,
`docs/reference/NATIVE_CLIENT_CONTRACT.md`,
`docs/reference/NATIVE_CLIENT_LANES.md`,
`docs/operations/NATIVE_CLIENT_READINESS_CHECKLIST.md`,
`scripts/validate_native_client_contract.py`, and focused operations/script
tests.

The decision is to define future native client inputs, Windows/Mac lane policy,
readiness gates, CLI current-state boundaries, snapshot/public-data/live
handoff/relay dependencies, Python oracle status, and Rust parity-only status
before any native app project exists. Windows 7 x64 WinForms/.NET 4.8 is the
first pragmatic future candidate, while XP, Windows 95/NT4, Win16, legacy Mac,
modern macOS, and Classic Mac lanes remain future, lab-verify, or research.
This adds no Visual Studio project, Xcode project, native GUI, FFI, native
snapshot reader runtime, relay sidecar, installer automation, package-manager
behavior, executable download/execution automation, live probes, external API
calls, scraping, crawling, deployment behavior, production native-client claim,
or Rust runtime wiring. The next Codex-safe milestone should be Native Action /
Download / Install Policy v0; Manual Observation Batch 0 remains human-operated
parallel work.

## ADR-095: Define Native Action Policy Before Download Or Install Work

Status: accepted

Native Action / Download / Install Policy v0 adds
`control/inventory/publication/action_policy.json`,
`docs/reference/ACTION_DOWNLOAD_INSTALL_POLICY.md`,
`docs/reference/EXECUTABLE_RISK_POLICY.md`,
`docs/reference/RIGHTS_AND_ACCESS_POLICY.md`,
`docs/reference/INSTALL_HANDOFF_CONTRACT.md`,
`scripts/validate_action_policy.py`, and focused operations/script tests.

The decision is to define future action, download, mirror, install handoff,
package-manager handoff, execute, restore, uninstall, rollback, malware-scan,
and rights/access policy before any native client, relay, snapshot consumer,
or public download surface implements those behaviors. The policy separates
safe read-only actions from risky future actions, requires future warnings and
explicit confirmation, keeps public-alpha/static Pages risky actions disabled,
and records that hashes prove identity/integrity rather than safety. This adds
no downloads, installers, install automation, package-manager integration,
malware scanning, rights clearance, native clients, relay runtime, executable
trust claims, live probes, external API calls, scraping, deployment behavior,
or production readiness. The next Codex-safe milestone should be Native Local
Cache / Privacy Policy v0; Manual Observation Batch 0 remains human-operated
parallel work.

## ADR-096: Define Native Local Cache Privacy Policy Before Project Readiness

Status: accepted

Native Local Cache / Privacy Policy v0 adds
`control/inventory/publication/local_cache_privacy_policy.json`,
`docs/reference/LOCAL_CACHE_PRIVACY_POLICY.md`,
`docs/reference/NATIVE_LOCAL_CACHE_CONTRACT.md`,
`docs/reference/TELEMETRY_AND_LOGGING_POLICY.md`,
`scripts/validate_local_cache_privacy_policy.py`, and focused
operations/script tests.

The decision is to define future native/local cache, private-data, local-path,
telemetry/logging, diagnostics, credentials, deletion/export/reset, portable
mode, snapshot, relay, and public-alpha privacy policy before any native
project readiness review or cache runtime work. The policy keeps private cache,
private ingestion, telemetry, analytics, accounts, cloud sync, uploads,
old-client private relay, and local archive scanning disabled by default. This
adds no cache runtime, private file ingestion, local archive scanning,
telemetry implementation, account system, cloud sync, uploads, native client,
relay runtime, live probes, external API calls, scraping, deployment behavior,
or production readiness. The next Codex-safe milestone should be Native Client
Project Readiness Review v0; Manual Observation Batch 0 remains
human-operated parallel work.

## ADR-097: Require Native Project Readiness Evidence Before Scaffolding

Status: accepted

Native Client Project Readiness Review v0 adds
`control/audits/native-client-project-readiness-v0/`,
`scripts/validate_native_project_readiness_review.py`, and focused
operations/script tests.

The decision is to record a conservative evidence review before any Visual
Studio, Xcode, GUI, FFI, cache runtime, download, installer, relay, live-probe,
or native runtime work. The review decision is
`ready_for_minimal_project_skeleton_after_human_approval` for the
`windows_7_x64_winforms_net48` lane only. That is not approval to create a
project in this milestone; it means a future human-approved planning milestone
may define project path, namespace, build-host assumptions, minimum read-only
screens, and validation strategy. This adds no native project files, native app
source tree, GUI behavior, FFI, local cache runtime, downloads, installers,
relay runtime, live probes, external API calls, scraping, deployment behavior,
or production readiness. The next Codex-safe milestone should be Windows 7
WinForms Native Skeleton Planning v0, not implementation. Manual Observation
Batch 0 remains human-operated parallel work.

## ADR-098: Plan Windows 7 WinForms Skeleton Before Project Files

Status: accepted

Windows 7 WinForms Native Skeleton Planning v0 adds
`control/audits/windows-7-winforms-native-skeleton-planning-v0/`,
`scripts/validate_windows_winforms_skeleton_plan.py`, and focused
operations/script tests.

The decision is to record the first future Windows native skeleton scope before
creating any project files. The plan proposes `clients/windows/winforms-net48/`
and `Eureka.Clients.Windows.WinForms`, requires a Windows host with Visual
Studio 2022, .NET Framework 4.8 targeting/developer pack, x64 target, and
Windows 7 SP1+ runtime verification, and limits any future skeleton to
read-only static public data and seed snapshot demo inspection. This adds no
`clients/`, Visual Studio solution, `.csproj`, C# source, GUI behavior, FFI,
local cache runtime, downloads, installers, package-manager integration,
telemetry, accounts, relay runtime, live probes, external API calls, scraping,
deployment behavior, or production readiness. A future implementation prompt
must include explicit human approval before any skeleton is created.

## ADR-099: Plan Local Static Relay Before Runtime

Status: accepted

Relay Prototype Planning v0 adds
`control/audits/relay-prototype-planning-v0/`,
`scripts/validate_relay_prototype_plan.py`, and focused operations/script
tests.

The decision is to make the first future relay prototype a
`local_static_http_relay_prototype`: localhost-only by default, read-only, and
limited to allowlisted static public data, text/files seed surfaces, and seed
snapshot files. The plan records allowed inputs and outputs, prohibited inputs
and outputs, security/privacy defaults, operator gates, and future test
requirements before any runtime exists. This adds no relay server, socket
listener, local HTTP relay behavior, FTP, SMB, AFP, NFS, WebDAV, Gopher, TLS
translation, protocol translation, native sidecar, snapshot mount, private file
serving, live backend proxying, live source probes, arbitrary local filesystem
ingestion, downloads, installers, telemetry, accounts, deployment behavior, or
production readiness claim. A future Relay Prototype Implementation v0 prompt
must include explicit human approval before any relay runtime is created.

## ADR-100: Use Full Project Audit Before Implementation Growth

Status: accepted

Full Project State Audit and Forward Plan v0 adds
`control/audits/full-project-state-audit-v0/`,
`scripts/validate_full_project_state_audit.py`, and focused
operations/script tests.

The decision is to checkpoint the whole repo after the
backend/publication/snapshot/relay/native-policy/Rust planning sequence before
starting approved-but-riskier implementation work. The audit records milestone
status, command results, eval/search status, external-baseline pending state,
publication/static/public-alpha status, source/retrieval state,
snapshot/relay/native/Rust status, risks, blockers, human-operated work,
deferrals, and the next 20 recommended milestones. It recommends Public Data
Contract Stability Review v0 next, with Generated Artifact Drift Guard v0 as
the alternative. This adds no runtime behavior, relay service, native project,
live probe, deployment behavior, external observation, download, installer,
local cache, telemetry, account, cloud sync, or production claim.

## ADR-101: Classify Public Data Stability Before Client Dependence

Status: accepted

Public Data Contract Stability Review v0 adds
`control/audits/public-data-contract-stability-review-v0/`,
`docs/reference/PUBLIC_DATA_STABILITY_POLICY.md`,
`scripts/validate_public_data_stability.py`, and focused operations/script
tests.

The decision is to keep generated public JSON under `site/dist/data/` as
pre-alpha static data while classifying individual field paths as
`stable_draft`, `experimental`, `volatile`, `internal`, `deprecated`, or
`future`. Future static, snapshot, relay, and native clients may depend only on
named `stable_draft` field paths with `schema_version` checks; experimental
fields are display-only unless version-pinned, volatile fields are diagnostic,
and internal fields are not public API. This adds no product behavior, live
API, live backend, live probes, relay runtime, native client, snapshot reader,
download/install behavior, deployment behavior, external observation, or
production API stability claim. The next Codex-safe milestone is Generated
Artifact Drift Guard v0.

## ADR-102: Guard Generated Artifact Drift Without Mutation

Status: accepted

Generated Artifact Drift Guard v0 adds
`control/inventory/generated_artifacts/`,
`docs/operations/GENERATED_ARTIFACT_DRIFT_GUARD.md`,
`control/audits/generated-artifact-drift-guard-v0/`,
`scripts/check_generated_artifact_drift.py`, and focused operations/script
tests.

The decision is to record ownership and deterministic check commands for
committed generated and generated-like artifacts before future clients depend
more heavily on static data and snapshots. The guard covers public data,
lite/text/files surfaces, static resolver demos, static snapshot seed files,
`site/dist`, Python oracle goldens, public-alpha rehearsal evidence,
publication inventories, test registry metadata, and AIDE metadata. Default
mode is non-mutating: it runs check commands and validators, not update
commands. This adds no product behavior, live API, live backend, live probes,
relay runtime, native client, snapshot reader, deployment behavior, external
observation, download/install behavior, network calls, or production API
stability claim. The next Codex-safe milestone is Repository Shape
Consolidation v0.

## ADR-103: Consolidate Static Publication Around Site Dist

Status: accepted

Repository Shape Consolidation v0 makes `site/dist/` the single generated
static deployment artifact, updates the GitHub Pages workflow and artifact
checkers to consume that path, removes the active legacy static artifact path,
records `static_site_dist` in the generated artifact inventory, and confirms
`external/` as the root for pinned outside references.

The decision is to end the dual static-artifact model before public search,
static publication review, source packs, snapshots, native clients, relay, or
hosted services build on top of it. This adds no public search runtime, public
API routes, live backend hosting, live source probes, crawling, external search
automation, relay runtime, native client, downloads, accounts, telemetry, auth,
TLS, rate limiting, production signing, or production readiness claim. The next
Codex-safe milestone is Static Artifact Promotion Review v0.

## ADR-104: Conditionally Promote Site Dist As Active Static Artifact

Status: accepted

Static Artifact Promotion Review v0 adds
`control/audits/static-artifact-promotion-review-v0/`,
`scripts/validate_static_artifact_promotion_review.py`, and focused tests for
the promotion review.

The decision is to conditionally promote `site/dist/` as the active repo-local
static publication artifact after repository shape consolidation. The review
records local validation evidence, workflow upload path, generated artifact
ownership, static safety, base-path behavior, public data surfaces, and
stale-reference classification. The condition is GitHub Actions evidence:
deployment success remains unverified until a run-evidence review checks and
records an actual Pages run. This adds no public search runtime, API routes,
backend hosting, live probes, crawling, external search automation, relay
runtime, native client, downloads, accounts, telemetry, auth, TLS, rate
limiting, production signing, or production readiness claim. The next
Codex-safe milestone is GitHub Pages Run Evidence Review v0.

## ADR-105: Record Pages Run Evidence Before Deployment Claims

Status: accepted

GitHub Pages Run Evidence Review v0 adds
`control/audits/github-pages-run-evidence-v0/`,
`scripts/validate_github_pages_run_evidence.py`, and focused tests for the
run-evidence review.

The decision is to treat local `site/dist` readiness and public deployment
evidence as separate gates. The current-head Pages workflow run exists and
matched the promoted static artifact state, but it failed at
`actions/configure-pages@v5` because the repository Pages site was not
found/enabled for GitHub Actions. Static build and validation steps passed
before the failure; the Pages artifact upload and deployment steps were
skipped; no deployment URL was emitted; and no deployment-success claim is
allowed. This adds no deployment implementation, backend hosting, public search
runtime, live probes, crawling, external source calls, custom domain, secrets,
auth, telemetry, downloads, native clients, relay runtime, or production
readiness claim. The next Codex-safe Pages milestone is GitHub Pages Workflow
Repair v0.

## ADR-106: Define Public Search Contract Before Runtime

Status: accepted

Public Search API Contract v0 adds
`contracts/api/search_request.v0.json`,
`contracts/api/search_response.v0.json`,
`contracts/api/error_response.v0.json`,
`control/inventory/publication/public_search_routes.json`,
`docs/reference/PUBLIC_SEARCH_API_CONTRACT.md`,
`docs/operations/PUBLIC_SEARCH_LOCAL_INDEX_ONLY_MODE.md`,
`scripts/validate_public_search_contract.py`, and focused tests.

The decision is to define the future public search API as governed contract
data before any hosted route or runtime handler exists. The first allowed mode
is `local_index_only`; `/search`, `/api/v1/search`, `/api/v1/query-plan`,
`/api/v1/status`, `/api/v1/sources`, and `/api/v1/source/{source_id}` are
reserved/future routes, not live routes. The contract records bounded request
limits, a response envelope with result lanes, user-cost, compatibility,
evidence, source, action, gap, warning, and absence fields, plus a stable error
envelope. This adds no route implementation, backend hosting, live probes,
external search automation, arbitrary URL fetch, crawling, downloads,
installs, uploads, local path search, credentials, accounts, telemetry, auth,
rate limiting implementation, or production API stability claim. The next
Codex-safe milestone is Public Search Result Card Contract v0; GitHub Pages
Workflow Repair v0 remains a separate operator/Pages follow-up before any
hosted deployment-success claim.

## ADR-107: Define Public Search Result Cards Before Runtime

Status: accepted

Public Search Result Card Contract v0 adds
`contracts/api/search_result_card.v0.json`,
`contracts/api/examples/search_result_card_*.v0.json`,
`docs/reference/PUBLIC_SEARCH_RESULT_CARD_CONTRACT.md`,
`control/audits/public-search-result-card-contract-v0/`,
`scripts/validate_public_search_result_card_contract.py`, and focused tests.
It also aligns `contracts/api/search_response.v0.json` so `results[]` are
explicitly public search result cards while preserving the compact aliases
reserved by Public Search API Contract v0.

The decision is to govern the reusable card shape before any search route
emits results. A card must expose title, lane, user-cost, source identity,
public identity, evidence, compatibility, parent/member context when relevant,
allowed/blocked/future-gated actions, rights caveats, risk caveats, warnings,
limitations, and gaps. Download, install, execute, upload, mirror, restore,
rollback, and private-source submission concepts are blocked or future-gated in
v0. The contract does not add runtime public search, `/search`, `/api/v1/search`,
backend hosting, live probes, arbitrary URL fetch, downloads, installers,
execution, uploads, native clients, relay runtime, snapshot reader runtime,
malware-safety claims, rights-clearance claims, production ranking guarantees,
or production API stability. The next Codex-safe milestone was Public Search
Safety / Abuse Guard v0.

## ADR-108: Gate Public Search Runtime With Safety Policy

Status: accepted

Public Search Safety / Abuse Guard v0 adds
`control/inventory/publication/public_search_safety.json`,
`docs/operations/PUBLIC_SEARCH_SAFETY_AND_ABUSE_GUARD.md`,
`docs/operations/PUBLIC_SEARCH_RUNTIME_READINESS_CHECKLIST.md`,
`scripts/validate_public_search_safety.py`, and focused tests.

The decision is to define safety, abuse, privacy, boundedness, and operator
guardrails before any public search runtime route exists. The first and only
allowed v0 mode is `local_index_only`; public search must not become live
external fanout, arbitrary URL fetch, caller-provided local path search,
downloads/installers/uploads, telemetry by default, or a production safety
claim. The policy defines request/result/time limits, forbidden parameters,
disabled behaviors, error mapping to the P26 envelope, privacy/logging posture,
future operator controls, public-alpha/static defaults, and runtime
prerequisites. It adds no runtime search route, rate-limit middleware,
auth/accounts, telemetry runtime, hosted backend, live probe,
download/install/upload surface, local path search, arbitrary URL fetch, or
production readiness claim. The next Codex-safe milestone is Local Public
Search Runtime v0 under these gates.

## ADR-109: Implement Local Public Search Runtime Behind the Gateway

Status: accepted

Local Public Search Runtime v0 adds
`runtime/gateway/public_api/public_search.py`, no-JS HTML rendering under
`surfaces/web/workbench/render_public_search.py`, stdlib web/API route wiring
for `/search`, `/api/v1/search`, `/api/v1/query-plan`, `/api/v1/status`,
`/api/v1/sources`, and `/api/v1/source/{source_id}`, `scripts/public_search_smoke.py`,
`scripts/validate_local_public_search_runtime.py`, and focused runtime, web,
integration, hardening, operations, and script tests.

The decision is to make the first runtime slice local/prototype backend only:
requests pass through the gateway public boundary, use `local_index_only`,
enforce bounded query/result/include/profile/mode validation, reject forbidden
URL/local-path/credential/download/install/upload/live-probe parameters, and
emit governed success/error/result-card envelopes. The service uses repo-owned
demo catalog and source-registry projections and does not accept caller-provided
index paths or expose private paths. It adds no hosted deployment, live probes,
external source calls, arbitrary URL fetching,
scraping, crawling, downloads, installers, uploads, accounts, telemetry
persistence, rate-limit middleware, native clients, relay runtime, production
API stability, or production readiness claim. The next Codex-safe milestone is
Public Search Static Handoff v0.

## ADR-110: Add Static Public Search Handoff Without Hosting Search

Status: accepted

Public Search Static Handoff v0 adds
`control/inventory/publication/public_search_handoff.json`,
`site/dist/search.html`, `site/dist/lite/search.html`,
`site/dist/text/search.txt`, `site/dist/files/search.README.txt`,
`site/dist/data/search_handoff.json`,
`scripts/validate_public_search_static_handoff.py`, and focused operations and
script tests.

The decision is to let the static publication site point users toward the
local/prototype public search runtime without pretending GitHub Pages runs
Python or that a hosted backend exists. The static page and old-client
surfaces are no-JS, publish a disabled hosted-search form while no backend URL
is configured, include local runtime instructions and sample queries, and
publish machine-readable handoff status. Hosted backend status remains
unavailable/unverified, and the handoff adds no backend hosting, provider
configuration, fake hosted URL, live probes, external calls, arbitrary URL
fetching, crawling, downloads, installers, uploads, local path search, accounts,
telemetry, production API stability, or production readiness claim. The next
Codex-safe milestone was Public Search Rehearsal v0, which is now implemented.

## ADR-111: Record Local Public Search Rehearsal Evidence

Status: accepted

Public Search Rehearsal v0 adds
`control/audits/public-search-rehearsal-v0/`, expands
`scripts/public_search_smoke.py`, adds
`scripts/validate_public_search_rehearsal.py`, and adds focused script,
operations, and hardening tests.

The decision is to rehearse the local/prototype public search stack before any
source expansion or hosted-search planning. The rehearsal records route
coverage for `/search`, `/api/v1/search`, `/api/v1/query-plan`,
`/api/v1/status`, `/api/v1/sources`, and `/api/v1/source/{source_id}`,
representative safe-query outcomes, governed blocked-request outcomes, static
handoff honesty, public-alpha posture, and contract alignment. It is evidence
only: no hosted deployment, provider config, custom domain, live probes,
external source calls, scraping, crawling, downloads, installers, uploads,
local path search, accounts, telemetry, rate-limit middleware, production API
stability, or production readiness claim is added. The next Codex-safe
milestone was Search Usefulness Source Expansion v2, fixture-only, which is now
implemented.

## ADR-112: Expand Search Usefulness Sources With Fixture-Only Recorded Metadata

Status: accepted

Search Usefulness Source Expansion v2 adds
`runtime/connectors/source_expansion_recorded/`, six fixture-only source records
under `control/inventory/sources/`, 15 tiny recorded metadata fixture records,
local catalog/index/public-search integration, an audit pack under
`control/audits/search-usefulness-source-expansion-v2/`,
`scripts/validate_source_expansion_v2.py`, and focused connector, index,
gateway, eval, operations, and script tests.

The decision is to improve the local search corpus only with committed
synthetic/recorded metadata fixtures for Wayback/Memento traces, Software
Heritage-style source snapshots, SourceForge-style releases, package registry
metadata, manuals/documents, and review/description notes. The broad
Search Usefulness Audit moved from `covered=5`, `partial=22`,
`source_gap=26`, `capability_gap=9`, `unknown=2` to `covered=5`,
`partial=40`, `source_gap=10`, `capability_gap=7`, `unknown=2`, while all
external baselines remain pending/manual. This adds no live probes, external
API calls, URL fetching, scraping, crawling, real binaries, downloads,
installers, uploads, arbitrary local ingestion, local path search, telemetry,
accounts, hosted search, malware-safety claim, rights-clearance claim,
hosted relevance claim, or production readiness claim. The next Codex-safe
milestone is Search Usefulness Delta v2, which is now implemented.

## ADR-113: Measure Source Expansion v2 With an Audit-Only Delta Pack

Status: accepted

Search Usefulness Delta v2 adds
`control/audits/search-usefulness-delta-v2/`,
`scripts/validate_search_usefulness_delta_v2.py`, and focused script and
operations tests. It measures Source Expansion v2 against the committed P32
report, recording baseline/current counts, exact status deltas, selected query
movement, current failure-mode counts, source-family impact, public-search
smoke status, hard-eval status, external-baseline pending status, remaining
gaps, and recommendations.

The decision is to treat the delta as governance evidence only. It adds no new
retrieval behavior, source loaders, live probes, URL fetching, scraping,
crawling, external observations, real binaries, downloads, installers, uploads,
local path search, telemetry, accounts, hosted search, or hosted-readiness
claim. Exact failure-mode deltas are marked unavailable because the pre-P32
failure-mode baseline was not committed as machine-readable JSON. Source Pack
Contract v0, Evidence Pack Contract v0, Index Pack Contract v0, Contribution
Pack Contract v0, and Master Index Review Queue Contract v0 are now
implemented; the next Codex-safe milestone is Source/Evidence/Index Pack Import
Planning v0.

## ADR-114: Define Source Packs Before Import Or Submission

Status: accepted

Source Pack Contract v0 adds `contracts/packs/source_pack.v0.json`,
`docs/reference/SOURCE_PACK_CONTRACT.md`, `docs/reference/PACK_LIFECYCLE.md`,
`examples/source_packs/minimal_recorded_source_pack_v0/`,
`scripts/validate_source_pack.py`, and
`control/audits/source-pack-contract-v0/`.

The decision is to define source packs as portable, validated source metadata
and fixture-evidence bundles before any import, indexing, upload, hosted
submission, or master-index review behavior exists. A source pack may declare
source records, public-safe evidence records, fixture files, rights/access
notes, privacy posture, disabled capabilities, prohibited behavior, and
checksums. Source-pack source records align with Source Registry v0 vocabulary,
but they are not canonical registry entries until a future review/import path
accepts them.

P34 deliberately does not implement source-pack import, indexing, upload,
executable plugin loading, live connectors, live probes, arbitrary URL fetch,
scraping, crawling, downloads, installers, private local path sharing,
master-index acceptance, production signing, rights clearance, malware-safety
claims, or production extension support. Evidence Pack Contract v0, Index Pack
Contract v0, Contribution Pack Contract v0, and Master Index Review Queue
Contract v0 are now implemented; the next Codex-safe milestone is
Source/Evidence/Index Pack Import Planning v0.

## ADR-115: Define Evidence Packs As Claims Before Truth Selection

Status: accepted

Evidence Pack Contract v0 adds `contracts/packs/evidence_pack.v0.json`,
`docs/reference/EVIDENCE_PACK_CONTRACT.md`,
`examples/evidence_packs/minimal_evidence_pack_v0/`,
`scripts/validate_evidence_pack.py`, and
`control/audits/evidence-pack-contract-v0/`.

The decision is to define evidence packs as portable, public-safe claim and
observation bundles before any import, indexing, upload, hosted submission, or
master-index review behavior exists. Evidence records may describe metadata,
compatibility, member paths, versions, checksums, source locators, absence, and
provenance, but they are not canonical truth until a future governed review path
accepts them.

P35 deliberately does not implement evidence-pack import, indexing, upload,
executable plugin loading, live connectors, live probes, arbitrary URL fetch,
scraping, crawling, downloads, installers, private cache sharing,
master-index acceptance, production signing, rights clearance, malware-safety
claims, canonical truth selection, or production extension support. Index Pack
Contract v0, Contribution Pack Contract v0, and Master Index Review Queue
Contract v0 are now implemented; the next Codex-safe milestone is
Source/Evidence/Index Pack Import Planning v0.

## ADR-116: Define Index Packs As Coverage Before Import Or Merge

Status: accepted

Index Pack Contract v0 adds `contracts/packs/index_pack.v0.json`,
`docs/reference/INDEX_PACK_CONTRACT.md`,
`examples/index_packs/minimal_index_pack_v0/`,
`scripts/validate_index_pack.py`, and
`control/audits/index-pack-contract-v0/`.

The decision is to define index packs as portable, public-safe coverage and
record-summary bundles before any import, merge, upload, hosted ingestion, or
master-index review behavior exists. Index packs may describe an index build,
source coverage, field coverage, query examples, and public-safe record
summaries, but they are not raw caches, raw SQLite databases, production search
indexes, or canonical proof.

P36 deliberately does not implement index-pack import, merge, upload, local
cache export, raw SQLite export, executable plugin loading, live connectors,
live probes, arbitrary URL fetch, scraping, crawling, downloads, installers,
private cache sharing, master-index acceptance, production signing, rights
clearance, malware-safety claims, canonical truth selection, hosted ingestion,
or production extension support. Contribution Pack Contract v0 and Master Index
Review Queue Contract v0 are now implemented; the next Codex-safe milestone is
Source/Evidence/Index Pack Import Planning v0.

## ADR-117: Define Contribution Packs As Review Candidates Before Intake

Status: accepted

Contribution Pack Contract v0 adds
`contracts/packs/contribution_pack.v0.json`,
`docs/reference/CONTRIBUTION_PACK_CONTRACT.md`,
`examples/contribution_packs/minimal_contribution_pack_v0/`,
`scripts/validate_contribution_pack.py`, and
`control/audits/contribution-pack-contract-v0/`.

The decision is to define contribution packs as portable, public-safe
review-candidate wrappers before any upload, import, moderation, identity,
account, or master-index review queue behavior exists. Contribution packs may
reference source/evidence/index packs and carry proposed metadata corrections,
alias suggestions, compatibility suggestions, member-path suggestions, absence
reports, pending manual observation placeholders, and result-quality feedback,
but those items are not canonical truth and are not accepted public records.

P37 deliberately does not implement contribution upload, source/evidence/index
pack import, master-index review queue runtime, moderation UI, accounts,
identity, automatic acceptance, executable plugin loading, live connectors,
live probes, arbitrary URL fetch, scraping, crawling, downloads, installers,
private cache sharing, raw SQLite export, master-index acceptance, production
signing, rights clearance, malware-safety claims, canonical truth selection,
hosted ingestion, or production extension support. Master Index Review Queue
Contract v0 is now implemented; the next Codex-safe milestone is
Source/Evidence/Index Pack Import Planning v0.

## ADR-118: Define Master Index Review Queue Governance Before Intake Runtime

Status: accepted

Master Index Review Queue Contract v0 adds
`contracts/master_index/review_queue_manifest.v0.json`,
`contracts/master_index/review_queue_entry.v0.json`,
`contracts/master_index/review_decision.v0.json`,
`control/inventory/master_index/`,
`docs/reference/MASTER_INDEX_REVIEW_QUEUE_CONTRACT.md`,
`docs/architecture/MASTER_INDEX_REVIEW_QUEUE.md`,
`examples/master_index_review_queue/minimal_review_queue_v0/`,
`scripts/validate_master_index_review_queue.py`, and
`control/audits/master-index-review-queue-contract-v0/`.

The decision is to define review-queue governance before any contribution
upload, pack import, moderation UI, account/identity system, hosted master
index, queue runtime, or master-index write path exists. Queue entries are
review candidates, not truth. Review decisions preserve validation state,
privacy, rights, risk, conflict, evidence/provenance, and publication
limitations before a future accepted-public result can be considered.

P38 deliberately does not implement queue runtime, uploads, contribution
import, source/evidence/index pack import, moderation UI, accounts, identity,
hosted master index, master-index writes, automatic acceptance, live
connectors, live probes, arbitrary URL fetch, scraping, crawling, downloads,
installers, private cache sharing, raw SQLite export, production signing,
rights clearance, malware-safety claims, canonical truth selection, hosted
ingestion, or production extension support. The next Codex-safe milestone is
Source/Evidence/Index Pack Import Planning v0.

## ADR-119: Plan Validate-Only Pack Import Before Import Runtime

Status: accepted

Source/Evidence/Index Pack Import Planning v0 adds
`control/audits/pack-import-planning-v0/`,
`docs/reference/PACK_IMPORT_PLANNING.md`,
`docs/architecture/PACK_IMPORT_PIPELINE.md`,
`scripts/validate_pack_import_planning.py`, and focused validator/tests.

The decision is to define future pack import as explicit user-selected
validation before any staging, indexing, public search, or master-index effect
exists. The default future mode is `validate_only`; the next future mode is
`stage_local_quarantine`. Staged records remain claims, candidates, or
summaries, with pack ID/version/checksum and validation reports preserved as
provenance. Pack import is local and separate from master-index review.

P39 deliberately does not implement pack import runtime, source/evidence/index
pack import, contribution pack import, master-index queue import, local
staging directories, arbitrary directory scanning, live fetch, local
search/index mutation, canonical source registry mutation, uploads,
submission, moderation UI, accounts, identity, hosted/master-index mutation,
automatic acceptance, executable plugins, downloads, installers, private cache
sharing, rights clearance, malware-safety claims, canonical truth selection,
or production extension support. The next Codex-safe milestone is Pack Import
Validator Aggregator v0, followed by AI Provider Contract v0.

## ADR-120: Aggregate Pack Validation Before Import Tooling

Status: accepted

Pack Import Validator Aggregator v0 adds `scripts/validate_pack_set.py`,
`control/inventory/packs/example_packs.json`,
`docs/operations/PACK_VALIDATION.md`, focused tests, and
`control/audits/pack-import-validator-aggregator-v0/`.

The decision is to route all known source, evidence, index, contribution, and
master-index review queue examples through one validate-only command before any
import runtime exists. The aggregate command detects pack type by root manifest,
delegates to existing validators, reports passed/failed/unavailable/unknown
type, emits machine-readable JSON, and records all side-effect flags as false.

P40 deliberately does not implement source/evidence/index/contribution import,
master-index queue import, staging/quarantine directories, local index
mutation, canonical registry mutation, upload, submission, moderation UI,
accounts, identity, hosted/master-index mutation, automatic acceptance, live
fetch, external observation collection, executable plugin loading, downloads,
installers, private cache sharing, rights clearance, malware-safety claims,
canonical truth selection, or production extension support. The next
Codex-safe milestone is AI Provider Contract v0; Pack Import Report Format v0
was the next pack-import-specific milestone and is now implemented.

## ADR-121: Define AI Providers Before AI Runtime

Status: accepted

AI Provider Contract v0 adds `contracts/ai/`,
`control/inventory/ai_providers/`,
`examples/ai_providers/disabled_stub_provider_v0/`,
`docs/reference/AI_PROVIDER_CONTRACT.md`,
`docs/reference/TYPED_AI_OUTPUT_CONTRACT.md`,
`docs/architecture/AI_ASSISTANCE_BOUNDARY.md`,
`scripts/validate_ai_provider_contract.py`, focused tests, and
`control/audits/ai-provider-contract-v0/`.

The decision is to define provider manifests, future task requests, and typed
AI output envelopes before any model runtime exists. Providers are disabled by
default. Remote providers require future explicit credentials and approval.
Private data, telemetry, prompt logging, output logging, cache runtime, local
filesystem access, and live source access are disabled by default. AI output is
a suggestion or review candidate, not truth.

P41 deliberately does not implement model calls, OpenAI/Anthropic/Ollama/LM
Studio calls, local model execution, browser AI, provider runtime loading,
API keys, credential storage, prompt logging runtime, telemetry, embeddings,
vector search, LLM reranking, AI extraction runtime, AI in public search,
AI-generated evidence acceptance, local index mutation, uploads, accounts,
hosted/master-index mutation, rights clearance, malware-safety claims,
canonical truth selection, source-trust authority, automatic identity merge,
automatic acceptance, or production AI support. The next Codex-safe milestone
was Typed AI Output Validator v0; Pack Import Report Format v0 was the next
pack-import-specific milestone and is now implemented.

## ADR-122: Validate Typed AI Outputs Before AI-Assisted Workflows

Status: accepted

Typed AI Output Validator v0 adds
`runtime/engine/ai/typed_output_validator.py`,
`scripts/validate_ai_output.py`,
`control/inventory/ai_providers/typed_output_examples.json`,
four disabled-stub typed output examples, `docs/operations/AI_OUTPUT_VALIDATION.md`,
focused tests, and `control/audits/typed-ai-output-validator-v0/`.

The decision is to make typed AI output validation the first reusable safety
gate before any future AI-assisted evidence or contribution workflow. Outputs
must be suggestions/candidates, require review, prohibit canonical truth,
rights clearance, malware safety, and automatic acceptance, preserve provider
provenance, keep generated text bounded, and avoid private-path or secret
leakage.

P42 deliberately does not implement model calls, OpenAI/Anthropic/Ollama/LM
Studio calls, provider runtime loading, API keys, credential storage, prompt
logging runtime, telemetry, embeddings, vector search, AI extraction runtime,
evidence-pack import, contribution-pack import, local index mutation, public
search AI, uploads, accounts, hosted/master-index mutation, rights clearance,
malware-safety claims, canonical truth selection, source-trust authority,
automatic acceptance, or production AI support. Pack Import Report Format v0
and Validate-Only Pack Import Tool v0 are now implemented; the next
recommended milestone is Manual Observation Batch 0 Execution, human-operated.

## ADR-123: Record Pack Validation Outcomes Before Import Tooling

Status: accepted

Pack Import Report Format v0 adds
`contracts/packs/pack_import_report.v0.json`,
`examples/import_reports/`, `scripts/validate_pack_import_report.py`,
`docs/reference/PACK_IMPORT_REPORT_FORMAT.md`, focused tests, and
`control/audits/pack-import-report-format-v0/`.

The decision is to define a durable, local, machine-readable and human-readable
report format between aggregate validation and any future validate-only import
tool. Reports record pack results, issue records, privacy/rights/risk
summaries, provenance, next actions, and hard false mutation-safety fields.
They can represent passed validation, failed validation, private-path blocks,
unknown pack types, unavailable validators, or future-gated actions without
turning validation into import or acceptance.

P43 deliberately does not implement pack import runtime, staging/quarantine
directories, source/evidence/index/contribution pack import, master-index queue
import, local index mutation, runtime source registry mutation, public-search
mutation, upload, submission, moderation UI, accounts, identity, hosted/master
index mutation, model calls, API keys, live fetch, external observation
collection, executable plugin loading, downloads, installers, private cache
sharing, rights clearance, malware-safety claims, canonical truth selection,
or production support. Validate-Only Pack Import Tool v0 is now implemented as
the next validate-only step; the next recommended milestone is Manual
Observation Batch 0 Execution, human-operated, with Local Quarantine/Staging
Model v0 as the Codex-safe planning-only alternative.

## ADR-124: Emit Pack Import Reports From Validate-Only Preflight

Status: accepted

Validate-Only Pack Import Tool v0 adds `scripts/validate_only_pack_import.py`,
`docs/operations/VALIDATE_ONLY_PACK_IMPORT.md`, focused tests, and
`control/audits/validate-only-pack-import-tool-v0/`.

The decision is to make explicit-root/all-examples validation the first
pack-import-related tool. The tool delegates to existing pack validators,
optionally includes typed AI output examples when requested, and emits Pack
Import Report v0 so users and maintainers can review validation status before
any future staging, quarantine, local indexing, contribution submission, or
master-index review path.

P44 deliberately does not implement pack import runtime, staging/quarantine
directories, source/evidence/index/contribution pack import, master-index queue
import, local index mutation, runtime source registry mutation, public-search
mutation, upload, submission, moderation UI, accounts, identity, hosted/master
index mutation, model calls, API keys, live fetch, external observation
collection, executable plugin loading, downloads, installers, private cache
sharing, rights clearance, malware-safety claims, canonical truth selection,
or production support. Local Quarantine/Staging Model v0 is now implemented as
the follow-up planning layer, and the next Codex-safe milestone is Staging
Report Path Contract v0. Manual Observation Batch 0 Execution remains
human-operated parallel work.

## ADR-125: Model Local Staging Before Creating Local State

Status: accepted

Local Quarantine/Staging Model v0 adds
`control/inventory/local_state/`,
`docs/architecture/LOCAL_QUARANTINE_STAGING_MODEL.md`,
`docs/reference/LOCAL_STAGING_PATH_POLICY.md`,
`scripts/validate_local_quarantine_staging_model.py`, focused tests, and
`control/audits/local-quarantine-staging-model-v0/`.

The decision is to define future local quarantine/staging before any staging
runtime writes local state. The model keeps future staged metadata
`local_private` by default, links it to Pack Import Report v0 provenance,
forbids public/generated/runtime/control/docs/example roots, requires
reset/delete/export semantics, and keeps search, local indexes, hosted public
search, relay, snapshots, and the master index unaffected by default.

P45 deliberately does not implement staging runtime, create `.eureka-local/`
or staged state, copy pack files, import source/evidence/index/contribution
packs, import master-index queue entries, mutate local indexes, mutate runtime
source registry state, mutate public search, upload, submit, add moderation
UI, add accounts or identity, call models, add API keys, call networks, load
executable plugins, add live connectors, add native clients, add relay runtime,
add snapshot reader runtime, claim rights clearance, claim malware safety,
claim canonical truth, or mutate the master index. The next Codex-safe
milestone is Staging Report Path Contract v0; Local Staging Manifest Format v0
is the alternative, while Manual Observation Batch 0 Execution remains
human-operated parallel work.

## ADR-126: Define Report Paths Before Local Staging Manifests

Status: accepted

Staging Report Path Contract v0 adds
`control/inventory/local_state/staging_report_path_contract.json`,
`docs/reference/STAGING_REPORT_PATH_CONTRACT.md`,
`docs/operations/LOCAL_REPORT_PATHS.md`,
`scripts/validate_staging_report_path_contract.py`, focused tests,
`.eureka-reports/` ignore protection, validate-only output-root enforcement,
and `control/audits/staging-report-path-contract-v0/`.

The decision is to make report output stdout by default, require explicit
output paths for file writes, reject forbidden public/runtime/canonical repo
roots, define future ignored local-private report roots, and require redaction
of private local paths before reports can be committed, published, projected by
relay, included in snapshots, or used for contribution/master-index review.

P46 deliberately does not implement report path runtime, staging runtime,
staged state, source/evidence/index/contribution pack import, master-index
queue import, local index mutation, runtime source registry mutation,
public-search mutation, upload, submission, moderation UI, accounts, identity,
model calls, API keys, live fetch, executable plugin loading, downloads,
installers, native clients, relay runtime, snapshot reader runtime, rights
clearance, malware-safety claims, canonical truth selection, or production
support. The next Codex-safe milestone is Local Staging Manifest Format v0;
Staged Pack Inspector v0 follows.

## ADR-127: Define Local Staging Manifest Envelopes Before Staged Inspection

Status: accepted

Local Staging Manifest Format v0 adds
`contracts/packs/local_staging_manifest.v0.json`,
`examples/local_staging_manifests/minimal_local_staging_manifest_v0/`,
`docs/reference/LOCAL_STAGING_MANIFEST_FORMAT.md`,
`scripts/validate_local_staging_manifest.py`, focused tests, local-state
inventory references, and `control/audits/local-staging-manifest-format-v0/`.

The decision is to define the future local/private manifest envelope before
any staged inspector or local staging runtime exists. The manifest records the
reviewed validate-only report reference, staged pack references, staged entity
candidates, counts, privacy/rights/risk posture, provenance, hard no-mutation
guarantees, and future reset/delete/export policy. Staged records remain
candidates and diagnostics, not canonical truth or accepted public state.

P47 deliberately does not implement staging runtime, create `.eureka-local/`
state, create staged state, copy pack files, import source/evidence/index/
contribution packs, import master-index queue entries, implement a staged pack
inspector runtime, mutate local indexes, mutate runtime source registry state,
mutate public search, upload, submit, add moderation UI, add accounts or
identity, call models, add API keys, call networks, load executable plugins,
add live connectors, add native clients, add relay runtime, add snapshot reader
runtime, claim rights clearance, claim malware safety, claim canonical truth,
or mutate the master index. The next Codex-safe milestone is Staged Pack
Inspector v0; Manual Observation Batch 0 Execution remains human-operated
parallel work.

## ADR-128: Inspect Staged Manifests Read-Only Before Staging Tooling

Status: accepted

Staged Pack Inspector v0 adds `scripts/inspect_staged_pack.py`,
`scripts/validate_staged_pack_inspector.py`,
`docs/operations/STAGED_PACK_INSPECTION.md`, focused tests, local-state
inventory references, and `control/audits/staged-pack-inspector-v0/`.

The decision is to add a read-only inspector before any future local
quarantine/staging tool writes state. The inspector reads explicit Local
Staging Manifest v0 files, explicit manifest roots, or committed synthetic
examples; validates manifests before inspection by default; emits human and
JSON summaries; redacts obvious private paths and secret-like fields; and
keeps staged source/evidence/index/contribution/AI entities as candidates, not
canonical records or accepted public state.

P48 deliberately does not implement staging runtime, create `.eureka-local/`
state, create staged state, copy pack files, import source/evidence/index/
contribution packs, import master-index queue entries, implement a local
staging tool, mutate local indexes, mutate runtime source registry state,
mutate public search, upload, submit, add moderation UI, add accounts or
identity, call models, add API keys, call networks, load executable plugins,
add live connectors, add native clients, add relay runtime, add snapshot reader
runtime, claim rights clearance, claim malware safety, claim canonical truth,
or mutate the master index. The immediate next milestone is Manual Observation
Batch 0 Execution, human-operated; AI-Assisted Evidence Drafting Plan v0 is the
Codex-safe alternative.

## ADR-129: Plan AI Drafting as Candidate Generation, Not Truth

Status: accepted

AI-Assisted Evidence Drafting Plan v0 adds
`control/inventory/ai_providers/ai_assisted_drafting_policy.json`,
`docs/architecture/AI_ASSISTED_EVIDENCE_DRAFTING.md`,
`docs/reference/AI_ASSISTED_DRAFTING_CONTRACT.md`,
`examples/ai_assisted_drafting/minimal_drafting_flow_v0/`,
`scripts/validate_ai_assisted_drafting_plan.py`, focused tests, and
`control/audits/ai-assisted-evidence-drafting-plan-v0/`.

The decision is to define optional future AI evidence drafting before any AI
runtime exists. AI may assist with drafting alias, metadata, compatibility,
review-description, member-path, source-match, identity-match, explanation,
absence, evidence-record, or contribution-item candidates only after explicit
future task requests, typed output validation, provenance references where
possible, and required review. AI output is candidate text or structured
candidate data, not truth, rights clearance, malware safety, source trust,
search ranking authority, local-index authority, or master-index acceptance.

P49 deliberately does not implement AI provider runtime, call models, call
remote or local model servers, add API keys, store credentials, add telemetry,
log prompts at runtime, implement embeddings, vector search, LLM reranking, AI
extraction runtime, evidence import, contribution import, public-search
mutation, local-index mutation, runtime source registry mutation, master-index
mutation, live source probes, external API calls, web scraping, downloads,
installers, native clients, relay runtime, snapshot reader runtime, rights
clearance claims, malware-safety claims, canonical truth claims, or production
AI support. The immediate next milestone is Manual Observation Batch 0
Execution, human-operated; Public Hosted Search Rehearsal Plan v0 is the
Codex-safe alternative.

## ADR-130: Audit Post-P49 State Before Query Learning Or Hosted Search

Status: accepted

Post-P49 Platform Audit v0 adds
`control/audits/post-p49-platform-audit-v0/`,
`scripts/validate_post_p49_platform_audit.py`, focused tests, and operating
metadata entries.

The decision is to treat P50 as an audit/consolidation checkpoint rather than
a feature milestone. The audit classifies current repo state after the public
search, source expansion, pack contract, staging, and AI planning queue. It
keeps Python as the reference/oracle backend, `site/dist` as the active static
artifact, public search as local/prototype only, pack import/staging as
validate-only/planning/read-only, and AI as candidate-only planning/validation.

P50 deliberately does not implement hosted public search, live connectors, live
source probes, query-learning runtime, shared query cache, miss ledger, probe
queue, candidate index, pack import runtime, local staging runtime, AI runtime,
model calls, credentials, telemetry, accounts, uploads, downloads, installers,
native GUI, relay runtime, Rust runtime replacement, public contribution
intake, public-search mutation, local-index mutation, runtime-index mutation,
master-index mutation, external API calls, scraping, or deployment changes.
The next branch is `p51-post-p50-remediation-pack-v0`.

## ADR-131: Remediate P50 Drift Without Expanding Product Behavior

Status: accepted

Post-P50 Remediation Pack v0 adds minimal root governance placeholders,
license-selection guidance, pack-validator CLI alignment, GitHub Pages
operator-evidence guidance, a remediation audit pack, and validator/test
coverage for that audit.

The decision is to fix bounded P50 drift without turning any contract,
prototype, fixture, or planning surface into product behavior. Individual pack
validators may accept `--all-examples` and `--known-examples` as registry-backed
validation aliases, but validation still does not import, stage, index, upload,
mutate runtime state, mutate public search, or accept master-index records.

P51 deliberately does not select a license, add hosted backend behavior, enable
GitHub Pages settings, fabricate deployment evidence, add live probes, add
live source connectors, call external APIs, scrape, add AI runtime, add model
calls, add credentials, add telemetry, add accounts, add uploads, add
downloads, add installers, stage real packs, import packs, mutate local or
runtime indexes, mutate the master index, wire Rust into runtime, or claim
production readiness. The next branch is
`p52-static-deployment-evidence-github-pages-repair-v0` unless Pages deployment
evidence is separately verified first.

## ADR-132: Treat Static Deployment Evidence As Evidence, Not Hosting

Status: accepted

Static Deployment Evidence / GitHub Pages Repair v0 adds
`control/audits/static-deployment-evidence-v0/`,
`scripts/validate_static_deployment_evidence.py`, focused tests, and metadata
updates.

The decision is to verify and record the static GitHub Pages path without
inventing deployment state. The Pages workflow is already configured for
`site/dist`, local static artifact validation passes, and the static artifact
checker accepts the current artifact. `gh` is unavailable in this environment,
so current-head Actions and Pages API evidence are unverified. Prior committed
evidence still records a Pages configuration failure before artifact upload and
no deployment URL.

P52 deliberately does not add hosted backend behavior, public search hosting,
live probes, source connectors, external source calls, scraping, model calls,
AI runtime, credentials, telemetry, accounts, uploads, downloads, installers,
deployment provider config, custom-domain setup, index mutation, master-index
mutation, or production readiness claims. The next Codex-safe branch is
`p53-public-search-production-contract-v0`; GitHub Pages settings enablement
and deployment evidence capture remain operator-parallel work.

## ADR-133: Freeze Public Search Contract Before Hosting

Status: accepted

Public Search Production Contract v0 adds
`control/audits/public-search-production-contract-v0/`,
production-facing public-search schemas under `contracts/api/`, reference docs,
`scripts/validate_public_search_production_contract.py`, focused tests, and
operating metadata updates.

The decision is to define the contract that P54 must implement before a hosted
wrapper exists. The active mode remains `local_index_only`; v0 search is
GET-compatible; query length is capped at 160; default/max result limits are
10/25; errors are public-safe; and result-card, source-status,
evidence-summary, absence, and status schemas align with the existing local
prototype runtime and static handoff.

P53 deliberately does not add hosted backend behavior, deployment provider
config, live probes, source connectors, external source calls, scraping, model
calls, AI runtime, credentials, telemetry runtime, accounts, uploads,
downloads, installers, arbitrary URL fetching, local path access, index
mutation, master-index mutation, or a hosted-search claim. The next Codex-safe
branch is `p54-hosted-public-search-wrapper-v0`; GitHub Pages settings
enablement and deployment evidence capture remain operator-parallel work.

## ADR-134: Add Hosted Public Search Wrapper Without Deploying It

Status: accepted

Hosted Public Search Wrapper v0 adds `scripts/run_hosted_public_search.py`,
`scripts/check_hosted_public_search_wrapper.py`,
`scripts/validate_hosted_public_search_wrapper.py`, focused tests, hosted
operation docs, inert Docker/Render templates, inventory updates, and
`control/audits/hosted-public-search-wrapper-v0/`.

The decision is to implement the P53 route contract as a narrow stdlib wrapper
over the existing gateway public search API while keeping the active mode
`local_index_only`. The wrapper exposes `/healthz`, `/status`, `/search`,
`/api/v1/status`, `/api/v1/search`, `/api/v1/query-plan`, `/api/v1/sources`,
and `/api/v1/source/{source_id}` for local rehearsal and later operator
deployment. It rejects forbidden public parameters and records disabled flags
for live probes, downloads, uploads, install actions, local paths, arbitrary URL
fetch, accounts, telemetry, external calls, and AI runtime.

P54 deliberately does not deploy a backend, call hosting provider APIs, configure
DNS/TLS, add credentials, enable live probes, add source connector runtime,
mutate indexes, import packs, stage packs, add telemetry/accounts/uploads/
downloads/installers, add model calls, or claim hosted availability. The next
Codex-safe branch is `p55-public-search-index-builder-v0`; operator-parallel
work is deploying the wrapper and recording hosted evidence.

## ADR-135: Generate Public Search Index From Controlled Corpus

Status: accepted

Public Search Index Builder v0 adds `scripts/build_public_search_index.py`,
`scripts/validate_public_search_index.py`,
`scripts/validate_public_search_index_builder.py`, generated
`data/public_index` artifacts, runtime integration, docs, tests, drift
metadata, and `control/audits/public-search-index-builder-v0/`.

The decision is to add a deterministic committed public search index bundle and
make the local/prototype public-search path prefer it over the older in-memory
demo catalog. The P54 hosted wrapper now has a controlled public-safe corpus
for local rehearsal and future operator deployment. The generated bundle is
built from governed source inventory plus committed fixture/recorded metadata
only, validates with drift checks, and records source coverage plus checksums.

The committed artifact is JSON/NDJSON plus manifests rather than a SQLite
binary. SQLite and FTS5 availability are recorded as optional local
capabilities, while deterministic lexical fallback remains the runtime
baseline.

P55 deliberately does not add live source calls, scraping, arbitrary URL
fetching, private local ingestion, executable payloads, downloads, uploads,
telemetry, AI runtime, pack import, staging runtime, local/runtime/master-index
mutation, hosted deployment, or production search-quality claims. The next
Codex-safe branch is `p56-static-site-search-integration-v0`.

## ADR-136: Keep Static Search Handoff Honest Until Backend Evidence Exists

Status: accepted

Static Site Search Integration v0 adds
`control/inventory/publication/static_search_config.json`, generated
`site/dist/search.html`, `site/dist/lite/search.html`,
`site/dist/text/search.txt`, `site/dist/files/search.README.txt`,
`site/dist/data/search_config.json`,
`site/dist/data/public_index_summary.json`,
`docs/operations/STATIC_SITE_SEARCH_INTEGRATION.md`,
`scripts/validate_static_site_search_integration.py`, focused tests, generated
artifact metadata, and `control/audits/static-site-search-integration-v0/`.

The decision is to make the static site a no-JS front door for search without
claiming hosted search. The default status is `backend_unconfigured`; hosted
form submission stays disabled; local wrapper instructions and public index
summary data are visible; and a real backend URL may be enabled only after
operator evidence records the URL, commit, environment, and route checks.

P56 deliberately does not deploy a backend, call hosting provider APIs,
configure DNS, hardcode a fake hosted URL, enable live probes, call external
source APIs, scrape, add source connector runtime, add model calls or AI
runtime, add credentials, telemetry, accounts, uploads, downloads, installers,
arbitrary URL fetching, local path access, local/runtime/master-index mutation,
pack import, staging runtime, or production search-quality claims. The next
Codex-safe branch is `p57-public-search-safety-evidence-v0`; operator-parallel
work remains deploying and verifying the hosted wrapper plus static deployment
evidence capture.

## ADR-137: Record Public Search Safety Evidence Before Hosted Rehearsal

Status: accepted

Public Search Safety Evidence v0 adds
`scripts/run_public_search_safety_evidence.py`,
`scripts/validate_public_search_safety_evidence.py`, focused tests,
`docs/operations/PUBLIC_SEARCH_SAFETY_EVIDENCE.md`, metadata updates, and
`control/audits/public-search-safety-evidence-v0/`.

The decision is to require executable local evidence before hosted rehearsal.
The evidence runner uses the P54 hosted wrapper in-process and checks safe
queries, 32 blocked dangerous request cases, limits, status endpoints, static
handoff safety, public index safety, hosted-wrapper safety, privacy/redaction,
and operator-gated rate-limit/edge status.

P57 deliberately does not deploy a backend, call hosting provider APIs,
configure DNS, enable live probes, call external source APIs, scrape, add
source connector runtime, add model calls or AI runtime, add credentials,
telemetry, accounts, uploads, downloads, installers, arbitrary URL fetching,
local path access, local/runtime/master-index mutation, pack import, staging
runtime, edge rate-limit claims, hosted availability claims, or production
safety claims. The next Codex-safe branch is
`p58-hosted-public-search-rehearsal-v0`.
## ADR-138: Hosted Public Search Rehearsal Is Local Evidence Only

Date: 2026-05-02

Decision: P58 may start `scripts/run_hosted_public_search.py` on localhost and
exercise public search routes over HTTP, but it must not claim hosted
deployment, production readiness, edge rate limits, or a public backend URL.

Rationale: local hosted-mode rehearsal is useful evidence before operator
deployment, while static Pages and public-search claims must remain honest until
real deployment evidence exists.

Consequences: the next Codex-safe branch is P59 Query Observation Contract v0.
Operator deployment, backend URL configuration, DNS/TLS, edge/rate limits, and
hosted evidence capture remain separate work.


## P59 Query Observation Decision

Decision: query observation is contract-only in P59. Raw query retention defaults to none, individual observations are not public by default, and no telemetry, runtime persistence, public query logging, result-cache mutation, miss-ledger mutation, probe enqueueing, candidate-index mutation, local-index mutation, or master-index mutation is implemented.

## P60 Shared Query/Result Cache Decision

Decision: shared query/result cache is contract-only in P60. Cache entries
summarize public-safe result and scoped absence outcomes against an index
snapshot, but no runtime cache writes, persistent cache storage, telemetry,
public query logging, miss-ledger mutation, search-need mutation, probe
enqueueing, candidate-index mutation, local-index mutation, or master-index
mutation is implemented.

## P61 Search Miss Ledger Decision

Decision: search miss ledger is contract-only in P61. Miss entries summarize
failed, weak, ambiguous, blocked, or incomplete searches with checked scope,
not-checked scope, cause taxonomy, weak-hit/near-miss summaries, scoped
absence, and future-only next steps, but no runtime ledger writes, persistent
ledger storage, telemetry, public query logging, search need creation, probe
enqueueing, result-cache mutation, candidate-index mutation, local-index
mutation, or master-index mutation is implemented.

## P62 Search Need Record Decision

Decision: search need records are contract-only in P62. Need records summarize
scoped unresolved needs with public-safe fingerprints, target objects, input
refs, gap models, future-only next steps, and no-mutation guarantees. P62 adds
no runtime need storage, telemetry, public query logging, demand-count runtime,
probe enqueueing, candidate-index mutation, result-cache mutation,
miss-ledger mutation, local-index mutation, or master-index mutation.

## P63 Probe Queue Decision

Decision: probe queue items are contract-only in P63. Queue items summarize
future work requests with public-safe fingerprints, probe kind taxonomy, source
policy, approval gates, expected outputs, safety requirements, and
no-execution/no-mutation guarantees. P63 adds no runtime queue, persistent
queue, probe execution, live source calls, source cache mutation, evidence
ledger mutation, candidate-index mutation, local-index mutation, or
master-index mutation.

## P64 Candidate Index Decision

Decision: candidate index records are contract-only in P64. Candidate records
summarize provisional object, evidence, compatibility, absence, conflict,
source, identity, extraction, and query-interpretation candidates with
public-safe fingerprints, provenance refs, confidence-not-truth, review gates,
conflict preservation, source/evidence/rights policy, visibility policy, and
no-truth/no-mutation guarantees. P64 adds no runtime candidate index, persistent
candidate store, public search candidate injection, candidate promotion
runtime, source cache mutation, evidence ledger mutation, local-index mutation,
or master-index mutation.

## P65 Decision

P65 adds Candidate Promotion Policy v0 as contract-only governance. Candidate promotion policy is not promotion runtime; candidate confidence is not truth; automatic promotion is forbidden; destructive merge is forbidden; future promotion assessment requires evidence, provenance, source policy, privacy, rights, risk, conflict, human, policy, and operator gates. No candidate, source, evidence, public index, local index, or master-index state is mutated.

## P66 Known Absence Page v0

Known Absence Page v0 is contract-only. It defines scoped absence, not global absence, for future no-result explanations with checked/not-checked scope, near misses, weak hits, gap explanations, safe next actions, privacy redaction, and no download/install/upload/live fetch. Known absence page is not a runtime page yet, not evidence acceptance, not candidate promotion, not master-index mutation, and not telemetry.

<!-- P67-QUERY-PRIVACY-AND-POISONING-GUARD-START -->
## P67 Query Privacy and Poisoning Guard

Decision: P67 defines query privacy and poisoning guard as contract-only governance. Guard approval is not truth, source trust, candidate promotion, rights clearance, malware safety, or production abuse protection. Automatic acceptance and mutation are forbidden.
<!-- P67-QUERY-PRIVACY-AND-POISONING-GUARD-END -->

## P68 Decision

Demand summaries are prioritization hints only. P68 examples are synthetic, privacy-filtered by policy, poisoning-aware, and not evidence of real public demand.

## P69 Decision

Source sync jobs are future bounded planning records only. They must be approval-gated, cache-first, evidence-attributed, rate-limited, timeout-bounded, and circuit-breaker protected before any live source access.

## P70 Source Cache And Evidence Ledger Decision

Source cache records are source observations, and evidence ledger records are evidence observations. Neither is accepted truth or master-index mutation by default.

<!-- P71-INTERNET-ARCHIVE-METADATA-CONNECTOR-APPROVAL-START -->
## P71 Internet Archive Metadata Connector Approval

`docs/reference/INTERNET_ARCHIVE_METADATA_CONNECTOR_APPROVAL.md` defines an approval-only, metadata-only future Internet Archive connector pack. It is not runtime, makes no external calls, enables no public-query fanout, performs no downloads/file retrieval/mirroring, and mutates no source cache, evidence ledger, candidate index, public/local/master index, telemetry, or credentials. Future work is blocked on official source policy review, User-Agent/contact policy, rate limits, timeouts, retry/backoff, circuit breakers, cache-first source cache output, and evidence ledger attribution.

This cross-reference keeps `docs/DECISIONS.md` aligned with the source-ingestion boundary: IA metadata may become future reviewed cache/evidence input, never direct truth or live public search fanout.
<!-- P71-INTERNET-ARCHIVE-METADATA-CONNECTOR-APPROVAL-END -->

## P72 Wayback/CDX/Memento Connector Approval Pack v0

Completed as an approval-only contract pack. It adds no Wayback/CDX/Memento connector runtime, no external calls, no archived content fetch, no capture replay, no WARC download, no public-query fanout, no telemetry, no credentials, and no source cache/evidence ledger/candidate/index mutation. Next recommended branch: P73 GitHub Releases Connector Approval Pack v0.

<!-- P73-GITHUB-RELEASES-SUMMARY-START -->
## P73 GitHub Releases Connector Approval Pack v0

Completed as an approval-only release metadata connector pack. It adds no live GitHub connector runtime, no external calls, no GitHub API calls, no repository clone, no release fetch, no release asset download, no source archive download, no public-query fanout, no telemetry, no credentials or tokens, and no source cache/evidence ledger/candidate/index mutation. Next recommended branch: P74 PyPI Metadata Connector Approval Pack v0.
<!-- P73-GITHUB-RELEASES-SUMMARY-END -->

<!-- P74-PYPI-METADATA-SUMMARY-START -->
## P74 PyPI Metadata Connector Approval Pack v0

Completed as an approval-only package metadata connector pack. It adds no live PyPI connector runtime, no external calls, no PyPI API calls, no package metadata fetch, no release fetch, no wheel download, no sdist download, no package file download, no package install, no dependency resolution, no package archive inspection, no public-query fanout, no telemetry, no credentials or tokens, and no source cache/evidence ledger/candidate/index mutation. Next recommended branch: P75 npm Metadata Connector Approval Pack v0.
<!-- P74-PYPI-METADATA-SUMMARY-END -->

<!-- P75-NPM-METADATA-SUMMARY-START -->
## P75 npm Metadata Connector Approval Pack v0

Completed as an approval-only package metadata connector pack. It adds no live npm connector runtime, no external calls, no npm registry API calls, no npm/yarn/pnpm CLI calls, no package metadata fetch, no version fetch, no dist-tag fetch, no tarball metadata fetch, no tarball download, no package file download, no package install, no dependency resolution, no package archive inspection, no lifecycle script execution, no npm audit, no public-query fanout, no telemetry, no credentials or tokens, and no source cache/evidence ledger/candidate/index mutation. It requires package identity review, scoped package review, dependency metadata caution, lifecycle script risk policy, source policy review, User-Agent/contact decisions, and cache-first evidence outputs. Next recommended branch: P76 Software Heritage Connector Approval Pack v0.
<!-- P75-NPM-METADATA-SUMMARY-END -->

<!-- P76-SOFTWARE-HERITAGE-SUMMARY-START -->
## P76 Software Heritage Connector Approval Pack v0

Completed as an approval-only software identity/archive metadata connector pack. It adds no live Software Heritage connector runtime, no external calls, no Software Heritage API calls, no SWHID resolution, no origin/visit/snapshot/release/revision/directory/content lookup, no source code download, no repository clone, no source archive download, no source file retrieval, no public-query fanout, no telemetry, no credentials or tokens, and no source cache/evidence ledger/candidate/index mutation. It requires SWHID/origin/repository identity review, source-code-content risk policy, source policy review, User-Agent/contact decisions, and cache-first evidence outputs. Next recommended branch: P77 Public Hosted Deployment Evidence v0.
<!-- P76-SOFTWARE-HERITAGE-SUMMARY-END -->

## P77 Decision

Configured URL evidence is required before public claims. P77 does not invent URLs: the repo-configured GitHub Pages URL currently fails required static checks, and no hosted backend URL exists.

<!-- P78-EXTERNAL-BASELINE-COMPARISON-START -->
## P78 External Baseline Comparison Report v0

P78 added local-only comparison readiness for manual external baselines. Current eligibility is `no_observations`: Batch 0 has 0 observed records and 39 pending slots. No web calls, source API calls, model calls, fabricated observations, fabricated comparisons, production readiness claim, or index/cache/ledger/candidate/master-index mutation were made. Codex-safe next branch is P79 Object Page Contract v0 while Manual Observation Batch 0 remains human-operated.
<!-- P78-EXTERNAL-BASELINE-COMPARISON-END -->

<!-- P79-OBJECT-PAGE-CONTRACT-START -->
## P79 Object Page Contract v0

Object Page Contract v0 is contract-only and evidence-first. It defines future public object pages that preserve provisional identity, source/evidence/provenance, compatibility, conflicts, scoped absence, and gaps without implementing runtime object pages.

Boundary notes:

- No runtime object routes, database, persistent object-page store, source connector runtime, source cache runtime, evidence ledger runtime, candidate promotion, public-index mutation, local-index mutation, master-index mutation, live source fanout, downloads, installs, execution, uploads, telemetry, accounts, rights clearance, or malware safety claim are added.
- Public search may reference object page links only after a future governed integration; P79 does not mutate public search result cards or the public index.
- Object pages are not app-store, downloader, installer, or execution surfaces.
<!-- P79-OBJECT-PAGE-CONTRACT-END -->

<!-- P80-SOURCE-PAGE-CONTRACT-START -->
## P80 Source Page Contract v0

Source Page Contract v0 is contract-only and evidence-first. It defines future public source pages for source identity, status, coverage, connector posture, source policy gates, source cache/evidence posture, public search projection, query-intelligence projection, limitations, provenance caution, and rights/risk posture.

Boundary notes:

- No runtime source routes, database, persistent source-page store, connector runtime, source sync runtime, source cache runtime, evidence ledger runtime, candidate promotion, public-index mutation, local-index mutation, master-index mutation, live source fanout, downloads, mirrors, installs, execution, uploads, telemetry, accounts, rights clearance, malware safety claim, or authoritative source trust claim are added.
- Public search may reference source page links or source badges only after a future governed integration; P80 does not mutate public search result cards or the public index.
- Source pages explain source posture and limitations; they are not source API proxies, scrapers, crawlers, download pages, mirrors, or connector health dashboards.
<!-- P80-SOURCE-PAGE-CONTRACT-END -->
