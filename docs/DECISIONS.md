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
