# Evidence Contract Location Decision

Decision: create `contracts/evidence/` as a minimal pointer namespace.

## Rationale

Track B warned that evidence contract material was described through reference
docs and inventories rather than a `contracts/evidence/` location. The repo
already has canonical schema-only evidence ledger contracts under
`contracts/evidence_ledger/`, plus governance policies under
`control/inventory/evidence_ledger/`.

Creating a second full evidence schema family would duplicate existing
contracts and risk speculative semantics. IA-BUNDLE-00 therefore adds only a
small `contracts/evidence/` index that points to the existing governed evidence
ledger contracts and policy inventories.

## Scope

The new namespace:

- identifies `contracts/evidence_ledger/` as the current canonical schema
  family for evidence ledger records and manifests
- identifies `control/inventory/evidence_ledger/` as the current policy and
  runtime-planning inventory
- keeps evidence acceptance, candidate acceptance, source-cache mutation,
  evidence-ledger mutation, public-index mutation, and master-index mutation
  disabled

## Non-Goals

- no evidence schema redesign
- no evidence runtime
- no source-cache write
- no evidence-ledger write
- no candidate promotion
- no accepted evidence truth
- no public truth
- no IA source access

## Follow-Up

H0 may later decide whether to keep `contracts/evidence/` as a permanent
namespace, split contract families, or promote additional source operating
system contracts. IA-BUNDLE-01 may reference this namespace, but should not
expand it unless the connector foundation task needs a concrete contract
pointer.
