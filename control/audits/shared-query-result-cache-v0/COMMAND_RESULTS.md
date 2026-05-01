# Command Results

P60-focused checks passed:

- `python scripts/validate_search_result_cache_entry.py --all-examples`
- `python scripts/validate_search_result_cache_entry.py --all-examples --json`
- `python scripts/validate_shared_query_result_cache_contract.py`
- `python scripts/validate_shared_query_result_cache_contract.py --json`
- `python scripts/dry_run_search_result_cache_entry.py --query "windows 7 apps" --json`

Compatibility, site, generated-artifact, and public-search checks passed,
including hosted rehearsal, safety evidence, static search integration, public
index validation, public-search smoke, static site build/validate, and generated
artifact drift.

Eval/status results:

- Archive resolution evals: 6 satisfied.
- Search usefulness audit: covered=5, partial=40, source_gap=10,
  capability_gap=7, unknown=2.
- External baselines: 192 pending manual observations; no external querying or
  scraping was performed.

Unittest lanes passed:

- `tests/scripts`: 274 tests.
- `tests/operations`: 449 tests.
- `tests/hardening`: 53 tests.
- `tests/parity`: 25 tests.
- `runtime`: 320 tests.
- `surfaces`: 168 tests.
- full `tests` discovery: 892 tests.

Final local checks:

- `python scripts/check_architecture_boundaries.py` passed.
- `git diff --check` passed.
- Optional `cargo --version` was unavailable because `cargo` was not installed
  in `PATH`.
