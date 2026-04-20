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
