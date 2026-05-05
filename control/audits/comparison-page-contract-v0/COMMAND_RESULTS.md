# Command Results

P81 verification completed on the local workspace.

## Focused P81 Commands

- Passed: `python scripts/validate_comparison_page.py --all-examples` (5 examples).
- Passed: `python scripts/validate_comparison_page.py --all-examples --json`.
- Passed: `python scripts/validate_comparison_page_contract.py`.
- Passed: `python scripts/validate_comparison_page_contract.py --json`.
- Passed: `python scripts/dry_run_comparison_page.py --label "Compare two Windows 7 compatible app candidates" --comparison-type object_identity_comparison --json`.
- Passed: `python -m unittest tests.operations.test_comparison_page_contract tests.scripts.test_validate_comparison_page tests.scripts.test_validate_comparison_page_contract tests.scripts.test_dry_run_comparison_page`.

## Adjacent Governance

- Passed adjacent page contracts: Source Page v0 and Object Page v0.
- Passed connector approval examples: Software Heritage, npm, PyPI, GitHub Releases, Wayback/CDX/Memento, and Internet Archive.
- Passed source/query contracts: source sync worker, source cache/evidence ledger, demand dashboard, privacy/poisoning guard, known absence, candidate promotion, candidate index, probe queue, search need, miss ledger, shared query result cache, and query observation.

## Public Search, Static Site, And Evals

- Passed hosted public search rehearsal and validator.
- Passed public search safety evidence runner and validator.
- Passed static site search integration, public search index builder/index, hosted wrapper, production contract, public search contracts/smokes, site build/validate, publication/static checks, generated artifact drift guard, public alpha smoke, archive evals, search usefulness audit, external baseline status, and Python oracle golden check.
- Search usefulness: covered=5, partial=40, source_gap=10, capability_gap=7, unknown=2, total=64.
- Archive evals: satisfied=6 of 6.

## Unit And Architecture Lanes

- Passed unittest discovery: tests/scripts=525, tests/operations=542, tests/hardening=53, tests/parity=25, runtime=320, surfaces=168, tests=1236.
- Passed `python scripts/check_architecture_boundaries.py` across 446 Python files.
- Passed `git diff --check`; only existing CRLF conversion warnings were emitted.

## Deployment/Baseline Status

- P77 hosted deployment evidence remains unchanged: static site status `verified_failed`, hosted backend `not_configured`.
- P78 external baseline status remains unchanged: Batch 0 has 0 observed and 39 pending manual observations.

## Optional Commands

- `cargo --version` failed because Cargo is not installed or not on PATH; optional cargo check/test were not run.
- `gh --version` and `gh auth status` failed because GitHub CLI is not installed or not on PATH; GitHub Actions status is unverified.
