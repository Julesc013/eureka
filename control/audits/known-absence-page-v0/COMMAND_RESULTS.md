# Command Results

Verified locally on 2026-05-02.

P66 required commands:

- `python scripts/validate_known_absence_page.py --all-examples`: passed
- `python scripts/validate_known_absence_page.py --all-examples --json`: passed
- `python scripts/validate_known_absence_page_contract.py`: passed
- `python scripts/validate_known_absence_page_contract.py --json`: passed
- `python scripts/dry_run_known_absence_page.py --query "no-such-local-index-hit" --absence-status scoped_absence --json`: passed
- `python -m unittest tests.operations.test_known_absence_page_contract tests.scripts.test_validate_known_absence_page tests.scripts.test_validate_known_absence_page_contract tests.scripts.test_dry_run_known_absence_page`: passed, 18 tests.

Regression sweep:

- 63 commands run.
- 63 passed.
- 0 failed.
- Included P59-P65 query-intelligence validators, hosted/public search rehearsal and safety validators, static search integration, public index builder/index validators, public search smoke checks, static site checks, archive/search usefulness evals, external baseline status, unit discovery lanes, architecture boundary checks, and `git diff --check`.

Search usefulness and archive status:

- Archive resolution evals: passed, `satisfied=6`.
- Search usefulness audit: passed, `covered=5`, `partial=40`, `source_gap=10`, `capability_gap=7`, `unknown=2`.
- External baseline status: ready with 192 global pending manual slots, 39 Batch 0 pending manual slots, and 0 observed slots.

Optional Rust:

- `cargo --version`: unavailable; Cargo is not recognized in this environment.
- `cargo check --workspace --manifest-path crates/Cargo.toml`: not run because Cargo is unavailable.
- `cargo test --workspace --manifest-path crates/Cargo.toml`: not run because Cargo is unavailable.

Final local checks before commit:

- `git diff --check`: passed. PowerShell reported expected CRLF normalization warnings for existing `site/dist` text files, but no whitespace errors.
- `git status --short --branch`: dirty with P66 changes before commit.

P66 remains contract-only. It adds no runtime known absence pages, no telemetry, no persistent query logging, no live probes, no source cache or evidence ledger runtime, no candidate promotion, and no public/master/local index mutation.
