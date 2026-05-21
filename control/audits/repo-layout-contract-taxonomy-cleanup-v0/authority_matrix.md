# Authority Matrix

The complete matrix is in
`control/inventory/contract_taxonomy_authority_matrix.json`.

Key decisions:

- `contracts/repo/` is the authority for repo layout contracts.
- `contracts/sources/` is preferred for future source-family contracts.
- `contracts/stores/` is preferred for durable store schemas.
- `contracts/packs/` is pack contract authority.
- `contracts/views/workbench/` is reserved for Workbench view models.
- `contracts/search/interaction/` is reserved for Search Interaction packets.
- `control/schemas/` is control-schema authority only.
- `examples/` and `runtime/` are not product contract authority.
