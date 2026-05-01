# Command Results

P61 contract checks:

- `python scripts/validate_search_miss_ledger_entry.py --all-examples`:
  passed.
- `python scripts/validate_search_miss_ledger_entry.py --all-examples --json`:
  passed.
- `python scripts/validate_search_miss_ledger_contract.py`: passed.
- `python scripts/validate_search_miss_ledger_contract.py --json`: passed.
- `python scripts/dry_run_search_miss_ledger_entry.py --query "no-such-local-index-hit" --miss-type no_hits --json`:
  passed.

Compatibility and public-search checks:

- P59/P60 query-intelligence validators: passed.
- Hosted public search rehearsal: passed, 60/60 checks.
- Public search safety evidence: passed, 64/64 checks.
- Public search smoke: passed, 30/30 checks.
- Public index validation: passed, 584 documents.
- Static site build/check/validate and GitHub Pages artifact check: passed
  after rerunning static validators sequentially.
- Generated artifact drift guard: passed, 12 artifact groups.
- Archive resolution evals: passed, 6 satisfied.
- Search usefulness audit: passed, covered=5, partial=40, source_gap=10,
  capability_gap=7, unknown=2.
- External baseline status: passed, 192 pending manual observations.

Unittest lanes:

- `tests/scripts`: passed, 289 tests.
- `tests/operations`: passed, 455 tests.
- `tests/hardening`: passed, 53 tests.
- `tests/parity`: passed, 25 tests.
- `runtime`: passed, 320 tests.
- `surfaces`: passed, 168 tests.
- `tests`: passed, 913 tests.

Final checks:

- `python scripts/check_architecture_boundaries.py`: passed.
- `git diff --check`: passed.
- `cargo --version`: unavailable; Cargo is not installed in PATH.
