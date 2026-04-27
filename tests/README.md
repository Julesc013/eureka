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

Search Usefulness Audit Delta v1 adds
`tests/operations/test_search_usefulness_audit_delta_v1.py` to validate the
second committed delta pack, v0 baseline reference, current audit counts,
archive-eval movement, pending/manual external-baseline posture, and Hard Eval
Satisfaction Pack v0 recommendation. It does not exercise product behavior.

Hard Eval Satisfaction Pack v0 adds
`tests/evals/test_hard_eval_satisfaction_pack.py` to validate the hard-eval
satisfaction report, source-backed partial movement, the unchanged
article-inside-scan capability gap, and the rule that no hard task is marked
overall satisfied without the still-deferred lane/bad-result checks.

Old-Platform Source Coverage Expansion v0 adds
`tests/integration/test_old_platform_source_coverage_expansion.py` and expands
component-local connector/index/compatibility tests. These checks guard the
expanded committed fixture corpus only; they do not add live source calls,
scraping, crawling, arbitrary local filesystem ingestion, or real binary
handling.
