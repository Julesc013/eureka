# Architecture

Eureka is organized as one product monorepo with four primary product-facing
partitions:

- `control/`: repo governance, inventories, matrices, research, and packaging planning
- `contracts/`: governed schemas, protocols, public APIs, and shared UI contracts
- `runtime/`: engine, gateway, and connector implementation space
- `surfaces/`: web and native user-facing surfaces

## AIDE Versus Eureka

`.aide/` is a pinned repo operating layer. It exists to describe repo identity, governed components, owned paths, dependency rules, commands, eval groupings, and compatibility metadata for the repo contract.

`.aide/` is not allowed to define product semantics or runtime behavior. Eureka product meaning lives in governed contracts and in future runtime implementations, not in AIDE metadata.

## Governed Components

The current governed component set is intentionally small:

1. `archive-contracts`
2. `engine`
3. `gateway`
4. `workbench-web`
5. `app-native`
6. `connectors`

`contracts/ui` is a shared surface-contract area jointly used by web and native surfaces, but it is not treated as a seventh governed component.

## Dependency Law

The current dependency policy is now expressed as concrete path globs in `.aide/policies/dependencies.yaml`. It is specific enough for future mechanical enforcement, but it is still advisory today.

Allowed:

- `surfaces/web/**` depends on `contracts/archive/**`, `contracts/gateway/public_api/**`, and `contracts/ui/**` in the normal path
- `surfaces/native/**` depends on `contracts/archive/**`, `contracts/gateway/public_api/**`, and `contracts/ui/**` in the normal path
- `surfaces/native/**` may depend on `runtime/engine/sdk/**` only as a future explicitly bounded offline path
- `runtime/gateway/**` depends on `runtime/engine/interfaces/public/**`, `runtime/engine/interfaces/service/**`, `contracts/archive/**`, and `contracts/gateway/public_api/**`
- `runtime/connectors/**` depends on `runtime/engine/interfaces/ingest/**`, `runtime/engine/interfaces/extract/**`, `runtime/engine/interfaces/normalize/**`, and `contracts/archive/**`

Forbidden:

- `runtime/engine/**` depends on `surfaces/*`
- `surfaces/web/**` depends on `runtime/engine` internals in the normal path
- `runtime/connectors/**` defines its own object model
- `runtime/connectors/**` owns trust semantics
- `.aide/` defines product semantics or runtime behavior

## Accepted Architecture Docs

Detailed product-architecture direction now lives under `docs/architecture/`:

- [Temporal Object Resolver](architecture/TEMPORAL_OBJECT_RESOLVER.md)
- [Logical Graphs](architecture/LOGICAL_GRAPHS.md)
- [Physical Subsystems](architecture/PHYSICAL_SUBSYSTEMS.md)
- [Data Model](architecture/DATA_MODEL.md)
- [Source Strategy](architecture/SOURCE_STRATEGY.md)
- [Query Planner](architecture/QUERY_PLANNER.md)
- [Resolution Memory](architecture/RESOLUTION_MEMORY.md)
- [Streaming Runs](architecture/STREAMING_RUNS.md)
- [Action Router](architecture/ACTION_ROUTER.md)
- [AI Policy](architecture/AI_POLICY.md)

These documents describe accepted architecture direction and staging. They do
not imply that every subsystem is already implemented in the current repo.

## Related Standards

The supporting standards and policy guidance for the architecture live under
`docs/standards/`:

- [Source Registry Schema](standards/SOURCE_REGISTRY_SCHEMA.md)
- [Identifier Policy](standards/IDENTIFIER_POLICY.md)
- [Privacy And Shared Evidence](standards/PRIVACY_AND_SHARED_EVIDENCE.md)

## Current Unresolved Questions

- What becomes the minimum normative object identity boundary for bundled or multi-file software artifacts?
- Which archive trust semantics should be first-class in `contracts/archive/trust`, and which remain policy overlays?
- How narrow should the future offline native path be before `runtime/engine/sdk` is exposed?
- Which gateway operations should be public product contracts versus internal broker or worker protocols?
- What packaging forms matter in v1 beyond software archives and repositories?

## Related Research

- See [control/research/temporal-object-resolution-engine.md](../control/research/temporal-object-resolution-engine.md) for a research-only candidate next operating layer that informed the accepted doctrine and architecture docs without being silently promoted wholesale into runtime claims.
