# View Model Policy Index Contract

ViewModelPolicyIndex v0 defines the governed Track A index over Eureka
representation contracts, semantic parity policies, the route/view/
representation matrix, canonical view-model policies, examples, validators,
tests, and reference documentation. It is contract and governance work only.

## Purpose

The policy index gives future renderer and runtime work one place to answer:

- which canonical view models exist
- which schema and policy inventory controls each one
- which route families bind to it
- which representation profiles may render it
- which semantic parity policies apply
- which examples demonstrate it
- which validators prove it
- which product-boundary claims must stay false

## Required Meaning

The index preserves the Track A doctrine:

- one resolver truth
- one route meaning
- one canonical view-model layer
- many compatible projections
- renderers may simplify presentation only
- renderers must not change source, evidence, status, rights, risk,
  limitation, action, route, absence, candidate, review, or provenance meaning

## Product Boundary

The policy index must keep all Track A product-boundary fields false. It does
not activate routes, hosting, live probes, source sync, connectors, downloads,
installers, execution, uploads, accounts, telemetry, native projects, node
runtime, pack import runtime, review runtime, or master-index mutation.

It also must not claim rights clearance, malware safety, verified
installability, public truth from candidates/packs/reviews/evidence,
exhaustive global search, or automatic merge/deduplication/promotion.

## Validation

Use:

```powershell
python scripts/validate_view_model_policy_index.py
python scripts/validate_track_a_contracts.py
```

The first command validates the index itself. The second command runs the full
Track A validator family in deterministic order.

## Related Contracts

- `contracts/view/pages/view_model_policy_index.v0.json`
- `control/inventory/publication/view_model_policy_index.json`
- `docs/operations/TRACK_A_VALIDATION.md`
- `contracts/representation/semantic_renderer_parity.v0.json`
- `contracts/representation/route_view_representation_matrix.v0.json`
- all Track A canonical view-model contracts under `contracts/view/pages/`

## No-Goals

- No runtime behavior changes.
- No route activation.
- No generated site artifact mutation.
- No hosted backend, live probes, source connectors, source sync, node runtime,
  autonomous runtime, pack import runtime, review/moderation runtime,
  downloads, installers, execution, uploads, accounts, or telemetry.
- No master-index mutation or native project creation.
- No public truth, exhaustive search, rights, malware, installability, or
  automatic promotion claims.
