# Contracts

`contracts/` holds governed assets that define shared meaning across Eureka:
schemas, packets, public API contracts, pack contracts, AI/provider boundaries,
index/review contracts, and shared UI contracts.

Contracts are authority for shape and semantics. They are not hidden runtime
behavior and do not by themselves implement import, indexing, uploads, live
connectors, model calls, executable plugins, public mutation, master-index
acceptance, or production behavior.

High-value contract areas:

- `contracts/archive/`: archive-facing contracts and fixtures
- `contracts/gateway/`: gateway/public API boundaries
- `contracts/pack/`: portable source/evidence/index/contribution/import report
  contracts
- `contracts/index/master/`: master index review queue contract material
- `contracts/ai/`: disabled-by-default future provider boundary
- `contracts/evidence/ledger/`: evidence ledger contract authority
- `contracts/surface/ui/`: shared surface/view-model contracts
- `contracts/connectors/`: connector contract boundaries

If a contract describes a future capability, look for matching validator, test,
audit, and runtime evidence before treating it as current behavior.
