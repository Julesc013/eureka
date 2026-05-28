# Architecture

Eureka is organized as a governed monorepo with explicit boundaries between
control-plane governance, contract authority, Python reference runtime, and
user-facing surfaces.

## Current Product Shape

The current executable product shape is:

- local-first Python reference backend
- local operator Workbench
- read-only public-alpha routes backed by reviewed snapshots
- governed source action and metadata source-family foundations
- focused validators and audit packs

It is not a deployed service, public launch, production platform, native app, or
marketplace/action manager.

## Primary Partitions

- `control/`: governance, inventories, audits, policies, and evidence.
- `contracts/`: governed schemas, protocols, packets, public APIs, and shared
  UI contracts.
- `runtime/`: Python reference runtime for engine, gateway, connectors, stores,
  local service, review, source, evidence, index, and worker families.
- `surfaces/`: user-facing projections over gateway/contracts.
- `site/`: static site source plus generated static artifacts.
- `snapshots/`: read-only snapshot schemas and examples.
- `native/`: native client skeleton/planning lane.
- `crates/`: Rust parity and future migration lane.

## Dependency Law

Allowed normal-path dependencies:

- Web surfaces use gateway public APIs and contracts.
- Native surfaces use contracts and gateway public APIs.
- Native may use `runtime/engine/sdk` only if an explicit offline/local mode is
  adopted later.
- Gateway may depend on `runtime/engine/interfaces/public/**`,
  `runtime/engine/interfaces/service/**`, and governed contract paths.
- Connectors may depend on `runtime/engine/interfaces/ingest/**`,
  `runtime/engine/interfaces/extract/**`,
  `runtime/engine/interfaces/normalize/**`, and governed archive contract
  paths.

Forbidden dependencies:

- Engine must not depend on `surfaces/*`.
- Web must not depend on engine internals in the normal path.
- Connectors must not invent object truth.
- Connectors must not own trust semantics.
- `.aide/` must not define product semantics or runtime behavior.

Run:

```powershell
python scripts/check_architecture_boundaries.py
```

## AIDE Versus Eureka

`.aide/` is repo-operating metadata for compact task packets, queues, reports,
and coordination. It is not product truth. Product truth lives in accepted
contracts, runtime behavior, reviewed records, and accepted architecture docs.

## Accepted Architecture Docs

Start with:

- [Temporal Object Resolver](architecture/TEMPORAL_OBJECT_RESOLVER.md)
- [Local Product Loop](architecture/LOCAL_PRODUCT_LOOP.md)
- [Workbench Local Loop](architecture/WORKBENCH_LOCAL_LOOP.md)
- [Public Alpha Launch Candidate](architecture/PUBLIC_ALPHA_LAUNCH_CANDIDATE.md)
- [Snapshot Relay](architecture/SNAPSHOT_RELAY.md)
- [Source Action Kernel](architecture/SOURCE_ACTION_KERNEL.md)
- [Source Family Model](architecture/SOURCE_FAMILY_MODEL.md)
- [Pack Import Pipeline](architecture/PACK_IMPORT_PIPELINE.md)
- [Master Index Review Queue](architecture/MASTER_INDEX_REVIEW_QUEUE.md)
- [Rust Backend Lane](architecture/RUST_BACKEND_LANE.md)
- [AI Policy](architecture/AI_POLICY.md)

The full architecture index is [architecture/README.md](architecture/README.md).

## Safety Posture

Architecture docs may describe future systems. Future architecture is not
current runtime behavior until implementation, validation, review, and promotion
evidence exist. Public mutation, live source fanout, downloads, uploads,
extraction, model/provider calls, deployment, native marketplace behavior, and
master/public index mutation remain disabled or gated as described in the root
[README](../README.md).
