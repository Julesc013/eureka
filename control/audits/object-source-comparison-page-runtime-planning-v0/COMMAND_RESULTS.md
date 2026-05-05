# Command Results

Initial inspection:

- `git status --short --branch`: clean and aligned with origin.
- `git rev-parse HEAD`: recorded in the report JSON.
- `git rev-parse origin/main`: matched local HEAD at inspection.
- `git log --oneline -n 80`: confirmed P79-P92 planning/contract lineage.

Prerequisite checks:

- Object page contract validator: passed.
- Source page contract validator: passed.
- Comparison page contract validator: passed.
- Public search index validator: passed.
- Public search contract, result card contract, safety, and local runtime validators: passed.

Verification:

- `python scripts/validate_page_runtime_plan.py`: passed.
- `python scripts/validate_page_runtime_plan.py --json`: passed.
- `python -m unittest tests.operations.test_page_runtime_plan tests.scripts.test_validate_page_runtime_plan`: passed.
- Object/source/comparison page contract validators: passed.
- Public search index validator: passed, 584 documents, no private paths detected.
- P87-P92 connector runtime planning validators and P82-P86 identity/merge/ranking/query-observation validators: passed.
- Public search contract/card/safety/local/smoke/safety-evidence/rehearsal lanes: passed.
- Static site, publication inventory, public static site, GitHub Pages static artifact check, and generated artifact drift guard: passed.
- Archive resolution evals: passed, 6/6 satisfied.
- Search usefulness audit: passed, 64 queries with capability_gap=7, covered=5, partial=40, source_gap=10, unknown=2.
- External baseline comparison: valid but not eligible, 0 observed and 39 pending in Batch 0.
- Hosted deployment evidence: valid with blockers recorded; hosted backend is not configured and configured static route verification remains failed.
- Full unittest discovers passed: tests/scripts 610, tests/operations 584, tests/hardening 53, tests/parity 25, runtime 320, surfaces 168, tests 1363.
- `python scripts/check_architecture_boundaries.py`: passed.
- `git diff --check`: passed.

Optional commands:

- `gh` unavailable.
- `cargo` unavailable.
