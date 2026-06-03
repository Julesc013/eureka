# TSIS-00 - Temporal Semantic Interface System Foundation

Status: completed locally pending final commit.

Purpose:

- Establish the Temporal Semantic Interface System foundation without adding
  top-level renderer/app/service/data/infra roots.
- Put semantic law in `contracts/`.
- Define the future Surface Kernel placement under `runtime/surface/` without
  implementing it in TSIS-00.
- Keep product-facing projections under existing `surfaces/` authority.

Evidence:

- `contracts/semantic/`
- `contracts/representation/renderer_contract.v0.json`
- `contracts/representation/skin_contract.v0.json`
- `contracts/representation/compatibility_budget.v0.json`
- `contracts/representation/fallback_rule.v0.json`
- `contracts/representation/cache_key.v0.json`
- `contracts/view/*/*.v0.json`
- `control/inventory/semantic_status_registry.json`
- `control/inventory/semantic_affordance_registry.json`
- `control/inventory/representation_profile_registry.json`
- `control/inventory/tsis_00_result.json`
- `control/audits/tsis-00-v0/`

Boundaries:

- no deployment
- no public launch
- no `site/dist` write
- no public/master index mutation
- no live source calls
- no downloads, file fetches, OCR, extraction, or model/provider calls
- no runtime behavior changes
- no Surface Kernel runtime implementation in TSIS-00
- no new top-level `renderers/`, `skins/`, `services/`, `apps/`, `data/`, or
  `infra/` roots
