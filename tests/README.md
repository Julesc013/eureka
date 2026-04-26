# Root Tests

`tests/` is reserved for verification that crosses component boundaries.

- `architecture/`: repo-local architectural guardrail checks and synthetic violation fixtures for the narrow boundary checker
- `evals/`: repo-level validation for shared benchmark and evaluation assets
- `hardening/`: high-risk regression guards for eval truth, public-alpha path
  safety, route/docs/README drift, parity/golden discipline, and repo
  operating metadata consistency
- `integration/`: cross-component checks across contracts, runtime, and surfaces
- `operations/`: repo-operating checks for public-alpha posture, hosting-pack
  evidence, test/eval operating-layer metadata, and audit packs
- `parity/`: planning docs for future Python-oracle to Rust-candidate parity checks
- `end_to_end/`: higher-level product workflow checks once real behavior exists

Component-local tests stay with their owning component and should not be duplicated here.

Result Lanes + User-Cost Ranking v0 adds component-local ranking tests under
`runtime/engine/ranking/tests/` plus cross-component checks where lane/cost
annotations flow through public search and index projection. These tests guard
bounded deterministic usefulness hints only, not production ranking.
