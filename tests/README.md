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

Compatibility Evidence Pack v0 adds component-local compatibility-evidence
tests under `runtime/engine/compatibility/tests/` plus projection checks where
source-backed evidence flows through local index, search, compatibility, CLI,
and web output. These tests guard fixture-backed evidence and unknown outcomes,
not a compatibility oracle or installer/runtime execution behavior.

Search Usefulness Audit Delta v0 adds
`tests/operations/test_search_usefulness_audit_delta.py` to validate the
committed delta pack, baseline limitations, selected wedges, current audit
counts, pending/manual external-baseline posture, and next recommendation. It
does not exercise product behavior.
