# Contract Taxonomy Cleanup Plan

R0-03 is a classification and validator task. It locks authority before
Workbench Foundation without broad moves or runtime changes.

## Scope

- Inventory `contracts/`, `contracts/control_schemas/`, `control/policies/`,
  `control/inventory/`, `examples/`, `runtime/`, and validator scripts.
- Classify product contracts, internal contracts, control schemas, policies,
  inventories, audit reports, fixtures, generated artifacts, and quarantine
  candidates.
- Record duplicate authority risks.
- Retain `contracts/control_schemas/` as control-schema authority only.
- Reserve Workbench contracts under `contracts/views/workbench/`.
- Reserve Search Interaction contracts under `contracts/search/interaction/`.

## Decisions

Product/public contracts live under `contracts/`.

Control schemas may remain under `contracts/control_schemas/` only for control-plane
schemas. Any product-like material there is migration debt, not product truth.

Examples are examples. They do not define registry authority or accepted truth.

Runtime owns implementation. Runtime helpers may validate local payloads, but
stable contract semantics live under `contracts/`.

## Migration Backlog

The backlog is recorded in
`control/inventory/contract_taxonomy_migration_backlog.json`. The immediate
items are:

- Reclassify or migrate `contracts/control_schemas/policies/packs/**`.
- Collapse `contracts/source_registry/**` vs `contracts/sources/**`.
- Clarify `contracts/source_cache/**` vs `contracts/stores/**`.
- Narrow `contracts/runtime/**` to stable boundary packets.
- Keep `contracts/archive/**` distinct from the top-level `archive/` root.
- Add concrete Workbench view-model contracts during Workbench Foundation.
- Add concrete Search Interaction packets during Search Interaction.
- Keep generated artifact exceptions under `contracts/repo/`.

## Why This Precedes Workbench

Workbench Foundation will touch view models, result lanes, packets, runtime
services, surfaces, docs, and validators. Without a taxonomy, Workbench could
accidentally place contract law in presentation code, runtime helper code, or
examples. R0-03 prevents that drift.

## No-Go

R0-03 does not move large trees, delete schemas, alter runtime behavior, run live
source probes, use model providers, deploy, or claim production/public readiness.
