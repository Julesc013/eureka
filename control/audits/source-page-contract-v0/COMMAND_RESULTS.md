# Command Results

P80 verification was run locally on Tuesday, May 5, 2026.

## Passed

- `python scripts/validate_source_page.py --all-examples`
- `python scripts/validate_source_page.py --all-examples --json`
- `python scripts/validate_source_page_contract.py`
- `python scripts/validate_source_page_contract.py --json`
- `python scripts/dry_run_source_page.py --source-id internet-archive-placeholder --source-family internet_archive --json`
- Source page unittest slice: `tests.operations.test_source_page_contract`, `tests.scripts.test_validate_source_page`, `tests.scripts.test_validate_source_page_contract`, `tests.scripts.test_dry_run_source_page`
- Adjacent object page, external baseline, hosted deployment, connector approval, source sync/cache/evidence, query-intelligence, public-search, site, generated-artifact, archive-eval, search-usefulness, public-alpha, and unit discovery lanes listed in the final P80 verification.
- `python scripts/check_architecture_boundaries.py` checked 446 Python files.
- `git diff --check` exited 0 with the existing CRLF warning for `site/dist/assets/site.css`.

## Eval Status

- Search usefulness: covered=5, partial=40, source_gap=10, capability_gap=7, unknown=2.
- Archive resolution evals: satisfied=6.
- External baseline comparison: not eligible; Batch 0 has 0 observed and 39 pending manual observations.
- Hosted deployment evidence: static site remains `verified_failed`; hosted backend remains `not_configured`.

## Optional

- `cargo --version` failed because Cargo is unavailable in this environment. Optional `cargo check` and `cargo test` were not run.
