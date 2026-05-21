# Duplicate Authority Report

The complete report is in
`control/inventory/contract_taxonomy_duplicate_authority_report.json`.

Recorded risks:

- `control/schemas/policies/packs/**` vs `contracts/packs/**`
- `contracts/source_registry/**` vs `contracts/sources/**`
- `contracts/source_cache/**` vs `contracts/stores/source_cache_*.json`
- `contracts/runtime/**` vs `runtime/**`
- `contracts/archive/**` vs `archive/**`
- `control/inventory/repo_layout_*.json` vs `contracts/repo/*.contract.toml`

All risks are recorded as migration backlog and do not block Workbench
Foundation because R0-03 reserves the future contract locations.
