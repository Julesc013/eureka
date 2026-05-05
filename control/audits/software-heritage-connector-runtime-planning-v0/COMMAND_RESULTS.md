# Command Results

Initial inspection:

- `git status --short --branch`: clean and aligned with origin.
- `git rev-parse HEAD`: recorded in the report JSON.
- `git rev-parse origin/main`: matched local HEAD at inspection.
- `git log --oneline -n 80`: confirmed P76 approval pack and P87-P91 runtime-planning lineage.

Policy inspection:

- P76 Software Heritage approval pack is present.
- `connector_approved_now` is false.
- Source sync, source cache, and evidence ledger contracts are present.
- Public search docs and hosted deployment evidence docs are present.

Verification:

- `python scripts/validate_software_heritage_connector_runtime_plan.py`: passed.
- `python scripts/validate_software_heritage_connector_runtime_plan.py --json`: passed.
- `python -m unittest tests.operations.test_software_heritage_connector_runtime_plan tests.scripts.test_validate_software_heritage_connector_runtime_plan`: passed.
- Software Heritage approval/contract validators and P87-P91 connector runtime planning validators: passed.
- Source sync, source cache, and evidence ledger contract validators: passed.
- P79-P86 page/identity/merge/ranking/query-observation validators: passed.
- Public search contract/card/safety/local/smoke/safety-evidence/rehearsal lanes: passed.
- Static site, publication inventory, public static site, GitHub Pages static artifact check, and generated artifact drift guard: passed.
- Archive resolution evals: passed, 6/6 satisfied.
- Search usefulness audit: passed, 64 queries with capability_gap=7, covered=5, partial=40, source_gap=10, unknown=2.
- External baseline comparison: valid but not eligible, 0 observed and 39 pending in Batch 0.
- Hosted deployment evidence: valid with blockers recorded; hosted backend is not configured and configured static route verification remains failed.
- Full unittest discovers passed: tests/scripts 607, tests/operations 580, tests/hardening 53, tests/parity 25, runtime 320, surfaces 168, tests 1356.
- `python scripts/check_architecture_boundaries.py`: passed.
- `git diff --check`: passed.

Optional commands:

- `gh` unavailable.
- `cargo` unavailable.
