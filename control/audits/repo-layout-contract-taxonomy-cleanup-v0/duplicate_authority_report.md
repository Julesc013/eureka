# Duplicate Authority Report

The complete report is in
`control/inventory/contract_taxonomy_duplicate_authority_report.json`.

Recorded risks:

- `contracts/schema/control/policies/packs/**` vs `contracts/pack/**`
- `contracts/source/registry/**` vs `contracts/source/records/**`
- `contracts/source/cache/**` vs `contracts/stores/source_cache_*.json`
- `contracts/runtime/**` vs `runtime/**`
- `contracts/archive/**` vs `archive/**`
- `control/inventory/repo_layout_*.json` vs `contracts/repo/*.contract.toml`

All risks are recorded as migration backlog and do not block Workbench
Foundation because R0-03 reserves the future contract locations.
